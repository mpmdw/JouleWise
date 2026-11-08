#!/usr/bin/env python3
"""Release exactly named group keys after the registered BYTES stage boundary."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.b6 import blinding


def release(pack_records_root, group, registrations_root, project_root, keys, stage, out, stage1_commit=None):
    if stage == "heldout" and not re.fullmatch(r"[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?", stage1_commit or ""):
        raise ValueError("stage 2 requires the stage-1 commit hash")
    keys = sorted(set(keys))
    allowed = blinding.registered_keys(registrations_root, group, project_root)
    directory = blinding.key_directory(pack_records_root, group, {"blinding_group": group})
    payloads = {}
    for key in keys:
        if key not in allowed:
            raise ValueError("key outside the group's registrations: " + key)
        if stage == "fit" and allowed[key] != "fit":
            raise ValueError("held-out key cannot be released at stage 1: " + key)
        # Read-only validation: release must never draw a missing key.
        blinding.stored_factor(directory, key)
        name = blinding._config_filename(key)
        payload = (directory / name).read_bytes()
        if json.loads(payload).get("key") != key:
            raise ValueError("drawn key identity differs from requested configuration")
        payloads[name] = payload
    payloads["pack.json"] = (directory / "pack.json").read_bytes()
    out = Path(out)
    if out.exists():
        raise ValueError("release directory already exists; choose a fresh directory")
    # Build the complete release beside its destination, then publish by rename.
    # Files are copied verbatim, including their factor identities and provenance.
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="." + out.name + ".", dir=out.parent))
    try:
        for name, payload in payloads.items():
            path = temporary / name
            path.write_bytes(payload)
            path.chmod(0o600)
        record = {"schema": "joulewise.b6_subset_release.v1", "blinding_group": group,
                  "stage": stage, "keys": keys, "stage1_commit": stage1_commit,
                  "released_utc": datetime.now(timezone.utc).isoformat(),
                  "sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in sorted(payloads.items())}}
        (temporary / "release.json").write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
        os.rename(temporary, out)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-records-root", required=True, type=Path)
    parser.add_argument("--blinding-group", required=True)
    parser.add_argument("--registrations-root", type=Path, default=ROOT / "configs/b6/packs")
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--keys", required=True, nargs="+")
    parser.add_argument("--stage", required=True, choices=("fit", "heldout"))
    parser.add_argument("--stage1-commit")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        record = release(args.pack_records_root, args.blinding_group, args.registrations_root,
                         args.project_root, args.keys, args.stage, args.out, args.stage1_commit)
        print(json.dumps({"release": str(args.out), "stage": record["stage"], "keys": record["keys"]}, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("refused: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
