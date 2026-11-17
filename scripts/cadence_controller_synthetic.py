#!/usr/bin/env python3
"""Real end-to-end synthetic runs of the standing queue (RL-172 (i) row 5): controller → bundle → Air → verdict.

    python3.13 -B scripts/cadence_controller.py synthetic --workdir DIR

Nothing on the decision path is hand-written:

- **Controller and runner.** The controller arms. The **pinned runner of each kit's own frozen commit** runs its
  mock span, exported from git: dev-04 and dev-05 run the pre-RL-171 runner at ``2d347f721``, with no
  ``soak_attempts``; the qualification kit runs ``e1b85a59c``, with the soak retry. The controller closes, packs
  the bundle with ``desk_final.pack_bundle`` and pushes an SSH-signed ref.
- **Air.** The Air verifies that signature and runs the real ``scripts/air/cadence_desk.py final`` on the verified
  tree, with the anchor taken from the signed ``transition.json``. It commits the verdict it wrote to the audit
  branch, signed by the desk key.
- **Back to the controller.** The controller reads the verdict by FORMAT.md section 4 and arms the next span, or
  holds.
- **The lead.** The lead's acts are explicit and named (a journal-copy marker, a hand table, a gate release),
  never a verdict.

What is synthetic:

- the clock (fake);
- the host readbacks (all clean; their parsing has its own tests);
- the issue tracker (a list);
- the mock leg runtime inside the pinned runner;
- the hand table, built from the bundle the lead would read. It stands in for the lead's journal read.

A pin missing from this clone falls back to HEAD's runner, and the run says so.

Scenarios:

- ``clean``: a dev-05 pilot, its class A gate, then the next span.
- ``soak_retry``: qual-01's pilot on the qualification pin, first soak refused.
- ``l005_timeout``: dev-04's pilot with L005's G0 timing out. The remainder holds on the derived L005 gate until
  the lead's record.
- ``redo``: a dev-05 pilot with a load redo. Its verdict waits for the hand table, and the k+2 rule holds span 3
  until it is final.
- ``tampered``: an unsigned bundle the Air refuses, and an unsigned verdict the controller refuses.
- ``denied_key``, ``prior_gate``, ``recovery``, ``repage``, ``night_window``: the second gate's findings.
- ``actions_watcher`` (RL-173 C.4), ``offload`` (A.2, A.7), ``l002_timeout`` (E), ``fence`` (E): RL-173's owner list.
- ``copy_gate``: the copy gate is per span (gate 3).

Every close also runs the MBP desk (RL-173 B: the real ``cadence_desk.py final`` from this checkout on the signed
bundle commit, its records signed with the controller's key); the Air's verdict is the off-host re-check, and the
two must agree.
"""
from __future__ import annotations

import contextlib
from datetime import datetime, timezone
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

from joulewise.cadence import desk_final, standing as law  # noqa: E402
from scripts import cadence_controller as cc  # noqa: E402

RD = "evidence/cadence-standing"
AUDIT = "audit/synthetic"
KITS = {"cl-dev-01": "docs/process/cadence/kits/cl-dev-01.json",
        "cl-dev-03": "docs/process/cadence/kits/cl-dev-03.v1.1.json",
        "cl-dev-04": "docs/process/cadence/kits/cl-dev-04.v1.1.json",
        "cl-dev-05": "docs/process/cadence/kits/cl-dev-05.v1.1.json",
        "cl-qual-01": "docs/process/cadence/kits/cl-qual-01.v1.1.json"}
START = datetime.fromisoformat("2026-11-17T08:00:00-08:00").timestamp()
L = [f"L{i:03d}" for i in range(1, 13)]
WATCHER = "com.joulewise.air-watch"


class FakeEnv(cc.Env):
    def __init__(self, epoch):
        self.t = float(epoch)
        self.night_labels = []          # labels a v4 window would have loaded
        self.launchctl_rc = 0

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds

    def wait_for_change(self, directory, timeout):
        self.t += timeout

    def watch(self, directory):
        env = self

        class W:
            def wait(self, timeout):
                env.t += timeout

            def close(self):
                pass
        return W()

    def kernel_frequency(self):
        return {"raw_word": 0}

    def run(self, argv, **kw):
        if argv and str(argv[0]).endswith("launchctl"):
            rows = ["PID\tStatus\tLabel", "-\t0\tcom.apple.synthetic"] + [f"123\t0\t{x}" for x in self.night_labels]
            return cc.Result(self.launchctl_rc, "\n".join(rows) + "\n" if self.launchctl_rc == 0 else "", "")
        if argv and argv[0] != "git":    # no host command in the synthetic run (pgrep: "none found")
            return cc.Result(1 if "pgrep" in str(argv[0]) else 0, "", "synthetic: not run")
        return super().run(argv, **kw)


def clean_proof(kind, allowed=()):
    lines = {name: {"ok": True, "detail": "synthetic"} for name, kinds in law.PROOF_LINES.items()
             if kind in kinds and name != "signing"}
    return {"kind": kind, "epoch": None, "lines": lines, "synthetic": True}


def git(cwd, *args, epoch=None, check=True):
    env = {**os.environ, "GIT_AUTHOR_NAME": "lead", "GIT_AUTHOR_EMAIL": "lead@localhost",
           "GIT_COMMITTER_NAME": "lead", "GIT_COMMITTER_EMAIL": "lead@localhost"}
    if epoch is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{int(epoch)} +0000"
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, env=env)
    if check and done.returncode != 0:
        raise RuntimeError(f"git {args}: {done.stderr.decode()}")
    return done.stdout


