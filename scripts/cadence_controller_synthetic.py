#!/usr/bin/env python3
"""A full synthetic launch-to-close run through the standing-queue controller (RL-172 (i) row 5).

    python3.13 -B scripts/cadence_controller.py synthetic --workdir DIR

Everything is real except the host and the span itself: a local bare ``origin`` with an audit branch
(the standing index, two queues, the kits by hash, the watcher stamp), the controller's own clone, the
SSH-signed bundle push, the receipt census, the pages and acknowledgements. The span is the campaign
runner's own ``run_mock`` (fake clock, feeds and leg runtime; no model, sensor or host command), so the
receipt and the desk bundle the close judges are the runner's real formats. Host readbacks are faked
all-clean; their parsing has its own tests. The fake clock starts Tue 17 Nov 08:00 PST.

The scenario: two dev-04 spans on one date (12 mixed-size legs, the second with five span-reference
consumers), the 300 s floor between them, a dev-05 span dated the next day (NOT_BEFORE), the k+2 desk
debt across the two queues until the Air desk's final record lands, a stalled-wait page and its
acknowledgement, the arm, the close, a READY v4 session (the controller cedes and pages), and the
drained queue. It prints one line per tick and exits 0 when every expectation held.
"""
from __future__ import annotations

import contextlib
from datetime import datetime
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.cadence import legs as legsmod, standing as law  # noqa: E402
from scripts import cadence_controller as cc, cadence_legs_runner as runner  # noqa: E402

RD = "evidence/cadence-standing"
AUDIT = "audit/synthetic"
KITS = {"cl-dev-04": "docs/process/cadence/kits/cl-dev-04.v1.1.json",
        "cl-dev-05": "docs/process/cadence/kits/cl-dev-05.v1.1.json"}
START = datetime.fromisoformat("2026-11-17T08:00:00-08:00").timestamp()


class FakeEnv(cc.Env):
    def __init__(self, epoch):
        self.t = float(epoch)

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds

    def kernel_frequency(self):
        return {"raw_word": 0}

    def run(self, argv, **kw):
        if argv and argv[0] != "git":    # no host command in the synthetic run (the log query, for one)
            return cc.Result(0, "", "synthetic: not run")
        return super().run(argv, **kw)


def clean_proof(kind, allowed=()):
    lines = {name: {"ok": True, "detail": "synthetic"} for name, kinds in law.PROOF_LINES.items() if kind in kinds}
    return {"kind": kind, "epoch": None, "lines": lines, "synthetic": True}


class MockPreparer:
    """No worktree: the measurement checkout is this one; the plan is the pinned library's, at the fake t0."""

    def __init__(self, cfg, guard):
        self.cfg, self.guard = cfg, guard

    def materialize(self, plan_id, kit_sha, kit_raw, frozen_commit):
        self.guard("synthetic: fetch the frozen commit")
        kit_path = Path(self.cfg["kits_dir"]) / f"{plan_id}-{kit_sha[:12]}.json"
        kit_path.parent.mkdir(parents=True, exist_ok=True)
        if not kit_path.exists():
            kit_path.write_bytes(kit_raw)
        return {"kit": str(kit_path), "repo": str(ROOT)}, None

    def check(self, paths, kit, kit_sha, legs, batch_rule, t0):
        plan = legsmod.plan_span(kit, t0_epoch=t0, windows=[], leg_ids=legs, max_span_s=runner.max_span_s())
        return {"plan": plan, "batch_window": None, "expected_windows": [],
                "deadline": runner.launch_deadline(plan) + cc.LAUNCH_GRACE_S, "worst_case_s": plan["worst_case_s"]}, None


