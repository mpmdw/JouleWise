"""Prepare and operate evidence candidates through the existing night executors."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import traceback
from typing import Callable

from joulewise import corecaptured_loop

KIND = "quiet_predicate_evidence"
REMOTE = "https://github.com/mpmdw/JouleWise"
SCHEMA = "joulewise.evidence_prepare.v1"
STEPS = ("clone", "venv", "plan", "wrapper", "render", "complete")
# Activation records 19/21: every arm needs a supervisor started after the
# canonical fast-forward; H must include the bracketed census cure. D-183:
# `check` performs that fast-forward itself when nothing is loaded.
CENSUS_FIX = "980f8d6452fb6923644bdac1e243ce0a344c881f"
CANONICAL = "/Users/edr/code/JouleWise"
SUPERVISOR_STATE = "/Users/edr/night-custody/magistrate/state.json"
FAST_FORWARD_TIMEOUT_S = 120
MAGISTRATE = "/Users/edr/night-custody/magistrate"
DIRECTIVES_ARGV = ("gh", "issue", "list", "--repo", "mpmdw/JouleWise", "--label",
                   "directive", "--state", "open", "--author", "mpmdw", "--json",
                   "number,title,body,author")


class Refused(Exception):
    """A preparation cannot safely advance.

    `evidence` is an optional mapping of the observation the refusal rests on.
    `check()` merges it into the failing check's row, so a refusal whose text
    points at a field (for example "observation in top_consumers_at_decision")
    leaves that field in check.json (lens S4, fix round 1).
    """

    def __init__(self, *args, evidence=None):
        super().__init__(*args)
        self.evidence = dict(evidence or {})


def run(argv, *, cwd=None, input=None):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                            text=True, capture_output=True, check=False, input=input)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise Refused(f"{Path(str(argv[0])).name} failed ({result.returncode}): {detail}")
    return result.stdout.strip()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_path(value):
    path = Path(os.path.abspath(Path(value).expanduser()))
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise Refused(f"symlink/path collision: {path}")
    return path


def absent(path):
    safe_path(path)
    if os.path.lexists(path):
        raise Refused(f"existing foreign or uncheckpointed output: {path}")


def parse_head(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", value):
        raise Refused("H must be a full SHA")
    return value.lower()


def unambiguous(epoch):
    local = datetime.fromtimestamp(epoch)
    candidates = {local.replace(fold=f).timestamp() for f in (0, 1)}
    return len({e for e in candidates if datetime.fromtimestamp(e) == local}) == 1


def parse_t0(value, now):
    if value == "next":
        epoch = math.ceil((now + 2400) / 60) * 60
        while not unambiguous(epoch):
            epoch += 60
        return epoch
    if not re.fullmatch(r"[0-9]+", str(value)):
        raise Refused("t0 must be epoch seconds or next")
    epoch = int(value)
    if epoch % 60:
        raise Refused("t0 is not minute aligned")
    if epoch <= now:
        raise Refused("t0 is in the past")
    if not unambiguous(epoch):
        raise Refused("t0 is ambiguous local time")
    return epoch


def verify_lock(root):
    lock = root / "env/mac-measurement-lock.txt"
    expected = sorted(line.strip() for line in lock.read_text().splitlines()
                      if line.strip() and not line.lstrip().startswith("#"))
    installed = sorted(run([root / ".venv/bin/python", "-B", "-m", "pip",
                            "freeze", "--exclude-editable"], cwd=root).splitlines())
    if installed != expected:
        raise Refused("lock mismatch: pip freeze differs from mac-measurement-lock.txt")


def build_venv(root):
    """The bench step-1 recipe; injected only by offline Python callers."""
    absent(root / ".venv")
    # The bench step-1 probe; it lives in the builder so that offline tests,
    # which inject a builder, need no python3.13 on the host (the hosted 3.11
    # shards have none: post-merge run 35522762217 after PR #372).
    run(["python3.13", "--version"])
    run(["python3.13", "-m", "venv", ".venv"], cwd=root)
    python = root / ".venv/bin/python"
    prefix = [python, "-B", "-m", "pip", "install", "-q", "-c", "env/mac-measurement-lock.txt"]
    run([*prefix, "-e", ".[mac]"], cwd=root)
    run([*prefix, "charset-normalizer", "requests", "urllib3"], cwd=root)
    verify_lock(root)


def interpreter(root):
    code = ("import json,sys; from joulewise.night_agent_install import interpreter_identity; "
            "print(json.dumps(interpreter_identity(sys.executable)))")
    return json.loads(run([root / ".venv/bin/python", "-B", "-c", code], cwd=root))


def checkout_ok(root, head):
    safe_path(root / ".git")
    if run(["git", "-C", root, "rev-parse", "HEAD"]) != head:
        raise Refused("clone HEAD differs from H")
    if run(["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"]) != "HEAD":
        raise Refused("clone is not detached")
    if run(["git", "-C", root, "--no-optional-locks", "status", "--porcelain=v1", "--untracked-files=all"]):
        raise Refused("dirty clone")


def locations(roots, stages, epoch, head):
    local = datetime.fromtimestamp(epoch)
    plan_id = "qpe01-pilot-n1-" + local.strftime("%Y%m%d-%H%M")
    stamp = f"{local:%Y%m%d-%H%M}-{epoch}-{head}"
    return dict(plan_id=plan_id,
                measurement_root=str(roots / f"JouleWise-measurement-{stamp}-qpe01-pilot-n1"),
                staging=str(stages / f"{plan_id}-{stamp}"),
                custody_root=str(roots / "night-custody" / f"{plan_id}-{stamp}"))


def read_state(path):
    safe_path(path)
    state = json.loads(path.read_text())
    if not isinstance(state, dict) or state.get("schema") != SCHEMA:
        raise Refused(f"unknown prior-preparation ownership: {path}")
    return state


def checkpoint(path, state, step=None, files=()):
    for file in files:
        safe_path(file)
        state["digests"][str(file)] = digest(file)
    if step:
        state["steps"].append(dict(step=step, completed_epoch_s=time.time()))
    saved_json(path, state)


def saved_json(path, value):
    """Publish a complete fsynced JSON record with the checkpoint protocol."""
    atomic_bytes(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def atomic_bytes(path, raw):
    path = safe_path(path)
    temporary = path.with_suffix(".tmp")
    absent(temporary)
    try:
        with temporary.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def staging_lock(stages, name):
    directory = safe_path(stages / ".locks")
    directory.mkdir(parents=True, exist_ok=True)
    with safe_path(directory / (name + ".lock")).open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Refused("concurrent preparation") from exc
        yield


def prior_records(stages, roots):
    records = []
    for directory in sorted(stages.glob("qpe01-pilot-n1-*")):
        safe_path(directory)
        if not directory.is_dir():
            continue
        # Also distinguish an in-progress first checkpoint from an orphan.
        with staging_lock(stages, directory.name):
            try:
                record = read_state(directory / "prepare.json")
            except (OSError, ValueError) as exc:
                raise Refused(f"unidentified prior preparation output: {directory}") from exc
        records.append(record)
    referenced = {r.get("custody_root") for r in records}
    for directory in sorted((roots / "night-custody").glob("qpe01-pilot-n1-*")):
        safe_path(directory)
        if (directory.is_dir() and not (directory / "night_plan.json").is_file()
                and str(directory) not in referenced):
            raise Refused(f"unidentified prior preparation output: {directory}")
    return records


def sealed_candidate(root, plan):
    code = """import hashlib,json,subprocess,sys
from pathlib import Path
from joulewise import night_gate
from joulewise.quiet_predicate_campaign import CHAIN_PATH, manifest_for, tracked_bytes, verify_manifest
check='plan'
try:
    p=night_gate.NightPlan.from_mapping(json.loads(Path(sys.argv[1]).read_text()))
    check='registration file'
    registration=Path(p.registration_path)
    if not registration.is_absolute(): registration=Path(p.measurement_root)/registration
    registration_raw=registration.read_bytes(); sha=hashlib.sha256(registration_raw).hexdigest()
    check='registration ruled digest'
    if not (sha in night_gate.RULED_REGISTRATIONS and night_gate.RULED_REGISTRATIONS[sha]['binds_chain']): raise ValueError(check)
    check='registration current digest'
    if sha!=night_gate.QPE01_PILOT_REGISTRATION_SHA256: raise ValueError(check)
    check='registration armability'
    if night_gate.armable_registration(sha) is None: raise ValueError(check)
    check='wrapper sidecar'
    wrapper=Path(p.chain_path); raw=wrapper.read_bytes(); text=raw.decode()
    if not (Path(p.chain_sha256_path).read_text().split()==[hashlib.sha256(raw).hexdigest(),wrapper.name]): raise ValueError(check)
    check='manifest'
    if not (json.loads((Path(p.custody_root)/'evidence_manifest.json').read_text())==manifest_for(p)): raise ValueError(check)
    verify_manifest(p,text)
    check='chain source'
    source=hashlib.sha256(tracked_bytes(p.measurement_root,p.measurement_head,CHAIN_PATH)).hexdigest()
    if not (night_gate.chain_literal(text,'EVIDENCE_CHAIN_SOURCE_SHA256')==source): raise ValueError(check)
    check='registration'
    if not (json.loads(registration_raw)['chain_source_sha256']==source): raise ValueError(check)
    check='published plan path'
    if not (night_gate.chain_literal(text,'EVIDENCE_PLAN_PATH')==str(Path(p.custody_root)/'night_plan.json')): raise ValueError(check)
    check='zsh -n'
    if not (subprocess.run(['/bin/zsh','-n',str(wrapper)],capture_output=True).returncode==0): raise ValueError(check)
except (OSError,ValueError,KeyError,AssertionError,subprocess.SubprocessError):
    print(json.dumps({'failed':check})); sys.exit(0)
print(json.dumps({'registration_path':str(registration),'registration_sha256':sha,
                  'chain_source_path':str(Path(p.measurement_root)/CHAIN_PATH),'chain_source_sha256':source}))
