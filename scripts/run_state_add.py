#!/usr/bin/env python3
"""Insert typed RUN_STATE items, allocating numbers on the latest remote head."""

from __future__ import annotations

import argparse
import base64
from collections.abc import Mapping
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid

if __package__:
    from . import gen_current, run_state_items as items
else:
    import gen_current
    import run_state_items as items


RUN_STATE = Path("RUN_STATE.md")
CURRENT = Path("docs/process/CURRENT.json")
TOP_MARKER = items.TOP_MARKER_PREFIX + " newest first. Add with scripts/run_state_add.py; never edit by hand. -->"
LEGACY_MARKER = "<!-- RUN_STATE LEGACY ITEMS below: prose, not typed; cutover {} -->"
RESERVED = {RUN_STATE.as_posix().casefold(), CURRENT.as_posix().casefold()}
SHA = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")


class GitFailure(RuntimeError):
    """A git or network failure, with the request eligible for spooling."""

    code = 3


class RetriesExhausted(GitFailure):
    code = 4


def render_item(number: int, heading: str, header: dict, body: str, pointer: str | None) -> str:
    heading = heading.replace("{{self}}", str(number))
    body = body.replace("{{self}}", str(number)).rstrip("\n")
    parts = [f"{number}. **{heading}**"]
    if pointer is not None:
        pointer = pointer.rstrip("\n")
        parts.append(f"```pointer\n{pointer}\n```")
    parts.append(f"```item\n{items.canonical(header)}\n```")
    if body:
        parts.append(body)
    return "\n\n".join(parts)


def insert(text: str, rendered: str) -> str:
    parsed = _validated(text)
    if parsed.top_line is None:
        raise ValueError("run init first")
    return _insert_at(text, parsed.top_line, rendered)


def _insert_at(text: str, top_line: int, rendered: str) -> str:
    lines = text.split("\n")
    next_line = next(index for index in range(top_line, len(lines)) if lines[index].strip())
    return ("\n".join(lines[:top_line]) + "\n\n" + rendered.rstrip("\n")
            + "\n\n" + "\n".join(lines[next_line:]))


def init_text(text: str) -> tuple[str, int]:
    parsed = _validated(text)
    if parsed.cutover is not None:
        raise ValueError("RUN_STATE is already initialized")
    line, number, _ = max(items.heading_lines(text), key=lambda row: (row[1], row[2]), default=(0, 0, ""))
    cutover = number + 1
    markers = f"{TOP_MARKER}\n\n{LEGACY_MARKER.format(cutover)}\n\n"
    if line:
        lines = text.split("\n")
        lines.insert(line - 1, markers.rstrip("\n") + "\n")
        updated = "\n".join(lines)
    else:
        updated = text + ("\n" if text and not text.endswith("\n") else "") + markers
    _validated(updated)
    return updated, cutover


def _validated(text: str) -> items.Parsed:
    parsed = items.parse(text)
    errors = items.validate(parsed)
    if errors:
        raise ValueError("\n".join(map(str, errors)))
    return parsed


