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