class MockLauncher:
    """The LaunchAgent's part: claim the fence, run the span (the runner's mock), and on ``finish`` exit."""

    def __init__(self, cfg, env):
        self.cfg, self.env = cfg, env
        self.live = None
        self.soak_refusals = {}      # plan output name prefix -> soaks refused before one is accepted

    def launch(self, request):
        from joulewise.cadence import kit as kitmod
        root = Path(request["custody_root"])
        root.mkdir(parents=True, exist_ok=True)
        purpose = f"align-r0:{uuid.uuid4().hex}"
        with cc.fence.fence_lock(root):
            cur = cc.fence.read_fence(root)
            if cur is not None and cur["purpose"] != request["standing_purpose"]:
                return {"rc": 3, "launch": None, "arm_child_pid": None, "stderr": f"foreign fence {cur}"}
            record = {"purpose": purpose, "pid": os.getpid(), "deadline": request["deadline"]}
            cc.fence.write_fence(root, record)
        kit, sha = kitmod.load_kit(request["kit"])
        legs = request["legs"].split(",")
        refusals = next((n for prefix, n in self.soak_refusals.items()
                         if Path(request["output"]).name.startswith(prefix)), 0)
        rc, summary, stops, _deps = runner.run_mock(kit=kit, kit_sha256=sha, output=Path(request["output"]),
                                                    t0_epoch=self.env.now(), windows=[], leg_ids=legs,
                                                    soak_refusals=refusals)
        receipt = json.loads((Path(request["output"]) / runner.RECEIPT_NAME).read_text())
        self.live = {"output": Path(request["output"]), "ended": receipt["ended"]["epoch_s"], "root": root,
                     "purpose": purpose, "mock_rc": rc, "mock_stops": stops}
        return {"rc": 0, "arm_child_pid": 2 ** 22 + 1, "stderr": "",
                "launch": {"label": f"com.joulewise.align-r0.{purpose[9:]}", "fence": record,
                           "plan": {"batch_windows": [], "worst_case_s": None, "expected_s": None},
                           "next": "exit the magistrate session now"}}

    def finish(self):
        live, self.live = self.live, None
        receipt = live["output"] / runner.RECEIPT_NAME
        os.utime(receipt, (live["ended"], live["ended"]))
        cc.fence.clear_owned(live["root"], live["purpose"])
        self.env.t = max(self.env.t, live["ended"] + 5)
        return live


def git(cwd, *args, epoch=None, check=True):
    env = {**os.environ, "GIT_AUTHOR_NAME": "lead", "GIT_AUTHOR_EMAIL": "lead@localhost",
           "GIT_COMMITTER_NAME": "lead", "GIT_COMMITTER_EMAIL": "lead@localhost"}
    if epoch is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{int(epoch)} +0000"
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise RuntimeError(f"git {args}: {done.stderr}")
    return done.stdout.strip()


def commit_files(seed, files, message, epoch):
    for rel, value in files.items():
        path = Path(seed) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, bytes):
            path.write_bytes(value)
        else:
            path.write_text(json.dumps(value, indent=1, sort_keys=True) + "\n")
        git(seed, "add", rel)
    git(seed, "commit", "-q", "-m", message, epoch=epoch)
    git(seed, "push", "-q", "origin", f"HEAD:refs/heads/{AUDIT}")
    return git(seed, "rev-parse", "HEAD")