"""
    result = json.loads(run([root / ".venv/bin/python", "-B", "-c", code, plan], cwd=root))
    if "failed" in result:
        raise Refused("sealed candidate failed " + result["failed"])
    return result


def notice_subject(state):
    return f'NIGHT NOTICE — {state["plan_id"]} (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt {state["attempt"]}'


def render_notice(state, *, checked=None, check_sha256=None):
    binding = state["bindings"]
    registration = Path(binding["registration_path"])
    if not registration.is_absolute():
        registration = Path(state["measurement_root"]) / registration
    raw = registration.read_bytes()
    registration_sha256 = hashlib.sha256(raw).hexdigest()
    if registration_sha256 != binding["registration_sha256"]:
        raise Refused("notice registration differs from sealed binding")
    protocol = json.loads(raw)
    rule = protocol["non_observer_process_busy"]
    span = (protocol["settle_s"] + (protocol["envelopes"] - 1)
            * protocol["slot_pitch_s"] + protocol["envelope_s"])
    if span > protocol["window_max_s"]:
        raise Refused("notice program exceeds registered window")
    words = ("zero", "one", "two", "three", "four", "five", "six", "seven",
             "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
             "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty")
    def count_word(number):
        return words[number] if isinstance(number, int) and 0 <= number < len(words) else str(number)
    plan = json.loads(Path(state["plan_path"]).read_text())
    s = state["schedule"]
    lines = ["DRAFT — NOT SENT; prerequisites and veto observations are not yet recorded.",
             "To: claude2.glaring610@passmail.net",
             'Subject: ' + notice_subject(state),
             "", "Ed,", "Launch needs no action from you unless you reply NO. Your NO overrides.",
             f'Arm attempt {state["attempt"]}; prior candidates for this date: {", ".join(state["prior_candidates"]) or "none"}.',
             "This idle-variance evidence night sizes a later experiment; it activates no new quietness cutoff.",
             f'After {protocol["settle_s"]} seconds settling, {count_word(protocol["envelopes"])} '
             f'{protocol["envelope_s"]}-second idle envelopes start {protocol["slot_pitch_s"]} seconds apart '
             f'and use {protocol["interior_s"]}-second interiors after {protocol["interior_offset_s"]}-second offsets.',
             "Power sampling is every 100 ms, with census, AC-power, thermal, timing and cleanup observations and a journal of busy cores (the average number of CPU cores a process kept busy).",
             f'The {span:,}-second program fits inside the {protocol["window_max_s"]:,}-second window; no top-up or automatic repeat.',
             f'A process outside the measurement apparatus (the night\'s own measurement processes) at or above {protocol["t0_non_observer_share_max"]:g} busy cores '
             'refuses the night at the arm check (the pre-arm checks run before this notice is sent and before the night is installed) or at t0, the scheduled start.',
             f'A process outside the measurement apparatus using {rule["bar_core_seconds"]:g} or more core-seconds '
             '(busy cores multiplied by seconds) '
             'inside an envelope excludes that envelope. '
             f'{count_word(rule["abort_after_consecutive"]).capitalize()} such exclusions in a row end the night.',
             "At t0 the gate reads launchd's log for the previous ten minutes; when that read succeeds, the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes. When the log cannot be read, the count is recorded as not measured and the night continues.",
             "During the night, read-only git show checks run in the measurement clone; successful results publication commits and pushes them from a separate results clone.",
             "Partial observations and refusals are kept. No model, load generator, calibration-ledger session or measurement pack runs.",
             "The scheduler supervises the program and the courier emails the result. Evidence remains PROVISIONAL.",
             "After delivery the lead sizes block two or records 'no cutoff qualifies'.",
             f'plan_id: {state["plan_id"]}', f'repo_head = measurement_head = H: {state["head"]}',
             f'clone: {state["measurement_root"]}', f'custody: {state["custody_root"]}',
             f'runs: {state["custody_root"]}/runs', f'staged plan: {state["plan_path"]}',
             f'authored_epoch_s: {plan["authored_epoch_s"]}']
    for name, epoch in s["boundaries"].items():
        lines.append(f"{name}: {datetime.fromtimestamp(epoch).astimezone().isoformat()} "
                     f"{datetime.fromtimestamp(epoch, timezone.utc).isoformat()} epoch {epoch}")
    for name in ("registration", "chain_source"):
        lines.append(f'{state["bindings"][name + "_path"]} sha256 {state["bindings"][name + "_sha256"]}')
    for index, (start, end) in enumerate(s["install_spans_today"], 1):
        for boundary, epoch in (("open", start), ("close EXCLUDED", end)):
            lines.append(f"install span {index} {boundary}: "
                         f"{datetime.fromtimestamp(epoch).astimezone().isoformat()} "
                         f"{datetime.fromtimestamp(epoch, timezone.utc).isoformat()} epoch {epoch}")
    lines.extend(f"{path} sha256 {sha}" for path, sha in state["digests"].items())
    lines += ["No-objection opens only on mail service acceptance of the exact notice. Publication follows acceptance with no additional minimum waiting interval.",
              "Every observed NO stops publication, including older threads. Reply NO on the thread or through an owner-authored directive; no reply is required.",
              "The magistrate checks readable NO/directive/stop channels before publication and exits before REQUEST.",
              "Keep agent applications closed and the machine untouched from REQUEST through completion, longer if the night remains active."]
    if checked is not None:
        observed = datetime.fromtimestamp(checked["finished_epoch_s"], timezone.utc).isoformat()
        lines = [f'Prepared candidate {state["plan_id"]}; pre-arm check {check_sha256[:12]} at {observed}',
                 "", *lines[4:]]
    return "\n".join(lines) + "\n"


def prepare(*, kind, t0, head=None, remote=REMOTE, roots_under="/Users/edr",
            staging_under="/Users/edr/night-plan-staging", builder=build_venv,
            lock_verifier=verify_lock):
    if kind != KIND:
        raise Refused("invalid or unresolved kind")
    now = time.time()
    explicit_t0 = None if t0 == "next" else parse_t0(t0, now)
    explicit_head = parse_head(head) if head is not None else None
    roots, stages = safe_path(roots_under), safe_path(staging_under)
    for parent in (roots, stages):
        if any(os.path.lexists(p / ".git") for p in (parent, *parent.parents)):
            raise Refused(f"fenced checkout: preparation locations must be outside worktrees: {parent}")
    # Look for an owned candidate before resolving defaults again.
    records = prior_records(stages, roots)
    candidates = [record for record in records
                  if (record.get("kind") == kind and record.get("remote") == remote
                      and record.get("roots_under") == str(roots)
                      and (explicit_t0 is None or record.get("t0") == explicit_t0)
                      and (explicit_head is None or record.get("head") == explicit_head))]
    if len(candidates) > 1:
        raise Refused("ambiguous prior preparations; supply explicit t0 and H")
    if candidates:
        state = candidates[0]
        epoch = parse_t0(state["t0"], now)
        resolved_head = parse_head(state["head"])
    else:
        epoch = explicit_t0 if explicit_t0 is not None else parse_t0(t0, now)
        resolved_head = explicit_head
        if resolved_head is None:
            refs = run(["git", "ls-remote", remote, "refs/heads/main"]).split()
            if len(refs) != 2 or refs[1] != "refs/heads/main":
                raise Refused("remote main could not be resolved")
            resolved_head = parse_head(refs[0])
        state = dict(schema=SCHEMA, kind=kind, t0=epoch, head=resolved_head,
                     remote=remote, roots_under=str(roots), digests={}, steps=[])
    paths = locations(roots, stages, epoch, resolved_head)
    root, stage, custody = (safe_path(paths[k]) for k in ("measurement_root", "staging", "custody_root"))
    if any(a == b or a in b.parents or b in a.parents
           for a, b in ((root, stage), (root, custody), (stage, custody))):
        raise Refused("overlapping preparation paths")
    if epoch - now < 2400:
        print("WARNING: runway below the 40-minute planning default", file=sys.stderr)
    # Early resource guard uses the running checkout; H's authoring check binds.
    from joulewise.night_gate import PLAN_MAX_AGE_S
    if epoch - now > PLAN_MAX_AGE_S:
        raise Refused("t0 is beyond the plan's maximum age at authoring")
    for parent in (stages, custody.parent):
        parent.mkdir(parents=True, exist_ok=True)
    if stages.stat().st_dev != custody.parent.stat().st_dev:
        raise Refused("staging and custody are not on one filesystem (atomic publication)")
    state_path = stage / "prepare.json"
    with staging_lock(stages, stage.name):
        if candidates:
            if any(state.get(k) != v for k, v in paths.items()):
                raise Refused("prior-preparation ownership/path mismatch")
        elif state_path.is_file():
            # A competing preparation finished between selection and this lock.
            state = read_state(state_path)
            if any(state.get(k) != v for k, v in paths.items()):
                raise Refused("prior-preparation ownership/path mismatch")
        else:
            for path in (root, stage, custody):
                absent(path)
            stage.mkdir()
            prefix = "qpe01-pilot-n1-" + datetime.fromtimestamp(epoch).strftime("%Y%m%d")
            prior = sorted(r["plan_id"] for r in records if r.get("plan_id", "").startswith(prefix))
            state.update(paths, plan_path=str(stage / "night_plan.json"),
                         attempt=1 + len(prior), prior_candidates=prior)
            checkpoint(state_path, state)
        state = read_state(state_path)
        done = [item["step"] for item in state["steps"]]
        if done != list(STEPS[:len(done)]) or len(done) > len(STEPS):
            raise Refused("unknown prior-preparation step ledger")
        expected_stage = {"prepare.json"}
        lifecycle = safe_path(stage / "lifecycle")
        if lifecycle.is_dir():
            expected_stage.add("lifecycle")  # Mutable journals are not sealed artifacts.
        if "plan" in done:
            expected_stage.add("night_plan.json")
        if "render" in done:
            expected_stage.add("render")
        if {p.name for p in stage.iterdir()} != expected_stage:
            raise Refused("unknown or uncheckpointed staging output")
        if "render" in done:
            actual = {str(p) for p in (stage / "render").rglob("*") if p.is_file() or p.is_symlink()}
            expected = {p for p in state["digests"] if Path(p).is_relative_to(stage / "render")}
            if actual != expected:
                raise Refused("unknown or missing render output")
        required = set()
        if "venv" in done:
            required.add(str(root / "env/mac-measurement-lock.txt"))
        if "plan" in done:
            required.add(str(stage / "night_plan.json"))
        if "wrapper" in done:
            required.update(str(custody / name) for name in
                            ("chain.zsh", "chain.zsh.sha256", "chain.zsh.chain-source.sha256", "evidence_manifest.json"))
        if not required.issubset(state["digests"]):
            raise Refused("unknown prior-preparation ownership: missing sealed digests")
        for path, sha in state["digests"].items():
            safe_path(path)
            if not Path(path).is_file() or digest(path) != sha:
                raise Refused(f"sealed-byte drift: {path}")
        if custody.exists():
            allowed = {Path(p).name for p in state["digests"] if Path(p).parent == custody}
            # The real renderer may make empty night/runs directories.
            for path in custody.iterdir():
                if path.name in ("night", "runs") and path.is_dir() and not path.is_symlink() and not any(path.iterdir()):
                    continue
                if path.name not in allowed or path.is_symlink():
                    raise Refused(f"published, invoked or unknown custody output: {path}")
        plan = stage / "night_plan.json"
        python = root / ".venv/bin/python"
        if "clone" not in done:
            absent(root)
            root.parent.mkdir(parents=True, exist_ok=True)
            run(["git", "clone", "-q", "--no-hardlinks", remote, root])
            run(["git", "-C", root, "checkout", "-q", "--detach", resolved_head])
            run(["git", "-C", root, "fetch", "-q", "origin", "main"])
            run(["git", "-C", root, "merge-base", "--is-ancestor", resolved_head, "refs/remotes/origin/main"])
            checkout_ok(root, resolved_head)
            checkpoint(state_path, state, "clone")
        checkout_ok(root, resolved_head)
        safe_path(root / ".venv/bin")
        if "venv" not in done:
            absent(root / ".venv")
            builder(root)
            lock_verifier(root)
            state["interpreter"] = interpreter(root)
            checkpoint(state_path, state, "venv", [root / "env/mac-measurement-lock.txt"])
        else:
            lock_verifier(root)
            if interpreter(root) != state["interpreter"]:
                raise Refused("interpreter identity drift")
        checkout_ok(root, resolved_head)
        if "plan" not in done:
            absent(plan)
            # Author with H's code, never the caller checkout's imports.
            code = """import json,sys,time
