#!/usr/bin/env python3
"""Exercise the next two MBP steps off the measurement host, using repo code only.

The lead-maintained manifest is trusted executable configuration. Live commands
are documentation only: only explicitly supplied synthetic seams run. No package
installation, model download, measurements, launchd operation or implicit fetch.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "joulewise.readiness_next2.v1"

# Run inside the selected tree, in a fresh interpreter for each module/opt-in.
# unittest's normal zero exit status permits skips and expected failures. Ours
# deliberately does not; report their exact identities and reasons as evidence.
TEST_RUNNER = r'''
import json, sys, unittest
sys.path.insert(0, '.')
suite = unittest.defaultTestLoader.loadTestsFromName(sys.argv[1])
result = unittest.TextTestRunner(verbosity=2).run(suite)
record = dict(tests=result.testsRun,
    skipped=[dict(test=str(t), reason=r) for t,r in result.skipped],
    expected_failures=[str(t) for t,_ in result.expectedFailures],
    unexpected_successes=[str(t) for t in result.unexpectedSuccesses],
    failures=[dict(test=str(t), reason=r) for t,r in result.failures],
    errors=[dict(test=str(t), reason=r) for t,r in result.errors])
with open(sys.argv[2], 'w') as f: json.dump(record, f)
sys.exit(0 if result.wasSuccessful() and result.testsRun and not
    (result.skipped or result.expectedFailures) else 1)
'''


def confined(root, relative):
    """Never follow receipt/config paths out of the inspected code tree."""
    if not isinstance(relative, str) or not relative:
        raise ValueError("path not specified")
    path = Path(relative)
    if path.is_absolute() or any(p in ("..", "restricted") for p in path.parts):
        raise ValueError(f"non-repository or restricted path refused: {relative}")
    root = root.resolve()
    # Check symlinks one component at a time, before following any of them.
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink refused: {relative}")
    return current


def run(argv, cwd, env=None, timeout=600):
    started = time.monotonic()
    try:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            return {"argv": argv, "returncode": None, "stdout": stdout,
                    "stderr": stderr, "error": f"timeout after {timeout}s"}
        return {"argv": argv, "returncode": proc.returncode, "stdout": stdout,
                "stderr": stderr, "seconds": round(time.monotonic() - started, 3)}
    except OSError as exc:
        return {"argv": argv, "returncode": None, "error": str(exc)}


def git(repo, *args):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
    result = run(["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", *args],
                 repo, env=env, timeout=120)
    if result.get("returncode") != 0:
        raise ValueError(result.get("error") or result.get("stderr", "").strip())
    return result["stdout"].strip()


@contextmanager
def checkout(repo, step, scratch, fetch=False):
    branch = step.get("branch")
    if not branch or branch.startswith("-"):
        raise ValueError("branch not specified")
    # A ref name, never a URL, remote option or arbitrary revision expression.
    git(repo, "check-ref-format", "refs/heads/" + branch)
    ref = "refs/remotes/origin/" + branch
    if fetch:
        git(repo, "fetch", "--no-tags", "origin", f"+refs/heads/{branch}:{ref}")
    head = git(repo, "rev-parse", "--verify", ref + "^{commit}")
    pin = step.get("commit")
    if pin:
        if len(pin) != 40 or any(c not in "0123456789abcdef" for c in pin):
            raise ValueError("commit must be a full lowercase SHA-1")
        git(repo, "merge-base", "--is-ancestor", pin, head)
        head = pin
    tree = scratch / "tree"
    git(repo, "worktree", "add", "--detach", str(tree), head)
    try:
        yield tree, head
    finally:
        git(repo, "worktree", "remove", "--force", str(tree))


def pending(value):
    if value is None or value == "" or value == {} or value == []:
        return True
    if isinstance(value, str):
        return value.upper().startswith(("PENDING", "TODO", "TBD"))
    if isinstance(value, dict):
        return any(pending(v) for k, v in value.items() if k != "fan_keys")
    if isinstance(value, list):
        return any(pending(v) for v in value)
    return False


def leaf(data, dotted):
    for key in dotted.split("."):
        data = data[key]
    return data


def aggregate(rows):
    states = {r["status"] for r in rows}
    return "RED" if "RED" in states else "UNKNOWN" if "UNKNOWN" in states else "GREEN"


def environment(scratch, extra=None):
    env = os.environ.copy()
    # Keep config-derived host caches and credentials out of synthetic runs.
    for key in list(env):
        if key.startswith(("JW_", "HF_", "HUGGINGFACE_", "AWS_", "GOOGLE_")):
            del env[key]
    env.update(extra or {})
    env.update(HOME=str(scratch), TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE="1",
               PYTHONNOUSERSITE="1",
               HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1",
               HF_HOME=str(scratch / "hf"), XDG_CACHE_HOME=str(scratch / "cache"))
    env.pop("PYTHONPATH", None)
    return env


def bounded_run(argv, cwd, env, timeout=600, deadline=None):
    if deadline is not None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return {"argv": argv, "returncode": None, "error": "readiness time budget exhausted; required check not run"}
        timeout = min(timeout, remaining)
    return run(argv, cwd, env, timeout=timeout)


def command(spec, tree, scratch, env, deadline=None):
    if not spec or not spec.get("argv"):
        return {"returncode": None, "error": "command not specified"}
    replacements = {"{python}": sys.executable, "{scratch}": str(scratch), "{tree}": str(tree)}
    argv = []
    for arg in spec["argv"]:
        for old, new in replacements.items():
            arg = arg.replace(old, new)
        argv.append(arg)
    # No shell expansion: embedded host paths in tracked JSON remain text.
    return bounded_run(argv, tree, env, timeout=spec.get("timeout_s", 600), deadline=deadline)


def explanation(result):
    return result.get("error") or (result.get("stderr", "") + result.get("stdout", "")).strip() or (
        f"exit {result.get('returncode')}")


def unexercised(step, reason):
    """One UNKNOWN row per prerequisite, even when its branch is unavailable."""
    names = ["kit --check"]
    names += ["kit:" + f for f in (step.get("kit") or {}).get("required_fields", [])]
    names += ["evidence:" + e["name"] for e in step.get("evidence", [])]
    names += ["PREQUAL:" + c for c in (step.get("prequal") or {}).get("checks", [])]
    names += ["tests:" + t["module"] for t in step.get("tests", [])]
    return [dict(prerequisite=n, status="UNKNOWN", reason=reason) for n in names]


def inspect_step(step, tree, scratch, deadline=None):
    rows = []
    env = environment(scratch)

    def add(name, status, reason, **detail):
        rows.append(dict(prerequisite=name, status=status, reason=reason, **detail))

    arm = step.get("arm") or {}
    missing_route_files = []
    for path in arm.get("route_files", []):
        try:
            if not confined(tree, path).is_file():
                missing_route_files.append(path)
        except ValueError as exc:
            missing_route_files.append(str(exc))
    if not arm.get("live_command") or not arm.get("synthetic") or not arm.get("exercises"):
        add("arm/launch", "RED", "no arm route: " + arm.get("pending_reason", "live command or synthetic seam missing"))
    elif not arm.get("route_files") or missing_route_files:
        add("arm/launch", "RED", "no arm route: " + (", ".join(missing_route_files) or "route files not specified"))
    else:
        result = command(arm["synthetic"], tree, scratch, env, deadline=deadline)
        status = "GREEN" if result.get("returncode") == 0 else "RED"
        # A CLI may exit zero while emitting a refused/incomplete record. The
        # seam must declare a machine-readable success assertion, not just rc=0.
        assertion = arm["synthetic"].get("assert_json")
        if not assertion:
            status = "RED"
            result["error"] = "synthetic arm seam has no success assertion"
        elif status == "GREEN":
            try:
                data = json.loads(confined(scratch, assertion["path"]).read_text())
                for field, expected in assertion["equals"].items():
                    actual = leaf(data, field)
                    if actual != expected:
                        raise ValueError(f"{field}={actual!r}, expected {expected!r}")
                if not assertion["equals"]:
                    raise ValueError("empty success assertion")
            except (OSError, ValueError, KeyError, TypeError) as exc:
                status = "RED"
                result["error"] = f"synthetic arm refused: {exc}"
        add("arm/launch", status, "synthetic route passed" if status == "GREEN" else explanation(result),
            command=result, live_command=arm["live_command"], exercises=arm["exercises"])

    kit = step.get("kit") or {}
    fields = kit.get("required_fields") or []
    if not fields:
        add("kit fields", "RED", "required kit fields not specified")
    for field in fields:
        try:
            value = leaf(json.loads(confined(tree, kit["path"]).read_text()), field)
            if pending(value):
                raise ValueError("missing or pending value")
            add("kit:" + field, "GREEN", "present (contents not echoed)")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            add("kit:" + field, "RED", str(exc))
    result = command(kit.get("check"), tree, scratch, env, deadline=deadline)
    add("kit --check", "GREEN" if result.get("returncode") == 0 else "RED",
        explanation(result) + ("; " + kit["pending_reason"] if kit.get("pending_reason") else ""), command=result)

    evidence = step.get("evidence") or []
    if not evidence:
        add("receipts/rulings", "RED", "required receipts/rulings not specified")
    for item in evidence:
        try:
            raw = confined(tree, item.get("path")).read_bytes()
            if not raw.strip():
                raise ValueError("empty receipt/ruling")
            if item.get("sha256") and hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError("receipt/ruling digest mismatch")
            for text in item.get("contains", []):
                if text.encode() not in raw:
                    raise ValueError(f"required text absent: {text}")
            add("evidence:" + item["name"], "GREEN", item["path"])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            add("evidence:" + item.get("name", "unnamed"), "RED", str(exc))

    prequal = step.get("prequal") or {}
    checks = prequal.get("checks") or []
    if not checks:
        add("PREQUAL", "RED", "applicable PREQUAL checks not specified")
    else:
        prequal_result = None
        try:
            script = confined(tree, "scripts/align_v4_prequal.py")
            if not script.is_file():
                raise ValueError("scripts/align_v4_prequal.py missing")
            out = scratch / "prequal"
            prequal_result = bounded_run([sys.executable, "-B", str(script), "--offline", "--stage", prequal["stage"],
                          "--only", ",".join(checks), "--output", str(out)], tree, env,
                         timeout=prequal.get("timeout_s", 600), deadline=deadline)
            report = json.loads(confined(out, "prequal.json").read_text())
            found = {r["check"]: r for r in report["checks"]}
            for check in checks:
                row = found.get(check, {"status": "not_run", "reason": "required check absent"})
                # Exit 1 can represent a different selected check's failure;
                # do not turn a passing prerequisite red because of its sibling.
                ok = row["status"] == "pass" and prequal_result.get("returncode") in (0, 1, 3)
                add("PREQUAL:" + check, "GREEN" if ok else "RED", json.dumps(row), command=prequal_result)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            for check in checks:
                add("PREQUAL:" + check, "RED", str(exc) + ("; " + explanation(prequal_result) if prequal_result else ""))

    tests = step.get("tests") or []
    if not tests or not any(t.get("env") for t in tests):
        add("required tests", "RED", "default and explicit opt-in test selectors must be listed")
    if not any(not t.get("env") for t in tests):
        add("default tests", "RED", "default test selector not specified")
    for i, test in enumerate(tests):
        summary = scratch / f"unittest-{i}.json"
        result = bounded_run([sys.executable, "-B", "-c", TEST_RUNNER, test["module"], str(summary)],
                     tree, environment(scratch, test.get("env")), timeout=test.get("timeout_s", 600), deadline=deadline)
        try:
            record = json.loads(summary.read_text())
            skips = record["skipped"]
            ok = result.get("returncode") == 0 and record["tests"] > 0 and not skips and not record["expected_failures"]
            reason = ("required test skipped: " + json.dumps(skips)) if skips else explanation(result)
            add("tests:" + test["module"], "GREEN" if ok else "RED", reason, test_result=record,
                command=result, env=test.get("env", {}))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            add("tests:" + test["module"], "RED", explanation(result) + f"; no unittest result: {exc}", command=result)
    return rows


def merge_defaults(defaults, overrides):
    """Dictionaries merge; arrays and explicit nulls replace the default."""
    result = dict(defaults)
    for key, value in overrides.items():
        result[key] = (merge_defaults(result[key], value)
                       if isinstance(value, dict) and isinstance(result.get(key), dict) else value)
    return result


def evaluate(repo, manifest, fetch=False, now=None, budget_s=1200):
    if not math.isfinite(budget_s) or budget_s <= 0:
        raise ValueError("budget must be positive and finite")
    deadline = time.monotonic() + budget_s
    now = now or datetime.now(timezone.utc)
    start = manifest.get("mbp_available_at")
    available = datetime.fromisoformat(start.replace("Z", "+00:00")) if start else now
    if available.tzinfo is None:
        raise ValueError("mbp_available_at must include a timezone")
    available = max(available, now)
    hour = (available - now).total_seconds() / 3600
    steps = manifest.get("steps")
    if manifest.get("schema") != SCHEMA or not isinstance(steps, list) or len(steps) < 2:
        raise ValueError("manifest must declare readiness_next2.v1 and at least two ordered steps")
    if any(not isinstance(s, dict) or not isinstance(s.get("id"), str) or not s["id"] for s in steps):
        raise ValueError("every step must have a nonempty id")
    if len({s["id"] for s in steps}) != len(steps):
        raise ValueError("step ids must be unique")
    results = []
    for entry in steps[:2]:
        step = merge_defaults(manifest.get("defaults", {}), entry)
        with tempfile.TemporaryDirectory(prefix="jw-readiness-") as tmp:
            scratch = Path(tmp)
            head = None
            try:
                with checkout(repo, step, scratch, fetch=fetch) as (tree, head):
                    rows = [dict(prerequisite="checkout", status="GREEN", reason=head)]
                    rows.extend(inspect_step(step, tree, scratch, deadline=deadline))
            except (OSError, ValueError, KeyError, TypeError) as exc:
                rows = [dict(prerequisite="checkout", status="RED", reason=str(exc)),
                        dict(prerequisite="arm/launch", status="RED", reason="no arm route: checkout unavailable")]
                rows.extend(unexercised(step, "checkout unavailable; not exercised"))
            status = aggregate(rows)
            alarm = status == "RED" and hour <= 24
            eta = now + timedelta(hours=hour)
            for row in rows:
                row.update(earliest_mbp_hour=round(hour, 3), earliest_mbp_at=eta.isoformat(),
                           critical_path_alarm=row["status"] == "RED" and hour <= 24)
            results.append(dict(id=step["id"], branch=step.get("branch"), commit=head,
                                status=status, earliest_mbp_hour=round(hour, 3),
                                earliest_mbp_at=eta.isoformat(), critical_path_alarm=alarm, prerequisites=rows))
        duration = step.get("minimum_duration_hours", 0)
        if isinstance(duration, bool) or not isinstance(duration, (float, int)) or not math.isfinite(duration) or duration < 0:
            raise ValueError("minimum_duration_hours must be finite and nonnegative")
        hour += duration
    return dict(schema=SCHEMA, generated_at=now.isoformat(), status=aggregate(results),
                budget_seconds=budget_s,
                manifest_sha256=hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
                critical_path_alarm=any(s["critical_path_alarm"] for s in results),
                refs="fetched from origin" if fetch else "cached origin refs (no network; freshness not asserted)",
                claims="Synthetic software readiness only; grants no hardware qualification or arm authority.",
                steps=results)


def markdown(report):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", "<br>")
    lines = ["# Next-two MBP readiness", "", f"Status: **{report['status']}**. " + report["claims"], "",
             "Critical-path alarm: " + str(report["critical_path_alarm"]) + ". " + report["refs"], "",
             "Full command output and refusal reasons are retained in the JSON; table reasons are abbreviated.", "",
             "| Step | Prerequisite | Status | Earliest MBP hour (UTC) | Reason |",
             "|---|---|---|---|---|"]
    for step in report["steps"]:
        for row in step["prerequisites"]:
            lines.append("| " + " | ".join(map(cell, [step["id"], row["prerequisite"], row["status"],
                         f"+{row['earliest_mbp_hour']}h ({row['earliest_mbp_at']})", row["reason"][:600]])) + " |")
    return "\n".join(lines) + "\n"


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as out:
        out.write(text)
        tmp = out.name
    os.replace(tmp, path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/readiness/next_steps.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tmp/readiness/status.json")
    parser.add_argument("--fetch", action="store_true", help="workflow only: fetch each named origin branch")
    parser.add_argument("--budget-seconds", type=float, default=1200, help="overall command budget (default 20 min)")
    args = parser.parse_args(argv)
    try:
        report = evaluate(args.repo, json.loads(args.config.read_text()), fetch=args.fetch, budget_s=args.budget_seconds)
    except Exception as exc:  # The diagnostic must publish RED even for a malformed manifest/runner error.
        report = dict(schema=SCHEMA, status="RED", critical_path_alarm=True, steps=[],
                      generated_at=datetime.now(timezone.utc).isoformat(), refs="not evaluated",
                      claims=f"Manifest/readiness runner error: {exc}")
    atomic_write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n")
    table = markdown(report)
    atomic_write(args.output.with_suffix(".md"), table)
    print(table)
    return {"GREEN": 0, "RED": 1, "UNKNOWN": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