class World:
    """The synthetic MBP (controller), origin, lead and Air desk."""

    def __init__(self, workdir, *, prior=True, freeze2=False, prior_evidence=True):
        self.w = Path(workdir).resolve()      # Mythos N17: a relative workdir broke the pinned children's paths
        if self.w.exists():
            shutil.rmtree(self.w)
        self.w.mkdir(parents=True)
        self.env = FakeEnv(START)
        self.origin, self.seed, self.clone = self.w / "origin.git", self.w / "seed", self.w / "ctl-clone"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.seed)], check=True, capture_output=True)
        git(self.seed, "checkout", "-q", "-b", AUDIT)
        self.keys = {}
        for name, principal in (("ctl", "cadence-controller"), ("air", "cadence-desk")):
            key = self.w / f"{name}_key"
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", principal, "-f", str(key)], check=True)
            pub = Path(f"{key}.pub").read_text().split()
            allowed = self.w / f"{name}_allowed_signers"
            allowed.write_text(f'{principal} namespaces="git" {pub[0]} {pub[1]}\n')
            self.keys[name] = {"key": key, "allowed": allowed}
        self.pins, self.pin_note = {}, {}
        kit_files = {f"kits/{cid}.json": (ROOT / path).read_bytes() for cid, path in KITS.items()}
        for raw in kit_files.values():
            commit = json.loads(raw)["frozen"]["commit"]
            if commit not in self.pins:
                self.pins[commit] = self._export_pin(commit)
        self.kit_commit = self.commit(kit_files, "kits", START - 7200)
        self.sha = {p.split("/")[1][:-5]: cc.sha256_bytes(r) for p, r in kit_files.items()}

        def entry(cid):
            return {"source": {"commit": self.kit_commit, "path": f"kits/{cid}.json"}, "line1": "synthetic seat",
                    "line2": "synthetic CI", "batch_window": "rl172" if cid.startswith("cl-dev") else "none"}
        self.standing = {
            "schema": law.STANDING_SCHEMA, "standing_id": "cs-synthetic", "queues": [],
            "kits": {self.sha[c]: entry(c) for c in KITS}, "hand_gates": [], "withdrawn": [],
            # the hand-armed dev-01 pilot's class A gate, released by the lead after its hand-read (Mythos N2)
            "gate_records": [] if not prior else [{"plan_id": "cq-dev-01-s01-a1", "gate": "class-a",
                                                   "decision": "release", "record": "item 320 (synthetic)"}],
            "dispositions": [], "sessions": [{"session_id": "r1-slot-1", "kind": "r1-slot",
                                              "route": "docs/align/r1_arm_runbook.md"}],
            "fallback": [], "freeze2": "synthetic freeze 2" if freeze2 else None,
            "prior_spans": [] if not prior else [
                {"plan_id": "cq-dev-01-s01-a1", "campaign_id": "cl-dev-01", "block_id": "dev-01",
                 "kit_sha256": self.sha["cl-dev-01"], "roster": L[:3], "legs": 3, "mixed": False,
                 "t0": "2026-11-15T01:00:00-08:00", "closed": "2026-11-15T03:00:00-08:00",
                 "desk_final": "synthetic hand table"},
                {"plan_id": "cq-dev-01-s03-a1", "campaign_id": "cl-dev-01", "block_id": "dev-01",
                 "kit_sha256": self.sha["cl-dev-01"], "roster": L[3:9], "legs": 6, "mixed": False,
                 "t0": "2026-11-16T10:00:00-08:00", "closed": "2026-11-16T13:00:00-08:00",
                 "desk_final": "synthetic automatic desk"}]}
        stamp = {"schema": law.WATCHER_STAMP_SCHEMA, "watcher": WATCHER, "by": "lead (synthetic)",
                 "observed_live_at": datetime.fromtimestamp(START - 3600, law.ZONE).isoformat()}
        self.commit({f"{RD}/STANDING.json": self.standing, f"{RD}/watcher-stamp.json": stamp}, "standing", START - 3000)
        subprocess.run(["git", "clone", "-q", "--no-checkout", str(self.origin), str(self.clone)], check=True,
                       capture_output=True)
        out, roots = self.w / "campaign-out", self.w / "jw-wt"
        (roots / "old-smoke").mkdir(parents=True)
        old = roots / "old-smoke" / cc.RECEIPT
        old.write_text("{}\n")
        os.utime(old, (START - 86400, START - 86400))
        out.mkdir()
        self.cfg = {
            "schema": cc.CONFIG_SCHEMA, "state_dir": str(self.w / "controller"), "git_dir": str(self.clone),
            "audit_ref": AUDIT, "records_dir": RD, "worktrees_root": str(roots), "output_root": str(out),
            "kits_dir": str(out / "kits"), "custody_root": str(self.w / "custody"),
            "measurement_python": sys.executable, "receipt_roots": [str(out), str(roots)],
            "signing_key": str(self.keys["ctl"]["key"]), "bundle_ref_prefix": "refs/heads/desk-bundles/",
            "verdict_signers": str(self.keys["air"]["allowed"]), "copy_marker_dir": str(self.w / "desk-copy"),
            "watcher_name": WATCHER, "owner_login": "mpmdw", "repo_slug": "mpmdw/JouleWise", "gh_argv": ["/bin/false"],
            "measurement_mode_script": "/nonexistent", "high_power_marker": str(self.w / "high-power.marker"),
            "poll_idle_s": 60, "poll_live_s": 60, "hold_standing_fence": True, "accept_mock_verdicts": True,
            "watcher_kind": "stamp", "controller_signers": str(self.keys["ctl"]["allowed"]), "offload_argv": None,
            "desk_commit": "0" * 40}
        (self.w / "custody").mkdir()
        (self.w / "desk-copy").mkdir()
        if self.standing["prior_spans"] and prior_evidence:
            self.record_prior_close(self.standing["prior_spans"][-1])
        self.issues, self.notices, self.history, self.watcher_runs = [], [], {}, []
        self.launcher = MockLauncher(self)
        self.ctl = None

    def record_prior_close(self, prior):
        """Materialize a clean hand-armed fixture with its own receipt and verified copy marker."""
        pid, roster = prior["plan_id"], prior["roster"]
        stamp = datetime.fromtimestamp(law.parse_time(prior["t0"]), timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        source = Path(self.cfg["output_root"]) / prior["campaign_id"] / f"{pid}-{stamp}"
        source.mkdir(parents=True)
        receipt = source / cc.RECEIPT
        receipt.write_text(json.dumps({
            "roster": roster, "kit": {"sha256": prior["kit_sha256"], "campaign_id": prior["campaign_id"]},
            "rc": 0, "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE",
                                    "fault": False, "outcome": "MEASURED_OK"},
            "steps": [{"name": "soak", "rc": 0}, {"name": "restore", "rc": 0}],
            "feeds": {"meter": {"stop": {"proven_stopped": True}}},
            "legs_finished": len(roster), "legs_planned": len(roster),
            "legs": [{"leg_id": leg, "summary": {"g0_outcome": "released"}} for leg in roster],
        }))
        closed = law.parse_time(prior["closed"])
        os.utime(receipt, (closed, closed))
        marker = offload_marker(pid, closed, str(source))
        (Path(self.cfg["copy_marker_dir"]) / f"{pid}.ok").write_text(json.dumps(marker))
        return receipt

    # -- the pinned runners -------------------------------------------------------------------------
    def _export_pin(self, commit):
        have = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{commit}^{{commit}}"],
                              capture_output=True).returncode == 0
        if not have:
            self.pin_note[commit] = "pin missing from this clone: HEAD's runner used"
            return ROOT
        target = self.w / "pins" / commit[:12]
        target.mkdir(parents=True)
        archive = subprocess.run(["git", "-C", str(ROOT), "archive", commit, "joulewise", "scripts"],
                                 capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(target)], input=archive, check=True)
        self.pin_note[commit] = "pinned runner exported from git"
        return target

    # -- lead and Air commits -----------------------------------------------------------------------
    def commit(self, files, message, epoch, *, sign=None):
        for rel, value in files.items():
            path = self.seed / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value if isinstance(value, bytes) else
                             (json.dumps(value, indent=1, sort_keys=True) + "\n").encode())
            git(self.seed, "add", rel)
        args = (["-c", "gpg.format=ssh", "-c", f"user.signingkey={self.keys[sign]['key']}", "commit", "-q", "-S"]
                if sign else ["commit", "-q"])
        git(self.seed, *args, "-m", message, epoch=epoch)
        git(self.seed, "push", "-q", "origin", f"HEAD:refs/heads/{AUDIT}")
        return git(self.seed, "rev-parse", "HEAD").decode().strip()

    def queue(self, name, spans, *, role="standing", notice=900):
        """The lead commits a queue file and lists it in the standing index."""
        path = f"{RD}/queues/QUEUE-{name}.json"
        doc = {"schema": "joulewise.cadence_queue.v1", "queue_id": f"cq-syn-{name}",
               "expires_at": "2026-11-23T00:00:00-08:00", "halt": None, "standing_notice": {"issue": notice},
               "spans": spans}
        if not any(q["path"] == path for q in self.standing["queues"]):
            self.standing["queues"].append({"path": path, "role": role})
        self.commit({path: doc, f"{RD}/STANDING.json": self.standing}, f"queue {name}", self.env.now() - 60)
        return path

    def span(self, seq, sid, cid, legs, nb="2026-11-17"):
        return {"seq": seq, "span_id": sid, "block_id": sid.rsplit("-s", 1)[0], "attempt": 1, "not_before": nb,
                "kit": {"path": KITS[cid], "sha256": self.sha[cid]}, "legs": legs}

    def lead_release(self, plan_id, gate, record="the lead's hand read (synthetic)"):
        self.env.t += 120          # the lead's hand-read takes time: a release is committed after the span closed
        self.standing["gate_records"].append({"plan_id": plan_id, "gate": gate, "decision": "release",
                                              "record": record})
        self.commit({f"{RD}/STANDING.json": self.standing}, f"release {gate} {plan_id}", self.env.now() - 30)

    def copy_journals(self, plan_id):
        """The offload tool's verified marker (RL-173 A.2; design 15.13), standing in for its encrypted upload."""
        intent = json.loads((Path(self.cfg["state_dir"]) / "spans" / plan_id / "intent.json").read_text())
        (Path(self.cfg["copy_marker_dir"]) / f"{plan_id}.ok").write_text(
            json.dumps(offload_marker(plan_id, self.env.now(), intent["output"])))

    def q1_record(self, plan_id):
        """The lead's typed RL-158 Q1 completion record (RL-173 E), committed on the audit branch after the print."""
        self.env.t += 60
        span_id, attempt = plan_id[3:].rsplit("-a", 1)
        doc = {"schema": desk_final.Q1_RECORD_SCHEMA, "plan_id": plan_id, "span_id": span_id, "attempt": int(attempt),
               "signer": "the lead (synthetic)", "recorded_at": datetime.fromtimestamp(self.env.now(), law.ZONE).isoformat(),
               "print_ref": f"synthetic Q1 print of {plan_id}"}
        self.commit({f"{RD}/q1/{plan_id}.json": doc}, f"q1 {plan_id}", self.env.now() - 30)

    # -- the controller -----------------------------------------------------------------------------
    def controller(self):
        ctl = cc.Controller(self.cfg, env=self.env, launcher=self.launcher, issues=lambda: self.issues,
                            proof=clean_proof, signing=lambda: cc.signing_check(self.cfg, cc.Env()),
                            clock=lambda: self.env.now(), notice=self._notice, pid=os.getpid(),
                            watcher_run=self._watcher_run,
                            desk_commit=lambda: {"ok": True, "detail": "synthetic: the checkout under test"})
        ctl.preparer = MockPreparer(self, ctl.guard)
        self.ctl = ctl
        return ctl

    def _watcher_run(self):
        """The Actions watcher's latest completed run (RL-173 C.4), as the API would return it."""
        self.ctl.guard("synthetic: gh api actions runs")
        return self.watcher_runs[-1] if self.watcher_runs and self.watcher_runs[-1] != "unreadable" else (
            "unreadable" if self.watcher_runs else None)

    def watcher_ran(self, conclusion="success", started=None):
        started = self.env.now() - 30 if started is None else started
        iso = datetime.fromtimestamp(started, law.ZONE).isoformat()
        self.watcher_runs.append(law.actions_run_view({
            "id": 7000 + len(self.watcher_runs), "name": "mbp-watcher", "path": ".github/workflows/mbp-watcher.yml",
            "status": "completed", "conclusion": conclusion, "run_started_at": iso,
            "updated_at": datetime.fromtimestamp(started + 20, law.ZONE).isoformat(), "event": "schedule",
            "head_branch": "main", "head_sha": "d" * 40, "html_url": "https://example.invalid/run",
            "head_repository": {"full_name": self.cfg["repo_slug"]}}))

    def _notice(self, issue, text):
        self.ctl.guard("synthetic: standing notice")
        self.notices.append((issue, text))
        return True

    def tick(self):
        return self.ctl.tick()

    def advance_wait(self, seconds):
        """Advance a parked scenario while simulating its intervening fence-renewal polls.

        Authority and host changes are evaluated by the caller's next real tick. Tests of a stopped controller
        deliberately advance env.t directly instead, so they still expose a genuine lease lapse.
        """
        end = self.env.now() + seconds
        while self.env.now() < end:
            self.env.t = min(end, self.env.now() + 60)
            assert self.ctl.refresh_fence() != "lapsed", "scenario skipped a fence-renewal poll"

    def ack_all(self, note="synthetic magistrate"):
        for p in self.ctl.unacked_pages():
            with contextlib.redirect_stdout(io.StringIO()):
                cc.cmd_ack(self.cfg, type("A", (), {"page_id": p["page_id"], "by": "magistrate", "note": note}))

    def drive(self, until, *, max_ticks=80, step=300):
        """Tick, advancing the fake clock on waits, until ``until(status)`` holds."""
        status = None
        for _ in range(max_ticks):
            status = self.tick()
            if until(status):
                return status
            if status["state"] in ("LIVE", "CLOSING"):
                if self.launcher.live is not None:
                    self.launcher.finish()
                continue
            self.env.t += step
        raise AssertionError(f"drive: never reached the condition; last {status}")

    # -- the Air desk --------------------------------------------------------------------------------
    def air_final(self, plan_id, *, hand_table=False):
        """The Air, as FORMAT.md section 2 runs it: fetch the bundle and verdict refs, ``cadence_desk.py final`` on the
        signed bundle ref (it verifies the controller's signature, the tree's shape, the anchor and the queue bytes),
        then ``cadence_desk.py publish`` with the desk key. Returns the verdict, or None if ``final`` wrote none."""
        git(self.seed, "fetch", "-q", "-f", "origin", "+refs/heads/desk-bundles/*:refs/remotes/origin/desk-bundles/*",
            "+refs/heads/cadence-desk-final/*:refs/remotes/origin/cadence-desk-final/*")
        cid = self._campaign(plan_id)
        work = self.w / "air" / f"{plan_id}-{uuid.uuid4().hex[:6]}"
        work.mkdir(parents=True)
        kit = work / "kit.json"
        kit.write_bytes(git(self.seed, "show", f"{self.kit_commit}:kits/{cid}.json"))
        out = work / "out"
        argv = [sys.executable, "-B", str(ROOT / "scripts/air/cadence_desk.py"), "final", "--plan-id", plan_id,
                "--repo", str(self.seed), "--bundle-ref", f"refs/remotes/origin/desk-bundles/{plan_id}",
                "--allowed-signers", str(self.keys["ctl"]["allowed"]), "--kit", str(kit), "--out", str(out),
                "--history-prefix", "refs/remotes/origin/cadence-desk-final/",
                "--history-signers", str(self.keys["air"]["allowed"]), "--allow-mock",
                "--lock", str(work / "AIR-QUIET.lock")]
        if not git(self.seed, "for-each-ref", "refs/remotes/origin/cadence-desk-final/").strip():
            argv.append("--history-empty")      # this Air has published nothing yet (#799 gate 3, Mythos T5)
        if hand_table:
            argv += ["--hand-table", str(self.hand_table(plan_id, work))]
        done = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT),
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.air_log = done.stdout + done.stderr
        if not (out / desk_final.VERDICT_NAME).is_file():
            return None
        verdict = json.loads((out / desk_final.VERDICT_NAME).read_text())
        if not (verdict.get("transport") or {}).get("signed"):
            return None      # the Air refused the bundle: nothing it may publish counts
        pub = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/air/cadence_desk.py"), "publish", "--plan-id",
                              plan_id, "--out", str(out), "--repo", str(self.seed), "--signing-key",
                              str(self.keys["air"]["key"])], capture_output=True, text=True, cwd=str(ROOT),
                             env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if pub.returncode != 0:
            raise AssertionError(f"publish failed: {pub.stdout} {pub.stderr}")
        return verdict

    def _campaign(self, plan_id):
        intent = json.loads((Path(self.cfg["state_dir"]) / "spans" / plan_id / "intent.json").read_text())
        return intent["kit"]["campaign_id"]

    def hand_table(self, plan_id, work):
        """The lead's hand table, standing in for the lead's journal read: every required field of every leg, read
        from the signed bundle the lead was sent, the soak attempt count, and the named stops the lead found (none
        in these spans)."""
        ref = f"refs/remotes/origin/desk-bundles/{plan_id}"
        receipt = json.loads(git(self.seed, "show", f"{ref}:bundle/runner_receipt.json"))
        legs = []
        for row in receipt["legs"]:
            summary = json.loads(git(self.seed, "show", f"{ref}:bundle/legs/{row['leg_id']}/leg_summary.json"))
            legs.append({"leg_id": row["leg_id"], **{k: summary.get(k) for k in desk_final.HAND_REQUIRED_V11
                                                     if k != "leg_id" and k in summary}})
        attempts = len(receipt.get("soak_attempts") or []) or sum(
            1 for st in receipt["steps"] if st["name"] == "soak" or st["name"].startswith("soak.a"))
        path = work / "hand_table.json"
        path.write_text(json.dumps({"schema": desk_final.HAND_TABLE_SCHEMA, "plan_id": plan_id, "legs": legs,
                                    "named_stops": [], "soak_attempts": attempts}))
        return path


