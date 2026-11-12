#!/usr/bin/env python3
"""Block 6 custody kit: source manifest, copy verification, run-input document.

Stdlib only. It hashes bytes and reads file NAMES. It never parses or prints
the content of a session file, with one exception: the path column of each
archive's sources/SHA256SUMS (parsed from the same bytes whose digest is
checked: at the source against itself, on the copy against the source manifest).

  manifest  (at the source)  digests of the pinned files of each archive; refuses a
                             sources/ file set that differs from its own SHA256SUMS;
                             prints per-session counts (never a digest but its own)
  verify    (on the copy)    rehash every SHA256SUMS row; no missing, extra
                             or changed file; refuses the source tree and the source
                             host; writes a counts-only receipt (--self-check: none)
  inputs    (on the Air)     the run-input document for
                             scripts/independent_recompute_b6.py; every digest
                             comes from the SOURCE manifest, never the copy; the
                             manifest and the receipt are each pinned by an
                             out-of-band digest

Outputs are created mode 0600 and only in a directory without group/other bits
(RL-100 item 2: the manifest and run-input document hold withheld/ digests).

Exit 0 on success, 4 on a refusal ("refused: <code>" on stderr), 2 on usage.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import socket
import stat
import subprocess
import sys

MANIFEST_SCHEMA = "joulewise.b6_custody_manifest.v1"
RECEIPT_SCHEMA = "joulewise.b6_custody_verify_receipt.v1"
SUMS = "sources/SHA256SUMS"
HARVEST = "harvest.json"
ACCEPTANCE = "derived/b6-acceptance.json"
INSIDE_LOG = "compression.jsonl"
DESK_SUFFIX = ".desk"
DESK_LOG = "compression.jsonl"
FAMILIES = ("monitor_cost", "arm_host", "battery_phase", "subject_temperature",
            "reference_history", "attempt_history", "g10_history", "block5_codes_carried")
CHUNK = 1 << 20


class Refusal(Exception):
    def __init__(self, code, name=None):
        super().__init__(code)
        self.name = name


# Where a refusal happened (cold review L1): the session's copy path and, when known, a relative file name.
# Names and copy paths are permitted content; exception messages stay suppressed.
WHERE = {"session": None}


def host_name():
    return socket.gethostname().split(".")[0].lower()


def refuse(code, name=None):
    raise Refusal(code, name)


def no_symlink_components(path):
    """Refuse a symlink anywhere on the absolute path, before touching the target."""
    path = Path(path).absolute()
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            refuse("symlink")
    return path


def hash_file(path):
    """SHA-256 and size of a regular file; never follows a final symlink."""
    # O_NONBLOCK: a FIFO is refused below instead of blocking the open.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    digest, size = hashlib.sha256(), 0
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            refuse("not_regular_file")
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def read_hashed(path):
    """Bytes and SHA-256 of a regular file from ONE read (cold review L5): the bytes parsed are the bytes hashed."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            refuse("not_regular_file")
        data = stream.read()
    return data, hashlib.sha256(data).hexdigest()


