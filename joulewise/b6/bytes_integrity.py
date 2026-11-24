"""Private, two-phase BYTES export integrity manifests."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile

NAME = "bytes-export-integrity.json"
SCHEMA = "joulewise.bytes_export_integrity.v1"
ROOT = Path(__file__).resolve().parents[2]


def _git(repo, *args):
    environment = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                   "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"}
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY"):
        environment.pop(name, None)
    result = subprocess.run(["git", *args], cwd=repo, env=environment, capture_output=True, check=False)
    if result.returncode:
        raise ValueError("BYTES export manifest: Git check failed for " + args[0])
    return result.stdout


def _repo(path, *, create=False):
    if path is None:
        raise ValueError("BYTES export manifest: private repository is required")
    path = Path(path).resolve()
    if path.is_relative_to(ROOT):
        raise ValueError("BYTES export manifest: use a private export repository")
    if create and not (path / ".git").exists():
        path.mkdir(parents=True, exist_ok=True)
        _git(path, "init", "--quiet")
    if Path(os.fsdecode(_git(path, "rev-parse", "--show-toplevel").strip())).resolve() != path:
        raise ValueError("BYTES export manifest: expected the private export Git root")
    if b"mpmdw/joulewise" in _git(path, "remote", "-v").lower():
        raise ValueError("BYTES export manifest: use a private export repository")
    return path


def _relative(value):
    if not isinstance(value, str) or not value or value == ".":
        raise ValueError("BYTES export manifest: invalid relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ValueError("BYTES export manifest: root-escaping or noncanonical path")
    return value


def _regular(root, relative):
    path = root / _relative(relative)
    if path.resolve() != path or not path.is_file():
        raise ValueError(f"BYTES export manifest: missing or nonregular file {relative}")
    return path


def _fingerprint(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("BYTES export manifest: nonregular input")
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def _scan(root, *, ignore=(), recursive=True, reject_withheld=False):
    if root.resolve() != root or not root.is_dir():
        raise ValueError("BYTES export manifest: missing or nonregular input root")
    names = []
    pending = [root]
    while pending:
        for path in pending.pop().iterdir():
            relative = path.relative_to(root).as_posix()
            if relative in ignore:
                continue
            if reject_withheld and (path.name == "withheld" or path.name.endswith(".withheld.csv")):
                raise ValueError("BYTES export manifest: held-out path in export root")
            if path.is_symlink():
                raise ValueError("BYTES export manifest: symlink in authorized input set")
            if recursive and path.is_dir():
                pending.append(path)
            else:
                names.append(relative)
    return sorted(names)


def _root(path, kind, *, names=(), ignore=()):
    return {"path": str(Path(path).resolve()), "kind": kind, "names": sorted(names), "ignore": sorted(ignore)}


def _membership(roots):
    members = {}
    for name, scope in sorted(roots.items()):
        root = Path(scope["path"])
        if not root.is_absolute() or root.resolve() != root:
            raise ValueError("BYTES export manifest: invalid input root")
        kind = scope["kind"]
        if kind == "named":
            filenames = scope["names"]
        elif kind == "compression":
            journal = root / "compression.jsonl"
            filenames = [journal.name] if journal.exists() or journal.is_symlink() else []
        elif kind in {"tables", "derived", "bindings", "release"}:
            filenames = _scan(root, ignore=scope["ignore"], recursive=kind in {"tables", "derived"},
                              reject_withheld=kind in {"tables", "derived"})
            if kind in {"bindings", "release"} and filenames != scope["names"]:
                raise ValueError(f"BYTES export manifest: unexpected or missing {kind} file")
        else:
            raise ValueError("BYTES export manifest: unknown input root")
        for relative in filenames:
            identity = (name, _relative(relative))
            if identity in members:
                raise ValueError("BYTES export manifest: duplicate path")
            members[identity] = _regular(root, relative)
    if len(set(members.values())) != len(members):
        raise ValueError("BYTES export manifest: duplicate physical path")
    return members


def _entries(members):
    rows = []
    for (root, path), physical in sorted(members.items()):
        size, digest = _fingerprint(physical)
        rows.append({"root": root, "path": path, "length": size, "sha256": digest})
    return rows


def _blob(repo, commit):
    if not isinstance(commit, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
        raise ValueError("BYTES export manifest: designate the full export commit SHA")
    if _git(repo, "rev-parse", "--verify", commit + "^{commit}").decode().strip() != commit:
        raise ValueError("BYTES export manifest: expected a commit")
    line = _git(repo, "ls-tree", commit, "--", NAME).decode().strip()
    entry, _, name = line.partition("\t")
    if name != NAME or entry.split()[:2] != ["100644", "blob"]:
        raise ValueError("BYTES export manifest: committed regular manifest is missing")
    return _git(repo, "cat-file", "blob", entry.split()[2])


def _document(raw):
    def unique_mapping(pairs):
        mapping = dict(pairs)
        if len(mapping) != len(pairs):
            raise ValueError("BYTES export manifest: duplicate object key")
        return mapping

    try:
        return json.loads(raw, object_pairs_hook=unique_mapping)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("BYTES export manifest: malformed document") from exc


def _check_release_entries(document, scope, entries):
    expected = {}
    for keys in document["bindings"].values():
        for name, digest in keys.items():
            if expected.setdefault(name, digest) != digest:
                raise ValueError("BYTES export manifest: inconsistent session key binding")
    names = {row["path"] for row in entries}
    if (set(expected) != set(document["fit_keys"]) or names - set(expected) - {"release.json"}
            or scope["kind"] != "release" or scope["ignore"] != document["heldout_names"]
            or sorted(names) != scope["names"]):
        raise ValueError("BYTES export manifest: unauthorized release entry")
    if {row["path"]: row["sha256"] for row in entries if row["path"] in expected} != expected:
        raise ValueError("BYTES export manifest: released key differs from its session binding")


def _check_release_extension(repo, commit, document):
    capture_commit = document["capture_commit"]
    captured = _document(_blob(repo, capture_commit))
    _git(repo, "merge-base", "--is-ancestor", capture_commit, commit)
    initial = {**document, "phase": "captured", "roots": dict(document["roots"]),
               "files": [row for row in document["files"] if row["root"] != "release"]}
    del initial["capture_commit"], initial["roots"]["release"]
    if initial != captured:
        raise ValueError("BYTES export manifest: finalization changed the captured inputs")
    _check_release_entries(captured, document["roots"]["release"],
                           [row for row in document["files"] if row["root"] == "release"])


def verify(repo, commit, *, phase="finalized"):
    """Authenticate the manifest before following any of its input paths."""
    repo = _repo(repo)
    expected = _blob(repo, commit)
    current = _regular(repo, NAME).read_bytes()
    if current != expected:
        raise ValueError("BYTES export manifest: working bytes differ from the designated commit")
    document = _document(current)
    if document["schema"] != SCHEMA or document["phase"] != phase:
        raise ValueError(f"BYTES export manifest: a {phase} manifest is required")
    entries = document["files"]
    for row in entries:
        if (set(row) != {"root", "path", "length", "sha256"} or type(row["length"]) is not int
                or row["length"] < 0 or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
            raise ValueError("BYTES export manifest: malformed file entry")
    identities = [(row["root"], _relative(row["path"])) for row in entries]
    if identities != sorted(set(identities)):
        raise ValueError("BYTES export manifest: unsorted or duplicate entry")
    if phase == "finalized":
        _check_release_extension(repo, commit, document)
    members = _membership(document["roots"])
    if set(members) != set(identities):
        raise ValueError("BYTES export manifest: missing or extra file")
    if _entries(members) != entries:
        raise ValueError("BYTES export manifest: changed input length or digest")
    return document


@contextmanager
def _publication(repo):
    git_dir = Path(os.fsdecode(_git(repo, "rev-parse", "--absolute-git-dir").strip()))
    with (git_dir / "bytes-export-integrity.lock").open("ab") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def _publish(repo, document):
    fd, temporary = tempfile.mkstemp(prefix=".bytes-export-integrity-", dir=repo)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write((json.dumps(document, sort_keys=True, indent=2) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, repo / NAME)
    finally:
        Path(temporary).unlink(missing_ok=True)
    _git(repo, "add", "--", NAME)
    _git(repo, "-c", "user.name=BYTES export", "-c", "user.email=bytes-export@invalid",
         "commit", "--only", "--no-gpg-sign", "-m", "Record BYTES " + document["phase"] + " export inventory",
         "--", NAME)
    return _git(repo, "rev-parse", "HEAD").decode().strip()


def _key_name(key):
    return "config-" + hashlib.sha256(key.encode()).hexdigest()[:16] + ".json"


def _table_paths(roots, sessions):
    found = {}
    for root_id, path in roots.items():
        root = Path(path["path"])
        for relative in _scan(root, ignore=path["ignore"], reject_withheld=True):
            name = Path(relative).name
            for suffix in (".runs.csv", ".session.json"):
                if name.endswith(suffix):
                    identity = (name.removesuffix(suffix), suffix)
                    if identity in found:
                        raise ValueError("BYTES export manifest: duplicate session export")
                    found[identity] = (root_id, relative)
                    break
            else:
                raise ValueError("BYTES export manifest: unexpected file in export root")
    if set(found) != {(sid, suffix) for sid in sessions for suffix in (".runs.csv", ".session.json")}:
        raise ValueError("BYTES export manifest: tables differ from expected campaign sessions")
    return found


def capture(repo, campaign_path, export_dirs, pack_records_root):
    """Publish the export-time inventory for the campaign's counting sessions."""
    repo = _repo(repo, create=True)
    campaign_path = Path(campaign_path).resolve(strict=True)
    campaign = json.loads(campaign_path.read_bytes())
    sessions = {}
    for row in campaign["sessions"]:
        sid = _relative(row["session_id"])
        if "/" in sid or sid in sessions:
            raise ValueError("BYTES export manifest: invalid or duplicate session")
        archive = Path(row["archive"])
        if not archive.is_absolute() or archive.resolve(strict=True) != archive:
            raise ValueError("BYTES export manifest: archive locator must be canonical and absolute")
        sessions[sid] = str(archive)
    tables = {}
    for index, path in enumerate(sorted({Path(path).resolve() for path in export_dirs})):
        ignore = [".git", NAME] if path == repo else []
        if campaign_path.is_relative_to(path):
            ignore.append(campaign_path.relative_to(path).as_posix())
        tables[f"tables:{index}"] = _root(path, "tables", ignore=ignore)
    exports = _table_paths(tables, sessions)
    bindings = Path(pack_records_root) / "bytes/blinding-sessions"
    names = [sid + ".json" for sid in sessions]
    scopes = {**tables, "campaign": _root(campaign_path.parent, "named", names=[campaign_path.name]),
              "bindings": _root(bindings, "bindings", names=names, ignore=[sid + ".lock" for sid in sessions])}
    keys = {"pack.json", _key_name("neg8_reference")}
    heldout = set()
    for model in campaign["models"]:
        (keys if model["role"] == "fit" else heldout).add(_key_name(model["config_key"]))
    for sid, archive in sessions.items():
        derived = Path(archive) / "derived"
        scopes[f"derived:{sid}"] = _root(derived, "derived")
        _regular(derived, "roster.json")
        scopes[f"harvest:{sid}"] = _root(archive, "named", names=["harvest.json"])
        journal_root = Path(archive + ".desk")
        scopes[f"compression:{sid}"] = _root(journal_root, "compression")
    members = _membership(scopes)
    entries = _entries(members)
    fingerprints = {(row["root"], row["path"]): row["sha256"] for row in entries}
    bindings_by_session = {}
    config_names = set()
    for sid in sessions:
        receipt = json.loads(members[(f"harvest:{sid}", "harvest.json")].read_bytes())
        if receipt["outputs"].get("derived/roster.json") != fingerprints[(f"derived:{sid}", "roster.json")]:
            raise ValueError("BYTES export manifest: roster differs from its export-time digest")
        binding = json.loads(members[("bindings", sid + ".json")].read_bytes())
        if binding.get("session_id") != sid:
            raise ValueError("BYTES export manifest: incorrect session binding")
        root_id, relative = exports[(sid, ".session.json")]
        sidecar = json.loads(members[(root_id, relative)].read_bytes())
        digests = binding["key_sha256"]
        if digests != sidecar["blinding"]["key_sha256"] or "pack.json" not in digests:
            raise ValueError("BYTES export manifest: session binding differs from export sidecar")
        bindings_by_session[sid] = {name: digest for name, digest in digests.items() if name in keys}
        config_names.update(bindings_by_session[sid])
    if keys != config_names:
        raise ValueError("BYTES export manifest: an expected fit key has no session binding")
    table_files = [str(members[exports[(sid, ".runs.csv")]]) for sid in sorted(sessions)]
    with _publication(repo):
        if (repo / NAME).exists():
            raise ValueError("BYTES export manifest: export inventory already exists")
        return _publish(repo, {"schema": SCHEMA, "phase": "captured", "files": entries,
                               "roots": scopes, "archive_roots": sessions, "table_files": table_files,
                               "bindings": bindings_by_session, "fit_keys": sorted(keys),
                               "heldout_names": sorted(heldout)})