from pathlib import Path
from joulewise.night_gate import NightPlan, PLAN_MAX_AGE_S
from joulewise.night_plan_writer import write_night_plan
from joulewise.quiet_predicate_campaign import PROTOCOL_PATH
s=json.load(sys.stdin); c=s['custody_root']
authored_epoch_s=int(time.time())
if s['t0']-authored_epoch_s > PLAN_MAX_AGE_S:
    print(json.dumps({'refused':"t0 is beyond the plan's maximum age at authoring"}))
    sys.exit(0)
p=NightPlan.from_mapping(dict(schema='joulewise.night_plan.v2',schema_version=2,
plan_id=s['plan_id'],receipt_class='DIAGNOSTIC_NO_PACK',t0_epoch_s=s['t0'],
window_max_s=9000,authored_epoch_s=authored_epoch_s,repo_head=s['head'],
measurement_root=s['measurement_root'],measurement_head=s['head'],
chain_path=c+'/chain.zsh',chain_sha256_path=c+'/chain.zsh.sha256',
custody_root=c,registration_path=PROTOCOL_PATH))
write_night_plan(s['plan_path'],p)
print(json.dumps({}))
"""
            result = json.loads(run([python, "-B", "-c", code], cwd=root, input=json.dumps(state)))
            if "refused" in result:
                raise Refused(result["refused"])
            checkpoint(state_path, state, "plan", [plan])
        if "wrapper" not in done:
            absent(custody)
            run([python, "-B", "scripts/gen_evidence_night.py", "--plan", plan, "--render-only"], cwd=root)
            state["bindings"] = sealed_candidate(root, plan)
            checkpoint(state_path, state, "wrapper", [custody / name for name in
                       ("chain.zsh", "chain.zsh.sha256", "chain.zsh.chain-source.sha256", "evidence_manifest.json")])
        else:
            sealed_candidate(root, plan)
        # Read validation uses the pinned executor even on a completed resume.
        run([python, "-B", "-c", """import json,sys,time
from joulewise.night_gate import NightPlan, PLAN_MAX_AGE_S
p=NightPlan.from_mapping(json.load(open(sys.argv[1])))
if not 0 <= time.time()-p.authored_epoch_s <= PLAN_MAX_AGE_S:
    raise ValueError('sealed plan stale or future-authored')
""", plan], cwd=root)
        render = stage / "render"
        if "render" not in done:
            absent(render)
            run([root / "scripts/install_night_agent.sh", "--plan", plan,
                 "--python", python, "--render-only", render], cwd=root)
            code = """import json,sys
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule, COURIER_DEADLINE_S
from scripts.magistrate_watchdog import PLAN_LEAD_S, TERM_LEAD_S, KILL_LEAD_S
p=NightPlan.from_mapping(json.load(open(sys.argv[1]))); s=schedule(p); t=p.t0_epoch_s
s['boundaries']={'install close EXCLUDED':s['install_close_epoch_s'],
'REQUEST / exit BEFORE':t-PLAN_LEAD_S, 'TERM':t-TERM_LEAD_S, 'KILL':t-KILL_LEAD_S,
't0':t, 'window end':t+p.window_max_s,
'completion / courier deadline':t+p.window_max_s+COURIER_DEADLINE_S,
'daily dead-man':s['deadman_epoch_s']}
print(json.dumps(s))
"""
            state["schedule"] = json.loads(run([python, "-B", "-c", code, plan], cwd=root))
            checkpoint(state_path, state, "render", sorted(p for p in render.rglob("*") if p.is_file()))
        if "complete" not in done:
            state["notice_draft"] = render_notice(state)
            state["frozen_triple"] = [state["plan_id"], str(root), resolved_head]
            checkpoint(state_path, state, "complete")
        if time.time() >= state["schedule"]["install_close_epoch_s"]:
            raise Refused("exclusive install close has passed")
        return state


def candidate_state(candidate):
    stage = safe_path(candidate)
    state = read_state(stage / "prepare.json")
    expected = locations(safe_path(state["roots_under"]), stage.parent,
                         state["t0"], parse_head(state["head"]))
    if (any(state.get(k) != v for k, v in expected.items())
            or state.get("plan_path") != str(stage / "night_plan.json")
            or state.get("kind") != KIND
            or [s["step"] for s in state["steps"]] != list(STEPS)):
        raise Refused("candidate is not a completed, owned preparation")
    return state


@contextmanager
def candidate_lock(candidate):
    stage = safe_path(candidate)
    with staging_lock(stage.parent, stage.name):
        yield


def lifecycle_dir(candidate):
    path = safe_path(Path(candidate) / "lifecycle")
    path.mkdir(exist_ok=True)
    return path


def sealed_state(state, *, published=False, lock_verifier=verify_lock):
    root = safe_path(state["measurement_root"])
    stage, custody = safe_path(state["staging"]), safe_path(state["custody_root"])
    plan = custody / "night_plan.json" if published else stage / "night_plan.json"
    required = {str(stage / "night_plan.json"), str(root / "env/mac-measurement-lock.txt")}
    required.update(str(custody / name) for name in
                    ("chain.zsh", "chain.zsh.sha256", "chain.zsh.chain-source.sha256", "evidence_manifest.json"))
    if not required.issubset(state["digests"]):
        raise Refused("missing sealed digests")
    render = stage / "render"
    actual = {str(p) for p in render.rglob("*") if p.is_file() or p.is_symlink()}
    expected = {p for p in state["digests"] if Path(p).is_relative_to(render)}
    if not actual or actual != expected:
        raise Refused("unknown or missing render output")
    for path, sha in state["digests"].items():
        physical = plan if path == state["plan_path"] else safe_path(path)
        safe_path(physical)
        if not physical.is_file() or digest(physical) != sha:
            raise Refused(f"sealed-byte drift: {physical}")
    checkout_ok(root, state["head"])
    lock_verifier(root)
    if interpreter(root) != state["interpreter"]:
        raise Refused("interpreter identity drift")
    sealed_candidate(root, plan)
    value = json.loads(plan.read_text())
    if any(value.get(k) != v for k, v in dict(
            plan_id=state["plan_id"], repo_head=state["head"], measurement_head=state["head"],
            measurement_root=str(root), custody_root=str(custody), t0_epoch_s=state["t0"]).items()):
        raise Refused("sealed plan differs from preparation identity")
    return plan


def clone_schedule(state, plan):
    code = """import json,sys,time
from joulewise.night_gate import NightPlan, PLAN_MAX_AGE_S
from scripts.run_night import schedule, COURIER_DEADLINE_S
from scripts.magistrate_watchdog import PLAN_LEAD_S, TERM_LEAD_S, KILL_LEAD_S
p=NightPlan.from_mapping(json.load(open(sys.argv[1])))
if not 0 <= time.time()-p.authored_epoch_s <= PLAN_MAX_AGE_S:
    raise ValueError('sealed plan stale or future-authored')
