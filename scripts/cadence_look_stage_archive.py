#!/usr/bin/env python3
"""Expand one pulled, decrypted span archive for a look, as its own hash-only process (RL-174 D.3; RL-194a section 1).

    python3 -I -B scripts/cadence_look_stage_archive.py --span-id ID --archive ARCHIVE --manifest SHA256SUMS
        --marker MARKER.json --manifest-sha256 HEX --staging-root DIR --out RESULT.json

Stage 1 launches this after it has admitted the look's pin list and before anything else touches the span. The
archive holds the span's traces, telemetry and meter streams, so the process that reads and hashes it is this one and
never the stage (RL-179 F-12: stage 1 opens and hashes no energy file).

Order of the checks:

1. ``SHA256SUMS`` is the span's pinned offload manifest: its sha256 is ``--manifest-sha256``, the digest the pin list
   carries for the span and the public Check item names. Nothing else is read before this holds.
2. The marker binds those bytes and the archive (``manifest_sha256``, ``archive_sha256``), names the span and says
   the provider confirmed the upload.
3. Each member is written once under a private directory inside the staging root and hashed from the bytes as they
   are written; an expanded file is never opened again here. Every file must be in ``SHA256SUMS`` with that digest,
   and every listed file must be present.
4. Only then is the span directory published, by one rename. A refusal leaves nothing in the staging root.

It writes one result file, created and never replaced: ``staged`` or ``refused``, a fixed phrase for a refusal, and
for a staged span the three digests and the file count. Hashes, words and one count: no size and no float. It
decodes no measurement, imports no look code and contacts nothing. Exit 0 staged, 1 refused, 2 when it could not be
run as asked.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile
import tempfile

RESULT_SCHEMA = "joulewise.cadence_look_staging.v1"
MARKER_SCHEMA = "joulewise.span_offload_marker.v1"
FLAGS = ("--span-id", "--archive", "--manifest", "--marker", "--manifest-sha256", "--staging-root", "--out")


class Refused(Exception):
    """A fixed phrase; never a value read from the archive."""


def relative(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or any(part in ("", ".", "..") for part in name.split("/")):
        raise Refused("unsafe archive or manifest path")
    return path


def stage(span_id, archive, manifest, marker, staging_root, manifest_sha256):
    """Expand and verify one span; return its record or raise ``Refused``."""
    if not isinstance(span_id, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", span_id):
        raise Refused("invalid span id")
    try:
        listed = Path(manifest).read_bytes()
        listed_sha = hashlib.sha256(listed).hexdigest()
        if listed_sha != manifest_sha256:
            raise Refused("the SHA256SUMS is not the span's pinned offload manifest")
        sealed = Path(marker).read_bytes()
        mark = json.loads(sealed)
        if (mark.get("schema") != MARKER_SCHEMA or mark.get("provider_confirmed") is not True
                or mark.get("manifest_sha256") != listed_sha):
            raise Refused("manifest does not match the verified marker")
        top = mark.get("span_name")
        if not isinstance(top, str) or len(relative(top).parts) != 1 or top != span_id:
            raise Refused("marker span name differs from the roster span")
        expected = {}
        for line in listed.decode("utf-8").splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  \./(.+)", line)
            if not match:
                raise Refused("invalid per-file manifest")
            digest, name = match.groups()
            relative(name)
            if name in expected:
                raise Refused("duplicate manifest file")
            expected[name] = digest
        if not expected or mark.get("manifest_files") != len(expected):
            raise Refused("manifest file count differs from the marker")
        root = Path(staging_root)
        root.mkdir(parents=True, exist_ok=True)
        destination = root / span_id
        if destination.exists() or destination.is_symlink():
            raise Refused("staged span already exists; use a fresh staging root")
        with tempfile.TemporaryDirectory(prefix=".look-stage-", dir=root) as private:
            private = Path(private)
            # Hash the same open archive later expanded. No time-field reader sees compressed bytes.
            with open(archive, "rb") as source:
                archive_sha = hashlib.file_digest(source, "sha256").hexdigest()
                if archive_sha != mark.get("archive_sha256"):
                    raise Refused("archive does not match the marker")
                source.seek(0)
                with tarfile.open(fileobj=source, mode="r:*") as tar:
                    seen, files = set(), set()
                    for member in tar:
                        parts = relative(member.name).parts
                        if parts[0] != top or member.name in seen:
                            raise Refused("unexpected or duplicate archive member")
                        seen.add(member.name)
                        path = private.joinpath(*parts)
                        if member.isdir():
                            path.mkdir(parents=True, exist_ok=True)
                        elif member.isfile():
                            name = "/".join(parts[1:])
                            if name not in expected:
                                raise Refused("archive file absent from the manifest")
                            path.parent.mkdir(parents=True, exist_ok=True)
                            written = hashlib.sha256()
                            with tar.extractfile(member) as content, path.open("xb") as target:
                                while chunk := content.read(1 << 20):
                                    written.update(chunk)
                                    target.write(chunk)
                            if written.hexdigest() != expected[name]:
                                raise Refused("staged file sha256 differs from the manifest")
                            files.add(name)
                        else:
                            raise Refused("archive member is not a regular file or directory")
            if files != set(expected):
                raise Refused("archive file set differs from the manifest")
            (private / top).rename(destination)
        return {"span_id": span_id, "archive_sha256": archive_sha, "manifest_sha256": listed_sha,
                "marker_sha256": hashlib.sha256(sealed).hexdigest(), "files_verified": len(expected)}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, tarfile.TarError) as error:
        raise Refused(f"cannot verify or expand archive ({type(error).__name__})") from None


def main(argv):
    options, index = {}, 0
    while index < len(argv):
        if argv[index] not in FLAGS or index + 1 >= len(argv) or argv[index] in options:
            return 2
        options[argv[index]] = argv[index + 1]
        index += 2
    if set(options) != set(FLAGS) or not re.fullmatch(r"[0-9a-f]{64}", options["--manifest-sha256"]):
        return 2
    try:
        record = stage(options["--span-id"], options["--archive"], options["--manifest"], options["--marker"],
                       options["--staging-root"], options["--manifest-sha256"])
        result = {"schema": RESULT_SCHEMA, "result": "staged", "reason": None, "record": record}
    except Refused as refusal:
        result = {"schema": RESULT_SCHEMA, "result": "refused", "reason": str(refusal), "record": None}
    try:                                # created, never replaced: no existing file becomes this result
        descriptor = os.open(options["--out"], os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                             0o600)
    except OSError:
        return 2
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return 0 if result["result"] == "staged" else 1


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main(sys.argv[1:]))
