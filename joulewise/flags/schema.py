"""The ``joulewise.flag.v1`` record: one flag, one JSON line.

Fields (plan section 3.1):

``flag_id``
    ``sha256(canonical({code, scope, observed, source}))[:20]``. Two emissions
    of the same fact from the same source share an id, so sinks deduplicate.
``code``
    The catalog key, dotted lower-case, for example ``battery.member_span``.
``family`` / ``klass``
    Grouping and inventory class (PHYSICS, NUMBER or REPRESENTATION).
``scope``
    ``{level, plan_id, attempt, stage_id, run_id, bundle_id}``; every key is
    present, unknown values are ``null``.
``interval``
    ``{monotonic_ns, monotonic_raw_ns, wall_s}``, each ``[a, b]`` or ``null``.
    ``monotonic_ns`` is the controller's ``time.monotonic_ns()`` domain, the
    domain member spans are stamped in.
``source``
    ``{stage, collector, legacy_site, legacy_code}``; ``stage`` is one of
    desk, arm, window, harvest.
``observed`` / ``expected``
    The measured value or recomputed digest, and the limit or pinned value.
``evidence``
    ``[{path, sha256}]`` with ``path`` relative to the custody root.
``detail``
    One line of text.
``emitted``
    ``{wall_s, monotonic_ns, boot_session_uuid}`` at emission.
``catalog_sha256``
    SHA-256 of the sealed catalog in force, or ``null`` when none was loaded.
``blinding``
    STRUCTURE, or RESTRICTED for anything computed from a science energy.

The exclusion function reads only ``code``, ``scope``, ``interval`` and
``flag_id``. It never reads ``observed``, ``expected``, ``evidence`` or
``detail``; that is what keeps it blind.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import re
import sys
import time
from typing import Any, Iterable, Mapping

FLAG_SCHEMA = "joulewise.flag.v1"

FAMILIES = (
    "PACK_IDENTITY",
    "CODE_IDENTITY",
    "MODEL_IDENTITY",
    "CALIBRATION",
    "NEG8",
    "INSTRUMENT",
    "MEMBER_VALIDITY",
    "PHYSICS_IN_SPAN",
    "CLOCK_SYSTEMATIC",
    "ROSTER",
    "RECORDS",
    "DIAGNOSTIC",
)
KLASSES = ("PHYSICS", "NUMBER", "REPRESENTATION")
LEVELS = ("window", "stage", "quad", "member")
STAGES = ("desk", "arm", "window", "harvest")
BLINDINGS = ("STRUCTURE", "RESTRICTED")

FIELDS = (
    "schema_version",
    "flag_id",
    "code",
    "family",
    "klass",
    "scope",
    "interval",
    "source",
    "observed",
    "expected",
    "evidence",
    "detail",
    "emitted",
    "catalog_sha256",
    "blinding",
)
SCOPE_KEYS = ("level", "plan_id", "attempt", "stage_id", "run_id", "bundle_id")
INTERVAL_KEYS = ("monotonic_ns", "monotonic_raw_ns", "wall_s")
SOURCE_KEYS = ("stage", "collector", "legacy_site", "legacy_code")
EMITTED_KEYS = ("wall_s", "monotonic_ns", "boot_session_uuid")

CODE_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")
FLAG_ID_RE = re.compile(r"^[0-9a-f]{20}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DETAIL_MAX = 2000


class FlagSchemaError(ValueError):
    """A record does not conform to ``joulewise.flag.v1``."""


def canonical_json_bytes(value: Any) -> bytes:
    """Sorted keys, no whitespace, UTF-8, no NaN or infinity."""

    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def compute_flag_id(
    code: str, scope: Mapping[str, Any], observed: Any, source: Mapping[str, Any]
) -> str:
    payload = {"code": code, "scope": dict(scope), "observed": observed, "source": dict(source)}
    return sha256_hex(canonical_json_bytes(payload))[:20]


_BOOT_SESSION_UUID: str | None = None
_BOOT_SESSION_READ = False


def boot_session_uuid() -> str | None:
    """``kern.bootsessionuuid`` read in process (no subprocess); ``None`` off macOS."""

    global _BOOT_SESSION_UUID, _BOOT_SESSION_READ
    if _BOOT_SESSION_READ:
        return _BOOT_SESSION_UUID
    _BOOT_SESSION_READ = True
    if sys.platform != "darwin":
        return None
    try:
        libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
        size = ctypes.c_size_t(0)
        name = b"kern.bootsessionuuid"
        if libc.sysctlbyname(name, None, ctypes.byref(size), None, ctypes.c_size_t(0)) != 0:
            return None
        buffer = ctypes.create_string_buffer(size.value)
        if libc.sysctlbyname(name, buffer, ctypes.byref(size), None, ctypes.c_size_t(0)) != 0:
            return None
        value = buffer.value.decode("ascii", errors="strict").strip()
    except (OSError, AttributeError, UnicodeDecodeError):
        return None
    _BOOT_SESSION_UUID = value or None
    return _BOOT_SESSION_UUID


def monotonic_raw_ns() -> int | None:
    clock_id = getattr(time, "CLOCK_MONOTONIC_RAW", None)
    if clock_id is None:
        return None
    try:
        return time.clock_gettime_ns(clock_id)
    except OSError:
        return None


def now_stamp() -> dict[str, Any]:
    """The ``emitted`` block: wall seconds, ``monotonic_ns`` and the boot session."""

    return {
        "wall_s": time.time(),
        "monotonic_ns": time.monotonic_ns(),
        "boot_session_uuid": boot_session_uuid(),
    }


def make_scope(
    level: str,
    *,
    plan_id: str | None = None,
    attempt: str | int | None = None,
    stage_id: str | None = None,
    run_id: str | None = None,
    bundle_id: str | None = None,
) -> dict[str, Any]:
    return {
        "level": level,
        "plan_id": plan_id,
        "attempt": attempt,
        "stage_id": stage_id,
        "run_id": run_id,
        "bundle_id": bundle_id,
    }


def make_interval(
    *,
    monotonic_ns: Iterable[int] | None = None,
    monotonic_raw_ns: Iterable[int] | None = None,
    wall_s: Iterable[float] | None = None,
) -> dict[str, Any]:
    def pair(value: Iterable[Any] | None) -> list[Any] | None:
        return None if value is None else list(value)

    return {
        "monotonic_ns": pair(monotonic_ns),
        "monotonic_raw_ns": pair(monotonic_raw_ns),
        "wall_s": pair(wall_s),
    }


def make_source(
    stage: str,
    collector: str,
    *,
    legacy_site: str | None = None,
    legacy_code: str | None = None,
) -> dict[str, Any]:
    return {
        "stage": stage,
        "collector": collector,
        "legacy_site": legacy_site,
        "legacy_code": legacy_code,
    }


def make_flag(
    *,
    code: str,
    family: str,
    klass: str,
    scope: Mapping[str, Any],
    source: Mapping[str, Any],
    observed: Any = None,
    expected: Any = None,
    evidence: Iterable[Mapping[str, str]] = (),
    detail: str = "",
    interval: Mapping[str, Any] | None = None,
    catalog_sha256: str | None = None,
    blinding: str = "STRUCTURE",
    emitted: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build and validate one flag; raises :class:`FlagSchemaError` if malformed."""

    scope_value = {key: scope.get(key) for key in SCOPE_KEYS}
    source_value = {key: source.get(key) for key in SOURCE_KEYS}
    flag = {
        "schema_version": FLAG_SCHEMA,
        "flag_id": compute_flag_id(code, scope_value, observed, source_value),
        "code": code,
        "family": family,
        "klass": klass,
        "scope": scope_value,
        "interval": dict(interval) if interval is not None else make_interval(),
        "source": source_value,
        "observed": observed,
        "expected": expected,
        "evidence": [dict(item) for item in evidence],
        "detail": " ".join(str(detail).split())[:DETAIL_MAX],
        "emitted": dict(emitted) if emitted is not None else now_stamp(),
        "catalog_sha256": catalog_sha256,
        "blinding": blinding,
    }
    require_flag(flag)
    return flag


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and math.isfinite(value)