s=schedule(p); t=p.t0_epoch_s
s['boundaries']={'install close EXCLUDED':s['install_close_epoch_s'],
'REQUEST / exit BEFORE':t-PLAN_LEAD_S, 'TERM':t-TERM_LEAD_S, 'KILL':t-KILL_LEAD_S,
't0':t, 'window end':t+p.window_max_s,
'completion / courier deadline':t+p.window_max_s+COURIER_DEADLINE_S,
'daily dead-man':s['deadman_epoch_s']}
print(json.dumps(s))
"""
    root = Path(state["measurement_root"])
    return json.loads(run([root / ".venv/bin/python", "-B", "-c", code, plan], cwd=root))


def probe_command(argv, *, cwd=None, timeout=None, env=None):
    return subprocess.run(list(map(str, argv)), cwd=cwd, capture_output=True, text=True,
                          check=False, timeout=timeout,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", **(env or {})))


def observation_record(result):
    return dict(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)


def contains_head(canonical, head, commit, runner):
    result = runner(["git", "-C", canonical, "merge-base", "--is-ancestor", head, commit])
    if result.returncode not in (0, 1):
        raise Refused("cannot determine canonical ancestry: " + result.stderr.strip())
    return result.returncode == 0


def canonical_status(canonical, runner):
    result = runner(["git", "-C", canonical, "--no-optional-locks", "status", "--porcelain", "-uno"])
    if result.returncode or result.stdout.strip():
        raise Refused("canonical checkout is dirty or unreadable: " + result.stdout + result.stderr)
    return result


def canonical_fast_forward(state, canonical, runner):
    # D-183 (Ed, 2026-09-21): a clean canonical checkout behind candidate H is
    # moved here by a fast-forward-only pull whenever no night agent is loaded;
    # it is never an owner action. A dirty tree, a divergent or unreachable
    # remote, or a pull that still lacks H refuses; nothing is reset or forced.
    clean_before = canonical_status(canonical, runner)
    before = runner(["git", "-C", canonical, "rev-parse", "HEAD"])
    if before.returncode:
        raise Refused("cannot read canonical HEAD: " + before.stderr.strip())
    # Bounded and prompt-free: an unreachable remote or a credential prompt must
    # refuse, never hang the unattended loop (the stall class D-183 removes).
    try:
        pull = runner(["git", "-C", canonical, "pull", "--ff-only"], timeout=FAST_FORWARD_TIMEOUT_S,
                      env={"GIT_TERMINAL_PROMPT": "0"})
    except subprocess.TimeoutExpired as exc:
        raise Refused(f"canonical fast-forward failed: timed out after {FAST_FORWARD_TIMEOUT_S} s") from exc
    if pull.returncode:
        raise Refused("canonical fast-forward failed: " + (pull.stderr.strip() or pull.stdout.strip()))
    after = runner(["git", "-C", canonical, "rev-parse", "HEAD"])
    if after.returncode:
        raise Refused("cannot read canonical HEAD after fast-forward: " + after.stderr.strip())
    moved = dict(before=before.stdout.strip(), after=after.stdout.strip(), pull=observation_record(pull),
                 clean_before=observation_record(clean_before))
    if not contains_head(canonical, state["head"], "HEAD", runner):
        raise Refused("canonical fast-forward failed: HEAD moved " + moved["before"] + " -> " + moved["after"]
                      + " but still does not contain candidate H")
    return moved


def canonical_check(state, canonical, runner, may_fast_forward=False):
    if not contains_head(Path(state["measurement_root"]), CENSUS_FIX, state["head"], runner):
        raise Refused("candidate H does not contain the census fix " + CENSUS_FIX)
    fast_forward = None
    if not contains_head(canonical, state["head"], "HEAD", runner):
        if not may_fast_forward:
            raise Refused("canonical checkout does not contain candidate H "
                          "(fast-forward not licensed while night agents are loaded)")
        fast_forward = canonical_fast_forward(state, canonical, runner)
    result = canonical_status(canonical, runner)
    return dict(path=str(canonical), required_head=state["head"], census_fix=CENSUS_FIX,
                status=observation_record(result), fast_forward=fast_forward)


def supervisor_check(state, canonical, state_path, runner):
    # Records 19/21: every arm needs a supervisor started after the canonical
    # fast-forward; use the oldest continuously H-containing reflog entry.
    resident = json.loads(safe_path(state_path).read_text())["resident_session"]
    evidence = dict(state_path=str(state_path), resident_session=resident)
    if resident is None:
        return evidence
    pid = resident["supervisor_pid"]
    if type(pid) is not int or pid <= 0:
        raise Refused("resident supervisor PID must be a positive integer")
    result = runner(["ps", "-o", "pid=,lstart=,command=", "-p", str(pid)])
    evidence["process"] = observation_record(result)
    if result.returncode == 1 and not result.stdout.strip():
        return dict(evidence, resident="absent")
    if result.returncode != 0 or not result.stdout.strip():
        raise Refused("cannot inspect resident supervisor process")
    fields = result.stdout.split(maxsplit=6)
    if len(fields) != 7 or fields[0] != str(pid):
        raise Refused("unparseable resident supervisor observation")
    if "magistrate_watchdog.py" not in fields[6]:
        return dict(evidence, resident="PID reused")
    started = datetime.strptime(" ".join(fields[1:6]), "%a %b %d %H:%M:%S %Y").timestamp()
    if not contains_head(canonical, state["head"], "HEAD", runner):
        raise Refused("canonical checkout does not contain H for supervisor freshness")
    reflog = runner(["git", "-C", canonical, "reflog", "--date=unix", "--format=%gd %H"])
    if reflog.returncode:
        raise Refused("cannot read canonical reflog")
    arrival = None
    walked = []
    for line in reflog.stdout.splitlines():
        ref, sha = line.split()
        if not contains_head(canonical, state["head"], sha, runner):
            break
        match = re.fullmatch(r"HEAD@\{([0-9]+)\}", ref)
        if not match:
            raise Refused("unparseable canonical reflog stamp")
        arrival = int(match[1])
        walked.append(dict(ref=ref, head=sha))
    if arrival is None:
        raise Refused("no reflog entry continuously contains H")
    if started <= arrival:
        raise Refused(f"stale resident supervisor pid {pid}: started {started}, H arrived {arrival}; "
                      "this session cannot arm — commit, push and exit so the watchdog's successor arms (D-183)")
    return dict(evidence, started_epoch_s=started, head_arrived_epoch_s=arrival,
                continuous_reflog=walked)


# Night records that classify a discovered custody root. Several families can
# coexist (a refusal written mid-chain, then chain.exited); an open chain takes
# precedence over every marker, and a retained root whose plan span is still
# active by the watchdog's rule is ACTIVE too. The installer refuses re-admission
# on the same names (night_agent_install); the refusal names come from the
# driver's own run_night._refusal_paths, and the span rule from the watchdog's
# plan_span_active — both entry-checkout modules, evaluated with the entry
# checkout's constants.
TERMINAL_NIGHT_RECORDS = ("courier.sent", "result.json", "chain.exited")


def retained_roots(state, now_epoch_s=None):
    from joulewise.night_gate import NightPlan, PlanError
    from scripts.magistrate_watchdog import Storage, plan_span_active
    from scripts.run_night import _refusal_paths
    now = time.time() if now_epoch_s is None else now_epoch_s
    inventory = []
    for plan in sorted((safe_path(state["roots_under"]) / "night-custody").glob("*/night_plan.json")):
        safe_path(plan)
        if not plan.is_file():
            raise Refused("retained plan is not a regular non-symlink file: " + str(plan))
        night = plan.parent / "night"
        markers = [night / name for name in TERMINAL_NIGHT_RECORDS if safe_path(night / name).is_file()]
        markers.extend(p for p in _refusal_paths(night) if safe_path(p).is_file())
        chain_open = (safe_path(night / "chain.started").is_file()
                      and not safe_path(night / "chain.exited").is_file())
        if chain_open:
            classification, reason = "ACTIVE", "chain.started without chain.exited"
        elif not markers:
            classification, reason = "UNKNOWN", "no terminal night record"
        else:
            classification, reason = "retained", None
            try:
                parsed = NightPlan.from_mapping(json.loads(plan.read_text(encoding="utf-8")))
                if os.path.realpath(parsed.custody_root) != os.path.realpath(plan.parent):
                    classification = "UNKNOWN"
                    reason = f"plan custody_root {parsed.custody_root} is not {plan.parent}"
                elif plan_span_active(parsed, now, Storage(plan.parent)):
                    classification = "ACTIVE"
                    reason = "plan span active (scripts/magistrate_watchdog.plan_span_active)"
                else:
                    reason = ("terminal record present; plan span inactive at observation time "
                              "(scripts/magistrate_watchdog.plan_span_active)")
            except (PlanError, ValueError, TypeError, OverflowError, OSError, RecursionError) as exc:
                classification, reason = "UNKNOWN", f"plan unreadable: {type(exc).__name__}: {exc}"
        inventory.append(dict(plan=str(plan), classification=classification, reason=reason,
                              evidence=[str(p) for p in markers]))
    return dict(inventory=inventory, now_epoch_s=now, verdict="pass" if all(
        row["classification"] == "retained" for row in inventory) else "fail")


def clone_census(state, caller_pid, observation=None, *, argv_only=False):
    # Fixture observations cross as data; all imports/classification belong to H.
    code = """import json,sys
from dataclasses import asdict
from types import SimpleNamespace
from joulewise import arm_census, night_gate
from joulewise.quiet_guard_process import KernelProcessTable, KernelProcessRecord, DarwinProcessRecord
request=json.load(sys.stdin); result={'argv':list(night_gate.AGENT_CENSUS_ARGV)}
if not request['argv_only']:
    data=request['observation']; pid=request['caller_pid']
    if data is None: observation=arm_census.observe_arm_census(caller_pid=pid)
    else:
        observation=arm_census.Observation(
            KernelProcessTable(tuple(KernelProcessRecord(**r) for r in data['inventory']['rows'])),
            tuple(DarwinProcessRecord(**dict(r,argv=tuple(r['argv']))) for r in data['records']),
            tuple(data['hit_pids']),tuple(data['diagnostics']))
    verdict=arm_census.classify_arm_census(SimpleNamespace(receipt_class='DIAGNOSTIC_NO_PACK'),observation,caller_pid=pid)
    result.update(observation=asdict(observation),classification=asdict(verdict))
