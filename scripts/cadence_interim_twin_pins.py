#!/usr/bin/env python3
"""The twin's side of RL-194 condition 4: check the look's content pins, then run the reviewed child unchanged.

    python3 -I -B scripts/cadence_interim_twin_pins.py <the child's arguments>

The reviewed child (``fit.twin``) is byte-identical to its #816 review. This wrapper is the code, not the
primary's, that checks the twin's inputs first:

* the pin list is the manifest's own (``inputs.pins``), read from the manifest the child is given, against the
  manifest's own digest: there is no other list (audit 2, lead ruling);
* the pinned spans are exactly the stage-1 roster's;
* each span's pins rebuild the offload manifest digest the span carries;
* each span directory holds exactly its pinned files: no symlink, no other file, none missing;
* every pinned file, read as opaque bytes in one pass, has its pinned size and sha256.

Any mismatch ends the process before the child starts, so no value is read, with the child's own failure notice
(``stage2_error`` and an error name on stderr, exit 1, nothing on stdout). Otherwise this process becomes the child
(``os.execv``) with the child's arguments untouched and the child's bytes checked against ``fit.twin.sha256``. The
child decodes in a second pass (RL-194a section 1 item 5: the custody root is on every seat's deny list for the run).

Standard library only. It imports no look code and no decoder, and parses no custody file.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys

PINS_SCHEMA = "joulewise.cadence_look_input_pins.v1"


def bound(path, sha256):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError("input digest mismatch")
    return data


def unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate input field")
        out[key] = value
    return out


def option(arguments, flag, *, many=False):
    values = [arguments[i + 1] for i, word in enumerate(arguments[:-1]) if word == flag]
    if many:
        return values
    if len(values) != 1:
        raise ValueError("invalid child arguments")
    return values[0]


def span_directories(custody, overrides, span_ids):
    root = Path(custody)
    requested = {}
    for raw in overrides:
        key, equal, value = raw.partition("=")
        if not equal or not value or key in requested or key not in span_ids:
            raise ValueError("invalid span override")
        requested[key] = Path(value)
    out = {}
    for key in span_ids:
        directory = requested.get(key, root / key)
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("span directory is a symlink or absent")
        out[key] = directory
    return out


def check_span(span, directory):
    """One span: its pins rebuild its offload manifest, its directory is its pin list, each file is its pin."""
    lines, pinned = [], {}
    for entry in span["files"]:
        relative, sha256, size = entry["path"], entry["sha256"], entry["size"]
        if (not isinstance(relative, str) or not relative or relative.startswith("/") or "\\" in relative
                or any(part in ("", ".", "..") for part in relative.split("/")) or relative in pinned
                or not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256)
                or type(size) is not int or size < 0):
            raise ValueError("invalid input pin")
        pinned[relative] = (sha256, size)
        lines.append(f"{sha256}  ./{relative}\n")
    if hashlib.sha256("".join(lines).encode("utf-8")).hexdigest() != span["offload_manifest_sha256"]:
        raise ValueError("input pins do not rebuild their offload manifest")
    present, pending = set(), [""]
    while pending:
        prefix = pending.pop()
        with os.scandir(directory / prefix if prefix else directory) as children:
            for child in children:
                relative = f"{prefix}/{child.name}" if prefix else child.name
                if child.is_symlink():
                    raise ValueError("symlink in pinned custody")
                if child.is_dir(follow_symlinks=False):
                    pending.append(relative)
                elif child.is_file(follow_symlinks=False):
                    present.add(relative)
                else:
                    raise ValueError("irregular file in pinned custody")
    if present != set(pinned):
        raise ValueError("custody files differ from the pin list")
    for relative, (sha256, size) in pinned.items():
        digest, count = hashlib.sha256(), 0
        with open(directory.joinpath(*relative.split("/")), "rb") as stream:
            while chunk := stream.read(1 << 20):
                digest.update(chunk)
                count += len(chunk)
        if count != size or digest.hexdigest() != sha256:
            raise ValueError("custody input differs from its pin")


def verify(argv):
    """Check every pin; return the reviewed child's path and its untouched arguments."""
    child = list(argv)
    if any(word in ("--custody-pins", "--custody-pins-sha256") for word in child):
        raise ValueError("a pin list other than the manifest's")       # there is no other (audit 2, lead ruling)
    repository = Path(__file__).resolve().parents[1]
    manifest = json.loads(bound(option(child, "--manifest"), option(child, "--manifest-sha256")),
                          object_pairs_hook=unique)
    stage1 = json.loads(bound(option(child, "--stage1"), option(child, "--stage1-sha256")), object_pairs_hook=unique)
    document = manifest["inputs"]["pins"]
    if (not isinstance(document, dict) or set(document) != {"schema", "spans"} or document["schema"] != PINS_SCHEMA
            or not isinstance(document["spans"], list)):
        raise ValueError("invalid input pin list")
    spans = {}
    for span in document["spans"]:
        if not isinstance(span, dict) or span.get("span_id") in spans:
            raise ValueError("invalid input pin list")
        spans[span.get("span_id")] = span
    roster = [row["span_id"] for row in stage1["roster"]["spans"]]
    if len(set(roster)) != len(roster) or set(roster) != set(spans):
        raise ValueError("pin list and stage-1 roster name different spans")
    directories = span_directories(option(child, "--custody"), option(child, "--span-dir", many=True), set(roster))
    for key in roster:
        check_span(spans[key], directories[key])
    twin = manifest["fit"]["twin"]
    path = (repository / twin["path"]).resolve()
    if not path.is_relative_to(repository) or hashlib.sha256(path.read_bytes()).hexdigest() != twin["sha256"]:
        raise ValueError("the reviewed child is not at its pin")
    return path, child


def main(argv):
    try:
        if not sys.flags.isolated:
            raise ValueError("isolated interpreter required")
        path, child = verify(argv)
    except BaseException as error:  # noqa: BLE001 - the child's own failure notice: a type name, never a value
        name = type(error).__name__ if type(error).__module__ == "builtins" else "OtherError"
        os.write(2, f"stage2_error\n{name}\n".encode("ascii"))
        os._exit(1)
    os.execv(sys.executable, [sys.executable, "-I", "-B", str(path), *child])


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main(sys.argv[1:])