def finalize(repo, capture_commit, key_dir):
    repo = _repo(repo)
    with _publication(repo):
        document = verify(repo, capture_commit, phase="captured")
        key_dir = Path(key_dir).resolve(strict=True)
        names = list(document["fit_keys"])
        if (key_dir / "release.json").exists():
            names.append("release.json")
        scope = _root(key_dir, "release", names=names, ignore=document["heldout_names"])
        # A release is fit-only at this boundary. Later held-out keys stay outside
        # the authorized fit membership and are never opened by this verifier.
        if _scan(key_dir, recursive=False) != sorted(names):
            raise ValueError("BYTES export manifest: released directory is not the authorized fit set")
        entries = _entries(_membership({"release": scope}))
        _check_release_entries(document, scope, entries)
        document["roots"]["release"] = scope
        document["files"] = sorted(document["files"] + entries, key=lambda row: (row["root"], row["path"]))
        document["phase"] = "finalized"
        document["capture_commit"] = capture_commit
        return _publish(repo, document)


def add_arguments(parser):
    parser.add_argument("--export-seal-repo", type=Path, help="private BYTES export Git root")
    parser.add_argument("--export-seal-commit", help="full commit object id for the BYTES export manifest")


def options(repo, commit):
    return ["--export-seal-repo", str(repo), "--export-seal-commit", commit]


