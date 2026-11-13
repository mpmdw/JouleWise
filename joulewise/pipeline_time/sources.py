"""Snapshot gathering for the pipeline watcher, and over-budget profiles.

Sources, all through an injectable `runner(argv, timeout) -> (rc, stdout, stderr)`:
- origin/main RUN_STATE.md: `git fetch` into the private ref `refs/pipeline-watch/main`
  (no working-tree change), then `git show`.
- directive-notice issues and in-progress CI runs: `gh`.
- the armed plan's results branch: `git ls-remote` (names only, never contents).
- the local process table: `ps`.
No source opens SSH. RL-128's MBP status probe is a disabled hook below.

Profiles (RL-127 term 8) never signal a process: three `ps` samples of the
process tree 10 s apart, the job's working directory from `lsof`, files
written in the last 5 min under it (names and counts by directory, bounded
walk), and optionally a short `sample` call stack on macOS.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import time

from joulewise.pipeline_time import ledger
from joulewise.pipeline_time.alarms import default_runner
from joulewise.pipeline_time.detect import Proc, Snapshot

LEDGER_DIR = Path("/Volumes/JW-EXT/ledger")
PRIVATE_REF = "refs/pipeline-watch/main"
ETIME_RE = re.compile(r"^(?:(\d+)-)?(?:(\d+):)?(\d+):(\d+(?:\.\d+)?)$")

# --- RL-128 status probe: DISABLED until its calibration gate passes ---------------------
#
# RL-128 (research lead, 2026-11-13) allows one bounded read-only status probe
# during an armed span, on these terms. Enabling it needs a reviewed PR that
# flips RL128_PROBE_ENABLED and names the calibration record; config cannot.
#  1. One fixed command by a dedicated key: the MBP's authorized_keys line carries
#     command=".../night_status.sh", no-pty, no forwarding. The ordinary key stays unused
#     during armed spans.
#  2. The command prints only: the time; the boot session id; whether the driver pid is
#     alive; the last three lines of chain-stages.jsonl (stage names and stamps); whether
#     chain.started, chain.exited and courier.sent exist; free disk in GB. No energy,
#     power, meter, temperature, transcript or result file is read; it writes nothing.
#  3. At most one every 30 min on a schedule, plus one when a stage deadline fires;
#     at most 60 in a night.
#  4. Run by this launchd job, not an agent. Alarm when the newest stage stamp is older
#     than that stage's cap + 10%, or the driver pid is gone without chain.exited. The
#     SSH-free `git ls-remote` results-branch check runs beside it (already live here).
#  5. One host-event line per probe on the Air (start, end, exit code, bytes returned),
#     committed to the night-results branch after the night closes.
#  6. No special treatment in analysis; the desk counts member requests within 5 s of a probe.
#  7. W1 registration carries the sentence that bounded read-only probes run and are logged.
#  8. Not on the slot night armed under the old rule.
# Gate: 20 probes 30 s apart on the unarmed MBP with the hazard monitor running; pass when
# no probe process exceeds 0.025 CPU-s/s in any interval and the DC-in mean over the probe
# intervals is within the idle trace's interval-to-interval spread. On a fail: hourly, back
# to the research lead.
RL128_PROBE_ENABLED = False
RL128_CALIBRATION_RECORD = None  # repo path of the passing calibration record, once it exists
RL128_MIN_INTERVAL_S = 30 * 60
RL128_MAX_PER_NIGHT = 60


def rl128_probe(state: dict, now: float, deadline_fired: bool = False, runner=default_runner) -> dict:
    """The disabled RL-128 hook. Returns why it did not run; it never opens SSH while disabled."""
    if not RL128_PROBE_ENABLED or not RL128_CALIBRATION_RECORD:
        return {"ran": False, "reason": "RL-128 calibration not passed; probe disabled"}
    probes = state.setdefault("rl128", {"times": []})
    recent = [t for t in probes["times"] if now - t < 36 * 3600]
    if len(recent) >= RL128_MAX_PER_NIGHT:
        return {"ran": False, "reason": "RL-128 per-night cap reached"}
    if not deadline_fired and recent and now - max(recent) < RL128_MIN_INTERVAL_S:
        return {"ran": False, "reason": "RL-128 30-min spacing"}
    raise NotImplementedError("RL-128 probe body lands with its calibration record and key")


# --- process table -----------------------------------------------------------------------

def parse_etime(text: str) -> float | None:
    match = ETIME_RE.match(text.strip())
    if not match:
        return None
    days, hrs, mins, secs = match.groups()
    return int(days or 0) * 86400 + int(hrs or 0) * 3600 + int(mins) * 60 + float(secs)


def parse_ps(text: str) -> list[Proc]:
    procs = []
    for line in text.splitlines():
        parts = line.split(None, 4)
        if len(parts) < 5 or not parts[0].isdigit():
            continue
        elapsed = parse_etime(parts[2])
        cpu = parse_etime(parts[3])
        if elapsed is None:
            continue
        procs.append(Proc(int(parts[0]), int(parts[1]), elapsed, cpu or 0.0, parts[4]))
    return procs


PS_ARGV = ["/bin/ps", "-Ao", "pid=,ppid=,etime=,time=,command=", "-ww"]


# --- the snapshot ------------------------------------------------------------------------

def read_queue(path: Path) -> list[dict]:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return []
    jobs = data.get("jobs") if isinstance(data, dict) else None
    return [job for job in jobs or [] if isinstance(job, dict)]


def gather(repo: Path, config: dict, state: dict, now: float | None = None, runner=default_runner,
           ledger_file: Path | None = None, queue_file: Path | None = None,
           run_state_text: str | None = None, offline: bool = False) -> Snapshot:
    """Collect one snapshot. Failures count per source in `state['sources']`; nothing raises."""
    now = time.time() if now is None else now
    failures = state.setdefault("sources", {})
    snap = Snapshot(now=now, host=ledger.host_name(), self_pid=os.getpid())

    def ok(name):
        failures[name] = 0

    def failed(name):
        failures[name] = int(failures.get(name, 0)) + 1

    from joulewise.pipeline_time import runstate
    text = run_state_text
    if text is None and not offline:
        rc, _, _ = runner(["git", "-C", str(repo), "-c", "maintenance.auto=false", "-c", "gc.auto=0",
                           "fetch", "--quiet", "--no-tags", "origin", f"+refs/heads/main:{PRIVATE_REF}"], timeout=90)
        if rc == 0:
            rc, out, _ = runner(["git", "-C", str(repo), "show", f"{PRIVATE_REF}:RUN_STATE.md"], timeout=60)
            text = out if rc == 0 else None
        (ok if text is not None else failed)("run_state")
    if text is not None:
        snap.run_state = runstate.read(text)

    repo_slug = config["repo"]
    if not offline:
        rc, out, _ = runner(["gh", "issue", "list", "--repo", repo_slug, "--label", "directive-notice",
                             "--state", "all", "--limit", "5", "--json", "number,title,createdAt,state"], timeout=60)
        try:
            snap.notices = json.loads(out) if rc == 0 else None
        except ValueError:
            snap.notices = None
        (ok if snap.notices is not None else failed)("gh_issues")
        rc, out, _ = runner(["gh", "run", "list", "--repo", repo_slug, "--status", "in_progress", "--limit", "50",
                             "--json", "databaseId,workflowName,event,headBranch,headSha,status,startedAt,createdAt,url"],
                            timeout=60)
        try:
            snap.ci_runs = json.loads(out) if rc == 0 else None
        except ValueError:
            snap.ci_runs = None
        (ok if snap.ci_runs is not None else failed)("gh_runs")
        for run in snap.ci_runs or []:
            sha = run.get("headSha")
            if sha and run.get("event") == "push" and sha not in snap.ci_state_only:
                snap.ci_state_only[sha] = state_only_commit(repo, sha, runner)

    session = snap.run_state.session() if snap.run_state else None
    seen = state.setdefault("results_first_seen", {})
    if session and session.closed_by is None and not offline:
        rc, out, _ = runner(["git", "-C", str(repo), "ls-remote", "origin",
                             f"refs/heads/night-results/{session.plan_id}"], timeout=60)
        present = bool(out.strip()) if rc == 0 else None
        snap.results_branch[session.plan_id] = present
        if present and session.plan_id not in seen:
            seen[session.plan_id] = now
    snap.results_first_seen = dict(seen)

    rc, out, _ = runner(PS_ARGV, timeout=30)
    snap.processes = parse_ps(out) if rc == 0 else None
    (ok if snap.processes is not None else failed)("ps")

    snap.ledger_rows = ledger.read_ledger(ledger_file)
    snap.mbp_queue = read_queue(queue_file or LEDGER_DIR / "mbp-queue.json")
    snap.source_failures = {k: v for k, v in failures.items() if v}
    return snap


STATE_ONLY_PATHS = re.compile(r"^(RUN_STATE\.md|TASK_QUEUE\.md|docs/.*|.*\.md)$")


def state_only_commit(repo: Path, sha: str, runner=default_runner) -> bool | None:
    """True when every path the commit changes is RUN_STATE, TASK_QUEUE, docs or Markdown."""
    rc, out, _ = runner(["git", "-C", str(repo), "diff-tree", "--no-commit-id", "--name-only", "-r", "-m",
                         "--first-parent", sha], timeout=30)
    if rc != 0:
        return None
    paths = [line for line in out.splitlines() if line.strip()]
    return bool(paths) and all(STATE_ONLY_PATHS.match(path) for path in paths)


# --- profiles ----------------------------------------------------------------------------

def descendants(pid: int, procs: list[Proc]) -> list[int]:
    children = {}
    for proc in procs:
        children.setdefault(proc.ppid, []).append(proc.pid)
    out, stack = [], [pid]
    while stack:
        current = stack.pop()
        if current in out:
            continue
        out.append(current)
        stack.extend(children.get(current, []))
    return out


def recent_files(root: Path, window_s: float, now: float, max_entries: int = 20000, max_depth: int = 6) -> list[str]:
    """Counts of files modified in the window, by directory; a bounded walk that skips .git."""
    counts, seen = {}, 0
    root = Path(root)
    base_depth = len(root.parts)
    for current, dirs, files in os.walk(root):
        depth = len(Path(current).parts) - base_depth
        dirs[:] = [d for d in dirs if d != ".git"] if depth < max_depth else []
        for name in files:
            seen += 1
            if seen > max_entries:
                break
            try:
                if now - os.stat(os.path.join(current, name)).st_mtime <= window_s:
                    counts[current] = counts.get(current, 0) + 1
            except OSError:
                continue
        if seen > max_entries:
            break
    rows = sorted(counts.items(), key=lambda kv: -kv[1])[:20]
    lines = [f"{count:6d}  {path}" for path, count in rows]
    if seen > max_entries:
        lines.append(f"(walk stopped after {max_entries} entries)")
    return lines or ["(no files modified in the window)"]


def capture_profile(pid: int, stage: str | None, out_dir: Path, procs: list[Proc], runner=default_runner,
                    sleep=time.sleep, now=time.time, samples: int = 3, interval_s: float = 10.0,
                    use_sample: bool = True, sample_s: int = 3, window_s: float = 300.0) -> str | None:
    """Write one profile file for an over-budget job and return its path. Signals nothing."""
    tree = descendants(pid, procs)
    stamp = time.strftime("%Y%m%dT%H%M%S", time.localtime(now()))
    lines = [f"profile of pid {pid} (stage {stage}) at {stamp}; tree {len(tree)} pids",
             "RL-127 term 8: three ps samples 10 s apart, cwd, files written in the last 5 min."]
    for index in range(samples):
        if index:
            sleep(interval_s)
        rc, out, _ = runner(["/bin/ps", "-o", "pid,ppid,stat,etime,time,%cpu,rss,command", "-ww",
                             "-p", ",".join(str(p) for p in tree)], timeout=30)
        cores = 0.0
        for row in out.splitlines()[1:]:
            parts = row.split()
            if len(parts) > 5:
                try:
                    cores += float(parts[5]) / 100.0
                except ValueError:
                    pass
        lines += [f"--- ps sample {index + 1} (rc {rc}; cores in use {cores:.2f})", out.rstrip()]
    rc, out, _ = runner(["/usr/sbin/lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"], timeout=30)
    cwd = next((line[1:] for line in out.splitlines() if line.startswith("n")), None) if rc == 0 else None
    lines.append(f"--- cwd: {cwd}")
    if cwd and Path(cwd).is_dir():
        lines.append(f"--- files modified in the last {int(window_s)} s, by directory")
        lines += recent_files(Path(cwd), window_s, now())
    if use_sample and sys.platform == "darwin":
        rc, out, _ = runner(["/usr/bin/sample", str(pid), str(int(sample_s)), "-mayDie"], timeout=sample_s + 30)
        lines.append(f"--- sample {sample_s} s (rc {rc})")
        lines += out.splitlines()[:300]
    try:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{stamp}-{re.sub(r'[^A-Za-z0-9_.-]', '_', stage or 'job')}-{pid}.txt"
        path.write_text("\n".join(lines) + "\n")
        return str(path)
    except OSError:
        return None
