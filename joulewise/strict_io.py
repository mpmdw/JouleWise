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