print(json.dumps(result))
"""
    root = Path(state["measurement_root"])
    request = dict(argv_only=argv_only, caller_pid=caller_pid,
                   observation=asdict(observation) if observation is not None else None)
    return json.loads(run([root / ".venv/bin/python", "-B", "-c", code], cwd=root, input=json.dumps(request)))


def candidate_payload_kind(state):
    """The sealed chain's payload kind, read the way the t0 gate reads it.

    The t0 gate spends its 30 s non-observer observation only when
    `probe_payload_kind` of the plan's chain says `quiet_predicate_evidence`
    (night_gate, the C5 `payload_kind` condition).  The arm check mirrors that
    scope on the same bytes: the custody `chain.zsh` the `sealed` check has
    just verified against its digest.
    """

    from joulewise import night_gate
    chain = safe_path(Path(state["custody_root"]) / "chain.zsh")
    return night_gate.probe_payload_kind(chain.read_text(encoding="utf-8"))


def machine_quiet_check(observer=None):
    """The arm check refuses on the SAME predicate as t0 (cold gate 10, Q2(i)).

    An arm that passes a check a busy machine would fail at t0 spends the
    whole span -- settle plus twelve slots -- to learn what thirty seconds at
    the check would have said.  The bar, the observation and the refusal text
    are the gate's, imported rather than restated, so the two can never drift.

    `observer` exists for tests and for a caller that already holds an
    observation; None spends the real thirty seconds.
    """

    from joulewise import night_gate
    # Any failure to observe, or an observation the gate cannot read, is a
    # REFUSAL recorded in check.json (`armable: false`), never an exception
    # that escapes `check()` before the record is written (lens S3, fix round
    # 1).  The t0 gate turns the same failures into `night_probe_error`.
    try:
        observation = night_gate.production_interval_observation() if observer is None else observer()
        offender = night_gate.non_observer_offender(observation)
    except (night_gate.ProbeError, RuntimeError, subprocess.SubprocessError, OSError,
            ValueError, TypeError, KeyError) as exc:
        raise Refused(f"non-observer interval observation failed: {type(exc).__name__}: {exc}") from exc
    interval_s = observation.get("interval_s") if isinstance(observation, dict) else None
    if type(interval_s) not in (int, float) or type(interval_s) is bool:
        raise Refused("non-observer observation carries no interval_s")
    consumers = (observation.get("metrics") or {}).get("top_consumers") or []
    if offender is not None:
        raise Refused(night_gate.non_observer_refusal_detail(offender, interval_s),
                      evidence=dict(top_consumers_at_decision=list(consumers), interval_s=interval_s,
                                    bar_busy_cores=night_gate.T0_NON_OBSERVER_SHARE_MAX))
    return dict(top_consumers_at_decision=list(consumers), interval_s=interval_s,
                bar_busy_cores=night_gate.T0_NON_OBSERVER_SHARE_MAX)


@dataclass(frozen=True)
class CorecapturedActuator:
    """All clock, log, radio and restart actions for the arm check."""

    run: Callable
    sleep: Callable[[float], None]
    now_epoch_s: Callable[[], float]


def production_corecaptured_actuator():
    return CorecapturedActuator(probe_command, time.sleep, time.time)


def corecaptured_arm_check(actuator, *, read_only=False):
    """Count spawns; on armable checks, try one bounded Wi-Fi reset if needed."""
    # A command that raises (a timeout, for example) has no exit code; its
    # exception is recorded here so check.json still shows the attempted move.
    command_errors = {}

    def command(argv, *, timeout, action):
        try:
            return actuator.run(argv, timeout=timeout)
        except Exception as exc:
            command_errors[action] = f"{type(exc).__name__}: {exc}"
            raise Refused(f"corecaptured {action} failed: {type(exc).__name__}: {exc}") from exc

    def observe(*, after=None):
        started = actuator.now_epoch_s()
        raw = command(corecaptured_loop.LOG_ARGV, timeout=30, action="log read")
        finished = actuator.now_epoch_s()
        if raw.returncode:
            raise Refused(f"corecaptured log not measured (exit {raw.returncode}): {raw.stderr.strip()}")
        try:
            return corecaptured_loop.count_spawns(
                raw.stdout, started, after_epoch_s=after, until_epoch_s=finished)
        except ValueError as exc:
            raise Refused(f"corecaptured log not measured: {exc}") from exc

    before = observe()
    result = dict(last_10m_spawns=before.count, first_spawn=before.first,
                  last_spawn=before.last, remediation="none", command_errors=command_errors)
    if read_only:
        result["remediation"] = "not_licensed"
        if before.count > corecaptured_loop.SPAWNS_MAX:
            raise Refused(
                f"night_refused_not_quiet: corecaptured: {before.count} launchd spawns "
                "in the last 10 minutes; remediation not licensed (an earlier check failed, "
                "a night is loaded, or this is a rehearsal)",
                evidence=result)
        return result
    if before.count <= corecaptured_loop.SPAWNS_MAX:
        return result

    result["remediation"] = "wifi_toggle_attempted"
    try:
        try:
            off = command(("/usr/sbin/networksetup", "-setairportpower", "en0", "off"),
                          timeout=30, action="Wi-Fi off")
            result["wifi_off_exit_code"] = off.returncode
            if not off.returncode:
                actuator.sleep(corecaptured_loop.WIFI_OFF_S)
        finally:
            # Restore radio power even when the off command or wait fails.
            on = command(("/usr/sbin/networksetup", "-setairportpower", "en0", "on"),
                         timeout=30, action="Wi-Fi on")
            result["wifi_on_exit_code"] = on.returncode
    except Exception as exc:
        raise Refused(f"night_refused_not_quiet: corecaptured: {before.count} spawns; "
                      f"Wi-Fi toggle failed: {exc}", evidence=result) from exc
    if off.returncode or on.returncode:
        raise Refused(f"night_refused_not_quiet: corecaptured: {before.count} spawns; "
                      f"Wi-Fi toggle exits off={off.returncode}, on={on.returncode}",
                      evidence=result)
    result["remediation"] = "wifi_toggled_once"
    try:
        completed = actuator.now_epoch_s()
        result["toggle_completed_epoch_s"] = completed
        actuator.sleep(corecaptured_loop.POST_TOGGLE_WAIT_S)
        after = observe(after=completed)
    except Exception as exc:
        raise Refused(f"night_refused_not_quiet: corecaptured: {before.count} spawns; "
                      f"post-toggle observation failed: {exc}", evidence=result) from exc
    result.update(post_toggle_spawns=after.count, post_toggle_first_spawn=after.first,
                  post_toggle_last_spawn=after.last)
    if after.count >= corecaptured_loop.POST_TOGGLE_SPAWNS_MIN:
        try:
            restart = command(("/usr/bin/sudo", "-n", "/usr/local/sbin/joulewise-restart-fseventsd"),
                              timeout=60, action="fseventsd restart")
        except Refused as exc:
            raise Refused(f"night_refused_not_quiet: corecaptured: {before.count} spawns before "
                          f"Wi-Fi toggle, {after.count} new spawns after toggle; "
                          f"fseventsd restart failed: {exc}", evidence=result) from exc
        result["fseventsd_restart_exit_code"] = restart.returncode
        raise Refused(
            f"night_refused_not_quiet: corecaptured: {before.count} spawns before Wi-Fi toggle, "
            f"{after.count} new spawns after toggle (first {after.first}, last {after.last}); "
            f"fseventsd restart exit {restart.returncode}", evidence=result)
    return result


def census_check(state, runner, observer, caller_pid):
    argv = clone_census(state, caller_pid, argv_only=True)["argv"]
    raw = runner(argv)
    raw_pids = set()
    if raw.returncode == 0:
        for line in raw.stdout.splitlines():
            match = re.match(r"^\s*([0-9]+)(?:\s|$)", line)
            if not match:
                raise Refused("unresolved raw census row: " + line)
            raw_pids.add(int(match[1]))
    observations = []
    for _ in range(2):
        result = clone_census(state, caller_pid, observer(caller_pid=caller_pid) if observer else None)
        observations.append(result)
        verdict, observed = result["classification"], result["observation"]
        resolved = set(verdict["own_pids"]) | set(verdict["foreign_pids"])
        resolved.update(pid for pid, _ in verdict["workloads"])
        unknown = set(observed["hit_pids"]) - {r["pid"] for r in observed["records"]}
        unresolved = raw_pids - resolved - unknown
        if not unresolved:
            break
    reason = f"unresolved raw census hit pid {min(unresolved)}" if unresolved else None
    if unknown and not reason:
        reason = "unknown census hit pid " + str(min(unknown))
    return dict(verdict="pass" if raw.returncode in (0, 1) and not (
                    verdict["foreign_pids"] or verdict["diagnostics"] or verdict["workloads"] or reason) else "fail",
                reason=reason, argv=argv, raw=observation_record(raw), observations=observations,
                classification=verdict, observation=observed, owned_helpers=verdict["own_pids"],
                instruction="Magistrate, all owned agents, MCP children and helpers must be gone before REQUEST.")


def night_agents(state, launchctl_bin):
    code = """import json,os,subprocess,sys
from pathlib import Path
from joulewise.night_agent_install import Target, LaunchctlAdapter, LABELS
directory=Path.home()/'Library/LaunchAgents'
target=Target.for_mode(directory)
listing=subprocess.run([sys.argv[1],'list'],capture_output=True,text=True)
labels=set(LABELS)
labels.update(line.split()[-1] for line in listing.stdout.splitlines()
              if line.split() and line.split()[-1].startswith(LABELS[0]))
adapter=LaunchctlAdapter(Target.for_mode(directory,labels=tuple(sorted(labels))),sys.argv[1])
jobs=[]
for label in sorted(labels):
    live=adapter.print(label)
    jobs.append(dict(label=label,liveness=live.kind.name,exit_code=live.rc,stdout=live.stdout,stderr=live.stderr))
paths={target.path(label) for label in LABELS}|{target.sidecar(label) for label in LABELS}
paths.update(directory.glob(LABELS[0]+'*.plist*'))
print(json.dumps(dict(jobs=jobs,plists=[str(p) for p in sorted(paths) if os.path.lexists(p)],
                     listing=dict(exit_code=listing.returncode,stdout=listing.stdout,stderr=listing.stderr))))