def _line(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip() or not value.isprintable():
        raise ValueError(f"{name} must be nonempty single-line text")


def _request_header(request: dict) -> dict:
    _line(request["heading"], "heading")
    if request["message"] is not None:
        _line(request["message"], "message")
    for trailer in request["trailers"]:
        _line(trailer, "trailer")
        if not re.fullmatch(r"[A-Za-z0-9-]+:[ \t]*\S.*", trailer):
            raise ValueError("trailer must be TOKEN: VALUE")
    header = {key: request[key] for key in items.HEADER_KEYS - {"schema", "number"}}
    header.update(schema=items.SCHEMA, number=1)
    errors = items.header_errors(header, 1, 1)
    if errors:
        raise ValueError("\n".join(map(str, errors)))
    return header


def _prepare(text: str, request: dict, header: dict) -> tuple[int, str, bytes]:
    parsed = _validated(text)
    if parsed.cutover is None:
        raise ValueError("run init first")
    body = request["body"]
    for line in body.splitlines():
        if line.strip() in ("```item", "```pointer"):
            raise ValueError("body cannot contain item or pointer fences")
        if (match := items.HEADING.match(line)) and int(match[1]) >= parsed.cutover:
            raise ValueError("body cannot contain a heading at or above the cutover")
    if (line := items.unclosed_code_fence(body)) is not None:
        raise ValueError(f"body line {line}: unclosed code fence")
    number = max((row[1] for row in items.heading_lines(text)), default=0) + 1
    rendered = render_item(number, request["heading"], {**header, "number": number}, body, request["pointer"])
    updated = _insert_at(text, parsed.top_line, rendered)
    new_items = items.parse(updated).items
    if len(new_items) != len(parsed.items) + 1 or new_items[0].number != number:
        raise ValueError("insertion must add exactly one typed item and preserve all previous typed items")
    for before, after in zip(parsed.items, new_items[1:]):
        if (before.number, before.heading, before.header) != (after.number, after.heading, after.header):
            raise ValueError(f"insertion must preserve previous typed item {before.number}")
    return number, updated, gen_current.render(updated)


def _stage_file(path: Path, data: bytes) -> Path:
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".run_state_add.", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            os.fchmod(stream.fileno(), mode)
            stream.write(data)
            stream.flush()
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    return temporary


def _write_pair(run_state: Path, current: Path, updated: str, document: bytes) -> None:
    if run_state.resolve() == current.resolve():
        raise ValueError("RUN_STATE and CURRENT must be different files")
    staged = []
    try:
        old = _stage_file(run_state, run_state.read_bytes())
        staged.append(old)
        new = _stage_file(run_state, updated.encode("utf-8"))
        staged.append(new)
        view = _stage_file(current, document)
        staged.append(view)
        os.replace(new, run_state)
        try:
            os.replace(view, current)
        except OSError:
            os.replace(old, run_state)
            raise
    finally:
        for path in staged:
            path.unlink(missing_ok=True)


def add_local(run_state: Path, current: Path, request: dict) -> int:
    header = _request_header(request)
    number, updated, document = _prepare(run_state.read_bytes().decode("utf-8"), request, header)
    _write_pair(run_state, current, updated, document)
    return number


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          env={**os.environ, "LC_ALL": "C"}).stdout


def _sha(output: str) -> str:
    value = output.strip()
    if not SHA.fullmatch(value):
        raise GitFailure(f"git returned an invalid revision: {value!r}")
    return value


def _repo_root(path: Path) -> Path:
    root = Path(_git(path, "rev-parse", "--show-toplevel").rstrip("\n"))
    if not root.is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise GitFailure("git returned an unexpected repository root")
    return root.resolve()


def _with_path(filename: str) -> Path:
    relative = Path(filename)
    if (not relative.parts or relative.is_absolute() or ".." in relative.parts
            or any(part.casefold() == ".git" for part in relative.parts)
            or relative.as_posix().casefold() in RESERVED):
        raise ValueError(f"--with must be a separate repository-relative file: {filename!r}")
    return relative


def _source_files(repo: Path, filenames: list[str]) -> dict[Path, Path]:
    sources = {}
    for filename in filenames:
        relative = _with_path(filename)
        source = repo / relative
        if source.resolve() != source or not source.is_file():
            raise ValueError(f"--with must be a regular file without symlinks: {filename!r}")
        sources[relative] = source
    return sources


@contextmanager
def _worktree(repo: Path, base: str):
    with tempfile.TemporaryDirectory(prefix="joulewise-run-state-") as temp:
        path = Path(temp).resolve() / "worktree"
        try:
            _git(repo, "worktree", "add", "--detach", str(path), base)
            if _sha(_git(path, "rev-parse", "HEAD")) != base:
                raise GitFailure("detached worktree did not start at the fetched head")
            yield path
        finally:
            if (path / ".git").is_file():
                _git(repo, "worktree", "remove", "--force", str(path))
                if path.exists():
                    raise GitFailure("git did not remove its temporary worktree")


def _remote_head(repo: Path, remote: str, ref: str) -> str:
    result = _git(repo, "ls-remote", "--exit-code", "--refs", "--", remote, ref).strip()
    sha, tab, name = result.partition("\t")
    if not tab or name != ref:
        raise GitFailure("git did not report the requested remote branch")
    return _sha(sha)