def hash_zst(path, zstd):
    """SHA-256 of the decompressed stream; zstd writes to a pipe, nothing on disk."""
    digest = hashlib.sha256()
    proc = subprocess.Popen([zstd, "-d", "-c", "-q", "--", str(path)], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    for chunk in iter(lambda: proc.stdout.read(CHUNK), b""):
        digest.update(chunk)
    proc.stdout.close()
    if proc.wait() != 0:
        refuse("decompression_failed")
    return digest.hexdigest()


def tree(root):
    """Relative file name -> size for every file below root. Names only; no content."""
    files = {}
    for here, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            if os.path.islink(os.path.join(here, name)):
                refuse("symlink")
        for name in names:
            mode = os.lstat(os.path.join(here, name)).st_mode
            if not stat.S_ISREG(mode):
                refuse("not_regular_file")
            files[os.path.relpath(os.path.join(here, name), root).replace(os.sep, "/")] = None
    for name in files:
        files[name] = os.lstat(os.path.join(root, name)).st_size
    return files


def relative(value):
    if not isinstance(value, str):
        refuse("path_invalid")
    p = PurePosixPath(value)
    if not value or p.is_absolute() or any(x in ("..", ".", "") for x in value.split("/")):
        refuse("path_invalid")
    return str(p)


def check_out(path):
    """An output is new and its directory is owner-only (RL-100 item 2: the documents hold withheld/ digests)."""
    if os.path.lexists(path):
        refuse("out_exists")
    if os.stat(Path(path).absolute().parent).st_mode & 0o077:
        refuse("out_dir_mode")


def write_new(path, document):
    data = (json.dumps(document, indent=1, sort_keys=True) + "\n").encode()
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        refuse("out_exists")
    with os.fdopen(fd, "wb") as out:
        out.write(data)
    return hashlib.sha256(data).hexdigest()


def read_json_artifact(path):
    """A kit-written manifest, receipt or mapping (never a session file)."""
    no_symlink_components(path)
    data = Path(path).read_bytes()
    return data, json.loads(data)


def copy_paths(sources):
    """Shortest unique trailing suffix, at most 3 names (production repeats 'archive':
    sessions/<id>/archive gives '<id>/archive')."""
    for depth in (1, 2, 3):
        names = ["/".join(s.parts[-depth:]) for s in sources]
        if len(set(names)) == len(names):
            return names
    refuse("copy_path_ambiguous")


def sums_names(data):
    """The path column of SHA256SUMS: '<64 hex>  <relative path>' per line."""
    rows = {}
    for line in data.decode("utf-8").splitlines():
        sha, sep, name = line.partition("  ")
        if not sep or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            refuse("sums_line_invalid")
        name = relative(name)
        if name in rows:
            refuse("sums_line_invalid")
        rows[name] = sha
    return rows


# -- manifest -----------------------------------------------------------------

def check_sources_set(files, rows):
    """Names only (cold review M1): sources/ holds exactly the SHA256SUMS rows (each plain or as <row>.zst,
    never both) plus SHA256SUMS itself. Refused at the source, before the MBP desk gap closes."""
    expected = {SUMS}
    for name in rows:
        found = [n for n in ("sources/" + name, "sources/" + name + ".zst") if n in files]
        if not found:
            refuse("listed_file_missing")
        expected.add(found[0])   # a row present plain AND compressed leaves the twin unexpected, refused below
    if {n for n in files if n.startswith("sources/")} != expected:
        refuse("unlisted_extra_file")


def session_manifest(source, copy_path):
    files = tree(source)
    for name in (SUMS, HARVEST, ACCEPTANCE):
        if name not in files:
            refuse("required_file_missing")
    sums_data, sums_sha = read_hashed(source / SUMS)
    check_sources_set(files, sums_names(sums_data))
    desk = Path(str(source) + DESK_SUFFIX)
    desk_files = {}
    if desk.is_symlink():
        refuse("symlink")
    if desk.is_dir():
        desk_files = {name: hash_file(desk / name)[0] for name in sorted(tree(desk))}
    inside, adjacent = INSIDE_LOG in files, DESK_LOG in desk_files
    if inside and adjacent:
        refuse("compression_log_ambiguous")
    outside = {name: hash_file(source / name)[0] for name in sorted(files) if not name.startswith("sources/")}
    compression = None
    if inside:
        compression = {"location": "inside", "name": INSIDE_LOG, "sha256": outside[INSIDE_LOG]}
    elif adjacent:
        compression = {"location": "adjacent", "name": DESK_LOG, "sha256": desk_files[DESK_LOG]}
    return {"copy_path": copy_path, "basename": source.name, "source_path": str(source),
            "sha256sums_sha256": sums_sha, "harvest_sha256": outside[HARVEST],
            "acceptance_sha256": outside[ACCEPTANCE], "compression": compression,
            "outside_sources": outside, "sources_sizes": {n: z for n, z in sorted(files.items()) if n.startswith("sources/")},
            "desk_present": desk.is_dir(), "desk_files": desk_files,
            "file_count": len(files), "total_bytes": sum(files.values())}


def located(copy_path, function, *arguments):
    WHERE["session"] = copy_path
    return function(*arguments)


def cmd_manifest(args):
    check_out(args.out)
    sources = [no_symlink_components(s) for s in args.session]
    if any(not s.is_dir() for s in sources):
        refuse("session_missing")
    if len(set(sources)) != len(sources):
        refuse("session_repeated")
    loop = {}
    for field in ("loop_attempts", "loop_state"):
        value = getattr(args, field)
        if value:
            loop[field] = {"name": relative(Path(value).name), "sha256": hash_file(no_symlink_components(value))[0]}
    # Cold review M4: both loop files sit in one directory, so one --loop-dir on the copy checks them by name.
    if len({Path(no_symlink_components(getattr(args, f))).parent for f in ("loop_attempts", "loop_state")
            if getattr(args, f)}) > 1 or len({v["name"] for v in loop.values()}) != len(loop):
        refuse("loop_files_split")
    names = copy_paths(sources)
    host = (args.source_host or host_name()).split(".")[0].lower()
    document = {"schema": MANIFEST_SCHEMA, "host": host, "loop": loop, "loop_state_waived": bool(args.no_loop_state),
                "sessions": [located(n, session_manifest, s, n) for s, n in zip(sources, names)]}
    digest = write_new(args.out, document)
    for entry in document["sessions"]:   # names and counts only: nobody needs to open the manifest
        print("session " + entry["copy_path"] + " files=" + str(entry["file_count"]) + " bytes="
              + str(entry["total_bytes"]) + " desk_files=" + str(len(entry["desk_files"])))
    print("manifest sessions=" + str(len(sources)) + " sha256=" + digest)
    return 0


# -- verify -------------------------------------------------------------------

def zstd_binary():
    binary = shutil.which("zstd")
    if binary is None:
        refuse("zstd_unavailable")
    version = subprocess.run([binary, "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if version.returncode != 0:
        refuse("zstd_unavailable")
    return {"path": binary, "version": version.stdout.strip()}


def verify_session(root, entry, tool):
    archive = no_symlink_components(root / relative(entry["copy_path"]))
    if not archive.is_dir():
        refuse("session_missing")
    files = tree(archive)
    if SUMS not in files:
        refuse("listed_file_missing")
    sums_data, sums_sha = read_hashed(archive / SUMS)
    if sums_sha != entry["sha256sums_sha256"]:
        refuse("sums_digest_mismatch")
    expected = {SUMS}
    for name, sha in entry["outside_sources"].items():
        expected.add(relative(name))
        if name not in files:
            refuse("listed_file_missing", name)
        if hash_file(archive / name)[0] != sha:
            refuse("digest_mismatch", name)
    rows = sums_names(sums_data)
    compressed = 0
    for name, sha in sorted(rows.items()):
        plain, packed = "sources/" + name, "sources/" + name + ".zst"
        if plain in files:
            expected.add(plain)
            got = hash_file(archive / plain)[0]
        elif packed in files:
            expected.add(packed)
            if tool.get("zstd") is None:
                tool["zstd"] = zstd_binary()
            got = hash_zst(archive / packed, tool["zstd"]["path"])
            compressed += 1
        else:
            refuse("listed_file_missing", plain)
        if got != sha:
            refuse("digest_mismatch", plain)
    if set(files) - expected:
        refuse("unlisted_extra_file", sorted(set(files) - expected)[0])
    if len(files) != entry["file_count"] or sum(files.values()) != entry["total_bytes"]:
        refuse("tree_size_mismatch")
    for name, size in entry["sources_sizes"].items():   # cold review L3: per-file, so two size changes cannot cancel
        if files.get(name) != size:
            refuse("file_size_mismatch", name)
    desk = Path(str(archive) + DESK_SUFFIX)
    if not entry["desk_present"] and os.path.lexists(desk):
        refuse("unexpected_desk_folder", archive.name + DESK_SUFFIX)   # cold review L2
    if entry["desk_present"]:
        no_symlink_components(desk)
        if not desk.is_dir() or set(tree(desk)) != set(entry["desk_files"]):
            refuse("desk_file_set_mismatch", archive.name + DESK_SUFFIX)
        for name, sha in entry["desk_files"].items():
            if hash_file(desk / relative(name))[0] != sha:
                refuse("digest_mismatch", name + " (desk)")
    return {"files": len(files), "bytes": sum(files.values()), "sums_rows": len(rows),
            "sums_rows_compressed": compressed, "desk_files": len(entry["desk_files"])}


def cmd_verify(args):
    if args.self_check and args.out:
        refuse("self_check_writes_no_receipt")
    if not args.self_check and not args.out:
        refuse("verify_out_missing")
    if args.out:
        check_out(args.out)
    data, manifest = read_json_artifact(args.manifest)
    if hashlib.sha256(data).hexdigest() != args.manifest_sha256:
        refuse("manifest_digest_mismatch")
    if manifest.get("schema") != MANIFEST_SCHEMA or not isinstance(manifest.get("host"), str):
        refuse("manifest_schema_invalid")
    if not args.self_check and manifest["host"] == host_name():
        # A manifest made on the machine being verified is a digest of the copy (BRIEF-B: not authentication).
        refuse("copy_on_source_host")
    root = no_symlink_components(args.root)
    tool = {"zstd": None}
    sessions = {}
    for e in manifest["sessions"]:
        if not args.self_check and str(root / relative(e["copy_path"])) == e["source_path"]:
            refuse("copy_is_source")
        sessions[e["copy_path"]] = located(e["copy_path"], verify_session, root, e, tool)
    loop_dir = no_symlink_components(args.loop_dir)
    for field, item in sorted(manifest["loop"].items()):
        if not no_symlink_components(loop_dir / relative(item["name"])).exists():
            refuse("loop_file_missing", item["name"])
        if hash_file(loop_dir / relative(item["name"]))[0] != item["sha256"]:
            refuse("digest_mismatch", item["name"] + " (loop)")
    totals = {k: sum(s[k] for s in sessions.values()) for k in
              ("files", "bytes", "sums_rows", "sums_rows_compressed", "desk_files")}
    if args.self_check:
        print("self-check sessions=" + str(len(sessions)) + " files=" + str(totals["files"])
              + " bytes=" + str(totals["bytes"]) + " (no receipt written)")
        return 0
    receipt = {"schema": RECEIPT_SCHEMA, "produced_by": RECEIPT_PRODUCER, "verdict": "verified", "manifest_sha256": args.manifest_sha256,
               "root": str(root), "sessions": sessions, "zstd": tool["zstd"], "totals": totals,
               "loop_files": sorted(v["name"] for v in manifest["loop"].values())}
    digest = write_new(args.out, receipt)
    print("verify sessions=" + str(len(sessions)) + " files=" + str(totals["files"])
          + " bytes=" + str(totals["bytes"]) + " receipt_sha256=" + digest)
    return 0


# -- inputs -------------------------------------------------------------------

COUNT_KEYS = ("files", "bytes", "sums_rows", "sums_rows_compressed", "desk_files")
RECEIPT_PRODUCER = "b6_custody_kit.py verify"


def verified_context(args):
    """The manifest and the receipt are each pinned by an out-of-band digest (cold review M3); the receipt must
    be one verify wrote for exactly this manifest: producer mark, every session with its five counts, and the
    counts equal to the manifest's file count and total bytes."""
    data, manifest = read_json_artifact(args.manifest)
    if hashlib.sha256(data).hexdigest() != args.manifest_sha256:
        refuse("manifest_digest_mismatch")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        refuse("manifest_schema_invalid")
    receipt_data, receipt = read_json_artifact(args.verify_receipt)
    if hashlib.sha256(receipt_data).hexdigest() != args.verify_receipt_sha256:
        refuse("receipt_digest_mismatch")
    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("verdict") != "verified":
        refuse("receipt_not_verified")
    if receipt.get("manifest_sha256") != args.manifest_sha256:
        refuse("receipt_manifest_mismatch")
    if set(receipt["sessions"]) != {e["copy_path"] for e in manifest["sessions"]}:
        refuse("receipt_manifest_mismatch")
    if receipt.get("produced_by") != RECEIPT_PRODUCER:
        refuse("receipt_invalid")
    for entry in manifest["sessions"]:
        counts = receipt["sessions"][entry["copy_path"]]
        if not isinstance(counts, dict) or set(counts) != set(COUNT_KEYS) \
                or counts["files"] != entry["file_count"] or counts["bytes"] != entry["total_bytes"]:
            refuse("receipt_invalid")
    return manifest, receipt, Path(receipt["root"])


def emitted_files(entry):
    """Products outside SHA256SUMS (flags, spans) bound by their SOURCE digests: derived/ and withheld/."""
    return {n: s for n, s in entry["outside_sources"].items() if n.split("/")[0] in ("derived", "withheld")}


def authenticated_names(root, entry):
    """Names a mapping may cite (RL-100): SHA256SUMS rows (as sources/...), the keys of the emitted
    `files`, and the three pinned files. Other manifest-hashed files (the inside desk log, markers)
    are not citable."""
    archive = no_symlink_components(root / relative(entry["copy_path"]))
    sums_data, sums_sha = read_hashed(archive / SUMS)
    if sums_sha != entry["sha256sums_sha256"]:
        refuse("sums_digest_mismatch")
    listed = {"sources/" + n for n in sums_names(sums_data)}
    return archive, listed | set(emitted_files(entry)) | {SUMS, HARVEST, ACCEPTANCE}


def session_pin(archive, entry, mapping, names):
    def cited(value):
        if relative(value) not in names:
            refuse("mapping_path_unlisted")
        return value

    if set(mapping) - {"meter_streams", "contention_journal", "clock_journal", "copied_records", "relocations"}:
        refuse("mapping_key_unknown")
    streams = mapping.get("meter_streams")
    if not isinstance(streams, list) or not streams:
        refuse("meter_streams_empty")
    if not isinstance(mapping.get("contention_journal"), str):
        refuse("contention_journal_missing")
    records = mapping.get("copied_records")
    if not isinstance(records, dict) or set(records) != set(FAMILIES):
        refuse("family_set_invalid")
    if any(not isinstance(v, list) or not v for v in records.values()):
        refuse("family_empty")
    pin = {"harvest_sha256": entry["harvest_sha256"], "acceptance_sha256": entry["acceptance_sha256"],
           "sha256sums_sha256": entry["sha256sums_sha256"],
           "files": emitted_files(entry),
           "meter_streams": [cited(s) for s in streams],
           "contention_journal": cited(mapping["contention_journal"]),
           "copied_records": {f: [cited(p) for p in records[f]] for f in FAMILIES}}
    if mapping.get("clock_journal") is not None:
        pin["clock_journal"] = cited(mapping["clock_journal"])
    log = entry["compression"]
    if log is None:
        if mapping.get("relocations"):
            refuse("relocations_without_log")
    elif log["location"] == "inside":
        pin["compression"] = {"path": log["name"], "sha256": log["sha256"]}
        if mapping.get("relocations"):
            pin["compression"]["relocations"] = mapping["relocations"]
    else:
        relocations = {entry["source_path"]: "."}
        for old, new in (mapping.get("relocations") or {}).items():
            if relocations.get(old, new) != new:
                refuse("relocation_conflict")
            relocations[old] = relative(new) if new != "." else "."
        pin["compression"] = {"external_path": str(Path(str(archive) + DESK_SUFFIX) / log["name"]),
                              "sha256": log["sha256"], "relocations": relocations}
    return pin


def cmd_inputs(args):
    manifest, receipt, root = verified_context(args)
    by_path = {e["copy_path"]: e for e in manifest["sessions"]}
    if args.list_names is not None:
        if args.list_names not in by_path:
            refuse("session_unknown")
        _, names = authenticated_names(root, by_path[args.list_names])
        sys.stdout.write("".join(n + "\n" for n in sorted(names)))
        return 0
    if not (args.mapping and args.l9_audit and args.out):
        refuse("inputs_arguments_missing")
    check_out(args.out)
    _, mapping = read_json_artifact(args.mapping)
    if not isinstance(mapping.get("sessions"), dict) or set(mapping["sessions"]) != set(by_path):
        refuse("mapping_session_mismatch")
    sessions = {}
    for copy_path, entry in by_path.items():
        archive, names = located(copy_path, authenticated_names, root, entry)
        sessions[str(archive)] = session_pin(archive, entry, mapping["sessions"][copy_path], names)
    document = {"host": "Air", "l9_audit": args.l9_audit, "sessions": sessions,
                "external": {k: v["sha256"] for k, v in manifest["loop"].items()}}
    digest = write_new(args.out, document)
    print("inputs sessions=" + str(len(sessions)) + " sha256=" + digest)
    return 0


def print_where(name):
    if WHERE["session"] or name:
        print("  at " + (WHERE["session"] or "-") + (": " + name if name else ""), file=sys.stderr)


def main(argv=None):
    WHERE["session"] = None
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    m = sub.add_parser("manifest", help="at the source: digests of each archive's pinned files")
    m.add_argument("--session", action="append", required=True, help="an archive root (repeat)")
    m.add_argument("--loop-attempts", required=True)
    loop_state = m.add_mutually_exclusive_group(required=True)
    loop_state.add_argument("--loop-state")
    loop_state.add_argument("--no-loop-state", action="store_true",
                            help="record that there is no loop-state file (the run-input document then carries none)")
    m.add_argument("--source-host", help="host name to record (default: this host; for rehearsals only)")
    m.add_argument("--out", required=True, help="new manifest file (refused if it exists)")
    v = sub.add_parser("verify", help="on the copy: rehash every SHA256SUMS row")
    v.add_argument("--manifest", required=True)
    v.add_argument("--manifest-sha256", required=True, help="the digest manifest printed at the source")
    v.add_argument("--root", required=True, help="copy root; each archive at <root>/<copy_path>")
    v.add_argument("--loop-dir", required=True, help="directory holding the copied loop files, checked by recorded name")
    v.add_argument("--out", help="new receipt file (counts and bytes only)")
    v.add_argument("--self-check", action="store_true",
                   help="rehash the SOURCE tree against its own manifest; no receipt is written (--out refused)")
    i = sub.add_parser("inputs", help="on the Air: the run-input document, digests from the source manifest")
    i.add_argument("--manifest", required=True)
    i.add_argument("--manifest-sha256", required=True, help="the digest manifest printed at the source")
    i.add_argument("--verify-receipt", required=True)
    i.add_argument("--verify-receipt-sha256", required=True, help="the receipt_sha256 verify printed")
    i.add_argument("--mapping", help="person-written mapping.json")
    i.add_argument("--l9-audit", choices=("not_run", "completed"))
    i.add_argument("--out", help="new run-input document")
    i.add_argument("--list-names", metavar="COPY_PATH",
                   help="print the names one session's mapping may cite (RL-100 item 1) and exit")
    args = parser.parse_args(argv)
    try:
        return {"manifest": cmd_manifest, "verify": cmd_verify, "inputs": cmd_inputs}[args.command](args)
    except Refusal as exc:
        print("refused: " + str(exc), file=sys.stderr)
        print_where(exc.name)
        return 4
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        # The type only: an exception message could quote bytes it failed on.
        print("refused: " + type(exc).__name__, file=sys.stderr)
        print_where(None)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
