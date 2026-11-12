"""Alarm when the newest completed CI run on main failed a required job.

Structure only: it reads run ids, job names and conclusions through `gh`. It
never reads logs. An unavailable or unauthenticated `gh` yields one INFO and no
alarm. Each red run id alarms once; the state file survives restarts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.air.night_results_watch import EXIT_CODES, Event, WatchError, parse_object, save_state  # noqa: E402

DEFAULT_STATE = Path.home() / "Library/Application Support/JouleWise/air-watch/main-ci-state.json"
FAILED = {"failure", "timed_out", "startup_failure", "cancelled"}
KEEP = 50


class GhUnavailable(Exception):
    pass


def required(job_name):
    return job_name in {"fences", "quick"} or job_name.startswith("test (")


def token(text):
    return re.sub(r"[^A-Za-z0-9_.,()=-]", "", text.replace(" ", ""))[:64]


def gh_json(gh, args, timeout):
    try:
        done = subprocess.run([gh, *args], stdin=subprocess.DEVNULL, capture_output=True,
                              timeout=timeout, check=False)
    except (OSError, subprocess.SubprocessError):
        raise GhUnavailable() from None
    if done.returncode != 0:
        raise GhUnavailable()
    try:
        return json.loads(done.stdout)
    except ValueError:
        raise GhUnavailable() from None


def latest_completed(gh, repo, workflow, timeout):
    base = ["--repo", repo] if repo else []
    runs = gh_json(gh, ["run", "list", *base, "--branch", "main", "--workflow", workflow,
                        "--limit", "5", "--json", "databaseId,status,conclusion,headSha,event"], timeout)
    done = [r for r in runs if isinstance(r, dict) and r.get("status") == "completed"
            and r.get("event") in (None, "push") and type(r.get("databaseId")) is int]
    if not done:
        return None, []
    run = done[0]  # gh lists newest first
    view = gh_json(gh, ["run", "view", str(run["databaseId"]), *base, "--json", "jobs"], timeout)
    jobs = view.get("jobs", []) if isinstance(view, dict) else []
    red = sorted(token(j["name"]) for j in jobs if isinstance(j, dict) and isinstance(j.get("name"), str)
                 and required(j["name"]) and j.get("conclusion") in FAILED)
    return run, red


def load(path):
    if not path.exists():
        return {"version": 1, "raised": [], "gh_unavailable": False}
    try:
        state = parse_object(path.read_bytes())
    except WatchError:
        state = {}
    if (state.get("version") != 1 or not isinstance(state.get("raised"), list)
            or not all(type(r) is int for r in state["raised"])):
        state = {"version": 1, "raised": []}
    state.setdefault("gh_unavailable", False)
    return state


def check(state, *, gh="gh", repo=None, workflow="ci.yml", timeout=30):
    """Return new events and mutate state. Caller saves state after delivery."""
    try:
        run, red = latest_completed(gh, repo, workflow, timeout)
    except GhUnavailable:
        if state["gh_unavailable"]:
            return []
        state["gh_unavailable"] = True
        return [Event("INFO", "GH_UNAVAILABLE", "main")]
    state["gh_unavailable"] = False
    if run is None or not red or run["databaseId"] in state["raised"]:
        return []
    state["raised"] = (state["raised"] + [run["databaseId"]])[-KEEP:]
    sha = run.get("headSha") if isinstance(run.get("headSha"), str) else ""
    fields = f"run={run['databaseId']} sha={token(sha)[:12]} jobs={','.join(red)}"
    return [Event("ALARM", "MAIN_CI_RED", "main", fields, str(run["databaseId"]))]


def run_once(state_path, notify=None, **kwargs):
    state = load(state_path)
    events = check(state, **kwargs)
    now = time.time()
    for event in events:
        line = event.line(now)
        print(line, flush=True)
        if notify:
            notify(line)
    save_state(state_path, state)
    levels = {e.level for e in events}
    return EXIT_CODES["alarm"] if "ALARM" in levels else EXIT_CODES["quiet"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--gh", default="gh")
    parser.add_argument("--repo", help="OWNER/NAME; default is the current directory's repo")
    parser.add_argument("--workflow", default="ci.yml")
    args = parser.parse_args(argv)
    try:
        return run_once(args.state, gh=args.gh, repo=args.repo, workflow=args.workflow)
    except (OSError, ValueError):
        print(Event("INFO", "MAIN_CI_WATCH_ERROR", "main").line(time.time()), flush=True)
        return EXIT_CODES["error"]


if __name__ == "__main__":
    raise SystemExit(main())