def offload_marker(plan_id, now, source):
    """A marker the offload tool writes (design 15.13), synthetic values."""
    return {"schema": law.OFFLOAD_MARKER_SCHEMA, "plan_id": plan_id, "source": source,
            "manifest_sha256": "a" * 64, "manifest_files": 12, "ciphertext_sha256": "b" * 64,
            "ciphertext_bytes": 1048576, "provider": "synthetic cloud", "remote_path": f"offload/{plan_id}.enc",
            "upload": {"confirmed": True, "readback": "sha256", "value": "b" * 64, "evidence": "synthetic readback"},
            "verified": True, "key_second_copy": "synthetic vault",
            "written_at": datetime.fromtimestamp(now, law.ZONE).isoformat()}


class MockPreparer:
    """No worktree: the pinned runner exported from git is the measurement checkout; ``plan`` is the pin's own."""

    def __init__(self, world, guard):
        self.world, self.guard = world, guard

    def materialize(self, plan_id, kit_sha, kit_raw, frozen_commit):
        self.guard("synthetic: fetch the frozen commit")
        kit_path = Path(self.world.cfg["kits_dir"]) / f"{plan_id}-{kit_sha[:12]}.json"
        kit_path.parent.mkdir(parents=True, exist_ok=True)
        if not kit_path.exists():
            kit_path.write_bytes(kit_raw)
        return {"kit": str(kit_path), "repo": str(self.world.pins[frozen_commit])}, None

    def check(self, paths, kit, kit_sha, legs, batch_rule, t0):
        windows = [None] if batch_rule == "none" else ["02:00-02:35", "13:14-13:15"]
        last = ""
        for window in windows:
            done = subprocess.run([sys.executable, "-B", "scripts/cadence_legs_runner.py", "plan", "--kit", paths["kit"],
                                   "--legs", ",".join(legs), "--t0", repr(t0),
                                   *(["--batch-window", window] if window else [])],
                                  cwd=paths["repo"], capture_output=True, text=True,
                                  env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            if done.returncode == 0:
                plan = json.loads(done.stdout)
                return {"plan": plan, "batch_window": window, "expected_windows": [window] if window else [],
                        "worst_case_s": plan["worst_case_s"]}, None
            last = done.stderr.strip()[:200]
        return None, "PLAN_REFUSED_AT_T0: " + last


class MockLauncher:
    """The arm child and the LaunchAgent: the atomic fence transfer, then the pinned runner's own mock span."""

    def __init__(self, world):
        self.world = world
        self.live = None
        self.flags = {}        # plan id -> runner mock flags (e.g. ["--g0-timeout", "L005"])
        self.launched = []
        self.fences_at_launch = []
        self.edit = {}         # plan id -> callable(output dir), run after the span (a faulty projection, say)

    def launch(self, request):
        env = self.world.env
        root = Path(request["custody_root"])
        if env.now() > request["lease_until"]:
            return {"rc": 4, "launch": None, "refused": "the arm lease expired", "stderr": ""}
        purpose = f"align-r0:{uuid.uuid4().hex}"
        with cc.fence.fence_lock(root):
            cur = cc.fence.read_fence(root)
            self.fences_at_launch.append(cur)
            if cur is not None and cur["purpose"] != request["standing_purpose"]:
                return {"rc": 3, "launch": None, "refused": f"foreign fence {cur}", "stderr": ""}
            record = {"purpose": purpose, "pid": os.getpid(), "deadline": env.now() + 12 * 3600}
            cc.fence.write_fence(root, record)        # replaces the standing fence: never a gap
        plan_id = Path(request["output"]).name.rsplit("-", 1)[0]
        t0_local = datetime.fromtimestamp(env.now(), law.ZONE).strftime("%Y-%m-%dT%H:%M:%S")
        argv = [sys.executable, "-B", "scripts/cadence_legs_runner.py", "mock", "--kit", request["kit"], "--legs",
                request["legs"], "--output", request["output"], "--t0-local", t0_local,
                *(["--batch-window", request["batch_window"]] if request["batch_window"] else []),
                *self.flags.get(plan_id, [])]
        done = subprocess.run(argv, cwd=request["repo"], capture_output=True, text=True,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "JW_B5_SYNTHETIC_ONLY": "1"})
        if plan_id in self.edit:
            self.edit[plan_id](Path(request["output"]))
        receipt = json.loads((Path(request["output"]) / cc.RECEIPT).read_text())
        self.live = {"output": Path(request["output"]), "ended": receipt["ended"]["epoch_s"], "root": root,
                     "purpose": purpose, "mock_rc": done.returncode}
        self.launched.append(plan_id)
        return {"rc": 0, "arm_child_pid": 2 ** 22 + 1, "t0": env.now(), "deadline": record["deadline"], "stderr": "",
                "launch": {"label": f"com.joulewise.align-r0.{purpose[9:]}", "fence": record,
                           "plan": {"batch_windows": [request["batch_window"]] if request["batch_window"] else []},
                           "next": "exit the magistrate session now"}}

    def finish(self):
        live, self.live = self.live, None
        receipt = live["output"] / cc.RECEIPT
        os.utime(receipt, (live["ended"], live["ended"]))
        cc.fence.clear_owned(live["root"], live["purpose"])
        self.world.env.t = max(self.world.env.t, live["ended"] + 5)
        return live