"""
    root = Path(state["measurement_root"])
    return json.loads(run([root / ".venv/bin/python", "-B", "-c", code, launchctl_bin], cwd=root))


def require_no_night_agents(evidence):
    conflicts = [j["label"] + "=" + j["liveness"] for j in evidence["jobs"] if j["liveness"] != "ABSENT"]
    conflicts.extend(evidence["plists"])
    if evidence["listing"]["exit_code"]:
        conflicts.append("night label discovery UNKNOWN")
    if conflicts:
        raise Refused("night agents already loaded or plists present: " + ", ".join(conflicts))
    return evidence


def refuse_root_attempt_records(candidate):
    """Fail closed on bench-style attempt records at the candidate root.

    The bench §1.4a procedure journals under ``$STAGE/arm-attempts/NNNNNN/``;
    the lifecycle's ONE home is ``<staging>/lifecycle/``. Records at the root
    would otherwise be silently ignored by check/publish-install (fresh eyes,
    round 2), so their presence refuses here as it does for ``prepare``.
    """
    candidate = Path(candidate)
    for name in ("attempts.json", "arm-attempts"):
        if os.path.lexists(candidate / name):
            raise Refused(f"attempt records at the candidate root: {candidate / name}; "
                          "the lifecycle home is <staging>/lifecycle/")


def retry_inventory(state, stage):
    refuse_root_attempt_records(stage)
    lifecycle = stage / "lifecycle"
    paths = sorted(set(lifecycle.glob("attempts.json")) | set(lifecycle.glob("arm-attempts/*/attempts.json")))
    records = []
    for path in paths:
        attempts = json.loads(safe_path(path).read_text())
        if not isinstance(attempts, list):
            raise Refused("malformed attempt inventory: " + str(path))
        records.extend(dict(path=str(path), cause=a.get("cause")) for a in attempts)
    # Our journal cannot establish a named retry cause from a bare nonzero rc.
    for path in sorted(lifecycle.glob("arm-attempts/*/install.json")):
        prior = json.loads(safe_path(path).read_text())
        cause = prior.get("cause")
        records.append(dict(path=str(path), cause=cause))
    # The clone at H owns retry policy, just as it owns census classification.
    code = """import json,sys
from joulewise.arm_retry import classify_abort
records=json.load(sys.stdin)
print(json.dumps([dict(record,route=classify_abort(record['cause'])) for record in records]))
"""
    root = Path(state["measurement_root"])
    records = json.loads(run([root / ".venv/bin/python", "-B", "-c", code], cwd=root, input=json.dumps(records)))
    return dict(verdict="fail" if any(r["route"] != "retry" for r in records) else "pass",
                consulted="joulewise.arm_retry.classify_abort", inventory=records,
                limitation="Routing only; full retry_allowed clearance remains lead-owned.")


def check(*, candidate, canonical=CANONICAL, supervisor_state=SUPERVISOR_STATE,
          runner=probe_command, census_observer=None, caller_pid=None, lock_verifier=verify_lock,
          launchctl_bin="launchctl", quiet_observer=None, corecaptured_actuator=None):
    with candidate_lock(candidate):
        state = candidate_state(candidate)
        record = dict(schema="joulewise.evidence_check.v1", started_epoch_s=time.time(),
                      prepare_sha256=digest(Path(candidate) / "prepare.json"), checks={}, armable=False,
                      launchctl_bin=str(launchctl_bin), fake_launchctl=str(launchctl_bin) != "launchctl")
        checks = record["checks"]

        def inspect(name, operation):
            try:
                evidence = operation()
                checks[name] = dict(verdict="pass")
                checks[name].update(evidence)
            except (Refused, OSError, ValueError, KeyError, TypeError) as exc:
                checks[name] = {**getattr(exc, "evidence", {}), "verdict": "fail", "reason": str(exc)}
            return checks[name]["verdict"] == "pass"

        def seal():
            plan = sealed_state(state, lock_verifier=lock_verifier)
            s = clone_schedule(state, plan)
            if time.time() >= s["install_close_epoch_s"]:
                raise Refused("exclusive install close has passed")
            return dict(digests=state["digests"], schedule=s)

        if inspect("sealed", seal):
            nothing_loaded = inspect("night_agents", lambda: require_no_night_agents(night_agents(state, launchctl_bin)))
            inspect("canonical", lambda: canonical_check(state, safe_path(canonical), runner,
                                                         may_fast_forward=nothing_loaded))
            inspect("supervisor", lambda: supervisor_check(state, safe_path(canonical), supervisor_state, runner))
            courier = shutil.which("claude")
            checks["courier"] = dict(verdict="pass" if courier else "fail", path=courier,
                                      reason="courier on PATH" if courier else "courier unavailable")
            inspect("retained_roots", lambda: retained_roots(state))
            inspect("census", lambda: census_check(state, runner, census_observer,
                                                   os.getpid() if caller_pid is None else caller_pid))
            inspect("retry", lambda: retry_inventory(state, Path(candidate)))
            # Scoped like the t0 gate (F12, fix round 1): the predicate is spent
            # only on a quiet_predicate_evidence chain.  Any other chain records
            # the decision as `skipped`, so check.json still shows it; a chain
            # whose kind cannot be read fails closed.
            try:
                payload_kind = candidate_payload_kind(state)
            except (Refused, OSError, ValueError) as exc:
                checks["machine_quiet"] = dict(
                    verdict="fail", reason=f"payload kind unreadable: {type(exc).__name__}: {exc}")
            else:
                if payload_kind == KIND:
                    actuator = corecaptured_actuator or production_corecaptured_actuator()
                    # A rehearsal decides "nothing loaded" with a fixture
                    # launchctl, so it never licenses the production radio or
                    # restart (counter-review S-1); an injected actuator is a fake.
                    rehearsal_on_real_machine = (record["fake_launchctl"]
                                                 and corecaptured_actuator is None)
                    if (nothing_loaded and not rehearsal_on_real_machine
                            and all(row["verdict"] == "pass" for row in checks.values())):
                        inspect("corecaptured", lambda: corecaptured_arm_check(actuator))
                    else:
                        # A loaded night or any other prior failure removes
                        # authority to touch the radio or restart fseventsd.
                        inspect("corecaptured", lambda: corecaptured_arm_check(actuator, read_only=True))
                    inspect("machine_quiet", lambda: machine_quiet_check(quiet_observer))
                else:
                    checks["corecaptured"] = dict(verdict="skipped", reason="not an evidence night",
                                                   payload_kind=payload_kind)
                    checks["machine_quiet"] = dict(verdict="skipped", reason="not an evidence night",
                                                   payload_kind=payload_kind)
        # One predicate decides both the verdict and the refusal text below,
        # so the text names exactly the checks that failed: a `skipped`
        # machine_quiet row is not a failure and is never listed as one
        # (fix round 2, delta re-audit N-b).
        failed = [name for name, c in checks.items()
                  if not (c["verdict"] == "pass" or (name in ("machine_quiet", "corecaptured")
                                                   and c["verdict"] == "skipped"))]
        passed = not failed
        record["armable"] = passed and not record["fake_launchctl"]
        record["rehearsal_ready"] = passed and record["fake_launchctl"]
        record["finished_epoch_s"] = time.time()
        path = lifecycle_dir(candidate) / "check.json"
        saved_json(path, record)
        if not passed:
            # These three name the machine, not the paperwork: their reason
            # text is the whole finding, and burying it behind "pre-arm checks
            # failed" would make the operator open check.json to learn which
            # process held the machine (cold gate 10, 2026-09-23, Q2(i)).
            for name in ("night_agents", "census", "corecaptured", "machine_quiet"):
                row = checks.get(name, {})
                if row.get("verdict") == "fail" and row.get("reason"):
                    raise Refused(row["reason"])
            stale = checks.get("supervisor", {}).get("reason", "")
            if stale.startswith("stale resident supervisor"):
                raise Refused(stale)
            raise Refused("pre-arm checks failed: " + ", ".join(failed) + "; see " + str(path))
        return record


def installer_call(state, flag=None, *, launchctl_bin="launchctl", runner=probe_command):
    root = Path(state["measurement_root"])
    argv = [root / "scripts/install_night_agent.sh", "--plan", Path(state["custody_root"]) / "night_plan.json"]
    if flag == "--uninstall":
        argv.append(flag)  # The shell intentionally uses system Python for cleanup.
    else:
        argv += ["--python", root / ".venv/bin/python"]
        if flag:
            argv.append(flag)
    argv += ["--launchctl-bin", launchctl_bin]
    started = time.time()
    result = runner(argv, cwd=root)
    return dict(argv=list(map(str, argv)), started_epoch_s=started, finished_epoch_s=time.time(),
                **observation_record(result))


def verify_state(state, *, launchctl_bin="launchctl", lock_verifier=verify_lock):
    plan = sealed_state(state, published=True, lock_verifier=lock_verifier)
    s = clone_schedule(state, plan)
    root = Path(state["measurement_root"])
    # Ruling 30a: typed liveness plus installed plist fields and exact rendered
    # bytes retain step-5 evidence without parsing launchctl calendar text.
    code = """import hashlib,json,sys,plistlib
from pathlib import Path
from joulewise.night_agent_install import Target, LaunchctlAdapter, Kind, LABELS
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
p=NightPlan.from_mapping(json.load(open(sys.argv[1]))); expected=schedule(p)
target=Target.for_mode(Path.home()/'Library/LaunchAgents')
adapter=LaunchctlAdapter(target,sys.argv[2]); results=[]
for label,key in zip(LABELS,('night_calendar','deadman_calendar')):
    live=adapter.print(label)
    if live.kind is not Kind.LOADED: raise ValueError(label+' is '+live.kind.name+': '+live.stderr)
    path=target.path(label)
    if path.is_symlink(): raise ValueError('symlink plist: '+str(path))
    installed_bytes=path.read_bytes()
    render_path=Path(sys.argv[3])/(label+'.plist')
    rendered_bytes=render_path.read_bytes()
    installed=plistlib.loads(installed_bytes)
    rendered=plistlib.loads(rendered_bytes)
    if installed['Label'] != label: raise ValueError('plist Label differs: '+label)
    if installed['StartCalendarInterval'] != expected[key]: raise ValueError('calendar differs: '+label)
    if installed['ProgramArguments'] != rendered['ProgramArguments']: raise ValueError('arguments differ: '+label)
    if str(Path(sys.argv[1])) not in installed['ProgramArguments']: raise ValueError('plan path differs: '+label)
    if installed['ProgramArguments'][0] != sys.argv[4]: raise ValueError('interpreter differs: '+label)
    if installed['WorkingDirectory'] != p.measurement_root: raise ValueError('working directory differs: '+label)
    if installed['RunAtLoad'] is not False: raise ValueError('RunAtLoad differs: '+label)
    if installed_bytes != rendered_bytes: raise ValueError('installed plist bytes differ from render: '+label)
    results.append(dict(label=label,plist=str(path),calendar=installed['StartCalendarInterval'],
                        liveness=live.kind.name,rendered_plist=str(render_path),
                        plist_sha256=hashlib.sha256(installed_bytes).hexdigest(),
                        render_sha256=hashlib.sha256(rendered_bytes).hexdigest(),
                        exit_code=live.rc,stdout=live.stdout,stderr=live.stderr))
