"""Registration-at-read for the generalized v2 authentication route.

The active session is deliberately context-local.  Shared readers can use
the helpers in this module without changing historical/v1 behavior: when no
session is active they delegate directly to :class:`pathlib.Path`.  During a
v2 mint, every returned byte string has already been strict-parsed when its
wire grammar is JSON/JSONL and registered against its first observed digest.

Inside a block-5 analysis run (``analysis_run_cache``), a successful strict
parse is remembered by (sha256, effective grammar, governed-vocabulary flag),
and identical bytes under the same key are not parsed again (D-188 L7).  Only
successes are remembered: a failing parse always re-runs and raises its own
error at its own read.  A passive read recorder
(``recording_authentication_reads``) lets the run-scoped derivation store see
every read these APIs perform; it never changes what a read returns or raises.
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
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, BinaryIO, Iterator, Literal, Mapping, TextIO

from joulewise import analysis_run_cache as _run_cache


AuthenticationGrammar = Literal["json", "jsonl", "raw"]
V2_AUTHENTICATION_INPUT_CHANGED = "v2_authentication_input_changed"
V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH = (
    "v2_authentication_input_digest_mismatch"
)


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


@dataclass(frozen=True)
class AuthenticationReadRow:
    """One successful read through an authentication_io API (D-188 AUTH-IO).

    ``identity`` is the absolute identity the v2 session uses for the input
    (``Path.resolve(strict=False)``; ``git:HEAD:<path>`` for git ingests), or
    ``None`` when it could not be computed, which makes the read
    unattributable.  ``grammar`` is the effective (forced) grammar this read's
    identity implies; ``caller_grammar`` is the grammar the caller asked for,
    so a consumer can recompute ``forced_grammar(its_identity,
    caller_grammar)`` instead of trusting the recorded grammar.
    ``grammar_verified`` is true only when this read itself ran the strict
    grammar check under ``(grammar, vocabulary_flag)`` and it succeeded (an
    in-session read); a session-less read never parses, so it is false there.
    ``relative`` carries the contained relative name of a no-follow read.
    """

    api: str
    identity: str | None
    sha256: str
    grammar: AuthenticationGrammar
    caller_grammar: AuthenticationGrammar
    label: str
    in_session: bool
    grammar_verified: bool
    vocabulary_flag: bool
    relative: str | None = None


# A passive recorder: a tuple of row sinks (one per nested recording scope),
# or None.  Recording never changes what a read returns or raises.
_READ_RECORDER: ContextVar[tuple[list[AuthenticationReadRow], ...] | None] = (
    ContextVar("joulewise_authentication_read_recorder", default=None)
)

# The run-scoped success-only memo of the strict grammar verdict (L7), keyed
# by (sha256 of the bytes, effective grammar, governed-vocabulary flag).
GRAMMAR_VERDICT_MEMO = "authentication_io.grammar_ok"


@contextmanager
def recording_authentication_reads() -> Iterator[list[AuthenticationReadRow]]:
    """Record every successful authentication_io read in this context.

    Nested scopes each receive every row read inside them.  Rows are appended
    after the read (and, in a session, its strict parse and registration)
    succeeded; a read that raises appends nothing.
    """

    rows: list[AuthenticationReadRow] = []
    sinks = _READ_RECORDER.get()
    token = _READ_RECORDER.set((rows,) if sinks is None else (*sinks, rows))
    try:
        yield rows
    finally:
        _READ_RECORDER.reset(token)


def authentication_read_recording_active() -> bool:
    return _READ_RECORDER.get() is not None


def _absolute_identity(path: Path | str) -> str | None:
    try:
        return str(Path(path).resolve(strict=False))
    except (OSError, RuntimeError, ValueError):
        return None


def _record_read(
    sinks: tuple[list[AuthenticationReadRow], ...],
    *,
    api: str,
    identity: str | None,
    digest: str,
    grammar: AuthenticationGrammar,
    caller_grammar: AuthenticationGrammar,
    label: str,
    in_session: bool,
    grammar_verified: bool,
    vocabulary_flag: bool,
    relative: str | None = None,
) -> None:
    row = AuthenticationReadRow(
        api=api,
        identity=identity,
        sha256=digest,
        grammar=grammar,
        caller_grammar=caller_grammar,
        label=label,
        in_session=in_session,
        grammar_verified=grammar_verified,
        vocabulary_flag=vocabulary_flag,
        relative=relative,
    )
    for sink in sinks:
        sink.append(row)


def _record_sessionless(
    sinks: tuple[list[AuthenticationReadRow], ...],
    *,
    api: str,
    identity_path: Path | str,
    raw_or_digest: bytes | str,
    caller_grammar: AuthenticationGrammar,
    label: str,
    relative: str | None = None,
) -> None:
    identity = _absolute_identity(identity_path)
    digest = (
        raw_or_digest
        if isinstance(raw_or_digest, str)
        else hashlib.sha256(raw_or_digest).hexdigest()
    )
    _record_read(
        sinks,
        api=api,
        identity=identity,
        digest=digest,
        grammar=_forced_grammar(
            identity if identity is not None else str(identity_path),
            caller_grammar,
        ),
        caller_grammar=caller_grammar,
        label=label,
        in_session=False,
        grammar_verified=False,
        vocabulary_flag=False,
        relative=relative,
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


class _RecordedAuthenticationPath(type(Path())):
    """A plain ``Path`` that also records its content reads (D-188 AUTH-IO).

    Injected by :func:`v2_authentication_path` only while a read recorder is
    active and no v2 session is: it lets a session-less fill account for the
    reads a capability path would register in a session (for example the
    reducer's direct ``read_bytes``), so a consumer can bridge their grammar.
    It never routes through a v2 session, even one entered later, so what it
    returns or raises is exactly what ``Path`` returns or raises.
    """

    __slots__ = ()

    def _record(self, api: str, raw: bytes) -> None:
        sinks = _READ_RECORDER.get()
        if sinks is not None:
            _record_sessionless(
                sinks,
                api=api,
                identity_path=self,
                raw_or_digest=raw,
                caller_grammar="raw",
                label=f"v2 path capability {self}",
            )

    def read_bytes(self) -> bytes:
        if _READ_RECORDER.get() is None:
            return super().read_bytes()
        # Path.read_bytes dispatches to self.open on some versions; open the
        # base way here so one read yields exactly one row.
        with super().open("rb") as handle:
            raw = handle.read()
        self._record("v2_path.read_bytes", raw)
        return raw

    def read_text(
        self,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> str:
        if _READ_RECORDER.get() is None:
            return super().read_text(encoding=encoding, errors=errors)
        with super().open("r", encoding=encoding, errors=errors) as handle:
            raw = handle.buffer.read()
            text = io.TextIOWrapper(
                io.BytesIO(raw),
                encoding=handle.encoding,
                errors=handle.errors,
            ).read()
        self._record("v2_path.read_text", raw)
        return text

    def open(
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> BinaryIO | TextIO:
        if _READ_RECORDER.get() is None or not (
            "r" in mode and not any(flag in mode for flag in ("w", "a", "x", "+"))
        ):
            return super().open(
                mode=mode,
                buffering=buffering,
                encoding=encoding,
                errors=errors,
                newline=newline,
            )
        with super().open(
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        ) as handle:
            if "b" in mode:
                raw = handle.read()
                served: BinaryIO | TextIO = io.BytesIO(raw)
            else:
                raw = handle.buffer.read()
                served = io.TextIOWrapper(
                    io.BytesIO(raw),
                    encoding=handle.encoding,
                    errors=handle.errors,
                    newline=newline,
                )
        self._record("v2_path.open", raw)
        return served


def v2_authentication_path(path: Path | str) -> Path:
    """Inject a registration-aware path only for an active v2 session.

    With no session but an active read recorder, the path is a plain-``Path``
    equivalent that records its content reads.
    """

    if _ACTIVE_SESSION.get() is None:
        if _READ_RECORDER.get() is not None:
            return _RecordedAuthenticationPath(path)
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


def forced_grammar(
    identity: str, caller_grammar: AuthenticationGrammar
) -> AuthenticationGrammar:
    """The effective grammar a v2 session applies to ``identity``.

    A consumer bridging recorded rows into its own session must use its own
    identity and the recorded ``caller_grammar`` here, not a recorded
    effective grammar (a session-less fill may have recorded ``raw``).
    """

    return _forced_grammar(identity, caller_grammar)


def _parse_strict_memoized(
    raw: bytes,
    digest: str,
    grammar: AuthenticationGrammar,
    label: str,
    allow_governed_spec_vocabulary: bool,
) -> None:
    """``_parse_strict`` behind the run's success-only verdict memo (L7).

    ``_parse_strict`` is a pure function of (bytes, grammar, vocabulary
    flag); ``label`` reaches only the text of a raised error.  A key is
    stored only after a parse returned normally, so every failure always
    re-runs the identical parse and raises its own type, message and
    position.  Outside an analysis run there is no memo and every read parses.
    """

    if grammar != "json" and grammar != "jsonl":
        _parse_strict(
            raw,
            grammar,
            label,
            allow_governed_spec_vocabulary=allow_governed_spec_vocabulary,
        )
        return
    table = _run_cache.memo(GRAMMAR_VERDICT_MEMO)
    key = (digest, grammar, allow_governed_spec_vocabulary)
    if table is not None and key in table:
        return
    _parse_strict(
        raw,
        grammar,
        label,
        allow_governed_spec_vocabulary=allow_governed_spec_vocabulary,
    )
    if table is not None:
        table[key] = True


def ensure_grammar_verdict(
    raw: bytes,
    sha256: str,
    grammar: AuthenticationGrammar,
    vocabulary_flag: bool,
    label: str,
) -> None:
    """Establish the strict grammar verdict for ``raw`` or raise exactly as a read would.

    Runs the identical ``_parse_strict`` that ``V2AuthenticationReadSession
    .read`` runs (same grammar, vocabulary flag and label) unless the run's
    success memo already holds ``(sha256, grammar, vocabulary_flag)``, and
    records a success.  ``sha256`` is cross-checked against ``raw``: on a
    mismatch the memo is neither consulted nor written and the bytes are
    parsed.  ``grammar`` must be the consumer's effective grammar
    (``forced_grammar(identity, caller_grammar)``).
    """

    digest = hashlib.sha256(raw).hexdigest()
    if digest != sha256:
        _parse_strict(
            raw,
            grammar,
            label,
            allow_governed_spec_vocabulary=vocabulary_flag,
        )
        return
    _parse_strict_memoized(raw, digest, grammar, label, bool(vocabulary_flag))


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

    def vocabulary_flag(self, identity: str) -> bool:
        """The governed-vocabulary flag a read of ``identity`` would parse under."""

        with self._lock:
            return identity in self._governed_spec_vocabulary_identities

    def ensure_grammar_verdict(
        self,
        identity: str,
        raw: bytes,
        *,
        caller_grammar: AuthenticationGrammar,
        label: str,
        sha256: str | None = None,
    ) -> AuthenticationGrammar:
        """Bridge a recorded read into this session's grammar check.

        Uses this session's own effective grammar
        ``forced_grammar(identity, caller_grammar)`` and vocabulary flag for
        ``identity`` (the absolute identity a read here would register), and
        raises exactly what ``read`` would for the same bytes and label.
        Returns the effective grammar.  It registers nothing.
        """

        effective = _forced_grammar(identity, caller_grammar)
        ensure_grammar_verdict(
            raw,
            hashlib.sha256(raw).hexdigest() if sha256 is None else sha256,
            effective,
            self.vocabulary_flag(identity),
            label,
        )
        return effective

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
            digest = hashlib.sha256(raw).hexdigest()
            vocabulary = normalized in self._governed_spec_vocabulary_identities
            _parse_strict_memoized(raw, digest, effective, label, vocabulary)
            self._register(normalized, digest, effective, label)
            sinks = _READ_RECORDER.get()
            if sinks is not None:
                _record_read(
                    sinks,
                    api="session.read",
                    identity=normalized,
                    digest=digest,
                    grammar=effective,
                    caller_grammar=grammar,
                    label=label,
                    in_session=True,
                    grammar_verified=True,
                    vocabulary_flag=vocabulary,
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
            digest = hashlib.sha256(raw).hexdigest()
            vocabulary = identity in self._governed_spec_vocabulary_identities
            _parse_strict_memoized(raw, digest, effective, label, vocabulary)
            self._register(identity, digest, effective, label)
            sinks = _READ_RECORDER.get()
            if sinks is not None:
                _record_read(
                    sinks,
                    api="session.read_nofollow",
                    identity=identity,
                    digest=digest,
                    grammar=effective,
                    caller_grammar=grammar,
                    label=label,
                    in_session=True,
                    grammar_verified=True,
                    vocabulary_flag=vocabulary,
                    relative=relative,
                )
            return raw

    def read_nofollow_pinned(
        self,
        directory: Path | str,
        relative: str,
        *,
        expected_sha256: str,
        grammar: AuthenticationGrammar,
        label: str,
    ) -> bytes:
        """Hash a no-follow read against its pin before strict parsing."""

        root = Path(directory)
        identity = str((root / relative).resolve(strict=False))
        effective = _forced_grammar(identity, grammar)
        with self._lock:
            raw = _read_nofollow_bytes(root, relative)
            digest = hashlib.sha256(raw).hexdigest()
            if digest != expected_sha256:
                raise V2AuthenticationInputError(
                    V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH,
                    f"{label} ({identity}) does not match its caller pin",
                )
            vocabulary = identity in self._governed_spec_vocabulary_identities
            _parse_strict_memoized(raw, digest, effective, label, vocabulary)
            self._register(identity, digest, effective, label)
            sinks = _READ_RECORDER.get()
            if sinks is not None:
                _record_read(
                    sinks,
                    api="session.read_nofollow_pinned",
                    identity=identity,
                    digest=digest,
                    grammar=effective,
                    caller_grammar=grammar,
                    label=label,
                    in_session=True,
                    grammar_verified=True,
                    vocabulary_flag=vocabulary,
                    relative=relative,
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
            vocabulary = identity in self._governed_spec_vocabulary_identities
            digest = hashlib.sha256(raw).hexdigest()
            _parse_strict_memoized(raw, digest, effective, label, vocabulary)
            self._register(identity, digest, effective, label)
            sinks = _READ_RECORDER.get()
            if sinks is not None:
                _record_read(
                    sinks,
                    api="session.ingest",
                    identity=identity,
                    digest=digest,
                    grammar=effective,
                    caller_grammar=grammar,
                    label=label,
                    in_session=True,
                    grammar_verified=True,
                    vocabulary_flag=vocabulary,
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
            sinks = _READ_RECORDER.get()
            if sinks is not None:
                _record_read(
                    sinks,
                    api="session.sha256_streaming_raw",
                    identity=normalized,
                    digest=hexdigest,
                    grammar="raw",
                    caller_grammar="raw",
                    label=label,
                    in_session=True,
                    grammar_verified=True,
                    vocabulary_flag=(
                        normalized in self._governed_spec_vocabulary_identities
                    ),
                )
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
        raw = Path(path).read_bytes()
        sinks = _READ_RECORDER.get()
        if sinks is not None:
            _record_sessionless(
                sinks,
                api="read_authentication_input",
                identity_path=path,
                raw_or_digest=raw,
                caller_grammar=grammar,
                label=label,
            )
        return raw
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
        sinks = _READ_RECORDER.get()
        if sinks is None:
            return Path(path).read_text(**kwargs)
        # Recording: the same text-mode open (same encoding resolution and
        # open errors) as Path.read_text, its bytes taken once from the
        # binary buffer and decoded by an identical TextIOWrapper.
        with Path(path).open("r", **kwargs) as handle:
            raw = handle.buffer.read()
            text = io.TextIOWrapper(
                io.BytesIO(raw),
                encoding=handle.encoding,
                errors=handle.errors,
            ).read()
        _record_sessionless(
            sinks,
            api="read_authentication_text",
            identity_path=path,
            raw_or_digest=raw,
            caller_grammar=grammar,
            label=label,
        )
        return text
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
        sinks = _READ_RECORDER.get()
        if sinks is None:
            return Path(path).open(mode, **kwargs)
        # Recording: the same open, its bytes taken once and served from
        # memory (as an active session serves them), so the recorded digest
        # is the digest of exactly the bytes the caller consumes.
        with Path(path).open(mode, **kwargs) as handle:
            if "b" in mode:
                raw = handle.read()
                served: BinaryIO | TextIO = io.BytesIO(raw)
            else:
                raw = handle.buffer.read()
                served = io.TextIOWrapper(
                    io.BytesIO(raw),
                    encoding=handle.encoding,
                    errors=handle.errors,
                    newline=newline,
                )
        _record_sessionless(
            sinks,
            api="open_authentication_input",
            identity_path=path,
            raw_or_digest=raw,
            caller_grammar=grammar,
            label=label,
        )
        return served
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
        raw = _read_nofollow_bytes(directory, relative)
        sinks = _READ_RECORDER.get()
        if sinks is not None:
            _record_sessionless(
                sinks,
                api="read_authentication_input_nofollow",
                identity_path=Path(directory) / relative,
                raw_or_digest=raw,
                caller_grammar=grammar,
                label=label,
                relative=relative,
            )
        return raw
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
        sinks = _READ_RECORDER.get()
        if sinks is not None:
            identity = f"git:HEAD:{relative_path}"
            _record_read(
                sinks,
                api="ingest_git_authentication_input",
                identity=identity,
                digest=hashlib.sha256(raw).hexdigest(),
                grammar=_forced_grammar(identity, grammar),
                caller_grammar=grammar,
                label=label,
                in_session=False,
                grammar_verified=False,
                vocabulary_flag=False,
            )
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
        hexdigest = digest.hexdigest()
        sinks = _READ_RECORDER.get()
        if sinks is not None:
            _record_sessionless(
                sinks,
                api="sha256_authentication_input",
                identity_path=path,
                raw_or_digest=hexdigest,
                caller_grammar="raw",
                label=label,
            )
        return hexdigest
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


def paper_supplier_signature_violations(
    source: str,
    *,
    marked_functions: set[str] | frozenset[str],
) -> tuple[str, ...]:
    """Reject public supplier signatures that can carry untrusted values.

    Paper suppliers receive one closed family ref.  Byte/object containers,
    arbitrary sequences, validation results, receipts, and variadic channels
    would recreate the bypass at the function boundary.
    """

    forbidden_annotations = {
        "Any",
        "Iterable",
        "Mapping",
        "MutableMapping",
        "Sequence",
        "bytearray",
        "bytes",
        "dict",
    }

    def annotation_names(annotation: ast.AST | None) -> set[str]:
        if annotation is None:
            return set()
        names: set[str] = set()
        for node in ast.walk(annotation):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
        return names

    tree = ast.parse(source)
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or (
            node.name not in marked_functions
        ):
            continue
        arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        for argument in arguments:
            forbidden = sorted(
                annotation_names(argument.annotation) & forbidden_annotations
            )
            if forbidden:
                violations.append(
                    f"{node.name}:{argument.arg}:annotation:{','.join(forbidden)}"
                )
            lowered = argument.arg.lower()
            if "receipt" in lowered or "validation_result" in lowered:
                violations.append(f"{node.name}:{argument.arg}:value-channel")
        if node.args.vararg is not None:
            violations.append(f"{node.name}:{node.args.vararg.arg}:variadic")
        if node.args.kwarg is not None:
            violations.append(f"{node.name}:{node.args.kwarg.arg}:variadic")
    return tuple(sorted(set(violations)))


__all__ = [
    "AuthenticationInputRecord",
    "AuthenticationReadRow",
    "GRAMMAR_VERDICT_MEMO",
    "V2AuthenticationPath",
    "V2AuthenticationInputError",
    "V2AuthenticationReadSession",
    "V2_AUTHENTICATION_INPUT_CHANGED",
    "V2_AUTHENTICATION_INPUT_DIGEST_MISMATCH",
    "active_v2_authentication_session",
    "authentication_read_recording_active",
    "direct_read_violations",
    "ensure_grammar_verdict",
    "forced_grammar",
    "ingest_git_authentication_input",
    "open_authentication_input",
    "paper_supplier_signature_violations",
    "read_authentication_input",
    "read_authentication_input_nofollow",
    "read_authentication_text",
    "recording_authentication_reads",
    "sha256_authentication_input",
    "v2_authentication_path",
]
