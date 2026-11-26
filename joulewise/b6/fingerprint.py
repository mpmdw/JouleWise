"""Plain session dependencies and the last passing smoke for each pack."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path

from joulewise.hazards import clock
from joulewise.hazards.base import canonical_json

METER_ARGV = ("/usr/sbin/ioreg", "-p", "IOUSB", "-l", "-w0")


def meter_device(text: str) -> dict | None:
    # An ioreg node begins at '+-o'; never combine properties of two devices.
    for node in re.split(r"(?m)^.*\+-o ", text):
        def prop(name):
            match = re.search(r'"' + re.escape(name) + r'"\s*=\s*("[^"\n]*"|0x[0-9a-fA-F]+|\d+)', node)
            return match.group(1).strip('"') if match else None
        vendor, product = prop("idVendor"), prop("idProduct")
        if vendor is None or product is None:
            continue
        if int(vendor, 0 if vendor.startswith("0x") else 10) == 0x5FC9 and int(
                product, 0 if product.startswith("0x") else 10) == 0x0063:
            return {"serial": prop("USB Serial Number"), "bcdDevice": prop("bcdDevice")}
    return None


def collect(measurement_root, pack_id, model_hashes, runtime_versions, *, ctx,
            read_bytes=Path.read_bytes) -> dict:
    root = str(measurement_root)

    def read(argv, name):
        result = ctx.run(argv, ctx.probe_timeout_s)
        ctx.keep_raw(name, result.stdout)
        return result.stdout.decode("utf-8", errors="replace").strip() if result.ok else None

    commit = read(("git", "-C", root, "rev-parse", "HEAD"), "fingerprint.commit.txt")
    dirty = read(("git", "-C", root, "status", "--porcelain", "--untracked-files=no"),
                 "fingerprint.dirty.txt")
    os_build = read(("/usr/sbin/sysctl", "-n", "kern.osversion"), "fingerprint.os.txt")
    try:
        boot = clock.read_boot_session(ctx)
    except (OSError, ValueError):
        boot = None
    usb = read(METER_ARGV, "fingerprint.usb.txt")
    try:
        version = hashlib.sha256(read_bytes(Path("/usr/bin/powermetrics"))).hexdigest()
    except OSError:
        version = None
    tree = read(("git", "-C", root, "rev-parse", f"HEAD:configs/campaigns/{pack_id}"),
                "fingerprint.pack.txt")
    return {"code_commit": commit, "code_dirty": None if dirty is None else bool(dirty),
            "os_build": os_build, "model_hashes": dict(model_hashes),
            "runtime_versions": dict(runtime_versions), "boot_session_uuid": boot,
            "meter_device": meter_device(usb) if usb is not None else None,
            "powermetrics_version": version, "pack": {"pack_id": pack_id, "tree_id": tree}}


def digest(fp) -> str:
    return hashlib.sha256(canonical_json(fp)).hexdigest()


def _has_null(value) -> bool:
    if isinstance(value, dict):
        return any(_has_null(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_has_null(item) for item in value)
    return value is None


def smoke_required(fp, index_path) -> tuple[bool, list[str]]:
    last = None
    try:
        lines = Path(index_path).read_text().splitlines()
    except (OSError, UnicodeError):
        lines = []
    pack_id = fp["pack"]["pack_id"]
    for line in lines:
        try:
            entry = json.loads(line)
            if not isinstance(entry, dict):
                raise ValueError("index line is not an object")
        except ValueError:
            # A torn line cannot be attributed safely to a pack.
            last = None
            continue
        if entry.get("pack_id") == pack_id:
            last = entry
    previous = last.get("fingerprint") if last else None
    if not isinstance(previous, dict):
        return True, sorted(fp)
    differing = sorted(key for key in set(fp) | set(previous)
                       if key not in fp or key not in previous or fp[key] != previous[key]
                       or _has_null(fp[key]))
    return bool(differing), differing


def record_pass(fp, smoke_dir, index_path) -> None:
    path = Path(index_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"pack_id": fp["pack"]["pack_id"], "fingerprint": fp,
             "fingerprint_sha256": digest(fp), "smoke_dir": str(smoke_dir),
             "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    with path.open("ab") as handle:
        handle.write(canonical_json(entry) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