def _state(s):
    return s["state"]


def _codes(s):
    return set((s.get("detail") or {}).get("codes") or [])


def _close(w, plan_id):
    return json.loads((Path(w.cfg["state_dir"]) / "spans" / plan_id / "close.json").read_text())


# --------------------------------------------------------------------------
# The scenarios
# --------------------------------------------------------------------------
def scenario_clean(workdir, log=print):
    """A dev-05 pilot on its pin, closed clean. The remainder holds on the copy gate and the derived class A gate;
    the Air's verdict needs the first span's hand table; the lead releases; the next span arms."""
    w = World(workdir)
    w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
    s = w.tick()
    assert _state(s) == "LIVE", s
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    close = _close(w, "cq-dev-05-s01-a1")
    assert close["gates"] == ["class-a"] and close["pushed"], close
    w.queue("dev05-rest", [w.span(1, "dev-05-s02", "cl-dev-05", L[6:])])
    w.env.t += 400
    s = w.tick()
    assert "JOURNAL_COPY" in _codes(s), s
    w.copy_journals("cq-dev-05-s01-a1")
    s = w.tick()
    assert _state(s) == "WAIT" and "HAND_GATE" in _codes(s), s
    v1 = w.air_final("cq-dev-05-s01-a1")
    assert v1 is not None and not v1["desk_final"], v1
    v2 = w.air_final("cq-dev-05-s01-a1", hand_table=True)
    assert v2["desk_final"], v2["reasons"]
    w.lead_release("cq-dev-05-s01-a1", "class-a")
    s = w.drive(lambda s: _state(s) == "LIVE")
    assert s["detail"]["plan_id"] == "cq-dev-05-s02-a1", s
    log(f"clean: dev-05-s01 CLOSED_OK on {w.pin_note}; JOURNAL_COPY then HAND_GATE held dev-05-s02; Air verdict "
        f"desk_final {v1['desk_final']} (pending {[p['code'] for p in v1['pending']]}) then {v2['desk_final']} with "
        f"the hand table; class A released; dev-05-s02 armed {s['at']}")
    return w


