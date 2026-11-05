"""Exact-byte custody of live battery observations and OFF-receipt layout."""
from __future__ import annotations
import os
import re
from pathlib import Path
from joulewise import receipt_readers as readiness

def sha(path):
    return readiness.sha256_bytes(Path(path).read_bytes())


class HarvestRefusal(ValueError):
    """Only fixed structural codes may cross the public boundary."""


def identifier(value):
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value) is None:
        raise HarvestRefusal("identity_invalid")
    return value


def reference(path):
    return {"path": str(path), "sha256": sha(path)}


def off_receipt_path(plan, night_dir=None):
    """Match capture_t0_step's pack custody and the diagnostic night layout."""
    from joulewise.hazards import network_time as network_time_off
    night = Path(night_dir) if night_dir is not None else Path(plan.custody_root) / "night"
    if plan.receipt_class == "TRANSACTION_PACK":
        return night.parent / identifier(plan.pack_night["pack_id"]) / "arm_readiness.t0.inputs" / network_time_off.RECEIPT_BASENAME
    return night / network_time_off.RECEIPT_BASENAME


def persist_battery_observation(directory, name, observation, raw):
    """Retain the exact observed stdout even when the predicate refuses."""
    if not isinstance(raw, bytes) or readiness.sha256_bytes(raw) != observation.get("raw_stdout_sha256"):
        raise HarvestRefusal("battery_boundary_raw_mismatch")
    directory = Path(directory)
    if any(path.is_symlink() for path in (directory, *directory.parents)):
        raise HarvestRefusal("battery_boundary_directory_symlink")
    directory.mkdir(parents=True, exist_ok=True)
    raw_path, record_path = directory / (name + ".ioreg"), directory / (name + ".json")
    for path, body in ((raw_path, raw), (record_path, readiness.render_json(observation))):
        with path.open("xb") as stream:
            os.chmod(path, 0o600)
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
    return {"record": reference(record_path.absolute()), "raw": reference(raw_path.absolute())}