print(json.dumps(results))
"""
    jobs = json.loads(run([root / ".venv/bin/python", "-B", "-c", code, plan,
                           launchctl_bin, Path(state["staging"]) / "render", root / ".venv/bin/python"], cwd=root))
    return dict(schema="joulewise.evidence_verify.v1", verified_epoch_s=time.time(), jobs=jobs,
                launchctl_bin=str(launchctl_bin), fake_launchctl=str(launchctl_bin) != "launchctl",
                baseline=baseline_drift(state),
                schedule=s, request_epoch_s=s["boundaries"]["REQUEST / exit BEFORE"],
                instruction="Exit every owned agent and helper strictly before REQUEST; this command does not terminate them.")


def verify(*, candidate, launchctl_bin="launchctl", lock_verifier=verify_lock):
    with candidate_lock(candidate):
        return verify_state(candidate_state(candidate), launchctl_bin=launchctl_bin, lock_verifier=lock_verifier)


def require_fresh_record(state, name, clearance, *, command="publish-install"):
    stage = Path(state["staging"])
    path = safe_path(stage / "lifecycle" / (name + ".json"))
    if not path.is_file():
        raise Refused(f"{name}.json is required before {command}")
    try:
        record = json.loads(path.read_text())
        if (not isinstance(record, dict)
                or record.get("schema") != f"joulewise.evidence_{name}.v1"
                or record.get(clearance) is not True
                or record.get("prepare_sha256") != digest(stage / "prepare.json")):
            raise Refused(f"{name}.json is not {clearance} or does not bind prepare.json")
        now = time.time()
        age = now - record.get("finished_epoch_s", 0)
        file_age = now - path.stat().st_mtime
        if not math.isfinite(age) or not 0 <= age <= 3600 or not 0 <= file_age <= 3600:
            raise Refused(f"{name}.json is older than 60 minutes or future-dated")
        sealed = [stage / "prepare.json", *(Path(p) for p in state["digests"])]
        if any(path.stat().st_mtime_ns <= p.stat().st_mtime_ns for p in sealed):
            raise Refused(f"{name}.json is not newer than every sealed artefact")
    except (OSError, ValueError, TypeError) as exc:
        raise Refused(f"malformed or unreadable {name}.json: {exc}") from exc
    return record


def require_fresh_check(state, launchctl_bin, *, command="publish-install"):
    fake = str(launchctl_bin) != "launchctl"
    checked = require_fresh_record(state, "check", "rehearsal_ready" if fake else "armable", command=command)
    if (checked.get("launchctl_bin") != str(launchctl_bin)
            or checked.get("fake_launchctl") is not fake):
        raise Refused("check.json is not armable with this launchctl executable")
    return checked


def notice(*, candidate, launchctl_bin="launchctl", lock_verifier=verify_lock):
    with candidate_lock(candidate):
        state = candidate_state(candidate)
        plan = sealed_state(state, lock_verifier=lock_verifier)
        checked = require_fresh_check(state, launchctl_bin, command="notice")
        state["schedule"] = clone_schedule(state, plan)
        if time.time() >= state["schedule"]["install_close_epoch_s"]:
            raise Refused("exclusive install close has passed")
        state["bindings"] = sealed_candidate(Path(state["measurement_root"]), plan)
        body = render_notice(state, checked=checked,
                             check_sha256=digest(Path(candidate) / "lifecycle/check.json"))
        atomic_bytes(lifecycle_dir(candidate) / "notice.txt", body.encode())
        print("To: claude2.glaring610@passmail.net")
        print("Subject: " + notice_subject(state))
        print("\n" + body, end="")
        return body


def veto(*, candidate, runner=probe_command, magistrate=MAGISTRATE):
    """Observe mechanical veto channels; mail remains the magistrate's job."""
    with candidate_lock(candidate):
        state = candidate_state(candidate)
        lifecycle = lifecycle_dir(candidate)
        return observe_veto(state, lifecycle / "veto.json", runner=runner, magistrate=magistrate)