def scenario_soak_retry(workdir, log=print):
    """qual-01's pilot on the qualification pin: the first soak is refused and the retry accepted; the close is clean
    and the Air judges the same receipt without a REFUSAL."""
    w = World(workdir, freeze2=True)
    w.controller()
    w.queue("qual01-pilot", [w.span(1, "qual-01-s01", "cl-qual-01", L[:6])], role="smoke")
    w.launcher.flags["cq-qual-01-s01-a1"] = ["--soak-refusals", "1"]
    s = w.tick()
    assert _state(s) == "LIVE", s
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    close = _close(w, "cq-qual-01-s01-a1")
    assert [a["attempt"] for a in close["transition"]["soak_attempts"]] == [1, 2], close["transition"]
    v = w.air_final("cq-qual-01-s01-a1")
    assert v is not None and not any(st["code"] == "REFUSAL" for st in v["named_stops"]), v["named_stops"]
    log(f"soak_retry: qual-01-s01 CLOSED_OK, soak attempts refused={[bool(a['refused']) for a in close['transition']['soak_attempts']]}; "
        f"Air: desk_final {v['desk_final']}, stops {[st['code'] for st in v['named_stops']]}, "
        f"hand table triggers {v['hand_table']['triggers']}")
    return w, v


def scenario_l005_timeout(workdir, log=print):
    """dev-04's pilot with L005's G0 timing out: a clean close (a G0 timeout is not a stop); the derived L005 gate
    holds dev-04-s02 with no gate in the standing index; the desk's verdict names the same gates."""
    w = World(workdir)
    w.controller()
    w.queue("dev04-pilot", [w.span(1, "dev-04-s01", "cl-dev-04", L[:6])], role="smoke")
    w.launcher.flags["cq-dev-04-s01-a1"] = ["--g0-timeout", "L005"]
    s = w.tick()
    assert _state(s) == "LIVE", s
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    close = _close(w, "cq-dev-04-s01-a1")
    assert close["gates"] == ["class-a", "L005"], close["gates"]
    w.queue("dev04-rest", [w.span(1, "dev-04-s02", "cl-dev-04", L[6:])])
    w.copy_journals("cq-dev-04-s01-a1")
    w.env.t += 400
    v = w.air_final("cq-dev-04-s01-a1", hand_table=True)
    s = w.tick()
    assert _state(s) == "WAIT" and "HAND_GATE" in _codes(s), s
    w.lead_release("cq-dev-04-s01-a1", "class-a")
    s = w.tick()
    assert _state(s) == "WAIT" and "HAND_GATE" in _codes(s) and "L005" in s["detail"]["detail"], s
    w.lead_release("cq-dev-04-s01-a1", "L005", "RL-165 section 4: dev-03 released >= 4 consumers (synthetic)")
    s = w.drive(lambda s: _state(s) == "LIVE")
    assert s["detail"]["plan_id"] == "cq-dev-04-s02-a1", s
    holds = sorted(h["gate"] for h in v["holds"] if str(h["scope"]).startswith("kit:"))
    log(f"l005_timeout: dev-04-s01 CLOSED_OK with L005 g0 timeout; derived gates {close['gates']}; desk kit holds "
        f"{holds}; dev-04-s02 held through the class A release, armed after the L005 record {s['at']}")
    return w, v


def scenario_redo(workdir, log=print):
    """A dev-05 pilot with a load redo on L002 (no prior spans): span 2 arms; span 3 waits on the k+2 rule until the
    Air's verdict for span 1 is final, which needs the hand table a redo makes mandatory."""
    w = World(workdir, prior=False)
    w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:4])], role="smoke")
    w.launcher.flags["cq-dev-05-s01-a1"] = ["--contaminate", "L002"]
    s = w.tick()
    assert _state(s) == "LIVE", s
    live = w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    receipt = json.loads((live["output"] / cc.RECEIPT).read_text())
    assert receipt["load_redos_used"] == 1, receipt["load_redos_used"]
    v1 = w.air_final("cq-dev-05-s01-a1")
    assert v1 is not None and not v1["desk_final"] and "redo" in json.dumps(v1["hand_table"]), v1["hand_table"]
    w.copy_journals("cq-dev-05-s01-a1")
    w.lead_release("cq-dev-05-s01-a1", "class-a")
    w.queue("dev05-rest", [w.span(1, "dev-05-s02", "cl-dev-05", L[4:8]), w.span(2, "dev-05-s03", "cl-dev-05", L[8:])])
    s = w.drive(lambda s: _state(s) == "LIVE")
    assert s["detail"]["plan_id"] == "cq-dev-05-s02-a1", s
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    w.copy_journals("cq-dev-05-s02-a1")
    w.env.t += 400
    s = w.tick()
    assert "K2_DESK_DEBT" in _codes(s), s
    assert "K2_Q1_DEBT" in _codes(s), s          # RL-173 E: span 1's Q1 record is also owed before span 3
    v2 = w.air_final("cq-dev-05-s01-a1", hand_table=True)
    assert v2["desk_final"], v2["reasons"]
    s = w.tick()
    assert "K2_Q1_DEBT" in _codes(s) and "K2_DESK_DEBT" not in _codes(s), s
    w.q1_record("cq-dev-05-s01-a1")
    s = w.drive(lambda s: _state(s) == "LIVE")
    assert s["detail"]["plan_id"] == "cq-dev-05-s03-a1", s
    log(f"redo: dev-05-s01 L002 redone (1 load redo), CLOSED_OK; Air verdict pending {v1['hand_table']['triggers']}; "
        f"dev-05-s02 armed; dev-05-s03 held on K2_DESK_DEBT until the hand table made span 1 final, then on "
        f"K2_Q1_DEBT until the lead's Q1 record (RL-173 E); armed {s['at']}")
    return w


def scenario_tampered(workdir, log=print):
    """A bundle replaced by an unsigned commit is refused by the Air (no verdict is published); a verdict ref forged
    without the desk's key is refused by the controller's reader (a halt)."""
    w = World(workdir, prior=False)
    ctl = w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
    w.tick()
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    ref = "refs/heads/desk-bundles/cq-dev-05-s01-a1"
    forge = w.w / "forge"
    subprocess.run(["git", "clone", "-q", str(w.origin), str(forge)], check=True, capture_output=True)
    git(forge, "fetch", "-q", "origin", f"{ref}:refs/remotes/b")
    git(forge, "checkout", "-q", "refs/remotes/b")
    summary = forge / "bundle/legs/L002/leg_summary.json"
    doc = json.loads(summary.read_text())
    doc["admitted"] = not doc["admitted"]
    summary.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    git(forge, "commit", "-q", "-am", "tampered")
    git(forge, "push", "-q", "-f", "origin", f"HEAD:{ref}")
    assert w.air_final("cq-dev-05-s01-a1") is None, "the Air refuses a bundle not signed by the controller"
    # A forged verdict on the verdict ref: the right shape and hash, desk_final true, committed without the desk's key.
    verdict = desk_final._finish({"schema": desk_final.VERDICT_SCHEMA, "plan_id": "cq-dev-05-s01-a1",
                                  "queue_id": "cq-syn-dev05-pilot", "span_id": "dev-05-s01", "attempt": 1,
                                  "desk_final": True, "next_arm_hold": False, "holds": [], "mock": False,
                                  "transport": {"signed": True},
                                  "identities": {"manifest_sha256": _close(w, "cq-dev-05-s01-a1")["manifest_sha256"]}})
    (forge / "desk_verdict.json").write_text(json.dumps(verdict, indent=1, sort_keys=True) + "\n")
    git(forge, "checkout", "-q", "--orphan", "forged")
    git(forge, "rm", "-rq", "--cached", ".")
    git(forge, "add", "desk_verdict.json")
    git(forge, "commit", "-q", "-m", "cadence desk verdict cq-dev-05-s01-a1\n\nVerdict-SHA256: "
        f"{verdict['verdict_sha256']}\nDesk-Final: true")
    git(forge, "push", "-q", "origin", "HEAD:refs/heads/cadence-desk-final/cq-dev-05-s01-a1")
    w.copy_journals("cq-dev-05-s01-a1")
    w.env.t += 400
    s = w.tick()
    pages = json.dumps([p["reasons"] for p in ctl.unacked_pages()])
    assert _state(s) in ("PAGED", "HALTED") and "DESK_VERDICT_INVALID" in pages, (s, pages)
    log("tampered: the Air refused the unsigned bundle (no verdict); the controller halted DESK_VERDICT_INVALID on "
        "the unsigned verdict")
    return w