def _push(repo: Path, remote: str, ref: str, base: str) -> bool:
    try:
        result = _git(repo, "push", "--porcelain", "--", remote, f"HEAD:{ref}")
    except subprocess.CalledProcessError as error:
        for line in (error.stdout or "").splitlines():
            flag, destination, reason = (line.split("\t") + ["", ""])[:3]
            if flag != "!" or destination.rpartition(":")[2] != ref:
                continue
            if reason in ("[rejected] (fetch first)", "[rejected] (non-fast-forward)"):
                return False
            if reason in ("[remote rejected] (failed to update ref)",
                          "[remote rejected] (incorrect old value provided)"):
                if _remote_head(repo, remote, ref) != base:
                    return False
        raise
    for line in result.splitlines():
        flag, destination, _ = (line.split("\t") + ["", ""])[:3]
        if flag in (" ", "*", "=") and destination.rpartition(":")[2] == ref:
            return True
    raise GitFailure("git push did not confirm the requested destination")


def _commit(path: Path, number: int, request: dict,
            sources: Mapping[Path, Path | tuple[bytes, int]]) -> str:
    for relative, source in sources.items():
        target = path / relative
        if target.resolve() != target or (target.exists() and not target.is_file()):
            raise ValueError(f"--with requires a regular checkout path without symlinks: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(source, Path):
            shutil.copy2(source, target)
        else:
            data, mode = source
            target.write_bytes(data)
            target.chmod(mode)
    allowed = {str(p) for p in (RUN_STATE, CURRENT, *sources)}
    _git(path, "--literal-pathspecs", "add", "--", *sorted(allowed))
    staged = set(_git(path, "diff", "--cached", "--name-only", "-z").strip("\0").split("\0"))
    if str(RUN_STATE) not in staged or staged - allowed:
        raise GitFailure("git staged an unexpected set of paths")
    for relative, source in sources.items():
        if isinstance(source, Path):
            continue
        blob = _git(path, "hash-object", "--no-filters", "--", str(relative)).strip()
        if _git(path, "rev-parse", "--verify", f":{relative}").strip() != blob:
            raise ValueError(f"Git staging changed the snapshotted --with bytes for {relative}")
    label = (request["message"] or request["heading"]).replace("{{self}}", str(number))
    subject = f"RUN_STATE {number}: {label}"[:100].rstrip()
    message = ["-m", subject]
    if request["trailers"]:
        message += ["-m", "\n".join(request["trailers"])]
    _git(path, "commit", *message)
    head = _sha(_git(path, "rev-parse", "HEAD"))
    if _git(path, "show", "-s", "--format=%s", head).rstrip("\n") != subject:
        raise GitFailure("git did not record the expected commit subject")
    return head


def _fetch(repo: Path, remote: str, ref: str, private_ref: str) -> str:
    _git(repo, "fetch", "--no-tags", "--no-write-fetch-head", "--refmap=", "--",
         remote, f"+{ref}:{private_ref}")
    return _sha(_git(repo, "rev-parse", "--verify", private_ref))


def _remove_ref(repo: Path, private_ref: str) -> None:
    _git(repo, "update-ref", "-d", private_ref)
    if private_ref in _git(repo, "for-each-ref", "--format=%(refname)", private_ref).splitlines():
        raise GitFailure("git left a private fetch ref behind")


def _land(repo: Path, request: dict, remote: str, branch: str, attempts: int, *,
          snapshots: dict[Path, tuple[bytes, int]] | None = None) -> tuple[int, str]:
    header = _request_header(request)
    repo = _repo_root(repo)
    sources = _source_files(repo, request["with"]) if snapshots is None else snapshots
    ref = f"refs/heads/{branch}"
    if _git(repo, "check-ref-format", "--normalize", ref).rstrip("\n") != ref:
        raise ValueError(f"invalid target branch: {branch!r}")
    private_ref = f"refs/joulewise/run-state-add/{uuid.uuid4().hex}"
    landed = None
    try:
        for _ in range(min(attempts, 5)):
            base = _fetch(repo, remote, ref, private_ref)
            with _worktree(repo, base) as path:
                source, current = path / RUN_STATE, path / CURRENT
                if source.resolve() != source or current.resolve() != current:
                    raise ValueError("RUN_STATE and CURRENT must be regular checkout paths")
                number, updated, document = _prepare(source.read_bytes().decode("utf-8"), request, header)
                source.write_text(updated, encoding="utf-8")
                current.write_bytes(document)
                head = _commit(path, number, request, sources)
                if _push(path, remote, ref, base):
                    landed = number, head
            if landed is not None:
                return landed
        raise RetriesExhausted(f"push rejected after {min(attempts, 5)} attempts")
    except (GitFailure, subprocess.CalledProcessError, OSError) as error:
        if landed is None:
            raise
        print(f"run_state_add: item landed; worktree cleanup failed: {_error_text(error)}", file=sys.stderr)
        return landed
    finally:
        try:
            _remove_ref(repo, private_ref)
        except (GitFailure, subprocess.CalledProcessError, OSError) as error:
            if landed is not None:
                print(f"run_state_add: item landed; ref cleanup failed: {_error_text(error)}", file=sys.stderr)
            else:
                raise


def _spool_dir() -> Path:
    return Path(os.environ.get("JW_RUN_STATE_SPOOL", "~/.joulewise/run_state_spool")).expanduser()


@contextmanager
def _locked(spool: Path):
    spool.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (spool / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def _pending(spool: Path):
    return (path for path in spool.iterdir() if path.name.endswith(".json"))


def _write_spool_file(target: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".request.", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(data)
            stream.flush()
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)


def _spool(spool: Path, request: dict, repo: Path) -> Path:
    if request["with"]:
        snapshots = {}
        for relative, source in _source_files(_repo_root(repo), request["with"]).items():
            with source.open("rb") as stream:
                snapshots[relative.as_posix()] = {
                    "mode": stat.S_IMODE(os.fstat(stream.fileno()).st_mode),
                    "data": base64.b64encode(stream.read()).decode("ascii"),
                }
        request = {**request, "with_snapshot": snapshots}
    target = spool / f"{time.time_ns():020d}-{uuid.uuid4().hex}.json"
    data = (json.dumps(request, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    _write_spool_file(target, data)
    return target


def _spooled_files(request: dict) -> dict[Path, tuple[bytes, int]]:
    relatives = dict.fromkeys(_with_path(filename) for filename in request["with"])
    snapshots = request.get("with_snapshot")
    if snapshots is None:
        if relatives:
            raise ValueError("missing --with snapshot for queued request")
        return {}
    if not isinstance(snapshots, dict) or snapshots.keys() != {path.as_posix() for path in relatives}:
        raise ValueError("--with snapshot paths must match the queued attachments")
    sources = {}
    for relative in relatives:
        snapshot = snapshots[relative.as_posix()]
        if not isinstance(snapshot, dict) or snapshot.keys() != {"mode", "data"}:
            raise ValueError(f"invalid --with snapshot for {relative}")
        mode, data = snapshot["mode"], snapshot["data"]
        if type(mode) is not int or not 0 <= mode <= 0o7777 or not isinstance(data, str):
            raise ValueError(f"invalid --with snapshot for {relative}")
        sources[relative] = base64.b64decode(data, validate=True), mode
    return sources


def _quarantine(path: Path, error: ValueError) -> None:
    failed = path.parent / "failed"
    failed.mkdir(mode=0o700, exist_ok=True)
    target = failed / path.name
    # Leave the request pending if its reason cannot be recorded.
    _write_spool_file(target.with_suffix(".reason"), f"{error}\n".encode("utf-8"))
    os.replace(path, target)
    print(f"run_state_add: quarantined {target}: {error}", file=sys.stderr)


def _error_text(error: Exception) -> str:
    if isinstance(error, subprocess.CalledProcessError):
        return (error.stderr or "").strip() or (error.stdout or "").strip() or str(error)
    return str(error)


def add_git(repo: Path, request: dict, *, remote="origin", branch="main", attempts=5) -> tuple[int, str]:
    spool = _spool_dir()
    with _locked(spool):
        if any(_pending(spool)):
            raise GitFailure(f"pending requests in {spool}; run python3 scripts/run_state_add.py flush-spool "
                             "before retrying this add")
        try:
            return _land(repo, request, remote, branch, attempts)
        except (GitFailure, subprocess.CalledProcessError, OSError) as error:
            target = _spool(spool, request, repo)
            failure = RetriesExhausted if isinstance(error, RetriesExhausted) else GitFailure
            raise failure(f"{_error_text(error)}; spooled at {target}") from error


def _flush(repo: Path) -> int:
    spool = _spool_dir()
    with _locked(spool):
        queue = sorted(_pending(spool))
        if not queue:
            repo = _repo_root(repo)
            private_ref = f"refs/joulewise/run-state-add/{uuid.uuid4().hex}"
            try:
                head = _fetch(repo, "origin", "refs/heads/main", private_ref)
                if _validated(_git(repo, "show", f"{head}:{RUN_STATE}")).cutover is None:
                    raise ValueError("run init first")
            finally:
                _remove_ref(repo, private_ref)
        quarantined = False
        for path in queue:
            try:
                request = json.loads(path.read_text(encoding="utf-8"))
                number, head = _land(repo, request, "origin", "main", 5,
                                     snapshots=_spooled_files(request))
            except ValueError as error:
                _quarantine(path, error)
                quarantined = True
                continue
            path.unlink()
            print(number, head)
        return 2 if quarantined else 0


def _iso(value: str, name: str) -> int:
    epoch = gen_current._epoch(value, name, 1)
    if type(epoch) is not int:
        raise ValueError(f"{name} must specify a whole second")
    return epoch


def _read_request(args) -> dict:
    changes = []
    for setting in args.set:
        match = re.fullmatch(r"([1-9][0-9]*)=([A-Z]+)@(.+)", setting)
        if not match:
            raise ValueError("--set requires N=STATUS@ISO")
        changes.append({"item": int(match[1]), "status": match[2], "at_epoch_s": _iso(match[3], "--set")})
    return {
        "heading": args.heading, "body": args.body.read_text(encoding="utf-8"),
        "pointer": args.pointer.read_text(encoding="utf-8") if args.pointer else None,
        "owner": args.owner, "status": args.status,
        "issued_epoch_s": _iso(args.issued, "--issued") if args.issued else int(time.time()),
        "expires_epoch_s": _iso(args.expires, "--expires") if args.expires else None,
        "supersedes": args.supersedes, "sets": changes, "with": args.with_files,
        "message": args.message, "trailers": args.trailer,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    add = commands.add_parser("add")
    commands.add_parser("flush-spool")
    for command in (add, init):
        command.add_argument("--run-state", type=Path)
        command.add_argument("--current", type=Path)
        command.add_argument("--no-git", action="store_true")
    add.add_argument("--heading", required=True)
    add.add_argument("--body", required=True, type=Path)
    add.add_argument("--owner", required=True, choices=items.OWNERS)
    add.add_argument("--status", required=True, choices=items.INITIAL)
    for field in ("issued", "expires", "message"):
        add.add_argument(f"--{field}")
    add.add_argument("--pointer", type=Path)
    for field in ("supersedes", "set", "trailer"):
        add.add_argument(f"--{field}", action="append", default=[])
    add.add_argument("--with", dest="with_files", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if args.command == "flush-spool":
            return _flush(Path.cwd())
        else:
            if args.no_git != bool(args.run_state and args.current) or (
                    (args.run_state is None) != (args.current is None)):
                raise ValueError("fixture mode requires --no-git, --run-state and --current together")
            if args.command == "init":
                root = _repo_root(Path.cwd()) if not args.no_git else None
                state, current = ((args.run_state, args.current) if args.no_git
                                  else (root / RUN_STATE, root / CURRENT))
                updated, cutover = init_text(state.read_bytes().decode("utf-8"))
                _write_pair(state, current, updated, gen_current.render(updated))
                print(cutover)
            elif args.no_git:
                if args.with_files:
                    raise ValueError("--with requires git mode")
                print(add_local(args.run_state, args.current, _read_request(args)))
            else:
                print(*add_git(Path.cwd(), _read_request(args)))
    except (GitFailure, subprocess.CalledProcessError) as error:
        print(f"run_state_add: {_error_text(error)}", file=sys.stderr)
        return error.code if isinstance(error, GitFailure) else 3
    except (OSError, ValueError, KeyError) as error:
        print(f"run_state_add: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
