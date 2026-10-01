#!/usr/bin/env python3
"""Authenticate and commit the records referenced by a Revision 6 harvest."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import issue_calibration_acceptance_generation as issuer


class LandingRefusal(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def land(harvest_path: Path, repo_root: Path, dest: str | None = None):
    root = repo_root.resolve()

    def git(*arguments):
        result = subprocess.run(["git", "-C", str(root), *arguments],
                                capture_output=True, text=True, check=False, timeout=120)
        if result.returncode:
            raise LandingRefusal(f"git {arguments[0]} failed: {result.stderr.strip()}")
        return result.stdout.strip()

    if Path(git("rev-parse", "--show-toplevel")).resolve() != root:
        raise LandingRefusal("repo-root must be the checkout root")
    if harvest_path.is_symlink():
        raise LandingRefusal("symlink harvest record")
    harvest_raw = harvest_path.read_bytes()
    harvest = issuer._revision_six_json(harvest_raw, "harvest")
    if harvest.get("schema") != "joulewise.harvest_window.v1":
        raise LandingRefusal("unrecognized harvest schema")
    try:
        session_id = harvest["sessions"][-1]["session_id"]
    except (KeyError, IndexError, TypeError) as error:
        raise LandingRefusal("harvest has no current session") from error
    if not isinstance(session_id, str) or not re.fullmatch(issuer.REVISION_SIX_SESSION_ID_PATTERN, session_id):
        raise LandingRefusal("invalid Revision 6 session id")
    destination = dest if dest is not None else f"docs/process_traces/rev6-windows/{session_id}"
    parts = issuer._canonical_relative_parts(destination, "landing destination")
    if ".git" in parts:
        raise LandingRefusal("destination is Git metadata")
    base = Path(*parts)

    references = [(key, harvest[key]) for key in ("r9_window", "start_conditions") if key in harvest]
    end = harvest.get("window_end")
    if end is not None:
        if not isinstance(end, dict):
            raise LandingRefusal("malformed window_end")
        if "source" in end:
            references.append(("window_end.source", end["source"]))

    # Authenticate all sources and existing destinations before writing any
    # copy. Absent references are deliberately absent from the landing set.
    copies = {base / "harvest.json": (harvest_raw, digest(harvest_raw))}
    if references:
        custody = Path(harvest["custody_root"])
        if not custody.is_absolute() or custody.is_symlink():
            raise LandingRefusal("custody root must be absolute and nonsymlink")
        for label, reference in references:
            if not isinstance(reference, dict):
                raise LandingRefusal(f"malformed {label} reference")
            _, raw = issuer._revision_six_bytes(custody, reference)
            relative = base / reference["path"]
            if relative in copies:
                raise LandingRefusal(f"record destination collision: {relative.as_posix()}")
            copies[relative] = (raw, reference["sha256"])

    for relative, (raw, _) in copies.items():
        for parent in (relative, *relative.parents):
            if (root / parent).is_symlink():
                raise LandingRefusal(f"symlink destination: {parent.as_posix()}")
        target = root / relative
        if target.exists() and (not target.is_file() or target.read_bytes() != raw):
            raise LandingRefusal(f"destination exists with different bytes: {relative.as_posix()}")

    paths = sorted(relative.as_posix() for relative in copies)
    for relative, (raw, expected) in copies.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            with target.open("xb") as handle:
                handle.write(raw)
        if digest(target.read_bytes()) != expected:
            raise LandingRefusal(f"copy sha256 mismatch: {relative.as_posix()}")
    git("add", "--", *paths)
    # Commit only these records even if the caller has unrelated staged work.
    git("commit", "--only", "-m", f"Harvest {session_id}: window records", "--", *paths)
    return paths, git("rev-parse", "HEAD")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harvest", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--dest", help="repo-relative directory; defaults to docs/process_traces/rev6-windows/<session_id>")
    args = parser.parse_args(argv)
    try:
        paths, commit = land(args.harvest, args.repo_root, args.dest)
    except (LandingRefusal, issuer.PrepareRefusal, OSError, ValueError, KeyError, TypeError,
            subprocess.SubprocessError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 3
    for path in paths:
        print(path)
    print(commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