class World:
    """The synthetic MBP, origin and Air desk."""

    def __init__(self, workdir):
        self.w = Path(workdir)
        if self.w.exists():
            shutil.rmtree(self.w)
        self.w.mkdir(parents=True)
        self.origin, self.seed, self.clone = self.w / "origin.git", self.w / "seed", self.w / "ctl-clone"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.seed)], check=True, capture_output=True)
        git(self.seed, "checkout", "-q", "-b", AUDIT)
        self.key = self.w / "bundle_key"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "cadence-bundle", "-f", str(self.key)],
                       check=True)
        self.env = FakeEnv(START)
        t = START - 3600
        kit_files = {f"kits/{cid}.json": (ROOT / path).read_bytes() for cid, path in KITS.items()}
        kit_commit = commit_files(self.seed, kit_files, "kits", t - 600)
        self.sha = {cid: cc.sha256_bytes(raw) for cid, raw in
                    ((p.split("/")[1][:-5], r) for p, r in kit_files.items())}
        entry = lambda cid: {"source": {"commit": kit_commit, "path": f"kits/{cid}.json"}, "line1": "synthetic seat",
                             "line2": "synthetic CI", "batch_window": "none",
                             "hand_gate": {"passed": True, "record": "synthetic class A pass"}}
        self.standing = {
            "schema": law.STANDING_SCHEMA, "standing_id": "cs-synthetic",
            "queues": [{"path": f"{RD}/queues/QUEUE-dev04.json", "role": "standing"},
                       {"path": f"{RD}/queues/QUEUE-dev05.json", "role": "standing"}],
            "kits": {self.sha[c]: entry(c) for c in KITS}, "hand_gates": [],
            "prior_spans": [
                {"plan_id": "cq-dev-01-s01-a1", "campaign_id": "cl-dev-01", "block_id": "dev-01", "legs": 12,
                 "mixed": False, "t0": "2026-11-15T01:00:00-08:00", "closed": "2026-11-15T06:00:00-08:00",
                 "desk_final": "synthetic hand table"},
                {"plan_id": "cq-dev-02-s01-a1", "campaign_id": "cl-dev-02", "block_id": "dev-02", "legs": 6,
                 "mixed": False, "t0": "2026-11-16T10:00:00-08:00", "closed": "2026-11-16T13:00:00-08:00",
                 "desk_final": "synthetic automatic desk"}],
            "withdrawn": [], "dispositions": [], "sessions": [{"session_id": "r1-slot-1", "kind": "r1-slot",
                                           "route": "docs/align/r1_arm_runbook.md"}],
            "fallback": [], "freeze2": None}

        def span(seq, sid, block, cid, legs, nb):
            return {"seq": seq, "span_id": sid, "block_id": block, "attempt": 1, "not_before": nb,
                    "kit": {"path": KITS[cid], "sha256": self.sha[cid]}, "legs": legs}
        legs = [f"L{i:03d}" for i in range(1, 13)]
        q04 = {"schema": "joulewise.cadence_queue.v1", "queue_id": "cq-syn-dev04",
               "expires_at": "2026-11-23T00:00:00-08:00", "halt": None, "standing_notice": None,
               "spans": [span(1, "dev-04-s01", "dev-04", "cl-dev-04", legs[:6], "2026-11-17"),
                         span(2, "dev-04-s02", "dev-04", "cl-dev-04", legs[6:], "2026-11-17")]}
        q05 = {"schema": "joulewise.cadence_queue.v1", "queue_id": "cq-syn-dev05",
               "expires_at": "2026-11-23T00:00:00-08:00", "halt": None, "standing_notice": None,
               "spans": [span(1, "dev-05-s01", "dev-05", "cl-dev-05", legs[:6], "2026-11-18")]}
        stamp = {"schema": law.WATCHER_STAMP_SCHEMA, "watcher": "com.joulewise.air-watch",
                 "observed_live_at": datetime.fromtimestamp(t, law.ZONE).isoformat(), "by": "lead (synthetic)"}
        commit_files(self.seed, {f"{RD}/STANDING.json": self.standing, f"{RD}/queues/QUEUE-dev04.json": q04,
                                 f"{RD}/queues/QUEUE-dev05.json": q05, f"{RD}/watcher-stamp.json": stamp},
                     "standing index, queues, watcher stamp", t)
        subprocess.run(["git", "clone", "-q", "--no-checkout", str(self.origin), str(self.clone)], check=True,
                       capture_output=True)
        out, seed_receipts = self.w / "campaign-out", self.w / "jw-wt"
        (seed_receipts / "old-smoke").mkdir(parents=True)
        old = seed_receipts / "old-smoke" / cc.RECEIPT
        old.write_text("{}\n")
        os.utime(old, (START - 86400, START - 86400))
        out.mkdir()
        self.cfg = {
            "schema": cc.CONFIG_SCHEMA, "state_dir": str(self.w / "controller"), "git_dir": str(self.clone),
            "audit_ref": AUDIT, "records_dir": RD, "worktrees_root": str(self.w / "jw-wt"),
            "output_root": str(out), "kits_dir": str(out / "kits"), "custody_root": str(self.w / "custody"),
            "measurement_python": sys.executable, "receipt_roots": [str(out), str(seed_receipts)],
            "signing_key": str(self.key), "bundle_ref_prefix": "refs/heads/cadence-desk/", "owner_login": "mpmdw",
            "repo_slug": "mpmdw/JouleWise", "gh_argv": ["/bin/false"],
            "measurement_mode_script": "/nonexistent", "high_power_marker": str(self.w / "high-power.marker"),
            "poll_idle_s": 60, "poll_live_s": 2, "hold_standing_fence": True}
        self.issues = []
        self.launcher = MockLauncher(self.cfg, self.env)
        self.ctl = None

    def controller(self):
        ctl = cc.Controller(self.cfg, env=self.env, launcher=self.launcher, issues=lambda: self.issues,
                            proof=clean_proof, pid=os.getpid())
        ctl.preparer = MockPreparer(self.cfg, ctl.guard)
        self.ctl = ctl
        return ctl

    def air_desk_final(self, plan_id, *, hand_table="not-sampled"):
        close = json.loads((Path(self.cfg["state_dir"]) / "spans" / plan_id / "close.json").read_text())
        ref = f"refs/heads/cadence-desk/{plan_id}"
        git(self.seed, "fetch", "-q", "origin", f"{ref}:refs/remotes/bundles/{plan_id}")
        manifest = git(self.seed, "show", f"refs/remotes/bundles/{plan_id}:manifest.json").encode() + b"\n"
        rec = {"schema": law.DESK_FINAL_SCHEMA, "plan_id": plan_id, "bundle_sha256": cc.sha256_bytes(manifest),
               "verdict": "FINAL", "hand_table": hand_table, "reference_print": True, "by": "air desk (synthetic)",
               "at": datetime.fromtimestamp(self.env.now(), law.ZONE).isoformat()}
        assert rec["bundle_sha256"] == close["bundle_sha256"], "the Air reads the bundle the MBP pushed"
        commit_files(self.seed, {f"{RD}/desk-final/{plan_id}.json": rec}, f"desk final {plan_id}", self.env.now() - 60)
        return rec

    def ready_session(self, session_id):
        rec = {"schema": law.SESSION_READY_SCHEMA, "session_id": session_id, "by": "lead (synthetic)",
               "ready_at": datetime.fromtimestamp(self.env.now(), law.ZONE).isoformat()}
        commit_files(self.seed, {f"{RD}/sessions/READY-{session_id}.json": rec}, f"READY {session_id}",
                     self.env.now() - 30)

    def verify_signature(self, plan_id):
        allowed = self.w / "allowed_signers"
        allowed.write_text(f"cadence-bundle {(self.w / 'bundle_key.pub').read_text().split(' ', 2)[0]} "
                           f"{(self.w / 'bundle_key.pub').read_text().split(' ', 2)[1]}\n")
        ref = f"refs/remotes/bundles/{plan_id}"
        git(self.seed, "fetch", "-q", "origin", f"refs/heads/cadence-desk/{plan_id}:{ref}")
        done = subprocess.run(["git", "-C", str(self.seed), "-c", "gpg.format=ssh", "-c",
                               f"gpg.ssh.allowedSignersFile={allowed}", "verify-commit", ref],
                              capture_output=True, text=True)
        return done.returncode == 0


