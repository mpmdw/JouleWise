#!/usr/bin/env python3
"""Derive a pread PLE artifact from a verified mmap artifact without reconversion."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _volume_identity(path: Path) -> str:
    """Return an APFS volume identity for an existing path, or refuse.

    ``diskutil info`` accepts only a device or mount point and exits 1 for an
    ordinary path inside a volume, so resolve the backing device with
    ``df -P`` first (this also follows the system/data firmlinks)."""
    lines = subprocess.check_output(["df", "-P", str(path)], text=True).splitlines()
    device = lines[1].split()[0] if len(lines) > 1 and lines[1].split() else ""
    if not device.startswith("/dev/"):
        raise ValueError(f"cannot resolve the backing device of {path}")
    info = plistlib.loads(subprocess.check_output(["diskutil", "info", "-plist", device]))
    if "apfs" not in str(info.get("FilesystemType", "")).lower():
        raise ValueError(f"clone source/destination must be on APFS: {path}")
    identity = info.get("VolumeUUID") or info.get("APFSVolumeUUID")
    if not identity:
        raise ValueError(f"cannot identify APFS volume: {path}")
    return str(identity)


def _clonefile(source: Path, destination: Path) -> None:
    """APFS copy-on-write clone; never falls back to copying or hard-linking."""
    libc = ctypes.CDLL(None, use_errno=True)
    clonefile = libc.clonefile
    clonefile.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32)
    clonefile.restype = ctypes.c_int
    if clonefile(os.fsencode(source), os.fsencode(destination), 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def derive(source: Path, pin: str, destination: Path, io_mode: str = "pread") -> str:
    import align_convert_qwen4_exp as converter

    source, destination = source.resolve(), destination.resolve()
    if io_mode != "pread":
        raise ValueError("the only supported derived I/O recipe is pread")
    manifest, blobs, _ = converter._verify(source, pin)
    config = json.loads(blobs["config.json"])
    old_io = config.get("ngram_tables", {}).get("io")
    if old_io != "mmap":
        raise ValueError("source artifact must use ngram_tables.io=mmap")
    if destination.exists():
        raise ValueError("destination must not exist")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if _volume_identity(source) != _volume_identity(destination.parent):
        raise ValueError("source and destination must be on the same APFS volume")

    destination.mkdir()
    try:
        for name in manifest["files"]:
            if name != "config.json":
                _clonefile(source / name, destination / name)
        config["ngram_tables"]["io"] = "pread"
        config_raw = (json.dumps(config, indent=2) + "\n").encode()
        (destination / "config.json").write_bytes(config_raw)

        derived = dict(manifest)
        derived["files"] = dict(manifest["files"])
        derived["files"]["config.json"] = hashlib.sha256(config_raw).hexdigest()
        derived["derived_from"] = {
            "pin": pin,
            "io": {"from": "mmap", "to": "pread"},
        }
        manifest_raw = (json.dumps(derived, indent=2) + "\n").encode()
        (destination / "manifest.json").write_bytes(manifest_raw)
        new_pin = hashlib.sha256(manifest_raw).hexdigest()
        known = {name: digest for name, digest in derived["files"].items() if name != "config.json"}
        converter._verify(destination, new_pin, known_digests=known)
        return new_pin
    except BaseException:
        # A failed attempt is not a usable artifact. Only files created here are removed.
        import shutil
        shutil.rmtree(destination)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, required=True, metavar="SRC")
    parser.add_argument("--manifest-sha256", required=True, metavar="PIN")
    parser.add_argument("--out", type=Path, required=True, metavar="DST")
    parser.add_argument("--io", choices=("pread",), required=True)
    args = parser.parse_args(argv)
    if len(args.manifest_sha256) != 64 or any(c not in "0123456789abcdef" for c in args.manifest_sha256):
        parser.error("--manifest-sha256 must be 64 lowercase hex characters")
    print(derive(args.artifact, args.manifest_sha256, args.out, args.io))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
