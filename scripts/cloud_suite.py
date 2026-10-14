#!/usr/bin/env python3
"""Run CI's unit-test jobs in separate cloud sessions, then save their results.

Stdlib only. Local commands are run/collect/cleanup; cloud commands are
remote-shard/remote-wait. collect and cleanup take --state PATH (run.json).
Timing overrides for synthetic tests: CLOUD_SUITE_TEST_CREATED_TIMEOUT (120),
CLOUD_SUITE_TEST_POST_CREATE_WAIT (10), CLOUD_SUITE_TEST_KILL_GRACE (3),
CLOUD_SUITE_TEST_WATCH_POLL (0.1), CLOUD_SUITE_TEST_PUSH_BACKOFF (10,30,90),
CLOUD_SUITE_TEST_TMP_ROOT (/tmp), and CLOUD_SUITE_TEST_LOG_LIMIT (41943040).
Backoff entries apply after failed push attempts; only the first two are
needed between the three attempts. TMP_ROOT contains jwsuite-RUN-JOB directories.
Test timing overrides do not alter the commands or result classifications.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import signal
import site
import subprocess
import sys
import textwrap
import time


class SuiteError(ValueError):
    """An actionable refusal, reported with exit code 2."""


STEPS = {
    "test": "Unit tests (stdlib core only, per D-009/D-017)",
    "calibration-exits-exclusive": "Exclusive calibration-exit module",
    "calibration-writer-crash-matrix-exclusive":
        "Exclusive calibration-writer crash-matrix module (shard ${{ matrix.shard }} of 2)",
}
SUMMARY = re.compile(
    r"^SHARD SUMMARY index=\d+/\d+ modules=(?P<modules>\d+) "
    r"tests=(?P<tests>\d+) failures=(?P<failures>\d+) errors=(?P<errors>\d+) "
    r"skipped=(?P<skipped>\d+) result=(?P<result>PASS|FAIL)\s*$"
)


def parse_ci_jobs(text) -> dict:
    """Extract the three named jobs/steps; refuse rather than guess on CI drift."""
    lines = text.splitlines()
    headers = [(i, m.group(1)) for i, line in enumerate(lines)
               if (m := re.fullmatch(r"  ([A-Za-z0-9_-]+):\s*", line))]
    blocks = {name: lines[start + 1: headers[n + 1][0] if n + 1 < len(headers)
                          else len(lines)] for n, (start, name) in enumerate(headers)}
    found = {}
    for name, step in STEPS.items():
        if name not in blocks:
            raise SuiteError(f"missing CI job {name}")
        block = blocks[name]
        marker = f"      - name: {step}"
        if marker not in block:
            raise SuiteError(f"missing CI step {name}: {step}")
        start = block.index(marker) + 1
        end = next((i for i in range(start, len(block))
                    if block[i].startswith("      - ")), len(block))
        step_lines = block[start:end]
        run = next((i for i, line in enumerate(step_lines)
                    if line.startswith("        run:")), None)
        if run is None:
            raise SuiteError(f"missing run in CI step {step}")
        value = step_lines[run].split("run:", 1)[1].strip()
        if name == "calibration-exits-exclusive":
            if not value or value in ("|", ">"):
                raise SuiteError(f"missing command in CI step {step}")
            found[name] = {"command": value}
            continue
        shell = textwrap.dedent("\n".join(step_lines[run + 1:])).splitlines()
        opening = next((i for i, line in enumerate(shell)
                        if line == "python - <<'PY'"), None)
        closing = next((i for i, line in enumerate(shell)
                        if opening is not None and i > opening and line == "PY"), None)
        if value != "|" or opening is None or closing is None:
            raise SuiteError(f"missing python heredoc in CI step {step}")
        body = "\n".join(shell[opening + 1:closing]) + "\n"
        try:
            compile(body, f"ci.yml:{name}", "exec")
        except SyntaxError as exc:
            raise SuiteError(f"invalid heredoc in CI step {step}: {exc}") from exc
        found[name] = {"body": body}
        if name.endswith("crash-matrix-exclusive"):
            matrix = next((re.fullmatch(r"\s+shard: \[([0-9, ]+)\]\s*", line)
                           for line in block if re.fullmatch(
                               r"\s+shard: \[([0-9, ]+)\]\s*", line)), None)
            if not matrix:
                raise SuiteError(f"missing shard matrix in CI job {name}")
            indices = [int(v.strip()) for v in matrix.group(1).split(",")]
            if indices != list(range(1, len(indices) + 1)):
                raise SuiteError(f"invalid shard matrix in CI job {name}")
            found[name]["shards"] = indices
    return found


def job_table(ci, shards, only=None):
    if shards < 1:
        raise SuiteError("--shards must be positive")
    jobs = {f"ord-{i}": {**ci["test"], "index": i, "shards": shards}
            for i in range(1, shards + 1)}
    jobs["excl-exits"] = {**ci["calibration-exits-exclusive"], "index": 1, "shards": 1}
    crash = ci["calibration-writer-crash-matrix-exclusive"]
    jobs.update({f"excl-crash-{i}": {"body": crash["body"], "index": i,
                                   "shards": len(crash["shards"])}
                 for i in crash["shards"]})
    if only:
        selected = only.split(",") if isinstance(only, str) else list(only)
        unknown = set(selected) - jobs.keys()
        if unknown:
            raise SuiteError(f"unknown jobs: {','.join(sorted(unknown))}")
        jobs = {name: jobs[name] for name in selected}
    return jobs


def build_prompt(run, job, shards, sha, branch_prefix):
    return (
        "Do not edit, fix, investigate or open a pull request. Run exactly: "
        f"`python3.13 scripts/cloud_suite.py remote-shard --run {run} --job {job} "
        f"--shards {shards} --sha {sha} --branch-prefix {branch_prefix} --detach`. "
        f"Then run `python3.13 scripts/cloud_suite.py remote-wait --run {run} "
        f"--job {job} --max-wait 540` repeatedly until it prints `DONE`. Then stop."
    )


def parse_created(text):
    # Require a complete created line: an early partial typescript read is common.
    for line in text.splitlines():
        if "Created cloud session:" in line:
            sid = re.search(r"\bsession_[A-Za-z0-9]+\b", line)
            url = re.search(r"https://claude\.ai/code/(session_[A-Za-z0-9]+)\b", line)
            if sid and url and sid.group() == url.group(1):
                return sid.group(), url.group()
    return None


def _setting(name, default):
    return float(os.environ.get(f"CLOUD_SUITE_TEST_{name}", default))


def _stop_group(process):
    """Signal the whole session, including children whose leader already exited."""
    grace = _setting("KILL_GRACE", 3)
    deadline = time.monotonic() + grace
    signalled = False
    try:
        os.killpg(process.pid, signal.SIGTERM)
        signalled = True
    except ProcessLookupError:
        pass
    except PermissionError:
        if process.returncode is None:
            raise
    try:
        process.wait(timeout=max(0, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        pass
    if signalled:
        time.sleep(max(0, deadline - time.monotonic()))
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        # macOS's sandbox may return EPERM for a group already reaped above.
        # Never suppress a refusal to signal a still-running leader.
        if process.returncode is None:
            raise
    process.wait()


@dataclass
class LaunchResult:
    status: str
    session_id: str | None = None
    url: str | None = None
    error: str | None = None
    attempts: int = 1


def launch(job, *, repo, out_dir, run, shards, sha, branch_prefix="claude/suite",
           cli="claude", pty_wrapper="/usr/bin/script", accept_trust=False):
    path = Path(out_dir) / "launch" / f"{job}.typescript"
    path.parent.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(run, job, shards, sha, branch_prefix)
    error_path = path.with_suffix(".stderr")
    for attempt in (1, 2):
        # Retain each attempt's transcript; the standard filename is the latest.
        if attempt == 2 and path.exists():
            path.replace(path.with_suffix(".attempt1.typescript"))
        path.write_text("")  # Do not mistake an earlier launch's transcript for this one.
        try:
            with error_path.open("wb") as errors:
                process = subprocess.Popen([pty_wrapper, "-q", str(path), cli, "--cloud", prompt],
                                           cwd=repo, stdin=subprocess.PIPE,
                                           stdout=errors, stderr=errors,
                                           start_new_session=True)
        except OSError as exc:
            return LaunchResult("LAUNCH_FAILED", error=str(exc), attempts=attempt)
        started = time.monotonic()
        accepted = False
        try:
            while time.monotonic() - started < _setting("CREATED_TIMEOUT", 120):
                transcript = path.read_text(errors="replace") if path.exists() else ""
                # BSD script can buffer its typescript until the child exits.
                # Its stdout mirror is unbuffered; retain/watch that stream too.
                transcript += "\n" + error_path.read_text(errors="replace")
                if re.search(r"trust (?:this|the) (?:folder|directory)|Do you trust|trust prompt",
                             transcript, re.IGNORECASE) and not accepted:
                    if not accept_trust:
                        return LaunchResult("LAUNCH_FAILED", error=
                                            "trust prompt; rerun with --accept-trust", attempts=attempt)
                    try:
                        process.stdin.write(b"\x1b[B\r")
                        process.stdin.flush()
                    except (BrokenPipeError, OSError) as exc:
                        return LaunchResult("LAUNCH_FAILED", error=str(exc), attempts=attempt)
                    accepted = True
                created = parse_created(transcript)
                if created:
                    time.sleep(_setting("POST_CREATE_WAIT", 10))
                    return LaunchResult("LAUNCHED", *created, attempts=attempt)
                if process.poll() is not None:
                    break
                time.sleep(_setting("WATCH_POLL", 0.1))
        finally:
            _stop_group(process)
            process.stdin.close()
    error = error_path.read_text(errors="replace").strip()
    return LaunchResult("LAUNCH_FAILED", error="no created line within timeout" +
                        (f": {error}" if error else f" (launcher rc={process.returncode})"), attempts=2)


def _git(repo, *args, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and result.returncode:
        raise SuiteError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result


def _save_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def _save_state(state):
    _save_json(Path(state["out_dir"]) / "run.json", state)


def _validate_identifiers(run, job=None):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run):
        raise SuiteError("invalid run identifier")
    if job is not None and not re.fullmatch(r"ord-[1-9][0-9]*|excl-exits|excl-crash-[1-9][0-9]*", job):
        raise SuiteError("invalid job identifier")


def _tmp_dir(run, job):
    return Path(os.environ.get("CLOUD_SUITE_TEST_TMP_ROOT", "/tmp")) / f"jwsuite-{run}-{job}"


def _run_logged(argv, *, repo, env, log, body, deadline):
    process = subprocess.Popen(argv, cwd=repo, env=env, stdin=subprocess.PIPE,
                               stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    timed_out = False
    try:
        process.communicate(body.encode() if body is not None else None,
                            timeout=max(0, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        timed_out = True
    finally:
        # Also reap descendants that survived normal completion.
        _stop_group(process)
    return process.returncode, timed_out


def _log_counts(path):
    counts = {}
    modules = []
    with path.open(errors="replace") as log:
        for line in log:
            if match := SUMMARY.fullmatch(line):
                counts = {k: int(v) if k != "result" else v
                          for k, v in match.groupdict().items()}
            if match := re.match(r"MODULE FAIL (\S+)", line):
                modules.append(match.group(1))
            if match := re.match(r"Ran (\d+) tests? in ", line):
                counts = {"tests": int(match.group(1)), "modules": 1,
                          "failures": 0, "errors": 0, "skipped": 0}
            if re.match(r"^(OK|FAILED)(?:\s|$)", line):
                counts["result"] = "PASS" if line.startswith("OK") else "FAIL"
                for key in ("failures", "errors", "skipped"):
                    if match := re.search(rf"\b{key}=(\d+)", line):
                        counts[key] = int(match.group(1))
    return counts, list(dict.fromkeys(modules))


def _trim_log(path):
    limit = int(_setting("LOG_LIMIT", 40 * 1024 * 1024))
    if path.stat().st_size <= limit:
        return
    portion = max(1, min(1024 * 1024, limit // 4))
    trimmed = path.with_suffix(".trimmed")
    with path.open("rb") as source, trimmed.open("wb") as target:
        target.write(source.read(portion))
        target.write(b"\n[cloud-suite log truncated; head, FAIL/ERROR blocks, tail retained]\n")
        source.seek(0)
        in_failure = False
        for line in source:
            if re.match(rb"(?:MODULE START |SHARD SUMMARY |Ran \d+ tests?)", line):
                in_failure = False
            if re.match(rb"(?:FAIL:|ERROR:|MODULE FAIL |MODULE LOAD ERROR )", line):
                in_failure = True
            if in_failure:
                target.write(line)
        target.write(b"\n[cloud-suite tail]\n")
        source.seek(max(0, path.stat().st_size - portion))
        target.write(source.read())
    trimmed.replace(path)


def _remote_worker(args, repo, actual_sha, zsh):
    tmp = _tmp_dir(args.run, args.job)
    tmp.mkdir(parents=True, exist_ok=True)
    directory = repo / "suite" / args.run
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / f"{args.job}.log"
    json_path = directory / f"{args.job}.json"
    result = {"run": args.run, "job": args.job, "sha": args.sha,
              "python": sys.version, "user_site": site.ENABLE_USER_SITE, "zsh": zsh,
              "rc": 1, "timed_out": False, "started": _utc(), "failed_modules": []}
    pushed = False
    try:
        with log_path.open("w") as log:
            if actual_sha != args.sha:
                result["status"] = "SHA_MISMATCH"
                log.write(f"SHA_MISMATCH expected={args.sha} actual={actual_sha}\n")
            else:
                job = args.job_spec
                env = dict(os.environ, TMPDIR=str(tmp), PYTHONDONTWRITEBYTECODE="1",
                           SHARD_COUNT=str(job["shards"]), SHARD_INDEX=str(job["index"]))
                deadline = time.monotonic() + args.job_timeout_min * 60
                rc, timed_out = _run_logged([sys.executable, "-m", "compileall", "-q", "joulewise", "tests"],
                                            repo=repo, env=env, log=log, body=None, deadline=deadline)
                if rc == 0 and not timed_out:
                    if "body" in job:
                        command = [sys.executable, "-B", "-"]
                    else:
                        command = shlex.split(job["command"])
                        if not command or command[0] not in ("python", "python3", "python3.13"):
                            raise SuiteError("exclusive CI command must start with python")
                        command[0] = sys.executable
                    rc, timed_out = _run_logged(command, repo=repo, env=env, log=log,
                                                body=job.get("body"), deadline=deadline)
                result.update(rc=rc, timed_out=timed_out)
        counts, failed = _log_counts(log_path)
        result.update(counts)
        result["failed_modules"] = failed
        result["finished"] = _utc()
        _trim_log(log_path)
        _save_json(json_path, result)
        branch = f"{args.branch_prefix}-{args.run}-{args.job}"
        _git(repo, "checkout", "-b", branch)
        paths = [str(p.relative_to(repo)) for p in (log_path, json_path)]
        _git(repo, "add", "-f", "--", *paths)
        _git(repo, "-c", "user.name=cloud-suite", "-c", "user.email=cloud-suite@invalid",
             "commit", "-m", f"suite {args.run} {args.job}", "--", *paths)
        delays = [float(v) for v in os.environ.get("CLOUD_SUITE_TEST_PUSH_BACKOFF", "10,30,90").split(",")]
        for attempt in range(3):
            if _git(repo, "push", "-u", "origin", branch, check=False).returncode == 0:
                pushed = True
                break
            if attempt < 2:
                time.sleep(delays[min(attempt, len(delays) - 1)])
    except Exception as exc:
        with log_path.open("a") as log:
            log.write(f"ERROR: remote worker: {exc}\n")
    finally:
        (tmp / "done").write_text("pushed" if pushed else "push_failed")
    return 0 if pushed else 1


def remote_shard(args):
    _validate_identifiers(args.run, args.job)
    repo = Path(args.repo).resolve()
    _git(repo, "check-ref-format", "--branch", f"{args.branch_prefix}-{args.run}-{args.job}")
    actual = _git(repo, "rev-parse", "HEAD").stdout.strip()
    if actual == args.sha:
        # CI drift is a refusal before detaching, rather than an opaque missing job.
        args.job_spec = job_table(parse_ci_jobs(_git(
            repo, "show", f"{args.sha}:.github/workflows/ci.yml").stdout), args.shards, args.job)[args.job]
    zsh = "present" if os.access(args.zsh_path, os.X_OK) else "missing"
    if actual == args.sha and zsh == "missing" and not args.no_install:
        try:
            install = subprocess.run(["sudo", "-n", "apt-get", "install", "-y", "-q", "zsh"],
                                     capture_output=True, timeout=120, check=False)
            if install.returncode == 0 and os.access(args.zsh_path, os.X_OK):
                zsh = "installed"
        except (OSError, subprocess.TimeoutExpired):
            pass  # Missing sudo/apt or a failed install is an environment note.
    tmp = _tmp_dir(args.run, args.job)
    tmp.mkdir(parents=True, exist_ok=True)
    if (tmp / "done").exists():
        raise SuiteError(f"job already has a done marker: {tmp}")
    if args.detach:
        pid = os.fork()
        if pid:
            return 0
        os.setsid()
        with open(os.devnull, "r+b", buffering=0) as devnull:
            for fd in (0, 1, 2):
                os.dup2(devnull.fileno(), fd)
        os._exit(_remote_worker(args, repo, actual, zsh))
    return _remote_worker(args, repo, actual, zsh)


def remote_wait(args):
    _validate_identifiers(args.run, args.job)
    done = _tmp_dir(args.run, args.job) / "done"
    deadline = time.monotonic() + args.max_wait
    while True:
        if done.exists():
            print(f"DONE {done.read_text().strip()}")
            return 0
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print("WAITING")
            return 0
        time.sleep(min(args.poll, remaining))


def classify(job_json, parent_sha):
    if job_json.get("status") == "SHA_MISMATCH" or parent_sha != job_json.get("sha"):
        return "SHA_MISMATCH"
    if job_json.get("timed_out"):
        return "TIMEOUT"
    if (job_json.get("rc") == 0 and job_json.get("result") == "PASS"
            and job_json.get("failures") == 0 and job_json.get("errors") == 0
            and not job_json.get("failed_modules")):
        return "PASS"
    return "FAIL"


def _branches(state):
    prefix = f"{state['branch_prefix']}-{state['run']}-"
    expected = {prefix + job for job in state["jobs"]}
    output = _git(state["repo"], "ls-remote", "origin", f"refs/heads/{prefix}*").stdout
    return [line.split()[1].removeprefix("refs/heads/") for line in output.splitlines()
            if len(line.split()) == 2 and line.split()[1].removeprefix("refs/heads/") in expected]


def collect(state):
    """Fetch exact run/job refs into FETCH_HEAD; persist each collected result."""
    out = Path(state["out_dir"])
    deadline = state["last_launch"] + state["deadline_min"] * 60
    while True:
        branches = _branches(state)
        state["branches"] = sorted(set(state.get("branches", [])) | set(branches))
        for name, job in state["jobs"].items():
            branch = f"{state['branch_prefix']}-{state['run']}-{name}"
            if job.get("collected") or job.get("status") == "LAUNCH_FAILED" or branch not in branches:
                continue
            # An empty refmap prevents Git's opportunistic remote-tracking updates.
            _git(state["repo"], "fetch", "--no-tags", "--refmap=", "origin", f"refs/heads/{branch}")
            parent = _git(state["repo"], "rev-parse", "FETCH_HEAD^", check=False)
            raw = _git(state["repo"], "show", f"FETCH_HEAD:suite/{state['run']}/{name}.json", check=False)
            log = _git(state["repo"], "show", f"FETCH_HEAD:suite/{state['run']}/{name}.log", check=False)
            (out / f"{name}.json").write_text(raw.stdout)
            (out / f"{name}.log").write_text(log.stdout)
            try:
                result = json.loads(raw.stdout)
                if not isinstance(result, dict):
                    raise ValueError("result must be an object")
            except (ValueError, TypeError):
                result = {}
            identity = (result.get("run"), result.get("job"), result.get("sha"))
            valid = (identity == (state["run"], name, state["sha"])
                     and raw.returncode == log.returncode == parent.returncode == 0)
            job.update(data=result, collected=True, status=
                       classify(result, parent.stdout.strip()) if valid else "SHA_MISMATCH")
            _save_state(state)
        if all(job.get("collected") or job.get("status") == "LAUNCH_FAILED"
               for job in state["jobs"].values()):
            break
        remaining = deadline - time.time()
        if remaining <= 0:
            for job in state["jobs"].values():
                if not job.get("collected") and job.get("status") != "LAUNCH_FAILED":
                    job["status"] = "MISSING"
            break
        _save_state(state)
        time.sleep(min(state["poll"], remaining))
    _save_state(state)
    return state


def write_report(state, *, emit=True):
    rows = []
    for name, job in state["jobs"].items():
        data = job.get("data", {})
        notes = []
        if data.get("zsh") == "missing":
            notes.append("zsh=missing")
        if data.get("user_site") is False:
            notes.append("user_site=false")
        rows.append({**data, "job": name, "status": job.get("status", "MISSING"),
                     "session_url": job.get("url"), "environment_notes": notes,
                     "launch_error": job.get("error")})
    passed = sum(row["status"] == "PASS" for row in rows)
    failed = sum(row["status"] in ("FAIL", "SHA_MISMATCH") for row in rows)
    incomplete = len(rows) - passed - failed
    outcome = "FAIL" if failed else "INCOMPLETE" if incomplete else "PASS"
    report = {"run": state["run"], "sha": state["sha"], "jobs": rows,
              "pass": passed, "fail": failed, "incomplete": incomplete, "result": outcome}
    out = Path(state["out_dir"])
    _save_json(out / "report.json", report)
    markdown = [f"# Cloud suite {state['run']}", "", f"SHA: `{state['sha']}`", "",
                "| Job | Status | Tests / failures / errors / skipped | Failed modules | Environment | Session |",
                "| --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        counts = " / ".join(str(row.get(k, "—")) for k in ("tests", "failures", "errors", "skipped"))
        detail = ", ".join(row.get("failed_modules", [])) or row.get("launch_error") or ""
        cells = [row["job"], row["status"], counts, detail,
                 ", ".join(row["environment_notes"]), row.get("session_url") or ""]
        markdown.append("| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in cells) + " |")
    (out / "report.md").write_text("\n".join(markdown) + "\n")
    if emit:
        print(f"CLOUD SUITE {state['run']} sha={state['sha']} jobs={len(rows)} "
              f"pass={passed} fail={failed} incomplete={incomplete} result={outcome}")
    return 1 if failed else 3 if incomplete else 0


def cleanup(state):
    branches = _branches(state)
    if branches:
        _git(state["repo"], "push", "origin", "--delete", *sorted(branches))
    state["deleted_branches"] = branches
    _save_state(state)
    return 0


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _run(args):
    repo = Path(args.repo).resolve()
    current = _git(repo, "branch", "--show-current").stdout.strip()
    ref = args.ref or current
    if not ref or current != ref:
        raise SuiteError("requested branch must be checked out in --repo")
    sha = _git(repo, "rev-parse", ref).stdout.strip()
    remote = _git(repo, "ls-remote", "origin", f"refs/heads/{ref}").stdout.split()
    if not remote or remote[0] != sha:
        raise SuiteError("push first: origin branch must equal the checked-out tip")
    run = datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ") + "-" + sha[:8]
    _git(repo, "check-ref-format", "--branch", f"{args.branch_prefix}-{run}-ord-1")
    out = Path(args.out_dir or f"/Users/edr/night-archive/cloud-suite/{run}").resolve()
    if out == repo or repo in out.parents:
        raise SuiteError("--out-dir must be outside --repo")
    jobs = job_table(parse_ci_jobs(_git(repo, "show", f"{sha}:.github/workflows/ci.yml").stdout),
                     args.shards, args.only)
    out.mkdir(parents=True, exist_ok=True)
    if (out / "run.json").exists():
        raise SuiteError("run.json already exists; use collect --state to resume")
    state = {"repo": str(repo), "ref": ref, "sha": sha, "run": run, "out_dir": str(out),
             "branch_prefix": args.branch_prefix, "shards": args.shards,
             "poll": args.poll, "deadline_min": args.deadline_min,
             "keep_branches": args.keep_branches, "jobs": {name: {} for name in jobs},
             "last_launch": time.time(), "branches": []}
    _save_state(state)
    with ThreadPoolExecutor(max_workers=args.launch_concurrency) as pool:
        futures = {pool.submit(launch, name, repo=str(repo), out_dir=str(out), run=run,
                               shards=args.shards, sha=sha, branch_prefix=args.branch_prefix,
                               cli=args.cli, pty_wrapper=args.pty_wrapper,
                               accept_trust=args.accept_trust): name for name in jobs}
        for future in as_completed(futures):
            state["jobs"][futures[future]] = asdict(future.result())
            state["last_launch"] = time.time()
            _save_state(state)
    collect(state)
    write_report(state, emit=False)
    if not state["keep_branches"]:
        cleanup(state)
    return write_report(state)


def _positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def _nonnegative(value):
    number = float(value)
    if not number >= 0 or number == float("inf"):
        raise argparse.ArgumentTypeError("must be finite and nonnegative")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--repo", required=True)
    run.add_argument("--ref")
    run.add_argument("--shards", type=_positive, default=12)
    run.add_argument("--only")
    run.add_argument("--out-dir")
    run.add_argument("--poll", type=_nonnegative, default=60)
    run.add_argument("--deadline-min", type=_nonnegative, default=75)
    run.add_argument("--launch-concurrency", type=_positive, default=5)
    run.add_argument("--keep-branches", action="store_true")
    run.add_argument("--accept-trust", action="store_true")
    run.add_argument("--branch-prefix", default="claude/suite")
    run.add_argument("--cli", default="claude")
    run.add_argument("--pty-wrapper", default="/usr/bin/script")
    for command in ("collect", "cleanup"):
        local = sub.add_parser(command)
        local.add_argument("--state", required=True, help="path to run.json")
        if command == "collect":
            local.add_argument("--poll", type=_nonnegative)
            local.add_argument("--deadline-min", type=_nonnegative)
            local.add_argument("--keep-branches", action="store_true", default=None)
    remote = sub.add_parser("remote-shard")
    remote.add_argument("--run", required=True)
    remote.add_argument("--job", required=True)
    remote.add_argument("--shards", type=_positive, required=True)
    remote.add_argument("--sha", required=True)
    remote.add_argument("--branch-prefix", default="claude/suite")
    remote.add_argument("--repo", default=".")
    remote.add_argument("--detach", action="store_true")
    remote.add_argument("--zsh-path", default="/bin/zsh")
    remote.add_argument("--no-install", action="store_true")
    remote.add_argument("--job-timeout-min", type=_nonnegative, default=45)
    wait = sub.add_parser("remote-wait")
    wait.add_argument("--run", required=True)
    wait.add_argument("--job", required=True)
    wait.add_argument("--max-wait", type=_nonnegative, default=540)
    wait.add_argument("--poll", type=_nonnegative, default=1)
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            return _run(args)
        if args.command == "remote-shard":
            return remote_shard(args)
        if args.command == "remote-wait":
            return remote_wait(args)
        state = json.loads(Path(args.state).read_text())
        if args.command == "cleanup":
            return cleanup(state)
        for key in ("poll", "deadline_min", "keep_branches"):
            if getattr(args, key) is not None:
                state[key] = getattr(args, key)
        collect(state)
        write_report(state, emit=False)
        if not state["keep_branches"]:
            cleanup(state)
        return write_report(state)
    except (SuiteError, OSError, ValueError) as exc:
        print(f"cloud-suite: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