def run(workdir, log=print):
    world = World(workdir)
    ctl = world.controller()
    transcript = []

    def tick(label):
        status = ctl.tick()
        row = {"label": label, "at": datetime.fromtimestamp(world.env.now(), law.ZONE).strftime("%a %H:%M:%S"),
               "state": status.get("state"), "detail": status.get("detail", {k: v for k, v in status.items()
                                                                              if k != "state"})}
        transcript.append(row)
        log(f"{row['at']}  {label:<34} {row['state']:<8} {json.dumps(row['detail'], default=str)[:150]}")
        return status

    def expect(cond, what):
        if not cond:
            raise AssertionError(what)

    s = tick("1 arm dev-04-s01")
    expect(s["state"] == "LIVE" and s["detail"]["plan_id"] == "cq-dev-04-s01-a1", "first span armed")
    intent = json.loads((Path(world.cfg["state_dir"]) / "spans/cq-dev-04-s01-a1/intent.json").read_text())
    arm = json.loads((Path(world.cfg["state_dir"]) / "spans/cq-dev-04-s01-a1/arm.json").read_text())
    expect(intent["network_end_epoch"] <= arm["launch_epoch"], "network work ended before the launch")
    expect(ctl.network_open is False, "network closed while armed")
    s = tick("2 live: fence held")
    expect(s["state"] == "LIVE", "live while the fence is held")
    world.launcher.finish()
    s = tick("3 close dev-04-s01")
    expect(s["state"] == "CLOSED", f"clean close, got {s}")
    expect(world.verify_signature("cq-dev-04-s01-a1"), "the bundle commit carries a valid SSH signature")
    s = tick("4 floor after a campaign close")
    expect(s["state"] == "WAIT" and "GAP" in s["detail"]["codes"], "300 s floor")
    expect(cc.fence.read_fence(Path(world.cfg["custody_root"]))["purpose"].startswith(cc.STANDING_FENCE_PREFIX),
           "the standing fence holds the magistrate off while waiting")
    world.env.t += law.GAP_AFTER_CAMPAIGN_S
    world.launcher.soak_refusals["cq-dev-04-s02-a1"] = 1      # RL-171: its first soak is refused, the retry runs
    s = tick("5 arm dev-04-s02 (consumers)")
    expect(s["state"] == "LIVE" and s["detail"]["plan_id"] == "cq-dev-04-s02-a1", "second span armed")
    live = world.launcher.finish()
    s = tick("6 close dev-04-s02")
    expect(s["state"] == "CLOSED", f"clean close, got {s}")
    receipt = json.loads((live["output"] / runner.RECEIPT_NAME).read_text())
    consumers = [leg["leg_id"] for leg in receipt["legs"] if "span_reference" in leg]
    expect(len(consumers) >= 1, "the second span has span-reference consumers")
    expect(len(receipt["soak_attempts"]) == 2 and receipt["soak_attempts"][0]["refused"],
           "the second span's soak was retried once, and the close is still clean")
    world.env.t += law.GAP_AFTER_CAMPAIGN_S
    s = tick("7 dev-05 dated tomorrow")
    expect(s["state"] == "WAIT" and "NOT_BEFORE" in s["detail"]["codes"], "not before its date")
    world.env.t = datetime.fromisoformat("2026-11-18T00:05:00-08:00").timestamp()
    s = tick("8 midnight: k+2 desk debt")
    expect("K2_DESK_DEBT" in json.dumps(s), f"campaign span 5 waits for span 3's desk: {s}")
    pages = ctl.unacked_pages()
    expect(s["state"] == "PAGED" and pages and pages[0]["kind"] == "WAIT_STALL", "a long wait pages once")
    world.air_desk_final("cq-dev-04-s01-a1")
    for p in pages:
        with contextlib.redirect_stdout(io.StringIO()):
            cc.cmd_ack(world.cfg, type("A", (), {"page_id": p["page_id"], "by": "magistrate (synthetic)",
                                             "note": "Air desk final landed"}))
    s = tick("9 arm dev-05-s01 across queues")
    expect(s["state"] == "LIVE" and s["detail"]["plan_id"] == "cq-dev-05-s01-a1", f"third span armed: {s}")
    world.launcher.finish()
    s = tick("10 close dev-05-s01")
    expect(s["state"] == "CLOSED", "clean close")
    world.env.t += law.GAP_AFTER_CAMPAIGN_S
    world.ready_session("r1-slot-1")
    s = tick("11 READY v4 session")
    expect(s["state"] == "PAGED" and "V4_SESSION_READY" in json.dumps(s), "cede and page, never launch")
    expect(cc.fence.read_fence(Path(world.cfg["custody_root"])) is None, "the fence is released for the magistrate")
    ledger = (Path(world.cfg["state_dir"]) / "transitions.jsonl").read_text().splitlines()
    kinds = [json.loads(line)["transition"] for line in ledger]
    expect(kinds.count("armed") == 3 and kinds.count("closed") == 3 and kinds.count("bundle_pushed") == 3,
           f"three arms, closes and pushes recorded: {kinds}")
    cp = json.loads((Path(world.cfg["state_dir"]) / "critical-path" / "dev-05-s01.json").read_text())
    expect({"NOT_BEFORE", "K2_DESK_DEBT"} <= set(cp["blocking"]) and cp["start"] and cp["end"],
           "the critical-path ledger records each prerequisite, the start and the end")
    return {"ok": True, "transcript": transcript, "transitions": kinds, "world": world}


def main(workdir):
    try:
        result = run(workdir)
    except AssertionError as exc:
        print(f"SYNTHETIC FAILED: {exc}")
        return 1
    print(f"SYNTHETIC OK: {len(result['transcript'])} ticks; transitions {result['transitions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/cadence-synthetic")))
