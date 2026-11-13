"""Pure detectors over one watcher snapshot (RL-127 terms 6 and 8).

Each detector reads a `Snapshot` and returns `Alarm`s. Nothing here runs a
command, reads the network or touches a process; `sources` gathers the snapshot.

| Code | Severity | Fires when |
|---|---|---|
| ARM_MISSING | alarm | the governing pointer is magistrate-owned and waits on an arm or install, its `deadline` has passed, and no later item is ARMED/INSTALLED (or a directive-notice arm issue is older than 60 min with no ARMED item since) |
| SESSION_OVERDUE | alarm | the latest armed pointer's `latest_end` (+ grace, default 0) has passed and no later item is CLOSED/COMPLETE/REFUSED |
| CLOSE_ITEM_MISSING | alarm | the armed plan's `night-results/<plan>` branch exists (ls-remote), was first seen more than 30 min ago, and no close item exists |
| REFUSED_ITEM / FAULT_ITEM | alarm | a non-lead item from the last 72 h is REFUSED/REFUSAL or FAULT/FAILED/STRANDED/NEVER MEASURED and no later lead item exists |
| MBP_IDLE | alarm | the MBP is unarmed, no magistrate work is pending, the queue is empty, for more than 30 min |
| SESSION_GAP | warn | more than 1.5 x 2 h (1.5 x 4 h after a code change) since the last session closed with no new arm |
| LEDGER_OVER | alarm | an open ledger run or phase is past 1.5 x its budget (profiled) |
| LEDGER_OVERRAN | warn | a run or phase that ended in the last 24 h took more than 1.5 x its budget (sent once) |
| LEDGER_ORPHAN | warn | an open ledger row on this host is past 1.5 x budget and its pid is gone |
| LOCAL_JOB_OVER | alarm | a matched local process tree (not under the ledger, not exempt) is past 1.5 x its rule's budget (profiled) |
| CI_RUN_SLOW | warn | an in-progress `ci` workflow run is past 1.5 x 30 min (1.5 x 5 min for a push of a state-only commit) |
| WATCH_SOURCE_FAILED | alarm | a snapshot source (RUN_STATE fetch, gh, ps) failed on 3 consecutive polls |
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
import time

from joulewise.pipeline_time import budgets, ledger, runstate
from joulewise.pipeline_time.alarms import Alarm

DEFAULT_LOCAL_JOBS = [
    {"name": "block-analysis", "stage": "block-analysis", "budget_s": 3600,
     "pattern": r"independent_recompute_b\d|run_b5_analysis\.py|release_b5\.py|release_v4\.py|b6_custody|custody_kit"},
    {"name": "local-suite", "stage": "pr-ci", "budget_s": 1800,
     "pattern": r"shard_tests\.py|-m (?:unittest|pytest)\b"},
    {"name": "rehearsal", "stage": "rehearsal", "budget_s": 7200,
     "pattern": r"b6_r12_|fixture_gen|_fixture\.py|rehearsal"},
]

DEFAULT_CONFIG = {
    "repo": "mpmdw/JouleWise",
    "session_overdue_grace_s": 0,
    "close_item_grace_s": budgets.BUDGETS_S["notice"],
    "notice_arm_window_s": 3600,
    "notice_lookback_s": 48 * 3600,
    "refused_lookback_s": 72 * 3600,
    "magistrate_pending_s": 12 * 3600,
    "finished_lookback_s": 24 * 3600,
    "source_failure_limit": 3,
    "ci_workflows": ["ci"],
    "local_jobs": DEFAULT_LOCAL_JOBS,
    "exempt": [],
}


@dataclass
class Proc:
    pid: int
    ppid: int
    elapsed_s: float
    cpu_s: float
    command: str


@dataclass
class Snapshot:
    now: float
    host: str = ""
    run_state: runstate.RunState | None = None
    notices: list | None = None            # directive-notice issues: {number, title, createdAt}
    results_branch: dict = field(default_factory=dict)      # plan_id -> True/False/None
    results_first_seen: dict = field(default_factory=dict)  # plan_id -> epoch
    ledger_rows: list = field(default_factory=list)
    processes: list | None = None
    ci_runs: list | None = None
    ci_state_only: dict = field(default_factory=dict)       # head sha -> bool
    mbp_queue: list = field(default_factory=list)
    source_failures: dict = field(default_factory=dict)
    self_pid: int | None = None


def fmt(epoch: float | None) -> str:
    if epoch is None:
        return "?"
    return time.strftime("%m-%d %H:%M %Z", time.localtime(epoch))


def hours(seconds: float) -> str:
    return f"{seconds / 3600:.1f} h" if seconds >= 3600 else f"{seconds / 60:.0f} min"


def short_command(command: str, width: int = 100) -> str:
    """The command with its interpreter path cut to a basename, for status lines."""
    head, _, rest = command.partition(" ")
    return (head.rsplit("/", 1)[-1] + (" " + rest if rest else ""))[:width]


def iso_epoch(text: str | None) -> float | None:
    return runstate.parse_time(text) if text else None


# --- RUN_STATE and notices -------------------------------------------------

def arm_missing(snap: Snapshot, config: dict) -> list[Alarm]:
    rs = snap.run_state
    if rs is None:
        return []
    out = []
    pointer = rs.pointer_item()
    if runstate.arm_expected(pointer):
        later = rs.after(pointer)
        deadline = pointer.pointer_times.get("deadline")
        if (deadline and snap.now > deadline and not any("armed" in i.classes for i in later)
                and not any(i.classes & {"refused", "fault"} for i in later)):
            out.append(Alarm(f"arm_missing:{pointer.label}", "ARM_MISSING", "alarm",
                             f"item {pointer.label} expected an arm or install by {fmt(deadline)}; "
                             f"no ARMED/INSTALLED item since ({hours(snap.now - deadline)} late)",
                             detail=f"next_observable: {pointer.pointer.get('next_observable', '')[:300]}"))
    armed_stamps = [i.stamp for i in rs.ordered() if "armed" in i.classes and i.stamp]
    for notice in snap.notices or []:
        created = iso_epoch(notice.get("createdAt"))
        if created is None or snap.now - created > config["notice_lookback_s"]:
            continue
        if snap.now - created <= config["notice_arm_window_s"]:
            continue
        if any(stamp >= created - 2 * 3600 for stamp in armed_stamps):
            continue
        out.append(Alarm(f"arm_missing:notice-{notice.get('number')}", "ARM_MISSING", "alarm",
                         f"arm notice issue #{notice.get('number')} opened {fmt(created)}; "
                         f"no ARMED/INSTALLED item within {hours(config['notice_arm_window_s'])}"))
    return out


def session_checks(snap: Snapshot, config: dict) -> list[Alarm]:
    rs = snap.run_state
    session = rs.session() if rs else None
    if session is None or session.closed_by is not None:
        return []
    out = []
    branch = snap.results_branch.get(session.plan_id)
    branch_text = {True: "present", False: "absent", None: "unknown"}[branch]
    if session.latest_end and snap.now > session.latest_end + config["session_overdue_grace_s"]:
        out.append(Alarm(f"session_overdue:{session.plan_id}", "SESSION_OVERDUE", "alarm",
                         f"session {session.plan_id} (item {session.item.label}) is past its latest end "
                         f"{fmt(session.latest_end)} by {hours(snap.now - session.latest_end)} with no close item; "
                         f"results branch {branch_text}"))
    first = snap.results_first_seen.get(session.plan_id)
    if branch and first and snap.now - first > config["close_item_grace_s"]:
        out.append(Alarm(f"close_missing:{session.plan_id}", "CLOSE_ITEM_MISSING", "alarm",
                         f"night-results/{session.plan_id} appeared by {fmt(first)}; no close item after "
                         f"{hours(snap.now - first)} (stranded or refused session not yet noticed)"))
    return out


def refused_items(snap: Snapshot, config: dict) -> list[Alarm]:
    rs = snap.run_state
    if rs is None:
        return []
    out = []
    for item in rs.ordered():
        hits = item.classes & {"refused", "fault"}
        if not hits or item.author == "lead" or item.stamp is None:
            continue
        if snap.now - item.stamp > config["refused_lookback_s"]:
            continue
        if any(other.author == "lead" for other in rs.after(item)):
            continue
        code = "REFUSED_ITEM" if "refused" in hits else "FAULT_ITEM"
        out.append(Alarm(f"item:{item.label}", code, "alarm",
                         f"item {item.label} ({item.author}, {fmt(item.stamp)}) reports "
                         f"{'/'.join(sorted(hits))}; no lead item since",
                         detail=item.heading[:400]))
    return out


def mbp_state(snap: Snapshot, config: dict) -> tuple[str, float | None, str]:
    """(state, idle_since, reason). state is armed, magistrate, queued, idle or unknown."""
    rs = snap.run_state
    if rs is None:
        return "unknown", None, "RUN_STATE unavailable"
    session = rs.session()
    if session and session.closed_by is None:
        return "armed", None, f"session {session.plan_id} (item {session.item.label}) has no close item"
    candidates = []
    pointer = rs.pointer_item()
    if pointer is not None and pointer.pointer.get("owner", "").strip().lower() == "magistrate":
        deadline = pointer.pointer_times.get("deadline")
        if deadline and snap.now <= deadline:
            return "magistrate", None, f"magistrate work pending on item {pointer.label} until {fmt(deadline)}"
        if not deadline and pointer.stamp and snap.now - pointer.stamp <= config["magistrate_pending_s"]:
            return "magistrate", None, f"magistrate work pending on item {pointer.label} (no deadline)"
        if deadline:
            candidates.append(deadline)
    for job in snap.mbp_queue:
        end = job.get("expected_end_epoch_s")
        start = job.get("started_epoch_s") or 0
        if end is None and snap.now - float(start) <= 24 * 3600:
            return "queued", None, f"queued MBP job {job.get('name')!r} (no expected end)"
        if end is not None and snap.now <= float(end):
            return "queued", None, f"queued MBP job {job.get('name')!r} until {fmt(float(end))}"
        if end is not None:
            candidates.append(float(end))
    if pointer is not None and pointer.stamp:
        candidates.append(pointer.stamp)
    last_end = rs.last_session_end()
    if last_end is not None and last_end.stamp:
        candidates.append(last_end.stamp)
    if session and session.closed_by and session.closed_by.stamp:
        candidates.append(session.closed_by.stamp)
    since = max(candidates) if candidates else None
    owner = pointer.pointer.get("owner") if pointer else None
    return "idle", since, f"no open session, no pending magistrate work (pointer item {pointer.label if pointer else '?'} owner {owner}), queue empty"


def mbp_idle(snap: Snapshot, config: dict) -> list[Alarm]:
    state, since, reason = mbp_state(snap, config)
    if state != "idle" or since is None:
        return []
    limit = budgets.BUDGETS_S["mbp-idle"]
    if snap.now - since <= limit:
        return []
    return [Alarm(f"mbp_idle:{int(since)}", "MBP_IDLE", "alarm",
                  f"MBP unarmed with nothing queued for {hours(snap.now - since)} (since {fmt(since)}; budget 30 min)",
                  detail=reason)]


def session_gap(snap: Snapshot, config: dict) -> list[Alarm]:
    rs = snap.run_state
    if rs is None:
        return []
    end = rs.last_session_end()
    if end is None or end.stamp is None:
        return []
    later = rs.after(end)
    if any("armed" in item.classes for item in later):
        return []
    session = rs.session()
    if session and session.closed_by is None:
        return []
    stage = "session-gap-code" if runstate.code_changed(later) else "session-gap"
    budget = budgets.BUDGETS_S[stage]
    gap = snap.now - end.stamp
    if gap <= budgets.ALARM_FACTOR * budget:
        return []
    return [Alarm(f"session_gap:{end.label}", "SESSION_GAP", "warn",
                  f"{hours(gap)} since item {end.label} ended a session ({fmt(end.stamp)}) with no new arm; "
                  f"budget {hours(budget)} ({stage}), alarm at 1.5x", stage=stage)]


# --- ledger, local jobs, CI ------------------------------------------------

def ledger_checks(snap: Snapshot, config: dict) -> list[Alarm]:
    open_rows, ended = ledger.pair_entries(snap.ledger_rows)
    pids = None if snap.processes is None else {proc.pid for proc in snap.processes}
    out = []
    for row in open_rows:
        budget = row.get("budget_s")
        start = row.get("start_epoch_s")
        if not budget or start is None:
            continue
        running = snap.now - float(start)
        if running <= budgets.ALARM_FACTOR * float(budget):
            continue
        label = f"{row.get('stage')}{'/' + row['phase'] if row.get('phase') else ''}"
        local = row.get("host") == snap.host
        child = row.get("child_pid")
        if local and pids is not None and child and int(child) not in pids:
            out.append(Alarm(f"ledger_orphan:{row['run_id']}", "LEDGER_ORPHAN", "warn",
                             f"ledger {label} run {row['run_id']} has no end row and pid {child} is gone "
                             f"(started {fmt(float(start))})", repeat=False, stage=row.get("stage")))
            continue
        out.append(Alarm(f"ledger:{row['run_id']}", "LEDGER_OVER", "alarm",
                         f"{label} on {row.get('host')} running {hours(running)}, budget {hours(float(budget))} "
                         f"(alarm at 1.5x); run {row['run_id']}",
                         detail=f"cmd: {row.get('cmd', '')[:300]}\ncwd: {row.get('cwd', '')}",
                         profile_pid=int(child) if local and child else None, stage=row.get("stage")))
    for row in ended:
        budget = row.get("budget_s")
        end = row.get("end_epoch_s")
        wall = row.get("wall_s")
        if not budget or end is None or wall is None:
            continue
        if snap.now - float(end) > config["finished_lookback_s"]:
            continue
        if float(wall) <= budgets.ALARM_FACTOR * float(budget):
            continue
        label = f"{row.get('stage')}{'/' + row['phase'] if row.get('phase') else ''}"
        out.append(Alarm(f"ledger_done:{row['run_id']}", "LEDGER_OVERRAN", "warn",
                         f"{label} took {hours(float(wall))}, budget {hours(float(budget))} "
                         f"({float(wall) / float(budget):.1f}x); exit {row.get('exit')}; profile it before a retry",
                         repeat=False, stage=row.get("stage")))
    return out


def _ancestors(proc: Proc, by_pid: dict) -> list[Proc]:
    chain, seen = [], {proc.pid}
    current = by_pid.get(proc.ppid)
    while current is not None and current.pid not in seen and current.pid > 1:
        chain.append(current)
        seen.add(current.pid)
        current = by_pid.get(current.ppid)
    return chain


def local_job_candidates(snap: Snapshot, config: dict) -> list[tuple]:
    """(proc, rule, status) for each top-level process tree a rule matches.

    status is "exempt" (it or an ancestor matches an exemption), "wrapped" (under
    an open ledger run on this host, so the ledger detector owns it) or "job".
    A process whose ancestor also matches a rule is folded into that ancestor.
    """
    if not snap.processes:
        return []
    rules = [(rule, re.compile(rule["pattern"])) for rule in config.get("local_jobs") or []]
    exempt = [re.compile(rule["pattern"]) for rule in config.get("exempt") or []]
    by_pid = {proc.pid: proc for proc in snap.processes}
    open_rows, _ = ledger.pair_entries(snap.ledger_rows)
    wrapped = set()
    for row in open_rows:
        if row.get("host") == snap.host:
            for key in ("pid", "child_pid"):
                if row.get(key):
                    wrapped.add(int(row[key]))
    watcher = {snap.self_pid} if snap.self_pid else set()

    def rule_for(proc):
        for rule, pattern in rules:
            if pattern.search(proc.command):
                return rule
        return None

    out = []
    for proc in snap.processes:
        if proc.pid in watcher:
            continue
        rule = rule_for(proc)
        if rule is None:
            continue
        chain = _ancestors(proc, by_pid)
        if any(p.pid in watcher for p in chain):
            continue
        if any(rule_for(p) is not None for p in chain):
            continue  # the matching ancestor is the job
        if proc.pid in wrapped or any(p.pid in wrapped for p in chain):
            status = "wrapped"
        elif any(pattern.search(p.command) for p in [proc] + chain for pattern in exempt):
            status = "exempt"
        else:
            status = "job"
        out.append((proc, rule, status))
    return out


def local_jobs(snap: Snapshot, config: dict) -> list[Alarm]:
    out = []
    for proc, rule, status in local_job_candidates(snap, config):
        if status != "job":
            continue
        budget = float(rule["budget_s"])
        if proc.elapsed_s <= budgets.ALARM_FACTOR * budget:
            continue
        digest = hashlib.sha1(proc.command.encode()).hexdigest()[:8]
        out.append(Alarm(f"job:{proc.pid}:{digest}", "LOCAL_JOB_OVER", "alarm",
                         f"{rule['name']} pid {proc.pid} running {hours(proc.elapsed_s)}, budget "
                         f"{hours(budget)} (alarm at 1.5x), cpu {hours(proc.cpu_s)}",
                         detail=f"cmd: {proc.command[:300]}", profile_pid=proc.pid, stage=rule["stage"]))
    return out


def ci_runs(snap: Snapshot, config: dict) -> list[Alarm]:
    out = []
    for run in snap.ci_runs or []:
        if run.get("status") not in (None, "in_progress", "queued", "waiting", "pending"):
            continue
        if run.get("workflowName") not in config["ci_workflows"]:
            continue
        start = iso_epoch(run.get("startedAt") or run.get("createdAt"))
        if start is None:
            continue
        # A PR run tests the whole PR tree, so only a push run is judged by its one commit.
        state_only = run.get("event") == "push" and snap.ci_state_only.get(run.get("headSha"))
        stage = "state-only-ci" if state_only else "pr-ci"
        budget = budgets.BUDGETS_S[stage]
        running = snap.now - start
        if running <= budgets.ALARM_FACTOR * budget:
            continue
        out.append(Alarm(f"ci:{run.get('databaseId')}", "CI_RUN_SLOW", "warn",
                         f"{run.get('workflowName')} run {run.get('databaseId')} on {run.get('headBranch')} "
                         f"running {hours(running)}, budget {hours(budget)} ({stage})",
                         detail=str(run.get("url") or ""), stage=stage))
    return out


def source_failures(snap: Snapshot, config: dict) -> list[Alarm]:
    out = []
    for name, count in sorted(snap.source_failures.items()):
        if count >= config["source_failure_limit"]:
            out.append(Alarm(f"source:{name}", "WATCH_SOURCE_FAILED", "alarm",
                             f"watcher source {name} failed {count} polls in a row; detections that need it are blind"))
    return out


DETECTORS = (arm_missing, session_checks, refused_items, mbp_idle, session_gap,
             ledger_checks, local_jobs, ci_runs, source_failures)


def run_all(snap: Snapshot, config: dict | None = None) -> list[Alarm]:
    merged = dict(DEFAULT_CONFIG, **(config or {}))
    alarms = []
    for detector in DETECTORS:
        alarms.extend(detector(snap, merged))
    return alarms


def status_lines(snap: Snapshot, config: dict | None = None) -> list[str]:
    """Human-readable state for a dry run or a heartbeat."""
    merged = dict(DEFAULT_CONFIG, **(config or {}))
    rs = snap.run_state
    lines = [f"now {fmt(snap.now)} host {snap.host}"]
    if rs is None:
        lines.append("RUN_STATE: unavailable")
        return lines
    latest = rs.latest()
    mag = rs.latest_by("magistrate")
    pointer = rs.pointer_item()
    lines.append(f"latest item {latest.label if latest else '?'} ({latest.author if latest else '?'}, {fmt(latest.stamp if latest else None)})")
    if mag:
        lines.append(f"latest magistrate item {mag.label} ({fmt(mag.stamp)}) classes {sorted(mag.classes) or '-'}"
                     f"{'; carries a pointer' if mag.pointer else ''}")
    if pointer:
        p = pointer.pointer
        lines.append(f"governing pointer: item {pointer.label} owner {p.get('owner')} armed {p.get('armed', '-')} "
                     f"deadline {fmt(pointer.pointer_times.get('deadline'))}; wait: {p.get('wait', '')[:80]}")
        if runstate.arm_expected(pointer):
            armed_since = any("armed" in i.classes for i in rs.after(pointer))
            lines.append(f"arm expected by {fmt(pointer.pointer_times.get('deadline'))}: "
                         f"{'ARMED item seen' if armed_since else 'no ARMED item yet'}")
    session = rs.session()
    if session:
        closed = f"closed by item {session.closed_by.label}" if session.closed_by else "OPEN (no close item)"
        lines.append(f"last armed session {session.plan_id} (item {session.item.label}) t0 {fmt(session.t0)} "
                     f"latest end {fmt(session.latest_end)}: {closed}; results branch "
                     f"{({True: 'present', False: 'absent', None: 'unknown'}).get(snap.results_branch.get(session.plan_id, 'n/a'), 'not checked')}")
    state, since, reason = mbp_state(snap, merged)
    lines.append(f"MBP: {state}{' since ' + fmt(since) if since else ''} ({reason})")
    notices = snap.notices or []
    if notices:
        newest = notices[0]
        lines.append(f"newest directive-notice issue #{newest.get('number')} {newest.get('state')} {newest.get('createdAt')}")
    open_rows, ended = ledger.pair_entries(snap.ledger_rows)
    lines.append(f"ledger: {len(open_rows)} open, {len(ended)} finished rows")
    for proc, rule, status in local_job_candidates(snap, merged):
        lines.append(f"local job {rule['name']} pid {proc.pid} {status}: running {hours(proc.elapsed_s)} "
                     f"of {hours(float(rule['budget_s']))} budget; {short_command(proc.command)}")
    lines.append(f"processes: {'unavailable' if snap.processes is None else len(snap.processes)}; "
                 f"CI in progress: {'unavailable' if snap.ci_runs is None else len(snap.ci_runs)}")
    return lines