def _remote_refs(w, pattern):
    return git(w.seed, "ls-remote", "origin", pattern).decode().strip()


def scenario_denied_key(workdir, log=print):
    """Mythos N1, Sol R1: a denied key inside an allowed file (``energy_j`` at the receipt's top level, ``samples_w`` in
    span/meter.json) is never signed or pushed: BUNDLE_REFUSED, no ref on the remote, a halt."""
    w = World(workdir, prior=False)
    w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")

    def taint(out):
        receipt = json.loads((out / cc.RECEIPT).read_text())
        receipt["energy_j"] = "SYNTHETIC_DENIED_KEY_CANARY"
        (out / cc.RECEIPT).write_text(json.dumps(receipt))
        meter = json.loads((out / "desk-bundle/span/meter.json").read_text())
        meter["samples_w"] = ["SYNTHETIC_CANARY"]
        (out / "desk-bundle/span/meter.json").write_text(json.dumps(meter))
    w.launcher.edit["cq-dev-05-s01-a1"] = taint
    w.tick()
    w.launcher.finish()
    s = w.tick()
    close = _close(w, "cq-dev-05-s01-a1")
    assert _state(s) == "HALTED" and "BUNDLE_REFUSED" in {r["code"] for r in close["reasons"]}, (s, close["reasons"])
    assert _remote_refs(w, "refs/heads/desk-bundles/*") == "", "nothing reaches the remote"
    log(f"denied_key: {[r['detail'] for r in close['reasons'] if r['code'] == 'BUNDLE_REFUSED']}; nothing pushed; HALTED")
    return w


def scenario_prior_gate(workdir, log=print):
    """Mythos N2: dev-04-s01 was hand-armed (a prior span with its roster and kit). dev-04-s02 holds on the derived
    class A and L005 gates of that prior span until the lead releases both."""
    w = World(workdir)
    w.standing["prior_spans"].append({
        "plan_id": "cq-dev-04-s01-a1", "campaign_id": "cl-dev-04", "block_id": "dev-04", "kit_sha256": w.sha["cl-dev-04"],
        "roster": L[:6], "legs": 6, "mixed": True, "t0": "2026-11-17T00:30:00-08:00",
        "closed": "2026-11-17T03:30:00-08:00", "desk_final": "synthetic hand table"})
    w.record_prior_close(w.standing["prior_spans"][-1])
    w.controller()
    w.queue("dev04-rest", [w.span(1, "dev-04-s02", "cl-dev-04", L[6:])])
    s = w.tick()
    assert _state(s) == "WAIT" and "HAND_GATE" in _codes(s) and "L005" in s["detail"]["detail"], s
    w.lead_release("cq-dev-04-s01-a1", "class-a")
    s = w.tick()
    assert "HAND_GATE" in _codes(s) and "L005" in s["detail"]["detail"], s
    w.lead_release("cq-dev-04-s01-a1", "L005", "RL-165 section 4 (synthetic)")
    s = w.drive(lambda s: _state(s) == "LIVE")
    assert s["detail"]["plan_id"] == "cq-dev-04-s02-a1", s
    log(f"prior_gate: hand-armed dev-04-s01's derived [class-a, L005] held dev-04-s02 until both releases; armed {s['at']}")
    return w


def scenario_recovery(workdir, log=print):
    """Mythos N3, Sol R9: qual-01's pilot is refused (both soaks refused, zero legs). The Air judges it (a REFUSAL that
    holds the next arm). The lead disposes of it as ``rerun`` and appends its re-run to the same smoke queue with
    ``rerun_of``: the re-run arms, closes clean, and the refused attempt never holds line 9."""
    w = World(workdir, freeze2=True)
    ctl = w.controller()
    pilot = w.span(1, "qual-01-s01", "cl-qual-01", L[:6])
    w.queue("qual01-pilot", [pilot], role="smoke")
    w.launcher.flags["cq-qual-01-s01-a1"] = ["--soak-refusals", "2"]
    w.tick()
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "HALTED" and _close(w, "cq-qual-01-s01-a1")["status"] == "REFUSED", s
    v = w.air_final("cq-qual-01-s01-a1")
    assert v is not None and v["next_arm_hold"] and any(st["code"] == "REFUSAL" for st in v["named_stops"]), v
    w.ack_all()
    w.env.t += 400
    assert "DESK_HOLD" in json.dumps([p["reasons"] for p in (ctl.unacked_pages() or [])] + [w.tick()]), "held"
    w.standing["dispositions"].append({"plan_id": "cq-qual-01-s01-a1", "resolution": "rerun",
                                       "record": "the lead: soak refused twice, re-run (synthetic)",
                                       "verdicts": {"offhost": v["verdict_sha256"],
                                                    "mbp": _close(w, "cq-qual-01-s01-a1")["mbp_desk"]["verdict_sha256"]}})
    rerun = dict(pilot, seq=2, span_id="qual-01-s01r", rerun_of="qual-01-s01")
    w.queue("qual01-pilot", [pilot, rerun], role="smoke")
    w.copy_journals("cq-qual-01-s01-a1")
    w.ack_all()
    s = w.drive(lambda s: _state(s) == "LIVE")
    assert s["detail"]["plan_id"] == "cq-qual-01-s01r-a1", s
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    log(f"recovery: refused pilot judged REFUSAL (hold); disposition rerun + appended re-run armed {s['at']} and closed")
    return w


def scenario_repage(workdir, log=print):
    """Mythos N4: a veto pages; acknowledged and withdrawn, the situation clears; a later veto pages again."""
    w = World(workdir)
    ctl = w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6], nb="2026-11-18")], role="smoke")
    veto = {"number": 901, "title": "STOP the campaign", "labels": [{"name": "directive"}],
            "author": {"login": "mpmdw"}, "state": "OPEN"}
    w.issues.append(veto)
    w.tick()
    first = [p["page_id"] for p in ctl.unacked_pages()]
    assert first and first[0].startswith("halt-"), first
    w.ack_all()
    w.issues.clear()
    w.env.t += 300
    w.tick()                      # the veto is gone: the acknowledged page clears
    w.advance_wait(3600)
    w.issues.append(dict(veto, number=907, title="STOP again"))
    w.tick()
    second = [p["page_id"] for p in ctl.unacked_pages()]
    assert second and second[0] != first[0], (first, second)
    assert any(r['code'] == 'VETO_OPEN' and '907' in r['detail']
               for p in ctl.unacked_pages() for r in p['reasons']), ctl.unacked_pages()
    log(f"repage: veto paged {first[0]}; acknowledged and cleared; a new veto paged {second[0]}")
    return w