def check_inputs(repo, commit, *, stage, campaign, export_dirs=(), tables=(), archives=(), key_dir=None,
                 probe=False):
    document = verify(repo, commit, phase="captured" if probe or stage == "blinded" else "finalized")
    scopes = document["roots"]
    source = scopes["campaign"]
    if Path(campaign).resolve() != Path(source["path"]) / source["names"][0]:
        raise ValueError("BYTES export manifest: campaign path differs")
    expected_dirs = {scope["path"] for scope in scopes.values() if scope["kind"] == "tables"}
    if bool(export_dirs) == bool(tables):
        raise ValueError("BYTES export manifest: name the sealed tables or their directories")
    if export_dirs and (len(export_dirs) != len(expected_dirs)
                        or {str(Path(path).resolve()) for path in export_dirs} != expected_dirs):
        raise ValueError("BYTES export manifest: table roots differ")
    if tables and (len(tables) != len(document["table_files"]) or
                   {str(Path(path).resolve()) for path in tables} != set(document["table_files"])):
        raise ValueError("BYTES export manifest: table paths differ")
    if archives is not None and stage != "blinded":
        expected = sorted(document["archive_roots"].values())
        if sorted(str(Path(archive).resolve()) for archive in archives) != expected:
            raise ValueError("BYTES export manifest: archive roots differ")
    if probe:
        if stage != "fit" or key_dir is None or not Path(key_dir).is_dir() or any(Path(key_dir).iterdir()):
            raise ValueError("BYTES export manifest: probe requires a fit command with an empty key directory")
    elif stage == "fit" and (key_dir is None or Path(key_dir).resolve() != Path(scopes["release"]["path"])):
        raise ValueError("BYTES export manifest: fit key directory differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    parser.add_argument("--stage", choices=("blinded", "fit", "heldout"), required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--export-dir", action="append", default=[], type=Path)
    parser.add_argument("--table", action="append", default=[], type=Path)
    parser.add_argument("--archive", action="append", default=[], type=Path)
    parser.add_argument("--key-dir", type=Path)
    parser.add_argument("--no-key-probe", action="store_true")
    args = parser.parse_args()
    try:
        check_inputs(args.export_seal_repo, args.export_seal_commit, stage=args.stage, campaign=args.manifest,
                     export_dirs=args.export_dir, tables=args.table, archives=args.archive, key_dir=args.key_dir,
                     probe=args.no_key_probe)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
