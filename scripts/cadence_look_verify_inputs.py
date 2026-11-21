#!/usr/bin/env python3
"""The hash-only verifier of a look's pinned inputs (RL-194a section 1, option c).

    python3 -I -B scripts/cadence_look_verify_inputs.py --pins PINS.json --pins-sha256 HEX
        --span SPAN_ID=DIRECTORY [--span ...] --out RESULT.json

It runs first, as its own process, before a stage parses anything and before the reservation. It reads every pinned
file of every named span as opaque bytes, computes its sha256, counts its bytes and retains nothing. It writes one
file: the word ``pass`` or ``fail``, and for each path the pinned and the observed digest with one word for its state
(``match``, ``mismatch``, ``size`` when the digest is the pin's and the byte count is not the pinned one,
``missing``, ``symlink``; a file in a span that is not pinned is listed as ``not_pinned`` and is not read). No size,
no count and no float is written: words and hashes only (RL-179 register row 26). A ``fail`` stops the run with
nothing consumed.

What passes here is what the stage and the twin's wrapper require inside the reservation: the same names, the same
digest and the same byte count. A pin this check passes is never refused there for a reason this check could see.

The result file is created, never replaced: an ``--out`` that already exists, or is a link, ends the run with exit 2
and nothing written.

This process holds no decoder. It imports no look code and no parsing or decoding code for any custody file; the
only thing it parses is the pin list. Exit 0 pass, 1 fail, 2 when it could not be run as asked.
"""
import hashlib
import json
import os
import stat
import sys

PINS_SCHEMA = "joulewise.cadence_look_input_pins.v1"
RESULT_SCHEMA = "joulewise.cadence_look_input_verification.v1"


def digest_of(path):
    """(sha256, byte count) of a regular file's bytes, read in pieces and kept nowhere; None when it is absent or
    not regular."""
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            return None
        digest, count = hashlib.sha256(), 0
        while True:
            chunk = os.read(descriptor, 1 << 20)
            if not chunk:
                return digest.hexdigest(), count
            digest.update(chunk)
            count += len(chunk)
    finally:
        os.close(descriptor)


def entries(directory):
    """(relative paths of regular files, relative paths of symlinks) under a span directory, by name only."""
    files, links, pending = set(), set(), [""]
    while pending:
        prefix = pending.pop()
        with os.scandir(os.path.join(directory, prefix) if prefix else directory) as children:
            for child in children:
                relative = f"{prefix}/{child.name}" if prefix else child.name
                if child.is_symlink():
                    links.add(relative)
                elif child.is_dir(follow_symlinks=False):
                    pending.append(relative)
                else:
                    files.add(relative)
    return files, links


def verify(document, directories):
    rows = []
    for span in document["spans"]:
        sid, directory = span["span_id"], directories[span["span_id"]]
        if os.path.islink(directory) or not os.path.isdir(directory):       # never read through a linked span
            state = "symlink" if os.path.islink(directory) else "missing"
            rows.extend((sid, entry["path"], entry["sha256"], None, state) for entry in span["files"])
            continue
        files, links = entries(directory)
        pinned = set()
        for entry in span["files"]:
            relative, expected, size = entry["path"], entry["sha256"], entry["size"]
            if type(size) is not int:
                raise TypeError("a pin without its byte count")
            pinned.add(relative)
            if relative in links or any(relative.startswith(link + "/") for link in links):
                rows.append((sid, relative, expected, None, "symlink"))
                continue
            read = digest_of(os.path.join(directory, *relative.split("/")))
            if read is None:
                rows.append((sid, relative, expected, None, "missing"))
                continue
            observed, count = read
            state = "mismatch" if observed != expected else "match" if count == size else "size"
            rows.append((sid, relative, expected, observed, state))
        for relative in sorted((files | links) - pinned):
            rows.append((sid, relative, None, None, "symlink" if relative in links else "not_pinned"))
    return rows


def main(argv):
    options, spans, index = {}, [], 0
    while index < len(argv):
        flag = argv[index]
        if flag not in ("--pins", "--pins-sha256", "--span", "--out") or index + 1 >= len(argv):
            return 2
        if flag == "--span":
            spans.append(argv[index + 1])
        elif flag in options:
            return 2
        else:
            options[flag] = argv[index + 1]
        index += 2
    if set(options) != {"--pins", "--pins-sha256", "--out"} or not spans:
        return 2
    try:
        with open(options["--pins"], "rb") as handle:
            raw = handle.read()
        if hashlib.sha256(raw).hexdigest() != options["--pins-sha256"]:
            return 2
        document = json.loads(raw)
        directories = {}
        for item in spans:
            sid, equal, directory = item.partition("=")
            if not equal or not directory or sid in directories:
                return 2
            directories[sid] = directory
        if (not isinstance(document, dict) or document.get("schema") != PINS_SCHEMA
                or sorted(span["span_id"] for span in document["spans"]) != sorted(directories)):
            return 2
        rows = verify(document, directories)
    except (OSError, ValueError, KeyError, TypeError):
        return 2
    passed = bool(rows) and all(state == "match" for *_, state in rows)
    result = {"schema": RESULT_SCHEMA, "result": "pass" if passed else "fail",
              "files": [{"span_id": sid, "path": path, "pinned": pinned, "observed": observed, "state": state}
                        for sid, path, pinned, observed, state in rows]}
    try:                                # created, never replaced: no existing file becomes this result
        descriptor = os.open(options["--out"], os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                             0o600)
    except OSError:
        return 2
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main(sys.argv[1:]))
