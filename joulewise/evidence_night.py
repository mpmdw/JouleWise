"""Prepare a sealed evidence candidate; stop before notice and publication."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

KIND = "quiet_predicate_evidence"
REMOTE = "https://github.com/mpmdw/JouleWise"
SCHEMA = "joulewise.evidence_prepare.v1"
STEPS = ("clone", "venv", "plan", "wrapper", "render", "complete")


class Refused(Exception):
    """A preparation cannot safely advance."""


def run(argv, *, cwd=None):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                            text=True, capture_output=True, check=False)
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
    if run(["git", "-C", root, "status", "--porcelain=v1", "--untracked-files=all"]):
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
    temporary = path.with_suffix(".tmp")
    absent(temporary)
    with temporary.open("x") as stream:
        json.dump(state, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


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
    registration=Path(p.registration_path)
    if not registration.is_absolute(): registration=Path(p.measurement_root)/registration
    raw=registration.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    if not (sha in night_gate.RULED_REGISTRATIONS and night_gate.RULED_REGISTRATIONS[sha]['binds_chain']): raise ValueError(check)
    if not (json.loads(raw)['chain_source_sha256']==source): raise ValueError(check)
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


def notice(state):
    s = state["schedule"]
    lines = ["DRAFT — NOT SENT; prerequisites and veto observations are not yet recorded.",
             "To: claude2.glaring610@passmail.net",
             f'Subject: NIGHT NOTICE — {state["plan_id"]} (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt {state["attempt"]}',
             "", "Ed,", "Launch needs no action from you unless you reply NO. Your NO overrides.",
             f'Arm attempt {state["attempt"]}; prior candidates for this date: {", ".join(state["prior_candidates"]) or "none"}.',
             "This first idle-variance evidence night sizes a later experiment; it activates no new quietness cutoff.",
             "After 600 seconds settling, twelve 600-second idle envelopes use 480-second interiors after 60-second offsets.",
             "Power sampling is every 100 ms, with census, AC-power, thermal, timing and cleanup observations and a busy-cores journal.",
             "Busy cores remain a descriptive covariate. The 7,800-second program fits inside 9,000 seconds; no top-up or automatic repeat.",
             "Partial observations and refusals are kept. No model, load generator, calibration-ledger session or measurement pack runs.",
             "The scheduler supervises the program and the courier emails the result. Evidence remains PROVISIONAL.",
             "During the night exactly one read-only git show verifies chain bytes in the clone; no commit, push, checkout or fetch (87a F2).",
             "After delivery the lead sizes block two or records 'no cutoff qualifies'.",
             f'plan_id: {state["plan_id"]}', f'repo_head = measurement_head = H: {state["head"]}',
             f'clone: {state["measurement_root"]}', f'custody: {state["custody_root"]}',
             f'runs: {state["custody_root"]}/runs', f'staged plan: {state["plan_path"]}',
             f'authored_epoch_s: {json.loads(Path(state["plan_path"]).read_text())["authored_epoch_s"]}']
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
            run(["python3.13", "--version"])
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
s=json.loads(sys.argv[1]); c=s['custody_root']
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
            result = json.loads(run([python, "-B", "-c", code, json.dumps(state)], cwd=root))
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
            state["notice_draft"] = notice(state)
            state["frozen_triple"] = [state["plan_id"], str(root), resolved_head]
            checkpoint(state_path, state, "complete")
        if time.time() >= state["schedule"]["install_close_epoch_s"]:
            raise Refused("exclusive install close has passed")
        return state


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
    try:
        args = vars(parser.parse_args(argv))
        args.pop("command")
        print(json.dumps(prepare(**args), indent=2, sort_keys=True))
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
