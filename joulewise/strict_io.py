"""Verification primitives grouped by their existing byte contracts.

Names distinguish Unicode escaping, NaN policy and trailing-newline/layout
choices. Do not normalize these variants: their bytes are hash inputs.
Application refusal mapping and semantic projections belong to the caller.
Independent recomputations, twins and oracles must not use this module.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import tempfile
from typing import Any


def sha256_value(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_raw(raw: bytes) -> str:
    return sha256_value(raw)


def sha256_data(data: bytes) -> str:
    return sha256_value(data)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_path_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_ascii_bytes_strict(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')) .encode("utf-8")


def json_ascii_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=True, separators=(',', ':'))


def json_pretty_ascii(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=True, indent=2) + "\n") .encode("utf-8")


def json_pretty_insertion_utf8_strict(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n") .encode("utf-8")


def json_pretty_utf8(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=True, indent=2) + "\n") .encode("utf-8")


def json_pretty_utf8_strict(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + "\n") .encode("utf-8")


def json_utf8_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=True, separators=(',', ':')) .encode("utf-8")


def json_utf8_bytes_strict(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')) .encode("utf-8")


def is_lower_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdefABCDEF" for c in value)


def finite_or_none(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def is_finite_float_projection(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(float(value))


def require_finite(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{name} must be a finite number")
    return converted


def collect_exact_keys(value: Any, expected: set[str], where: str, errors: list[str]) -> bool:
    if not isinstance(value, Mapping):
        errors.append(f"{where}: must be an object")
        return False
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        errors.append(f"{where}: missing key(s): {', '.join(missing)}")
    if extra:
        errors.append(f"{where}: unrecognized key(s): {', '.join(extra)}")
    return not missing and not extra


def parse_finite_float(value: str, reject: Callable[[str], None]) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        reject(value)
    return parsed