def scenario_night_window(workdir, log=print):
    """Mythos N5, N15, Sol R2: a W1/C/T window (night agents, no desk fence). While it is loaded the controller is quiet:
    no network, no fence. When it goes, its close is observed with its restore unproven: a halt until note-run records
    its Check, then the 1,200 s floor from the observed close."""
    w = World(workdir)
    ctl = w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
    w.env.night_labels = ["com.joulewise.night.w1"]
    fetch = ctl.git.fetch_audit
    ctl.git.fetch_audit = lambda: (_ for _ in ()).throw(AssertionError("network inside a v4 window"))
    for _ in range(3):
        s = w.tick()
        assert _state(s) == "WAIT" and s["detail"]["quiet"] and _codes(s) == {"NIGHT_AGENT"}, s
        w.env.t += 300
    w.env.launchctl_rc = 5
    s = w.tick()
    assert _codes(s) == {"NIGHT_UNKNOWN"}, s      # an unreadable census is not "no window"
    w.env.launchctl_rc, w.env.night_labels = 0, []
    ctl.git.fetch_audit = fetch
    s = w.tick()
    assert "FOREIGN_CLOSE_UNPROVEN" in json.dumps([p["reasons"] for p in ctl.unacked_pages()]), s
    closed = w.env.now()
    with contextlib.redirect_stdout(io.StringIO()):
        cc.cmd_note_run(w.cfg, type("A", (), {"run_id": "night:com.joulewise.night.w1", "kind": "v4", "t0": closed - 900,
                                              "closed": closed, "restore_ok": "yes",
                                              "evidence": "RUN_STATE n: the window's Check, every restore line OK"}))
    w.ack_all()
    w.env.t += 60
    s = w.tick()
    assert "GAP" in _codes(s), s
    w.advance_wait(law.GAP_AFTER_OTHER_S)
    s = w.tick()
    assert _state(s) == "LIVE", s
    log(f"night_window: quiet while loaded (no network); NIGHT_UNKNOWN on a failed read; after it: unproven until "
        f"note-run, then the 1,200 s floor; armed {s['at']}")
    return w


def scenario_actions_watcher(workdir, log=print):
    """RL-173 C.4: line 7 by the GitHub Actions watcher. Each arm reads its latest completed run through the API; that
    run must have succeeded and have started after the previous span's close. A failed read is a wait, a failed run a
    halt; the run is bound into the arm record."""
    w = World(workdir, prior=False)
    w.cfg.update(watcher_kind="actions", watcher_name="mbp-watcher.yml")
    ctl = w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
    w.watcher_runs.append("unreadable")
    s = w.tick()
    assert _state(s) == "WAIT" and "WATCHER_UNREADABLE" in _codes(s), s
    w.watcher_ran()
    s = w.tick()
    assert _state(s) == "LIVE", s
    intent = json.loads((Path(w.cfg["state_dir"]) / "spans/cq-dev-05-s01-a1/intent.json").read_text())
    assert intent["watcher"]["kind"] == "actions" and intent["watcher"]["run"]["id"] == 7001, intent["watcher"]
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    closed = _close(w, "cq-dev-05-s01-a1")["closed_epoch"]
    w.queue("dev05-rest", [w.span(1, "dev-05-s02", "cl-dev-05", L[6:])])
    w.copy_journals("cq-dev-05-s01-a1")
    w.air_final("cq-dev-05-s01-a1", hand_table=True)
    w.lead_release("cq-dev-05-s01-a1", "class-a")
    w.env.t += 400
    s = w.tick()
    assert _state(s) == "WAIT" and "WATCHER_NOT_NEWER" in _codes(s), s      # the run is from before the close
    w.watcher_ran(conclusion="failure", started=closed + 60)
    s = w.tick()
    assert "WATCHER_FAILED" in json.dumps([p["reasons"] for p in ctl.unacked_pages()]), s
    w.ack_all()
    w.watcher_ran(started=closed + 120)
    s = w.drive(lambda s: _state(s) == "LIVE")
    intent = json.loads((Path(w.cfg["state_dir"]) / "spans/cq-dev-05-s02-a1/intent.json").read_text())
    assert intent["watcher"]["run"]["id"] == 7003 and intent["leases"]["watcher"] > closed, intent["watcher"]
    log(f"actions_watcher: unreadable -> WAIT; run 7001 bound to dev-05-s01; after the close WATCHER_NOT_NEWER, a failed "
        f"run halted WATCHER_FAILED; run 7003 (started after the close) armed dev-05-s02 {s['at']}")
    return w


OFFLOAD_TOOL = r'''
import json, sys, time, os
from datetime import datetime, timezone
plan_id, output, marker, flag = sys.argv[1:5]
if os.path.exists(flag):
    print("synthetic offload: upload not confirmed", file=sys.stderr)
    sys.exit(7)
if os.path.exists(marker):
    sys.exit(0)    # an idempotent replay; the controller independently validates the existing marker
doc = {"schema": "joulewise.offload_marker.v1", "plan_id": plan_id, "source": output, "manifest_sha256": "a" * 64,
       "manifest_files": 12, "ciphertext_sha256": "b" * 64, "ciphertext_bytes": 1048576, "provider": "synthetic cloud",
       "remote_path": "offload/" + plan_id + ".enc",
       "upload": {"confirmed": True, "readback": "sha256", "value": "b" * 64, "evidence": "synthetic readback"},
       "verified": True, "key_second_copy": "synthetic vault",
       # the synthetic clock: just after the span's receipt (the real tool writes its own time)
       "written_at": datetime.fromtimestamp(os.stat(os.path.join(output, "runner_receipt.json")).st_mtime + 1,
                                            timezone.utc).isoformat()}
with open(marker, "x") as handle:
    json.dump(doc, handle)
'''


def scenario_offload(workdir, log=print):
    """RL-173 A: the controller runs the offload tool in the close interval (``offload_argv``) and reads only its exit and
    its marker. A failed offload holds the next arm and F0 too (A.7): OFFLOAD_FAILED, with an F0 fallback configured
    and due, and no F0 page. A marker that does not verify (A.2) is the same halt. The lead's re-run of the tool writes
    a verified marker and the next span arms."""
    w = World(workdir, prior=False)
    tool, flag = w.w / "offload_tool.py", w.w / "offload-fails"
    tool.write_text(OFFLOAD_TOOL)
    w.cfg["offload_argv"] = [sys.executable, "-I", str(tool), "{plan_id}", "{output}", "{marker}", str(flag)]
    w.standing["fallback"] = [{"kind": "F0", "standing_item": "item 346 (synthetic)", "worst_case_s": 12180}]
    ctl = w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
    flag.write_text("fail\n")
    w.tick()
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED" and _close(w, "cq-dev-05-s01-a1")["offload"]["rc"] == 7, s
    w.queue("dev05-rest", [w.span(1, "dev-05-s02", "cl-dev-05", L[6:], nb="2026-11-19")])
    for _ in range(cc.OFFLOAD_ATTEMPTS + 1):    # retried in the close interval, then held (gate 3, Mythos T14)
        w.env.t += 400
        s = w.tick()
        pages = json.dumps([p["reasons"] for p in ctl.unacked_pages()])
        if "OFFLOAD_FAILED" in pages:
            break
    assert "OFFLOAD_FAILED" in pages and "FALLBACK_F0_DUE" not in pages, pages
    assert _close(w, "cq-dev-05-s01-a1")["offload"]["attempts"] == cc.OFFLOAD_ATTEMPTS
    w.ack_all()
    marker = Path(w.cfg["copy_marker_dir"]) / "cq-dev-05-s01-a1.ok"
    out1 = json.loads((Path(w.cfg["state_dir"]) / "spans/cq-dev-05-s01-a1/intent.json").read_text())["output"]
    bad = offload_marker("cq-dev-05-s01-a1", w.env.now(), out1)
    bad["upload"] = {**bad["upload"], "value": "f" * 64}              # a readback that is not the ciphertext's
    marker.write_text(json.dumps(bad))
    w.env.t += 300
    s = w.tick()
    assert _state(s) in ("HALTED", "PAGED") and "OFFLOAD_FAILED" in json.dumps(s), s   # the same episode: no re-page
    assert "readback" in json.dumps(law.offload_marker_problems(bad, "cq-dev-05-s01-a1", w.env.now(), source=out1))
    assert not any(p["kind"] == "FALLBACK_F0_DUE" for p in ctl.unacked_pages())
    w.ack_all()
    marker.unlink()
    flag.unlink()
    subprocess.run(w.cfg["offload_argv"][:3] + ["cq-dev-05-s01-a1", out1, str(marker), str(flag)], check=True)
    w.env.t += 300
    s = w.tick()
    assert "OFFLOAD_FAILED" not in json.dumps(s) and "OFFLOAD_FAILED" not in json.dumps(
        [p["reasons"] for p in ctl.unacked_pages()]), s
    # Recovery is a controller-observed tool run too: the floor starts at its completion (gate 4 F4).
    if "GAP" in json.dumps(s):
        w.env.t += law.GAP_AFTER_CAMPAIGN_S + 1
        s = w.tick()
    assert any(p["kind"] == "FALLBACK_F0_DUE" for p in ctl.unacked_pages()), s   # F0 only once copy and floor pass
    log(f"offload: the tool failed in the close interval (rc 7): OFFLOAD_FAILED held every arm and F0 (no F0 page); a "
        f"marker with a wrong readback held the same; the lead's re-run wrote a verified marker, and only then was F0 "
        f"due ({s['state']} {sorted(_codes(s))})")
    return w


