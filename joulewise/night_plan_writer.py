"""Canonical writer for frozen v2 packless and v3 pack night plans."""

from __future__ import annotations

import dataclasses
import json
import os
import uuid
from pathlib import Path
from typing import Any

from joulewise.night_gate import (
    PACK_PLAN_SCHEMA, PACK_PLAN_SCHEMA_VERSION, PLAN_SCHEMA,
    PLAN_SCHEMA_VERSION, NightPlan,
)


def night_plan_mapping(plan: NightPlan) -> dict[str, Any]:
    """Return the exact class-specific mapping, preserving the armed attempt."""

    if not isinstance(plan, NightPlan):
        raise TypeError("plan must be a NightPlan")
    fields = dataclasses.asdict(plan)
    is_pack = plan.receipt_class == "TRANSACTION_PACK"
    if not is_pack and plan.pack_night is None:
        del fields["pack_night"]
    value = {
        "schema": PACK_PLAN_SCHEMA if is_pack else PLAN_SCHEMA,
        "schema_version": PACK_PLAN_SCHEMA_VERSION if is_pack else PLAN_SCHEMA_VERSION,
        **fields,
    }
    # Keep the producer and consumer in one executable contract.
    NightPlan.from_mapping(value)
    return value


def night_plan_json_bytes(plan: NightPlan) -> bytes:
    """Serialize a validated plan deterministically with a trailing newline."""

    return (
        json.dumps(night_plan_mapping(plan), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_night_plan(path: str | os.PathLike[str], plan: NightPlan) -> Path:
    """Atomically publish one complete plan and return its resolved path."""

    target = Path(path).expanduser().resolve(strict=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = night_plan_json_bytes(plan)
    temporary = target.with_name(
        f".{target.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    )
    try:
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise OSError("could not write night plan")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, target)
        directory = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)
    return target