def observe_veto(state, output, *, runner, magistrate):
    """One observation path for the earlier veto and the publication boundary."""
    lifecycle = lifecycle_dir(state["staging"])
    record = dict(schema="joulewise.evidence_veto.v1", started_epoch_s=time.time(),
                  prepare_sha256=digest(Path(state["staging"]) / "prepare.json"), channels={}, clear=False,
                  production=runner is probe_command and Path(magistrate) == Path(MAGISTRATE),
                  non_owner_directives=[])
    channels = record["channels"]
    directives = channels["directives"] = dict(argv=list(DIRECTIVES_ARGV), clear=False)
    reasons = []
    try:
        observed = runner(list(DIRECTIVES_ARGV), timeout=60)
        directives.update(observation_record(observed))
        if observed.returncode:
            raise ValueError(f"gh exited {observed.returncode}")
        issues = json.loads(observed.stdout)
        if not isinstance(issues, list) or any(
                not isinstance(issue, dict) or type(issue.get("number")) is not int
                or issue["number"] <= 0 or not isinstance(issue.get("title"), str)
                or not isinstance(issue.get("body"), str)
                or not isinstance(issue.get("author"), dict)
                or not isinstance(issue["author"].get("login"), str)
                or not issue["author"]["login"] for issue in issues):
            raise ValueError("invalid directive issue inventory")
        owner_issues = [issue for issue in issues if issue["author"]["login"] == "mpmdw"]
        record["non_owner_directives"] = [issue for issue in issues if issue["author"]["login"] != "mpmdw"]
        directives.update(issues=issues, clear=not owner_issues)
        reasons.extend(f"open owner directive #{issue['number']} — the lead reads it before publication"
                       for issue in owner_issues)
    except subprocess.TimeoutExpired:
        directives["error"] = "timeout"
        reasons.append("cannot read directives: timeout")
    except (Refused, OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        directives["error"] = str(exc)
        reasons.append("cannot read directives: " + str(exc))
    root = record["magistrate_root"] = dict(path=str(magistrate), clear=False)
    try:
        if not safe_path(magistrate).is_dir():
            raise Refused("missing or non-directory root")
        root["clear"] = True
    except (Refused, OSError) as exc:
        root["error"] = str(exc)
        reasons.append("cannot read the magistrate root: " + str(exc))
    # Observe every channel even when another has already refused. lstat
    # counts dangling symlinks and directories as present; never run data.
    for name, path in (("standdown", Path(magistrate) / "standdown.request"),
                       ("STOP", Path(magistrate) / "STOP"), ("NO", lifecycle / "NO")):
        evidence = channels[name] = dict(path=str(path), clear=False)
        try:
            safe_path(path.parent)
            try:
                st = path.lstat()
            except FileNotFoundError:
                evidence.update(present=False, clear=True)
            else:
                evidence.update(present=True, size=st.st_size, mtime_ns=st.st_mtime_ns,
                                mode=st.st_mode)
                reasons.append(f"veto present: {path}")
        except (Refused, OSError) as exc:
            evidence["error"] = str(exc)
            reasons.append(f"cannot read veto channel {path}: {exc}")
    record.update(clear=root["clear"] and all(c["clear"] for c in channels.values()), reasons=reasons,
                  finished_epoch_s=time.time())
    saved_json(output, record)
    if not record["clear"]:
        raise Refused("; ".join(reasons))
    return record


def custody_inventory(state):
    root = safe_path(state["custody_root"])
    files = {}

    def failed(exc):
        raise exc

    # os.walk's default ignores scan errors; an incomplete baseline must fail.
    for directory, dirs, names in os.walk(root, onerror=failed):
        for name in dirs + names:
            safe_path(Path(directory) / name)
        for name in names:
            path = Path(directory) / name
            if not path.is_file():
                raise Refused(f"nonregular custody file: {path}")
            st = path.stat()
            files[path.relative_to(root).as_posix()] = dict(size=st.st_size, mtime_ns=st.st_mtime_ns)
    return files


def baseline_drift(state):
    attempts = safe_path(Path(state["staging"]) / "lifecycle/arm-attempts")
    newest = max((p for p in attempts.iterdir() if p.name.isdecimal() and int(p.name) > 0),
                 key=lambda p: int(p.name), default=None) if attempts.exists() else None
    if newest is None:
        return None
    path = safe_path(newest / "baseline.json")
    if not path.exists():
        return None
    try:
        baseline = json.loads(path.read_text())
        if (baseline["schema"] != "joulewise.evidence_baseline.v1"
                or baseline["custody_root"] != state["custody_root"]
                or not isinstance(baseline["files"], dict)):
            raise ValueError("invalid baseline identity")
        before = baseline["files"]
        after = custody_inventory(state)
        added, removed = sorted(after.keys() - before.keys()), sorted(before.keys() - after.keys())
        changed = {name: dict(before=before[name], after=after[name]) for name in sorted(before.keys() & after.keys())
                   if before[name] != after[name]}
        return dict(path=str(path), drift=bool(added or removed or changed),
                    added=added, removed=removed, changed=changed)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise Refused(f"cannot read custody baseline: {exc}") from exc


def notice_unused(state, notice_id):
    stage = Path(state["staging"])
    prefix = "qpe01-pilot-n1-" + datetime.fromtimestamp(state["t0"]).strftime("%Y%m%d")
    candidates = set(stage.parent.glob(prefix + "*")) | {stage}
    for candidate in sorted(candidates):
        safe_path(candidate)
        refuse_root_attempt_records(candidate)
        base = candidate / "lifecycle"
        paths = set(base.glob("arm-attempts/*/install.json")) | set(base.glob("arm-attempts/*/attempts.json"))
        paths.update(base.glob("attempts.json"))
        for path in sorted(paths):
            try:
                value = json.loads(safe_path(path).read_text())
                records = value if isinstance(value, list) else [value]
                if any(not isinstance(r, dict) for r in records):
                    raise ValueError("invalid attempt")
            except (OSError, ValueError, TypeError) as exc:
                raise Refused("malformed attempt journal: " + str(path)) from exc
            if any(r.get("notice_accepted") == notice_id for r in records):
                raise Refused("notice id already used by attempt " + str(path))


def publish_install(*, candidate, notice_accepted=None, launchctl_bin="launchctl",
                    runner=probe_command, magistrate=MAGISTRATE, lock_verifier=verify_lock):
    with candidate_lock(candidate):
        state = candidate_state(candidate)
        stage = Path(state["staging"])
        plan = sealed_state(state, lock_verifier=lock_verifier)
        lifecycle = lifecycle_dir(stage)
        require_fresh_check(state, launchctl_bin)
        fake = str(launchctl_bin) != "launchctl"
        if not isinstance(notice_accepted, str) or not notice_accepted.strip():
            raise Refused("notice acceptance message id is required")
        notice_unused(state, notice_accepted)
        veto_record = require_fresh_record(state, "veto", "clear")
        if not fake and veto_record.get("production") is not True:
            raise Refused("rehearsal veto evidence cannot authorize a real arm")
        notice_path = safe_path(lifecycle / "notice.txt")
        if not notice_path.is_file():
            raise Refused("notice.txt is required before publish-install")
        notice_inputs = [stage / "prepare.json", lifecycle / "check.json",
                         *(Path(p) for p in state["digests"])]
        if any(notice_path.stat().st_mtime_ns <= p.stat().st_mtime_ns for p in notice_inputs):
            raise Refused("notice.txt is not newer than every sealed artefact and check.json")
        s = clone_schedule(state, plan)
        if time.time() >= s["install_close_epoch_s"]:
            raise Refused("exclusive install close has passed")
        target = safe_path(Path(state["custody_root"]) / "night_plan.json")
        absent(target)
        if plan.stat().st_dev != target.parent.stat().st_dev:
            raise Refused("staging and custody are not on one filesystem (atomic publication)")
        # No prior evidence is overwritten; install.json at staging is the
        # current view of the immutable per-attempt terminal journal.
        attempts = safe_path(lifecycle / "arm-attempts")
        attempts.mkdir(exist_ok=True)
        ordinals = [int(p.name) for p in attempts.iterdir() if p.name.isdecimal()]
        attempt = attempts / f"{max(ordinals, default=0) + 1:06d}"
        attempt.mkdir()
        raw = plan.read_bytes()
        atomic_bytes(attempt / "plan.json", raw)
        record = dict(schema="joulewise.evidence_install.v1", started_epoch_s=time.time(),
                      plan_sha256=hashlib.sha256(raw).hexdigest(), published_plan=str(target),
                      notice_accepted=notice_accepted, notice_verified=False, commands=[],
                      attempt_path=str(attempt), outcome="not_published",
                      phase="prepared", launchctl_bin=str(launchctl_bin), fake_launchctl=fake,
                      plist_paths=[str(Path.home() / "Library/LaunchAgents" / (label + ".plist"))
                                   for label in ("com.joulewise.night", "com.joulewise.night.deadman")],
                      probe_receipt_sha256=None)

        def save():
            saved_json(attempt / "install.json", record)
            saved_json(lifecycle / "install.json", record)

        def invoke(flag):
            record["phase"] = "probing" if flag else "installing"
            save()
            observed = installer_call(state, flag, launchctl_bin=launchctl_bin, runner=runner)
            record["commands"].append(observed)
            if observed["exit_code"]:
                for line in observed["stderr"].splitlines():
                    match = re.match(r"^([a-z][a-z0-9_]+):", line)
                    if match:
                        record["cause"] = match[1]
                        break
            record["phase"] = "probe_finished" if flag else "install_finished"
            save()
            if observed["exit_code"]:
                raise Refused(f"installer {flag or 'install'} failed ({observed['exit_code']}): {observed['stderr']}")

        save()
        published = False
        publication_started = False
        try:
            absent(target)
            record["pre_publication"] = night_agents(state, launchctl_bin)
            save()
            require_no_night_agents(record["pre_publication"])
            record["phase"] = "observing-veto"
            save()
            observed_veto = observe_veto(state, attempt / "veto-at-publication.json",
                                         runner=runner, magistrate=magistrate)
            if not fake and observed_veto["production"] is not True:
                raise Refused("rehearsal veto evidence cannot authorize a real arm")
            record["phase"] = "publishing"
            save()  # Durable intent precedes the rename, including lost acknowledgement.
            publication_started = True
            os.replace(plan, target)
            published = True
            record.update(published_epoch_s=time.time(), outcome="published", phase="published")
            save()
            if target.read_bytes() != raw:
                raise Refused("published plan bytes differ from staged snapshot")
            invoke("--launchd-probe")
            # The real install validates freshness, identity and cleanup again.
            receipt = safe_path(target.parent / "night_probe_receipt.json")
            record["probe_receipt_sha256"] = digest(receipt)
            invoke(None)
            record["phase"] = "verifying"
            save()
            record["verification"] = verify_state(state, launchctl_bin=launchctl_bin, lock_verifier=lock_verifier)
            baseline_path = attempt / "baseline.json"
            saved_json(baseline_path, dict(schema="joulewise.evidence_baseline.v1",
                custody_root=state["custody_root"], recorded_epoch_s=time.time(),
                files=custody_inventory(state)))
            record["baseline_path"] = str(baseline_path)
            record.update(outcome="rehearsal_installed" if fake else "installed", phase="complete",
                          installed=not fake, finished_epoch_s=time.time())
            save()
            return record
        except BaseException as exc:
            record["failure"] = f"{type(exc).__name__}: {exc}"
            # A signal/exception can arrive after replace has moved the file
            # but before the next Python assignment acknowledges publication.
            published = published or (publication_started and not os.path.lexists(plan))
            if published:
                try:
                    # Transaction rc 2/3 means refused/rolled back; teardown
                    # retention overrides these with rc 1/4. A probe never
                    # installs the night pair. Only rc 0 transfers ownership.
                    installs = [c for c in record["commands"] if "--launchd-probe" not in c["argv"]]
                    installed = installs and installs[-1]["exit_code"] == 0
                    uncertain = (record["phase"] == "installing" or
                                 (installs and installs[-1]["exit_code"] not in (0, 2, 3)))
                    record["phase"] = "recovering"
                    save()
                    if installed:
                        cleanup = installer_call(state, "--uninstall", launchctl_bin=launchctl_bin, runner=runner)
                        record["commands"].append(cleanup)
                        save()
                        if cleanup["exit_code"] != 0:
                            raise Refused(f"uninstall failed ({cleanup['exit_code']})")
                    elif uncertain:
                        raise Refused("installer ownership/rollback unknown; jobs and plists preserved")
                    else:
                        record["recovery"] = "foreign_jobs_preserved"
                        record["retained_state"] = record["pre_publication"]
                    safe_path(target)
                    if not target.is_file() or target.read_bytes() != raw:
                        raise Refused("published plan bytes changed or missing")
                    absent(plan)
                    os.replace(target, plan)
                    record.update(outcome="restored_unpublished", phase="complete")
                except BaseException as recovery:
                    record.update(outcome="retained", recovery_failure=f"{type(recovery).__name__}: {recovery}")
                    record["finished_epoch_s"] = time.time()
                    save()
                    raise Refused(f"{exc}; recovery stopped: {recovery}; retained state: {target}, {attempt}") from exc
            record["finished_epoch_s"] = time.time()
            save()
            raise


def uninstall(*, candidate, launchctl_bin="launchctl", runner=probe_command):
    with candidate_lock(candidate):
        state = candidate_state(candidate)
        # Cleanup deliberately does not validate plan bytes, age, lock or HEAD;
        # the existing uninstall accepts malformed/retired published plans.
        path = safe_path(Path(candidate) / "lifecycle/uninstall.json")
        try:
            history = json.loads(path.read_text()) if os.path.lexists(path) else []
            if not isinstance(history, list) or any(not isinstance(r, dict) or
                    type(r.get("exit_code")) is not int or not isinstance(r.get("argv"), list) for r in history):
                raise ValueError("invalid records")
        except (OSError, ValueError, TypeError) as exc:
            raise Refused("malformed uninstall journal") from exc
        lifecycle_dir(candidate)
        record = installer_call(state, "--uninstall", launchctl_bin=launchctl_bin, runner=runner)
        history.append(record)
        saved_json(path, history)
        if record["exit_code"] != 0:
            raise Refused(f"uninstall failed ({record['exit_code']}); retained state: {state['custody_root']}")
        return record


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Refused(message)


def main(argv=None):
    parser = Parser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    prep = sub.add_parser("prepare")
    prep.add_argument("--kind", required=True)
    prep.add_argument("--t0", required=True)
    prep.add_argument("--head")
    prep.add_argument("--remote", default=REMOTE)
    prep.add_argument("--roots-under", default="/Users/edr")
    prep.add_argument("--staging-under", default="/Users/edr/night-plan-staging")
    for command in ("check", "notice", "veto", "publish-install", "verify", "uninstall"):
        action = sub.add_parser(command)
        action.add_argument("--candidate", required=True)
        if command != "veto":
            action.add_argument("--launchctl-bin", default="launchctl")
        if command == "publish-install":
            action.add_argument("--notice-accepted")
    try:
        args = vars(parser.parse_args(argv))
        command = args.pop("command")
        operation = {"prepare": prepare, "check": check, "publish-install": publish_install,
                     "verify": verify, "uninstall": uninstall, "notice": notice, "veto": veto}[command]
        result = operation(**args)
        if command != "notice":
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Refused as exc:
        print("REFUSED: " + " ".join(str(exc).splitlines()), file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