def _check_pair(value: Any, where: str, integer: bool, problems: list[str]) -> None:
    if value is None:
        return
    check = _is_int if integer else _is_number
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(check(item) for item in value)
        or value[0] > value[1]
    ):
        problems.append(f"{where} must be null or an ordered pair [a, b]")


def validate_flag(value: Any) -> list[str]:
    """Every schema problem in ``value``; an empty list means it conforms."""

    problems: list[str] = []
    if not isinstance(value, Mapping):
        return ["flag must be a JSON object"]
    keys = set(value)
    missing = [key for key in FIELDS if key not in keys]
    extra = sorted(keys - set(FIELDS))
    if missing:
        problems.append(f"missing fields: {missing}")
    if extra:
        problems.append(f"unknown fields: {extra}")
    if missing:
        return problems
    if value["schema_version"] != FLAG_SCHEMA:
        problems.append("schema_version must be joulewise.flag.v1")
    code = value["code"]
    if not isinstance(code, str) or CODE_RE.fullmatch(code) is None:
        problems.append("code must be dotted lower-case, e.g. battery.member_span")
    if value["family"] not in FAMILIES:
        problems.append(f"family must be one of {FAMILIES}")
    if value["klass"] not in KLASSES:
        problems.append(f"klass must be one of {KLASSES}")
    if value["blinding"] not in BLINDINGS:
        problems.append(f"blinding must be one of {BLINDINGS}")

    scope = value["scope"]
    if not isinstance(scope, Mapping) or set(scope) != set(SCOPE_KEYS):
        problems.append(f"scope must have exactly {SCOPE_KEYS}")
    else:
        if scope["level"] not in LEVELS:
            problems.append(f"scope.level must be one of {LEVELS}")
        for key in ("plan_id", "stage_id", "run_id", "bundle_id"):
            if scope[key] is not None and not isinstance(scope[key], str):
                problems.append(f"scope.{key} must be a string or null")
        attempt = scope["attempt"]
        if attempt is not None and not isinstance(attempt, str) and not _is_int(attempt):
            problems.append("scope.attempt must be a string, integer or null")
        if scope["level"] == "member" and not scope["run_id"]:
            problems.append("a member-level flag needs scope.run_id")
        if scope["level"] == "stage" and not scope["stage_id"]:
            problems.append("a stage-level flag needs scope.stage_id")

    interval = value["interval"]
    if not isinstance(interval, Mapping) or set(interval) != set(INTERVAL_KEYS):
        problems.append(f"interval must have exactly {INTERVAL_KEYS}")
    else:
        _check_pair(interval["monotonic_ns"], "interval.monotonic_ns", True, problems)
        _check_pair(interval["monotonic_raw_ns"], "interval.monotonic_raw_ns", True, problems)
        _check_pair(interval["wall_s"], "interval.wall_s", False, problems)

    source = value["source"]
    if not isinstance(source, Mapping) or set(source) != set(SOURCE_KEYS):
        problems.append(f"source must have exactly {SOURCE_KEYS}")
    else:
        if source["stage"] not in STAGES:
            problems.append(f"source.stage must be one of {STAGES}")
        if not isinstance(source["collector"], str) or not source["collector"]:
            problems.append("source.collector must be a nonempty string")
        for key in ("legacy_site", "legacy_code"):
            if source[key] is not None and not isinstance(source[key], str):
                problems.append(f"source.{key} must be a string or null")

    evidence = value["evidence"]
    if not isinstance(evidence, list):
        problems.append("evidence must be a list")
    else:
        for index, item in enumerate(evidence):
            if (
                not isinstance(item, Mapping)
                or set(item) != {"path", "sha256"}
                or not isinstance(item["path"], str)
                or not item["path"]
                or item["path"].startswith("/")
                or ".." in item["path"].split("/")
                or not isinstance(item["sha256"], str)
                or SHA256_RE.fullmatch(item["sha256"]) is None
            ):
                problems.append(
                    f"evidence[{index}] must be {{path relative to custody, sha256}}"
                )

    if not isinstance(value["detail"], str) or "\n" in value["detail"]:
        problems.append("detail must be one line of text")

    emitted = value["emitted"]
    if not isinstance(emitted, Mapping) or set(emitted) != set(EMITTED_KEYS):
        problems.append(f"emitted must have exactly {EMITTED_KEYS}")
    else:
        if not _is_number(emitted["wall_s"]):
            problems.append("emitted.wall_s must be a finite number")
        if not _is_int(emitted["monotonic_ns"]):
            problems.append("emitted.monotonic_ns must be an integer")
        if emitted["boot_session_uuid"] is not None and not isinstance(
            emitted["boot_session_uuid"], str
        ):
            problems.append("emitted.boot_session_uuid must be a string or null")

    catalog_sha = value["catalog_sha256"]
    if catalog_sha is not None and (
        not isinstance(catalog_sha, str) or SHA256_RE.fullmatch(catalog_sha) is None
    ):
        problems.append("catalog_sha256 must be a SHA-256 or null")

    try:
        canonical_json_bytes({"observed": value["observed"], "expected": value["expected"]})
    except (TypeError, ValueError) as exc:
        problems.append(f"observed/expected must be finite JSON: {exc}")
        return problems

    flag_id = value["flag_id"]
    if not isinstance(flag_id, str) or FLAG_ID_RE.fullmatch(flag_id) is None:
        problems.append("flag_id must be 20 lower-case hex characters")
    elif not problems:
        expected_id = compute_flag_id(code, scope, value["observed"], source)
        if flag_id != expected_id:
            problems.append("flag_id does not match canonical(code, scope, observed, source)")
    return problems


def require_flag(value: Any) -> Mapping[str, Any]:
    problems = validate_flag(value)
    if problems:
        raise FlagSchemaError("; ".join(problems))
    return value


def render_line(flag: Mapping[str, Any]) -> bytes:
    """One canonical JSON line, newline-terminated."""

    return canonical_json_bytes(flag) + b"\n"