def scenario_l002_timeout(workdir, log=print):
    """RL-161, RL-173 E: dev-03's pilot with L002's G0 timing out. Nothing arms after it - not dev-03's remainder, and
    not another campaign's ready pilot - until the lead's L002 release record (after the research lead's ruling)."""
    w = World(workdir)
    ctl = w.controller()
    w.queue("dev03-pilot", [w.span(1, "dev-03-s01", "cl-dev-03", L[:3])], role="smoke")
    w.launcher.flags["cq-dev-03-s01-a1"] = ["--g0-timeout", "L002"]
    w.tick()
    w.launcher.finish()
    s = w.tick()
    close = _close(w, "cq-dev-03-s01-a1")
    assert _state(s) == "CLOSED" and close["gates"] == ["class-a", "L002"] and close["g0_unreleased"] == ["L002"], close
    w.copy_journals("cq-dev-03-s01-a1")
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
    w.env.t += 400
    s = w.tick()
    pages = json.dumps([p["reasons"] for p in ctl.unacked_pages()])
    assert "L002_TIMEOUT" in pages and _state(s) != "LIVE", (s, pages)
    w.ack_all()
    w.lead_release("cq-dev-03-s01-a1", "L002", "RL-17x: the research lead's ruling on the L002 timeout (synthetic)")
    s = w.drive(lambda s: _state(s) == "LIVE")
    assert s["detail"]["plan_id"] == "cq-dev-05-s01-a1", s
    log(f"l002_timeout: dev-03-s01 closed with L002 timed out; L002_TIMEOUT held dev-05's ready pilot too; after the "
        f"lead's L002 record dev-05-s01 armed {s['at']}")
    return w


def scenario_fence(workdir, log=print):
    """RL-173 E: the controller holds its own fence continuously from startup through arm and close while a queue is
    live. At startup (before any network), at every waiting tick, at the arm (the launcher replaces it atomically) and
    from the wrapper's unlink (the close tick takes it before anything else) to the next arm."""
    w = World(workdir, prior=False)
    ctl = w.controller()
    root = Path(w.cfg["custody_root"])
    mine = ctl.standing_purpose()

    def held():
        cur = cc.fence.read_fence(root)
        return cur is not None and cur["purpose"] == mine and cur["pid"] == ctl.pid
    fetch = ctl.git.fetch_audit
    seen = []

    def watched_fetch():
        seen.append(held())          # the fence is already held when the first network work starts
        return fetch()
    ctl.git.fetch_audit = watched_fetch
    assert ctl.startup_fence() == "held" and held()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6], nb="2026-11-18")], role="smoke")
    for _ in range(3):
        s = w.tick()
        assert _state(s) == "WAIT" and held(), s
        w.advance_wait(3600)
    w.advance_wait(law.date_start("2026-11-18") + 600 - w.env.now())
    s = w.tick()
    assert _state(s) == "LIVE" and w.launcher.fences_at_launch[-1]["purpose"] == mine, w.launcher.fences_at_launch
    w.launcher.finish()                      # the wrapper unlinks the launch fence
    s = w.tick()                             # the close tick: the fence is taken before the close's work
    assert _state(s) == "CLOSED" and held(), s
    assert all(seen), seen
    log(f"fence: held from startup (before the first fetch), at {len(seen)} network reads, handed atomically to the "
        f"launch, and taken back at the close")
    return w


def scenario_copy_gate(workdir, log=print):
    """Gate 3 (Opus 1): the copy gate is per span. With span 1's offload marker not yet written, a READY v4 session is
    not ceded to (A.3: the copy ends before its soak), and a newer receipt on the host (the session's, an F0's) does
    not dissolve span 1's gate: nothing arms until span 1's own verified marker exists."""
    w = World(workdir, prior=False)
    ctl = w.controller()
    w.queue("dev05-pilot", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
    w.tick()
    w.launcher.finish()
    s = w.tick()
    assert _state(s) == "CLOSED", s
    w.queue("dev05-rest", [w.span(1, "dev-05-s02", "cl-dev-05", L[6:])])
    w.air_final("cq-dev-05-s01-a1", hand_table=True)
    w.lead_release("cq-dev-05-s01-a1", "class-a")
    ready = {"schema": law.SESSION_READY_SCHEMA, "session_id": "r1-slot-1", "by": "lead (synthetic)",
             "ready_at": datetime.fromtimestamp(w.env.now(), law.ZONE).isoformat()}
    w.commit({f"{RD}/sessions/READY-r1-slot-1.json": ready}, "session READY", w.env.now() - 30)
    w.env.t += 400
    s = w.tick()
    assert _state(s) == "WAIT" and _codes(s) == {"JOURNAL_COPY"}, s           # not ceded while span 1 copies
    assert not any(p["kind"] == "V4_SESSION" for p in ctl.unacked_pages())
    w.commit({f"{RD}/sessions/DONE-r1-slot-1.json": {"schema": law.SESSION_DONE_SCHEMA, "session_id": "r1-slot-1"}},
             "session done (synthetic: withdrawn)", w.env.now() - 30)
    newer = w.w / "jw-wt" / "f0-run" / cc.RECEIPT          # a newer receipt on the host (an F0, say)
    newer.parent.mkdir(parents=True)
    newer.write_text("{}\n")
    os.utime(newer, (w.env.now(), w.env.now()))
    w.advance_wait(1300)
    s = w.tick()
    assert _state(s) == "WAIT" and "JOURNAL_COPY" in _codes(s), s             # span 1's gate is not forgotten
    w.copy_journals("cq-dev-05-s01-a1")
    s = w.drive(lambda s: _state(s) == "LIVE")
    assert s["detail"]["plan_id"] == "cq-dev-05-s02-a1", s
    log(f"copy_gate: span 1's missing marker held the READY session's cede and survived a newer receipt; with its "
        f"marker dev-05-s02 armed {s['at']}")
    return w


SCENARIOS = {"clean": scenario_clean, "soak_retry": scenario_soak_retry, "l005_timeout": scenario_l005_timeout,
             "redo": scenario_redo, "tampered": scenario_tampered, "denied_key": scenario_denied_key,
             "prior_gate": scenario_prior_gate, "recovery": scenario_recovery, "repage": scenario_repage,
             "night_window": scenario_night_window, "actions_watcher": scenario_actions_watcher,
             "offload": scenario_offload, "l002_timeout": scenario_l002_timeout, "fence": scenario_fence,
             "copy_gate": scenario_copy_gate}


def run(workdir, log=print):
    for name, fn in SCENARIOS.items():
        fn(Path(workdir) / name, log=log)
    return list(SCENARIOS)


def main(workdir):
    try:
        names = run(workdir)
    except AssertionError as exc:
        print(f"SYNTHETIC FAILED: {exc}")
        return 1
    print(f"SYNTHETIC OK: {', '.join(names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/cadence-synthetic")))
