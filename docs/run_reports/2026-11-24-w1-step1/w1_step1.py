#!/usr/bin/env python3.13
"""W1 promotion runbook step 1: complete the policy, bind R0, commit w1_plan.json, regenerate, check.

Trial PR #958 report §9 step 1 (lead L8; RL-207, RL-210). It is mechanical once PR #824 is admitted and
the authorized R0 record's digest is named. It runs on a clean checkout of the W1 integration branch
(--repo). It prints digests, key names and pass/fail lines only, never a value from inputs.json,
r1_slots.json or the planning release. Run it without GIT_DIR or GIT_WORK_TREE exported (F-10).

    python3.13 -B w1_step1.py --repo "$J" --r0-record-sha256 <64 hex> \
        --member-seconds member_s.json --plan-id <id> [--r0-note "<one line>"] [--out DIR] [--trace]

--member-seconds is the lead's file of R1's member_s for the 18 W1 members: a JSON list of 18 numbers
in ordinal order, or an object {"1": s, ..., "18": s}. The script never chooses or derives one.

What it does, in order (any failure stops it with exit 2 and changes nothing further):
  0. Preconditions: no GIT_DIR or GIT_WORK_TREE, a clean tree, the ten R1 source blobs equal to the pin.
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
  6. Optional (--trace, about 22 min): the dynamic closure trace into --out; it is copied over
     docs/align/v4/dynamic_closure_trace.json only if every scenario is ok.
  7. A digest table of every changed path (blob id and sha256) for the receipt and RL-211's list, and
     step1-receipt.json in --out. Nothing is committed or pushed: the lead reviews `git status` and commits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

PIN = "b2e01464d6d4fbf2901ff4d4154df9455104a12a"
INPUTS = "configs/campaigns/align_v4/registration/inputs.json"
R1_SLOTS = "configs/campaigns/align_v4/registration/r1_slots.json"
W1_PLAN = "configs/campaigns/align_v4/registration/w1_plan.json"
RUNTIME = "configs/align/v4/r1_runtime.json"
TRACE = "docs/align/v4/dynamic_closure_trace.json"
RECEIPT_STOP = "registration_receipt is pending or malformed"
ADDED = (("R0", "record_sha256"), ("R1", "thermal_policy", "heavy"), ("R1", "thermal_policy", "per_turn"),
         ("R1", "thermal_policy", "sensors", "fan_keys"), ("R1", "thermal_policy", "sensors", "r0_sha256"))
DEC2 = (("R1", "B_D"), ("R1", "T_dead"), ("R1", "thermal_policy", "g0_cap_s"),
        ("R1", "thermal_policy", "contrast_g0_cap_s"), ("R1", "thermal_policy", "contrast_fit"))


class Stop(Exception):
    pass


def say(text):
    print(text, flush=True)


def run(repo, *argv, quiet=True, check=True):
    done = subprocess.run(list(argv), cwd=repo, capture_output=True, text=True)
    if check and done.returncode != 0:
        tail = (done.stderr or done.stdout).strip().splitlines()[-1:] or ["(no output)"]
        raise Stop(f"{' '.join(argv[:4])} exited {done.returncode}: {tail[0][:300]}")
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


def tree_state(repo):
    out = run(repo, "git", "status", "--porcelain=v1", "--untracked-files=all").stdout  # unstripped: column 1 matters
    state = {}
    for line in out.splitlines():
        path = line[3:]
        file = repo / path
        state[path] = hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else "<deleted>"
    return state


def ten_blobs(repo):
    source = git(repo, "show", f"HEAD:joulewise/align/apple/v4_registration.py")
    import ast
    tree = ast.parse(source)
    paths = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                 and any(getattr(t, "id", None) == "R1_EXECUTED_SOURCES" for t in node.targets))
    if len(set(paths)) != 10:
        raise Stop("R1_EXECUTED_SOURCES is not ten paths")
    bad = [p for p in paths if git(repo, "rev-parse", f"{PIN}:{p}") != git(repo, "rev-parse", f"HEAD:{p}")]
    if bad:
        raise Stop(f"ten-blob check failed: {bad}")
    return paths


def complete_policy(repo, digest, note):
    path = repo / INPUTS
    before = json.loads(path.read_bytes())
    runtime = json.loads((repo / RUNTIME).read_bytes())
    fan_keys = runtime["sensors"]["fan_keys"]
    frozen_r0 = runtime["sensors"]["r0_sha256"]
    if digest != frozen_r0 and not (note and note.strip()):
        raise Stop("the R0 digest is not r1_runtime.json's sensors.r0_sha256: RL-207 requires the lead's one line "
                   "(--r0-note) naming which record each digest names and why")
    after = json.loads(path.read_bytes())
    policy = after["R1"]["thermal_policy"]
    wanted = {ADDED[0]: digest, ADDED[1]: True, ADDED[2]: True, ADDED[3]: fan_keys, ADDED[4]: digest}
    for key_path, value in wanted.items():
        present = leaf(before, key_path)
        if present != ("<absent>",) and present != value:
            raise Stop(f"{'.'.join(key_path)} is already set to a different value; refusing to overwrite")
    after["R0"]["record_sha256"] = digest
    policy["heavy"] = True
    policy["per_turn"] = True
    policy["sensors"]["fan_keys"] = list(fan_keys)
    policy["sensors"]["r0_sha256"] = digest
    old, new = dict(flat(before)), dict(flat(after))
    changed = sorted(set(old) ^ set(new) | {k for k in set(old) & set(new) if old[k] != new[k]})
    if any(k not in ADDED for k in changed):
        raise Stop(f"unexpected inputs.json change at {['.'.join(k) for k in changed if k not in ADDED]}")
    dec2_before = hashlib.sha256(b"".join(canonical(leaf(before, p)) for p in DEC2)).hexdigest()
    dec2_after = hashlib.sha256(b"".join(canonical(leaf(after, p)) for p in DEC2)).hexdigest()
    if dec2_before != dec2_after:
        raise Stop("DEC2's five leaves changed")
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
    raise Stop(f"regeneration did not reach a fixed point in {rounds} rounds")


def member_seconds(path):
    doc = json.loads(Path(path).read_bytes())
    if isinstance(doc, dict):
        doc = [doc[str(i)] for i in range(1, 19)]
    if not isinstance(doc, list) or len(doc) != 18:
        raise Stop("--member-seconds must give 18 values in ordinal order")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in doc):
        raise Stop("--member-seconds values must be finite numbers")
    return doc


def build_plan(repo, seconds, plan_id, status):
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(repo / "scripts"))
    import validate_align_v4_w1_plan as validator  # noqa: E402  (the repo's own validator)
    if Path(validator.__file__).resolve().parent != (repo / "scripts").resolve():
        raise Stop("imported a validator from outside --repo")
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
        raise Stop("w1_plan.json did not validate")
    say(f"step 3: {W1_PLAN} VALID (18 members; arithmetic per the validator)")


def digest_table(repo):
    rows = []
    for path in sorted(tree_state(repo)):
        file = repo / path
        if not file.is_file():
            rows.append({"path": path, "blob": None, "sha256": None})
            continue
        blob = run(repo, "git", "hash-object", path).stdout.strip()
        rows.append({"path": path, "blob": blob, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--r0-record-sha256", required=True)
    ap.add_argument("--r0-note")
    ap.add_argument("--member-seconds", required=True)
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--status", default="LEAD_FILLED_FROM_R1")
    ap.add_argument("--out", type=Path, default=Path("w1-step1-out"))
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--reader-census", type=Path,
                    help="the reader-census module (RL-193 item 5); run with --signing-head if given")
    args = ap.parse_args(argv)
    repo = args.repo.resolve()
    receipt = {"schema": "joulewise.align_v4.w1_step1_receipt.v1"}
    try:
        if os.environ.get("GIT_DIR") or os.environ.get("GIT_WORK_TREE"):
            raise Stop("GIT_DIR or GIT_WORK_TREE is exported (F-10)")
        digest = args.r0_record_sha256.lower()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise Stop("--r0-record-sha256 must be 64 lowercase hex digits")
        if tree_state(repo):
            raise Stop("the checkout is not clean")
        receipt["head"] = git(repo, "rev-parse", "HEAD")
        ten_blobs(repo)
        say(f"step 0: head {receipt['head'][:12]}, clean, ten R1 blobs equal the pin")
        seconds = member_seconds(args.member_seconds)
        receipt["inputs"] = complete_policy(repo, digest, args.r0_note)
        run(repo, sys.executable, "-B", "scripts/align_v4_kit.py")
        say("step 2: kit regenerated with R0 bound")
        for attempt in range(1, 4):
            build_plan(repo, seconds, args.plan_id, args.status)
            regenerate(repo)
            # The plan binds collection_plan.json's member configs; if regeneration moved them, rebuild.
            if run(repo, sys.executable, "-B", "scripts/validate_align_v4_w1_plan.py", W1_PLAN,
                   check=False).returncode == 0:
                break
            say(f"step 4: w1_plan.json bindings moved during regeneration; rebuilding (round {attempt})")
        else:
            raise Stop("w1_plan.json and the kit did not converge in 3 rounds")
        check = run(repo, sys.executable, "-B", "scripts/align_v4_kit.py", "--check", check=False)
        tail = ((check.stderr or check.stdout).strip().splitlines()[-1:] or [""])[0]
        if check.returncode == 0:
            receipt["check"] = "exit 0"
            say("step 5: align_v4_kit.py --check exit 0")
        elif tail.endswith(RECEIPT_STOP):
            # Everything before require_registration passes: inputs, R0 binding, policy, sizing, WP18.
            # The receipt, U3 bar, B policy and WP19 come later in the runbook (section 9 steps 2-4).
            receipt["check"] = "stops at the receipt, as expected at step 1"
            say(f"step 5: --check passes every pre-registration gate and stops at the receipt: {RECEIPT_STOP!r}")
        else:
            raise Stop(f"--check exited {check.returncode} before the receipt: {tail[:300]}")
        run(repo, sys.executable, "-B", "-m", "tests.hazards.refusal_census")
        say("step 5: refusal census: no difference")
        args.out.mkdir(parents=True, exist_ok=True)
        if args.reader_census:
            run(repo, sys.executable, "-B", str(args.reader_census), "--repo", ".", "--rev", receipt["head"],
                "--signing-head")
            say("step 5: reader census PASS at the pre-commit head (rerun at the signing head)")
        if args.trace:
            out = (args.out / "dynamic_closure_trace.json").resolve()
            run(repo, sys.executable, "-B", "scripts/align_v4_dynamic_trace.py", "--out", str(out))
            trace = json.loads(out.read_bytes())
            bad = sorted(name for name, row in trace["scenarios"].items() if not row.get("ok"))
            if bad:
                raise Stop(f"dynamic trace scenarios not ok: {bad}; trace left at {out}, not copied")
            (repo / TRACE).write_bytes(out.read_bytes())
            say("step 6: dynamic closure trace regenerated, every scenario ok, copied into the tree")
        receipt["changed"] = digest_table(repo)
        receipt["result"] = "READY_FOR_LEAD_REVIEW"
        write_json(args.out / "step1-receipt.json", receipt)
        say("step 7: changed paths (blob, sha256):")
        for row in receipt["changed"]:
            say(f"  {row['blob'] or '-':<40} {row['sha256'] or '-':<64} {row['path']}")
        say("done: review `git status`, commit, then run step 4 (RL-184 three-blob check) on this head (§9 step 2)")
        return 0
    except Stop as stop:
        receipt["result"] = f"STOPPED: {stop}"
        try:
            args.out.mkdir(parents=True, exist_ok=True)
            write_json(args.out / "step1-receipt.json", receipt)
        except OSError:
            pass
        say(f"STOP: {stop}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
