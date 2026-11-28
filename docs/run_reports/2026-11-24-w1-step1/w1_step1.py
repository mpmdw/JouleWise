#!/usr/bin/env python3.13
"""W1 promotion runbook step 1: complete the policy, bind R0, commit w1_plan.json, regenerate, check.

Trial PR #958 report §9 step 1 (lead L8; RL-207, RL-210). It is mechanical once PR #824 is admitted and
the authorized R0 record's digest is named. It runs on a clean checkout of the W1 integration branch
(--repo). It prints digests, key names and pass/fail lines only, never a value from inputs.json,
r1_slots.json or the planning release. Run it without GIT_DIR or GIT_WORK_TREE exported (F-10).

    python3.13 -B w1_step1.py --repo "$J" --pin <commit> --component-heads heads.json \
        --r0-record-sha256 <64 hex> --member-seconds member_s.json --plan-id <id> \
        --trace --reader-census /path/to/run_census.py [--r0-note "<one line>"] [--out DIR]

--member-seconds is the lead's file of R1's member_s for the 18 W1 members: a JSON list of 18 numbers
in ordinal order, or an object {"1": s, ..., "18": s}. The script never chooses or derives one.

What it does, in order (any failure stops it with exit 2 and changes nothing further):
  0. Preconditions: no Git directory, worktree or index override, a clean tree, all named component
     heads in HEAD, and the ten R1 source blobs equal to the pin using the pin's source inventory.
  1. RL-207 completion of inputs.R1.thermal_policy: heavy true, per_turn true, sensors.fan_keys from the
     frozen configs/align/v4/r1_runtime.json, and sensors.r0_sha256 = R0.record_sha256 = the given digest.
     It proves the only changed key paths are those five and that DEC2's five leaves (R1.B_D, R1.T_dead,
     thermal_policy.g0_cap_s, .contrast_g0_cap_s, .contrast_fit) are byte-unchanged (digest compare).
     If the digest is not the frozen config's sensors.r0_sha256, --r0-note is required (RL-207's missing
     fact: the lead records in one line which record each names and why).
  2. Kit regeneration (scripts/align_v4_kit.py) so collection_plan.json carries the bound configs.
  3. w1_plan.json: the validator's own template, filled with inputs' B_D, I_D, T_dead, effort and
     thermal_policy, r1_slots' max_r1_tail_s and the lead's member_s; arithmetic as the validator
     defines it; scripts/validate_align_v4_w1_plan.py must print VALID.
  4. Regenerate the kit (derives sizing_b5.json) and the template bindings until nothing changes.
  5. scripts/align_v4_kit.py --check must pass every gate before registration. At step 1 its first stop
     must be exactly "registration_receipt is pending or malformed" (require_registration reads the
     receipt, then u3_bar.json, battery_window_policy.json and wp19_receipt.json, which the later
     runbook steps supply); exit 0 comes only after the signed receipt. The refusal census must report
     no difference.
  6. Build the dynamic closure trace (--trace, about 22 min) and install it only if every scenario
     is ok. Run the reader census against a Git tree object made from the generated working tree.
     Both checks are required for READY_FOR_LEAD_REVIEW.
  7. A digest table of every changed path (blob id and sha256) for the receipt and RL-211's list, and
     step1-receipt.json in --out. Nothing is committed or pushed: the lead reviews `git status` and commits.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

PIN_SOURCE = "joulewise/align/apple/v4_registration.py"
INPUTS = "configs/campaigns/align_v4/registration/inputs.json"
R1_SLOTS = "configs/campaigns/align_v4/registration/r1_slots.json"
W1_PLAN = "configs/campaigns/align_v4/registration/w1_plan.json"
RUNTIME = "configs/align/v4/r1_runtime.json"
TRACE = "docs/align/v4/dynamic_closure_trace.json"
RECEIPT_STOP = "registration_receipt is pending or malformed"
EVIDENCE = ("registration_receipt_stop", "refusal_census", "trace", "reader_census")
ADDED = (("R0", "record_sha256"), ("R1", "thermal_policy", "heavy"), ("R1", "thermal_policy", "per_turn"),
         ("R1", "thermal_policy", "sensors", "fan_keys"), ("R1", "thermal_policy", "sensors", "r0_sha256"))
DEC2 = (("R1", "B_D"), ("R1", "T_dead"), ("R1", "thermal_policy", "g0_cap_s"),
        ("R1", "thermal_policy", "contrast_g0_cap_s"), ("R1", "thermal_policy", "contrast_fit"))


class Stop(Exception):
    def __init__(self, code, *fields, exception="Stop", message_sha256=None):
        super().__init__(code)
        self.diagnostic = {"code": code, "exception": exception, "fields": list(fields)}
        if message_sha256 is not None:
            self.diagnostic["message_sha256"] = message_sha256


def say(text):
    print(text, flush=True)


def child_refusal(code, done, *fields):
    # The kit CLI formats this specific ValueError itself. Construct field names
    # from constants and never copy captures, argv, or any child output to the receipt.
    if re.fullmatch(r"align_v4_kit: inputs\.R1\.I_D .+ differs from r1_slots\.slots\.I_D .+\n?",
                    done.stderr):
        return Stop(code, *fields, "inputs.R1.I_D", "r1_slots.slots.I_D", exception="ValueError")
    raw = (done.stderr + "\0" + done.stdout).encode("utf-8", errors="surrogateescape")
    return Stop(code, *fields, exception="CalledProcessError", message_sha256=hashlib.sha256(raw).hexdigest())


def run(repo, *argv, check=True, env=None):
    env = {**(os.environ if env is None else env), "GIT_NO_REPLACE_OBJECTS": "1", "GIT_OPTIONAL_LOCKS": "0"}
    done = subprocess.run(argv, cwd=repo, capture_output=True, encoding="utf-8",
                          errors="surrogateescape", env=env)
    if check and done.returncode != 0:
        raise child_refusal("SUBPROCESS_FAILED", done)
    return done


def git(repo, *argv):
    return run(repo, "git", *argv).stdout.strip()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def leaf(doc, path):
    for key in path:
        if not isinstance(doc, dict) or key not in doc:
            return ("<absent>",)
        doc = doc[key]
    return doc


def flat(doc, prefix=()):
    if isinstance(doc, dict) and doc:
        for key, value in doc.items():
            yield from flat(value, prefix + (key,))
    else:
        yield prefix, canonical(doc)


def write_json(path, doc):
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dirty_paths(repo):
    out = run(repo, "git", "status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all").stdout
    return [entry[3:] for entry in out.split("\0") if entry]


def tree_state(repo):
    state = {}
    for path in dirty_paths(repo):
        file = repo / path
        state[path] = hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else "<deleted>"
    return state


def ten_blobs(repo, pin):
    source = git(repo, "show", f"{pin}:{PIN_SOURCE}")
    tree = ast.parse(source)
    specs = [node.value for node in tree.body if isinstance(node, ast.Assign)
             and any(getattr(t, "id", None) == "R1_EXECUTED_SOURCES" for t in node.targets)]
    paths = ast.literal_eval(specs[0]) if len(specs) == 1 else None
    if (not isinstance(paths, (tuple, list)) or len(paths) != 10
            or any(not isinstance(p, str) or not p or "\0" in p or PurePosixPath(p).is_absolute()
                   or ".." in PurePosixPath(p).parts for p in paths) or len(set(paths)) != 10):
        raise Stop("INVALID_PIN_INVENTORY", PIN_SOURCE, "R1_EXECUTED_SOURCES")
    bad = []
    for path in paths:
        pinned = run(repo, "git", "rev-parse", "--verify", f"{pin}:{path}", check=False)
        current = run(repo, "git", "rev-parse", "--verify", f"HEAD:{path}", check=False)
        if (pinned.returncode or current.returncode or pinned.stdout != current.stdout
                or git(repo, "cat-file", "-t", pinned.stdout.strip()) != "blob"):
            bad.append(path)
    if bad:
        raise Stop("FROZEN_SOURCE_MISMATCH", *bad)


def require_component_heads(repo, path, head):
    heads = json.loads(path.read_bytes())
    if not isinstance(heads, dict) or not heads or any(
            not re.fullmatch(r"[0-9]+", pr) or not isinstance(oid, str)
            or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", oid) for pr, oid in heads.items()):
        raise Stop("INVALID_COMPONENT_HEADS", "--component-heads")
    missing = []
    for pr, oid in heads.items():
        component = run(repo, "git", "cat-file", "-t", oid, check=False)
        if (component.returncode or component.stdout.strip() != "commit"
                or run(repo, "git", "merge-base", "--is-ancestor", oid, head, check=False).returncode):
            missing.append(f"PR #{pr}")
    if missing:
        raise Stop("COMPONENT_NOT_IN_HEAD", *missing)
    return heads


def generated_tree(repo, head):
    with tempfile.TemporaryDirectory(prefix="w1-step1-index-") as temp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(temp) / "index")}
        run(repo, "git", "read-tree", head, env=env)
        run(repo, "git", "add", "--all", "--", ".", env=env)
        return run(repo, "git", "write-tree", env=env).stdout.strip()


def complete_policy(repo, digest, note):
    path = repo / INPUTS
    before = json.loads(path.read_bytes())
    runtime = json.loads((repo / RUNTIME).read_bytes())
    fan_keys = runtime["sensors"]["fan_keys"]
    frozen_r0 = runtime["sensors"]["r0_sha256"]
    if digest != frozen_r0 and not (note and note.strip()):
        raise Stop("R0_NOTE_REQUIRED", RUNTIME, "sensors.r0_sha256", "--r0-note")
    after = json.loads(path.read_bytes())
    policy = after["R1"]["thermal_policy"]
    wanted = {ADDED[0]: digest, ADDED[1]: True, ADDED[2]: True, ADDED[3]: fan_keys, ADDED[4]: digest}
    for key_path, value in wanted.items():
        present = leaf(before, key_path)
        if present != ("<absent>",) and present != value:
            raise Stop("INPUT_ALREADY_FILLED", ".".join(key_path))
    after["R0"]["record_sha256"] = digest
    policy["heavy"] = True
    policy["per_turn"] = True
    policy["sensors"]["fan_keys"] = list(fan_keys)
    policy["sensors"]["r0_sha256"] = digest
    old, new = dict(flat(before)), dict(flat(after))
    changed = sorted(set(old) ^ set(new) | {k for k in set(old) & set(new) if old[k] != new[k]})
    if any(k not in ADDED for k in changed):
        raise Stop("UNEXPECTED_INPUT_CHANGE", *(".".join(k) for k in changed if k not in ADDED))
    dec2_before = hashlib.sha256(b"".join(canonical(leaf(before, p)) for p in DEC2)).hexdigest()
    dec2_after = hashlib.sha256(b"".join(canonical(leaf(after, p)) for p in DEC2)).hexdigest()
    if dec2_before != dec2_after:
        raise Stop("DEC2_CHANGED", *(".".join(k) for k in DEC2))
    write_json(path, after)
    say(f"step 1: inputs.json completed at {len(changed)} key path(s): {', '.join('.'.join(k) for k in changed)}")
    say(f"step 1: DEC2 five-leaf digest unchanged {dec2_after[:16]}...")
    say(f"step 1: R0 digest {'equals' if digest == frozen_r0 else 'DIFFERS FROM'} r1_runtime.json sensors.r0_sha256 "
        f"{frozen_r0[:8]}...{frozen_r0[-4:]}")
    return {"changed_key_paths": [".".join(k) for k in changed], "dec2_digest": dec2_after,
            "r0_digest": digest, "r0_equals_frozen_config": digest == frozen_r0, "r0_note": note or None}


def regenerate(repo, rounds=4):
    for attempt in range(1, rounds + 1):
        before = tree_state(repo)
        run(repo, sys.executable, "-B", "scripts/align_v4_kit.py")
        run(repo, sys.executable, "-B", "scripts/validate_align_v4_w1_plan.py", "--regenerate-template")
        if tree_state(repo) == before:
            say(f"regeneration: fixed point after {attempt} round(s)")
            return
    raise Stop("REGENERATION_DID_NOT_CONVERGE")


def member_seconds(path):
    doc = json.loads(Path(path).read_bytes())
    if isinstance(doc, dict):
        doc = [doc[str(i)] for i in range(1, 19)]
    if not isinstance(doc, list) or len(doc) != 18:
        raise Stop("INVALID_MEMBER_COUNT", "--member-seconds")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in doc):
        raise Stop("INVALID_MEMBER_SECONDS", "--member-seconds")
    return doc


def build_plan(repo, seconds, plan_id, status):
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "scripts"))
    import validate_align_v4_w1_plan as validator  # noqa: E402  (the repo's own validator)
    if Path(validator.__file__).resolve().parent != (repo / "scripts").resolve():
        raise Stop("VALIDATOR_OUTSIDE_REPO", "scripts/validate_align_v4_w1_plan.py")
    inputs = json.loads((repo / INPUTS).read_bytes())
    slots = json.loads((repo / R1_SLOTS).read_bytes())
    collection = json.loads((repo / "configs/campaigns/align_v4/collection_plan.json").read_bytes())
    plan = validator.build_template(collection)
    block, r1 = plan["align_v4"], inputs["R1"]
    block.update(B_D=r1["B_D"], I_D=r1["I_D"], T_dead=r1["T_dead"], max_r1_tail_s=slots["max_r1_tail_s"],
                 effort=inputs["R0"]["reasoning_effort"], thermal_policy=json.loads(canonical(r1["thermal_policy"])),
                 status=status)
    for member, value in zip(block["members"], seconds):
        member["member_s"] = value
    align_s = math.fsum(m["member_s"] for m in block["members"])
    span = math.ceil(block["arithmetic"]["scaffold_s"] + align_s)
    block["arithmetic"].update(align_s=align_s, programmed_span_s=span)
    plan["window_max_s"] = 60 * math.ceil((span + validator.T0_STAGE_CAP_S + validator.PAUSE_LIMIT_S
                                           + validator.SESSION_WAIT_BUDGET_S) / 60)
    plan["plan_id"] = plan_id
    write_json(repo / W1_PLAN, plan)
    done = run(repo, sys.executable, "-B", "scripts/validate_align_v4_w1_plan.py", W1_PLAN)
    if '"status": "VALID"' not in done.stdout:
        raise Stop("PLAN_NOT_VALID", W1_PLAN)
    say(f"step 3: {W1_PLAN} VALID (18 members; arithmetic per the validator)")


def digest_table(repo):
    rows = []
    for path in sorted(tree_state(repo)):
        file = repo / path
        if not file.is_file():
            rows.append({"path": path, "blob": None, "sha256": None})
            continue
        blob = run(repo, "git", "hash-object", "--", path).stdout.strip()
        rows.append({"path": path, "blob": blob, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--pin", required=True, help="commit supplying the frozen R1 source inventory and blobs")
    ap.add_argument("--component-heads", type=Path, required=True,
                    help="JSON object mapping PR numbers to full commit IDs")
    ap.add_argument("--r0-record-sha256", required=True)
    ap.add_argument("--r0-note")
    ap.add_argument("--member-seconds", required=True)
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--status", default="LEAD_FILLED_FROM_R1")
    ap.add_argument("--out", type=Path, default=Path("w1-step1-out"))
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--reader-census", type=Path,
                    help="the reader-census module (RL-193 item 5), run against the generated Git tree")
    args = ap.parse_args(argv)
    repo = args.repo.resolve()
    receipt = {"schema": "joulewise.align_v4.w1_step1_receipt.v1", "missing": list(EVIDENCE)}
    try:
        git_overrides = [name for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE") if name in os.environ]
        if git_overrides:
            raise Stop("GIT_ENV_OVERRIDE", *git_overrides)
        digest = args.r0_record_sha256.lower()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise Stop("INVALID_R0_DIGEST", "--r0-record-sha256")
        if dirty_paths(repo):
            raise Stop("UNCLEAN_WORKTREE")
        receipt["head"] = git(repo, "rev-parse", "HEAD")
        receipt["pin"] = git(repo, "rev-parse", "--verify", "--end-of-options", f"{args.pin}^{{commit}}")
        receipt["component_heads"] = require_component_heads(repo, args.component_heads, receipt["head"])
        ten_blobs(repo, receipt["pin"])
        out = args.out.resolve()
        if args.trace and out / Path(TRACE).name == (repo / TRACE).resolve():
            raise Stop("OUTPUT_OVERLAPS_TRACE", "--out", TRACE)
        say(f"step 0: head {receipt['head'][:12]}, clean, component ancestors present, ten R1 blobs equal the pin")
        seconds = member_seconds(args.member_seconds)
        receipt["inputs"] = complete_policy(repo, digest, args.r0_note)
        run(repo, sys.executable, "-B", "scripts/align_v4_kit.py")
        say("step 2: kit regenerated with R0 bound")
        for attempt in range(1, 4):
            build_plan(repo, seconds, args.plan_id, args.status)
            regenerate(repo)
            # The plan binds collection_plan.json's member configs; if regeneration moved them, rebuild.
            validation = run(repo, sys.executable, "-B", "scripts/validate_align_v4_w1_plan.py", W1_PLAN, check=False)
            if validation.returncode == 0:
                break
            say(f"step 4: w1_plan.json bindings moved during regeneration; rebuilding (round {attempt})")
        else:
            raise child_refusal("PLAN_DID_NOT_CONVERGE", validation, W1_PLAN)
        check = run(repo, sys.executable, "-B", "scripts/align_v4_kit.py", "--check", check=False)
        if check.returncode == 0:
            raise child_refusal("KIT_CHECK_UNEXPECTED_SUCCESS", check, "registration_receipt")
        if check.returncode != 1 or check.stdout or check.stderr != f"align_v4_kit: {RECEIPT_STOP}\n":
            raise child_refusal("KIT_CHECK_UNEXPECTED_STOP", check)
        receipt["check"] = RECEIPT_STOP
        receipt["missing"].remove("registration_receipt_stop")
        say(f"step 5: --check stopped at {RECEIPT_STOP}")
        run(repo, sys.executable, "-B", "-m", "tests.hazards.refusal_census")
        receipt["missing"].remove("refusal_census")
        say("step 5: refusal census: no difference")
        trace_bytes = None
        if args.trace:
            with tempfile.TemporaryDirectory(prefix="w1-step1-trace-") as temp:
                trace_path = Path(temp) / Path(TRACE).name
                run(repo, sys.executable, "-B", "scripts/align_v4_dynamic_trace.py", "--out", str(trace_path))
                trace_bytes = trace_path.read_bytes()
            scenarios = json.loads(trace_bytes)["scenarios"]
            if not scenarios or any(row.get("ok") is not True for row in scenarios.values()):
                out.mkdir(parents=True, exist_ok=True)
                (out / Path(TRACE).name).write_bytes(trace_bytes)
                raise Stop("DYNAMIC_TRACE_FAILED", TRACE)
            (repo / TRACE).write_bytes(trace_bytes)
            receipt["missing"].remove("trace")
            say("step 6: dynamic closure trace regenerated, every scenario ok, copied into the tree")
        if args.reader_census:
            tree = generated_tree(repo, receipt["head"])
            run(repo, sys.executable, "-B", str(args.reader_census.resolve()), "--repo", ".", "--rev", tree)
            if generated_tree(repo, receipt["head"]) != tree:
                raise Stop("WORKTREE_CHANGED_DURING_CENSUS")
            receipt["reader_census_tree"] = tree
            receipt["missing"].remove("reader_census")
            say(f"step 6: reader census PASS at generated tree {tree}")
        receipt["changed"] = digest_table(repo)
        receipt["result"] = "PARTIAL" if receipt["missing"] else "READY_FOR_LEAD_REVIEW"
        out.mkdir(parents=True, exist_ok=True)
        if trace_bytes is not None:
            (out / Path(TRACE).name).write_bytes(trace_bytes)
        write_json(out / "step1-receipt.json", receipt)
        say("step 7: changed paths (blob, sha256):")
        for row in receipt["changed"]:
            say(f"  {row['blob'] or '-':<40} {row['sha256'] or '-':<64} {row['path']}")
        if receipt["missing"]:
            say("PARTIAL: missing " + ", ".join(receipt["missing"]))
            return 1
        say("READY_FOR_LEAD_REVIEW")
        return 0
    except Exception as exc:
        if isinstance(exc, Stop):
            diagnostic = exc.diagnostic
        else:
            digest = hashlib.sha256(str(exc).encode("utf-8", errors="backslashreplace")).hexdigest()
            diagnostic = Stop("STEP1_EXCEPTION", exception=type(exc).__name__, message_sha256=digest).diagnostic
        receipt["result"] = "PARTIAL"
        receipt["refusal"] = diagnostic
        try:
            args.out.mkdir(parents=True, exist_ok=True)
            write_json(args.out / "step1-receipt.json", receipt)
        except OSError:
            pass
        say("REFUSED " + json.dumps(diagnostic, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
