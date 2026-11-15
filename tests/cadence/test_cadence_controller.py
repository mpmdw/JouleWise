"""The standing-queue controller (scripts/cadence_controller.py): the real end-to-end runs (RL-172 (i) row 5), and a
regression for each controller-side gate finding (Sol 2026-11-15 #800 gate; Mythos #800 gate). Synthetic only: no
host command, no run bundle; the spans are the pinned runners' own mocks."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from joulewise.cadence import desk_transport, standing as law
from scripts import cadence_controller as cc, cadence_controller_synthetic as synth

ROOT = Path(__file__).resolve().parents[2]
HAVE_TOOLS = shutil.which("git") is not None and shutil.which("ssh-keygen") is not None
L = synth.L


def quiet(*_a, **_k):
    pass


class WorldCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def world(self, **kw):
        w = synth.World(Path(self.tmp.name) / "w", **kw)
        w.controller()
        return w

    def pilot_world(self, key="cl-dev-05", **kw):
        w = self.world(**kw)
        sid = "dev-04-s01" if key == "cl-dev-04" else "dev-05-s01"
        w.queue("pilot", [w.span(1, sid, key, L[:6])], role="smoke")
        return w

    def state(self, w, *parts):
        return Path(w.cfg["state_dir"]).joinpath(*parts)

    def pages(self, w):
        return json.dumps([p["reasons"] for p in w.ctl.unacked_pages()])


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class EndToEnd(WorldCase):
    """RL-172 (i) row 5: the controller, the pinned runner, the signed bundle, the real Air desk, the signed verdict."""

    def test_clean_span(self):
        synth.scenario_clean(Path(self.tmp.name) / "clean", log=quiet)

    def test_retried_soak_span(self):
        _w, v = synth.scenario_soak_retry(Path(self.tmp.name) / "soak", log=quiet)
        self.assertTrue(any("retried soak" in t for t in v["hand_table"]["triggers"]), v["hand_table"])

    def test_g0_timeout_l005_span(self):
        _w, v = synth.scenario_l005_timeout(Path(self.tmp.name) / "l005", log=quiet)
        self.assertIn("L005 consumer gate", {h.get("gate") for h in v["holds"]})

    def test_redo_span(self):
        synth.scenario_redo(Path(self.tmp.name) / "redo", log=quiet)

    def test_tampered_bundle_and_verdict(self):
        synth.scenario_tampered(Path(self.tmp.name) / "tampered", log=quiet)


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class BundleProtocol(WorldCase):
    def test_the_pushed_commit_is_exactly_the_format_tree(self):          # Sol 1, Mythos F1
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        self.assertEqual(w.tick()["state"], "CLOSED")
        close = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())
        ref = "refs/remotes/origin/desk-bundles/cq-dev-05-s01-a1"
        synth.git(w.seed, "fetch", "-q", "origin", "+refs/heads/desk-bundles/*:refs/remotes/origin/desk-bundles/*")
        tree = sorted(synth.git(w.seed, "ls-tree", "-r", "--name-only", ref).decode().split())
        self.assertEqual(tree, sorted(["transition.json", "bundle/BUNDLE_MANIFEST.json", "bundle/runner_receipt.json",
                                       "bundle/span_plan.json", "bundle/span/result.json", "bundle/span/meter.json",
                                       *[f"bundle/legs/{x}/leg_summary.json" for x in L[:6]]]))
        transition = json.loads(synth.git(w.seed, "show", f"{ref}:transition.json"))
        self.assertEqual(desk_transport.validate_transition(transition), [])
        self.assertEqual(transition["manifest_sha256"], close["manifest_sha256"])
        subject = synth.git(w.seed, "log", "-1", "--format=%s", ref).decode().strip()
        self.assertEqual(subject, "cadence close bundle cq-dev-05-s01-a1")
        self.assertTrue(desk_transport.verify_signed_commit(str(w.seed), ref, allowed_signers=w.keys["ctl"]["allowed"],
                                                            principal="cadence-controller"))

    def test_an_unexpected_file_is_never_read_or_shipped(self):          # Sol 2
        w = self.pilot_world()
        w.tick()
        live = w.launcher.finish()
        (live["output"] / "desk-bundle" / "meter-samples.txt").write_text("SYNTHETIC-CANARY\n")
        self.assertEqual(w.tick()["state"], "HALTED")
        close = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())
        self.assertIn("BUNDLE_REFUSED", {r["code"] for r in close["reasons"]})
        remote = synth.git(w.seed, "ls-remote", "origin", "refs/heads/desk-bundles/*").decode()
        self.assertEqual(remote.strip(), "")
        self.assertFalse(self.state(w, "spans/cq-dev-05-s01-a1/publish").exists())


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class LiveInterlock(WorldCase):
    def test_a_held_fence_past_its_deadline_alarms_and_never_closes(self):   # Sol 3
        w = self.pilot_world()
        self.assertEqual(w.tick()["state"], "LIVE")
        (w.launcher.live["output"] / cc.RECEIPT).unlink()       # an unfinished runner
        w.ctl.git.fetch_audit = lambda: self.fail("network while the span holds the host")
        w.env.t += 14 * 3600
        self.assertEqual(w.tick()["state"], "LIVE")
        self.assertFalse(self.state(w, "spans/cq-dev-05-s01-a1/close.json").exists())
        self.assertIn("STRANDED_ALARM", self.pages(w))
        with self.assertRaises(cc.NetworkClosed):
            w.ctl.guard("anything")

    def test_no_transport_retry_while_another_run_holds_the_host(self):   # Sol 3
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        w.ctl.git.push_commit = lambda sha, ref: (None, "synthetic outage")
        w.tick()
        self.assertFalse(json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())["pushed"])
        cc.fence.write_fence(Path(w.cfg["custody_root"]), {"purpose": "align-r0:f0", "pid": os.getpid(),
                                                            "deadline": w.env.now() + 9000})
        w.ctl.git.push_commit = lambda sha, ref: self.fail("pushed while a foreign fence was live")
        self.assertEqual(w.tick()["detail"]["codes"], ["SPAN_LIVE"])

    def test_the_standing_fence_is_taken_when_the_launch_fence_goes(self):   # Mythos F14, Sol 15
        w = self.pilot_world()
        w.tick()
        seen = []
        w.ctl.close = lambda rec, stranded=None: seen.append(cc.fence.read_fence(Path(w.cfg["custody_root"]))) or {}
        w.launcher.finish()
        w.tick()
        self.assertTrue(seen and seen[0]["purpose"].startswith(cc.STANDING_FENCE_PREFIX), seen)

    def test_a_foreign_close_is_unproven_until_noted(self):                 # Sol 10
        w = self.pilot_world()
        custody = Path(w.cfg["custody_root"])
        cc.fence.write_fence(custody, {"purpose": "align-r0:f0", "pid": os.getpid(), "deadline": w.env.now() + 9000})
        self.assertEqual(w.tick()["detail"]["codes"], ["SPAN_LIVE"])
        cc.fence.clear_owned(custody, "align-r0:f0")
        w.env.t += 1300
        self.assertIn(w.tick()["state"], ("PAGED", "HALTED"))
        self.assertIn("FOREIGN_CLOSE_UNPROVEN", self.pages(w))
        with contextlib.redirect_stdout(io.StringIO()):
            cc.cmd_note_run(w.cfg, type("A", (), {"run_id": "align-r0:f0", "kind": "F0", "t0": w.env.now() - 9000,
                                                  "closed": w.env.now() - 1300, "restore_ok": "yes",
                                                  "evidence": "RUN_STATE 999 Check: every restore line OK"}))
        w.ack_all()
        self.assertEqual(w.tick()["state"], "LIVE")


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class FreshAuthority(WorldCase):
    def hook_prep(self, w, action):
        check = w.ctl.preparer.check

        def wrapped(*a, **k):
            action()
            return check(*a, **k)
        w.ctl.preparer.check = wrapped

    def test_a_veto_issued_during_preparation_stops_the_arm(self):        # Sol 4
        w = self.pilot_world()
        self.hook_prep(w, lambda: w.issues.append({"number": 9, "title": "STOP", "labels": [{"name": "directive"}],
                                                   "author": {"login": "mpmdw"}, "state": "OPEN"}))
        self.assertNotEqual(w.tick()["state"], "LIVE")
        self.assertEqual(w.launcher.launched, [])
        self.assertIn("VETO_OPEN", self.pages(w))

    def test_a_session_ready_during_preparation_cedes(self):              # Sol 4
        w = self.pilot_world()
        self.hook_prep(w, lambda: w.commit({f"{synth.RD}/sessions/READY-r1-slot-1.json": {
            "schema": law.SESSION_READY_SCHEMA, "session_id": "r1-slot-1", "by": "lead",
            "ready_at": "2026-11-17T07:59:00-08:00"}}, "ready", w.env.now() - 5))
        w.tick()
        self.assertEqual(w.launcher.launched, [])
        self.assertIn("V4_SESSION_READY", self.pages(w))

    def test_a_watcher_stamp_gone_stale_during_preparation_halts(self):   # Sol 4
        w = self.pilot_world()
        stale = {"schema": law.WATCHER_STAMP_SCHEMA, "watcher": synth.WATCHER, "by": "lead",
                 "observed_live_at": "2026-11-16T07:00:00-08:00"}
        self.hook_prep(w, lambda: w.commit({f"{synth.RD}/watcher-stamp.json": stale}, "stale stamp", w.env.now() - 5))
        w.tick()
        self.assertEqual(w.launcher.launched, [])
        self.assertIn("WATCHER_STALE", self.pages(w))

    def test_the_lease_binds_the_date_and_the_actual_t0_is_recorded(self):   # Sol 4, Mythos F10, F19
        w = self.pilot_world()
        w.tick()
        intent = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/intent.json").read_text())
        self.assertLessEqual(intent["lease_until"], law.date_end("2026-11-17") - law.MIDNIGHT_MARGIN_S)
        self.assertLessEqual(intent["lease_until"], intent["decided_epoch"] + cc.LEASE_S)
        w.launcher.finish()
        w.tick()
        close = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/close.json").read_text())
        arm = json.loads(self.state(w, "spans/cq-dev-05-s01-a1/arm.json").read_text())
        receipt = json.loads((Path(arm["output"]) / cc.RECEIPT).read_text())
        self.assertEqual(close["transition"]["t0_epoch"], receipt["started"]["epoch_s"])   # the runner's own t0

    def test_an_expired_lease_is_refused_by_the_arm_child(self):          # Sol 4
        w = self.pilot_world()
        launch = w.launcher.launch
        w.launcher.launch = lambda req: launch({**req, "lease_until": w.env.now() - 1})
        self.assertEqual(w.tick()["state"], "HALTED")
        self.assertIn("LAUNCH_REFUSED", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_host_clock_off_the_servers_halts(self):                    # Mythos F23
        w = self.pilot_world()
        w.ctl.clock = lambda: w.env.now() + 600
        w.tick()
        self.assertIn("CLOCK_SKEW", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_the_standing_notice_line_posts_before_the_launch(self):      # Mythos F16
        w = self.pilot_world()
        self.assertEqual(w.tick()["state"], "LIVE")
        self.assertEqual([n[0] for n in w.notices], [900])
        self.assertIn("cq-dev-05-s01-a1", w.notices[0][1])

    def test_no_notice_line_no_arm(self):                                  # Mythos F16
        w = self.pilot_world()
        w.ctl.notice = lambda issue, text: False
        self.assertEqual(w.tick()["state"], "WAIT")
        self.assertEqual(w.launcher.launched, [])


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class QueueAuthority(WorldCase):
    def test_a_force_pushed_rewrite_of_the_audit_branch_halts(self):      # Mythos F4
        w = self.world()
        w.queue("dev05", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6], nb="2026-11-18")], role="smoke")
        self.assertIn("NOT_BEFORE", w.tick()["detail"]["codes"])   # read and remembered
        path = w.seed / synth.RD / "queues/QUEUE-dev05.json"
        doc = json.loads(path.read_text())
        doc["spans"][0]["legs"], doc["spans"][0]["not_before"] = L[6:12], "2026-11-17"
        path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
        synth.git(w.seed, "commit", "-q", "-a", "--amend", "-m", "rewrite", epoch=w.env.now() - 5)
        synth.git(w.seed, "push", "-q", "-f", "origin", f"HEAD:refs/heads/{synth.AUDIT}")
        w.env.t += 600
        w.tick()
        self.assertIn("AUDIT_REWRITTEN", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_missing_listed_queue_halts_while_another_could_arm(self):  # Sol 5
        w = self.world()
        w.standing["queues"].append({"path": f"{synth.RD}/queues/QUEUE-gone.json", "role": "standing"})
        w.queue("dev05", [w.span(1, "dev-05-s01", "cl-dev-05", L[:6])], role="smoke")
        w.tick()
        self.assertIn("QUEUE_MISSING", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_ready_session_silences_the_network_until_acknowledged(self):   # Mythos F5
        w = self.pilot_world()
        w.commit({f"{synth.RD}/sessions/READY-r1-slot-1.json": {
            "schema": law.SESSION_READY_SCHEMA, "session_id": "r1-slot-1", "by": "lead",
            "ready_at": "2026-11-17T07:00:00-08:00"}}, "ready", w.env.now() - 5)
        self.assertEqual(w.tick()["state"], "PAGED")
        w.ctl.git.fetch_audit = lambda: self.fail("network while ceded")
        for _ in range(3):
            w.env.t += 60
            self.assertTrue(w.tick()["detail"].get("silent"))
        self.assertIsNone(cc.fence.read_fence(Path(w.cfg["custody_root"])))


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class BoundsAndLedger(WorldCase):
    def test_an_arm_internal_wait_pages_after_its_bound(self):            # Mythos F7
        w = self.pilot_world()

        def agent(kind, allowed=()):
            p = synth.clean_proof(kind)
            if kind == "arm":
                p["lines"]["agents"] = {"ok": False, "detail": "4242 claude"}
            return p
        w.ctl.proof = agent
        self.assertEqual(w.tick()["detail"]["codes"], ["AGENT_PRESENT"])
        w.env.t += law.STALL_SHORT_S + 60
        self.assertEqual(w.tick()["state"], "PAGED")
        self.assertIn("WAIT_STALL", self.pages(w))

    def test_the_ledger_records_failed_prerequisites_and_refusals(self):  # Sol 14
        w = self.pilot_world()

        def bad(kind, allowed=()):
            p = synth.clean_proof(kind)
            p["lines"]["powermode"] = {"ok": False, "detail": "powermode 2"}
            return p
        w.ctl.proof = bad
        self.assertEqual(w.tick()["state"], "HALTED")
        doc = json.loads(self.state(w, "critical-path/dev-05-s01.json").read_text())
        self.assertIsNone(doc["ready_all"])
        self.assertIsNone(doc["prereqs"]["HOST_PROOF_FAILED"]["ready_at"])
        self.assertIsNotNone(doc["prereqs"]["PREPARE"]["ready_at"])
        self.assertIn("HOST_PROOF_FAILED", doc["refusal"] or "")

    def test_no_signing_key_halts_before_any_launch(self):                 # Mythos F11
        w = self.pilot_world()
        os.unlink(w.cfg["signing_key"])
        self.assertEqual(w.tick()["state"], "HALTED")
        self.assertIn("SIGNING_UNAVAILABLE", self.pages(w))
        self.assertEqual(w.launcher.launched, [])

    def test_a_journal_copy_marker_is_needed_after_a_campaign_close(self):   # Sol 11
        w = self.pilot_world()
        w.tick()
        w.launcher.finish()
        w.tick()
        w.queue("rest", [w.span(1, "dev-05-s02", "cl-dev-05", L[6:])])
        w.lead_release("cq-dev-05-s01-a1", "class-a")
        w.env.t += 400
        self.assertIn("JOURNAL_COPY", w.tick()["detail"]["codes"])
        w.copy_journals("cq-dev-05-s01-a1")
        self.assertEqual(w.drive(lambda s: s["state"] == "LIVE")["detail"]["plan_id"], "cq-dev-05-s02-a1")


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class Restart(WorldCase):
    def test_restart_adopts_a_launched_span_and_never_relaunches(self):
        w = self.pilot_world()
        self.assertEqual(w.tick()["state"], "LIVE")
        self.state(w, "spans/cq-dev-05-s01-a1/arm.json").unlink()   # crash before the record
        calls = []
        launch = w.launcher.launch
        w.launcher.launch = lambda req: calls.append(req) or launch(req)
        w.controller()
        self.assertEqual(w.tick()["state"], "LIVE")
        w.launcher.finish()
        self.assertEqual(w.tick()["state"], "CLOSED")
        self.assertEqual(calls, [])

    def test_a_launch_fence_without_output_is_waited_for_not_adopted(self):   # Mythos F21
        w = self.pilot_world()
        w.tick()
        live = w.launcher.live
        self.state(w, "spans/cq-dev-05-s01-a1/arm.json").unlink()
        moved = live["output"].with_name(live["output"].name + ".hidden")
        live["output"].rename(moved)
        w.controller()
        self.assertEqual(w.tick()["state"], "WAIT")
        self.assertFalse(self.state(w, "spans/cq-dev-05-s01-a1/arm.json").exists())
        moved.rename(live["output"])
        self.assertEqual(w.tick()["state"], "LIVE")

    def test_restart_with_no_trace_of_a_launch_halts(self):
        w = self.pilot_world()
        w.launcher.launch = lambda req: (_ for _ in ()).throw(SystemExit("crash inside the launch"))
        with self.assertRaises(SystemExit):
            w.tick()
        calls = []
        w.launcher.launch = lambda req: calls.append(req)
        w.controller()
        self.assertEqual(w.tick()["state"], "HALTED")
        self.assertEqual(calls, [])
        self.assertIn("ARM_INDETERMINATE", self.pages(w))


class ArmChild(unittest.TestCase):
    """The arm child: the atomic fence transfer, the lease, the pin's own deadline, and a foreign fence refused."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "repo/scripts").mkdir(parents=True)
        shutil.copy(ROOT / "scripts/launch_align_r0.py", self.tmp / "repo/scripts/launch_align_r0.py")
        (self.tmp / "repo/scripts/cadence_legs_runner.py").write_text(
            "def launch_deadline(plan):\n    return plan['t0'] + 1000.0\n")
        (self.tmp / "repo/scripts/launch_cadence_span.py").write_text(
            "import json, os, sys, time\nfrom pathlib import Path\nfrom scripts import launch_align_r0 as base\n"
            "def cadence_plan(kit, legs=None, batch_window=None, t0=None):\n    return {'t0': 5000.0}\n"
            "def main(argv):\n"
            "    root = Path(argv[argv.index('--custody-root') + 1]); pid = int(argv[argv.index('--magistrate-pid') + 1])\n"
            "    with base.fence_lock(root):\n"
            "        cur = base.read_fence(root)\n"
            "        if cur and base.pid_alive(cur['pid']):\n"
            "            print('active fence', file=sys.stderr); return 2\n"
            "        existed = (root / base.FENCE_NAME).exists()\n"
            "        base.write_fence(root, {'purpose': 'align-r0:t', 'pid': pid, 'deadline': 4e9})\n"
            "    (root / 'argv.json').write_text(json.dumps({'argv': argv, 'fence_existed_at_write': existed}))\n"
            "    print(json.dumps({'fence': {'purpose': 'align-r0:t'}, 'next': 'exit the magistrate session now'}))\n"
            "    return 0\n")
        self.custody = self.tmp / "custody"
        self.custody.mkdir()

    def run_child(self, lease=4e9):
        req = {"repo": str(self.tmp / "repo"), "python": sys.executable, "kit": "/k.json", "legs": "L001,L002",
               "batch_window": None, "output": "/o", "custody_root": str(self.custody), "lease_until": lease,
               "standing_purpose": "cadence-controller:abc", "controller_pid": os.getpid()}
        return subprocess.run([sys.executable, "-I", "-B", "-c", cc.ARM_CHILD, json.dumps(req)], capture_output=True,
                              text=True, cwd=self.tmp / "repo")

    def test_the_standing_fence_is_replaced_atomically(self):            # Sol 15
        cc.fence.write_fence(self.custody, {"purpose": "cadence-controller:abc", "pid": os.getpid(), "deadline": 4e9})
        done = self.run_child()
        self.assertEqual(done.returncode, 0, done.stderr)
        rec = json.loads((self.custody / "argv.json").read_text())
        self.assertTrue(rec["fence_existed_at_write"], "the controller's fence stood until the launch fence replaced it")
        argv = rec["argv"]
        child = json.loads(done.stdout.splitlines()[-1])
        self.assertEqual(argv[argv.index("--magistrate-pid") + 1], str(child["arm_child_pid"]))
        self.assertEqual(float(argv[argv.index("--deadline") + 1]), 5000.0 + 1000.0 + 60)   # Mythos F10
        self.assertNotIn("--batch-window", argv)
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "align-r0:t")

    def test_a_foreign_fence_is_refused_untouched(self):
        cc.fence.write_fence(self.custody, {"purpose": "align-r0:other", "pid": os.getpid(), "deadline": 4e9})
        done = self.run_child()
        self.assertEqual(done.returncode, 3)
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "align-r0:other")
        self.assertFalse((self.custody / "argv.json").exists())

    def test_an_expired_lease_launches_nothing(self):                    # Sol 4
        cc.fence.write_fence(self.custody, {"purpose": "cadence-controller:abc", "pid": os.getpid(), "deadline": 4e9})
        done = self.run_child(lease=time.time() - 1)
        self.assertEqual(done.returncode, 4)
        self.assertFalse((self.custody / "argv.json").exists())
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "cadence-controller:abc")


class FakeRunEnv(cc.Env):
    def __init__(self, table, freq=0):
        self.table, self.freq, self.t = table, freq, 1.8e9

    def now(self):
        return self.t

    def run(self, argv, **_kw):
        key = " ".join(str(a) for a in argv)
        for prefix, result in self.table.items():
            if key.startswith(prefix):
                return result
        return cc.Result(1, "", "")       # pgrep: none

    def kernel_frequency(self):
        return {"raw_word": self.freq}


class HostProofParsing(unittest.TestCase):
    GOOD = {"/usr/bin/pmset -g batt": cc.Result(0, "Now drawing from 'AC Power'\n -InternalBattery-0 100%\n", ""),
            "/usr/bin/pmset -g": cc.Result(0, "System-wide power settings:\nCurrently in use:\n powermode            0\n", ""),
            "/usr/bin/sudo -n /usr/sbin/systemsetup": cc.Result(0, "Network Time: Off\n", ""),
            "/usr/bin/sudo -n -l": cc.Result(0, "/bin/kill\n", ""),
            "/bin/launchctl list": cc.Result(0, "PID\tStatus\tLabel\n-\t0\tcom.apple.x\n", ""),
            "/bin/zsh": cc.Result(0, "verify OK\n", "")}

    def cfg(self, tmp):
        return {"high_power_marker": str(Path(tmp) / "marker"), "custody_root": str(Path(tmp) / "custody"),
                "measurement_mode_script": "/x.zsh"}

    def proof(self, table, kind, freq=0):
        with tempfile.TemporaryDirectory() as tmp:
            p = cc.host_proof(self.cfg(tmp), FakeRunEnv(table, freq), kind)
        p["lines"]["signing"] = {"ok": True}
        return p

    def test_clean_host(self):
        self.assertEqual(law.proof_reasons(self.proof(dict(self.GOOD), "arm")["lines"], "arm"), [])

    def test_each_bad_readback(self):
        cases = {"/usr/bin/sudo -n /usr/sbin/systemsetup": cc.Result(0, "Network Time: On\n", ""),
                 "/usr/bin/pmset -g batt": cc.Result(0, "Now drawing from 'Battery Power'\n", ""),
                 "/bin/launchctl list": cc.Result(0, "123\t0\tcom.joulewise.night.plan\n", ""),
                 "/usr/bin/pgrep -u root -x powermetrics": cc.Result(0, "4242\n", ""),
                 "/usr/bin/pgrep -fl km003c": cc.Result(2, "", "pgrep: error"),
                 "/bin/zsh": cc.Result(1, "FAIL spotlight agent loaded\nFAIL agent process present\n", "")}
        for key, result in cases.items():
            table = {key: result, **{k: v for k, v in self.GOOD.items() if k != key}}
            self.assertEqual(law.category(law.proof_reasons(self.proof(table, "close")["lines"], "close")), "halt", key)

    def test_frequency_word_and_marker(self):
        self.assertFalse(self.proof(dict(self.GOOD), "close", freq=397)["lines"]["kernel_frequency"]["ok"])
        with tempfile.TemporaryDirectory() as tmp:
            Path(self.cfg(tmp)["high_power_marker"]).write_text("")
            proof = cc.host_proof(self.cfg(tmp), FakeRunEnv(dict(self.GOOD)), "close")
            self.assertFalse(proof["lines"]["high_power_marker"]["ok"])

    def test_an_agent_at_the_arm_is_a_wait(self):
        table = {"/usr/bin/pgrep -x claude": cc.Result(0, "777\n", ""), **self.GOOD}
        self.assertEqual(law.category(law.proof_reasons(self.proof(table, "arm")["lines"], "arm")), "wait")

    def test_a_full_issue_page_is_unreadable(self):                       # Mythos F22
        page = json.dumps([{"number": i} for i in range(cc.VETO_LIMIT)])
        env = FakeRunEnv({"gh": cc.Result(0, page, "")})
        self.assertIsNone(cc.read_issues({"gh_argv": ["gh"], "repo_slug": "r", "owner_login": "o"}, env, lambda w: None))


class ConfigAndInstall(unittest.TestCase):
    def cfg(self):
        return json.loads((ROOT / "configs/launchd/cadence-controller.config.json.template").read_text()
                          .replace("@@MEASUREMENT_PYTHON@@", "/opt/venv/bin/python3.13"))

    def test_config_template_loads_and_refusals(self):
        base = self.cfg()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.json"
            path.write_text(json.dumps(base))
            self.assertEqual(set(cc.load_config(path)), cc.CONFIG_KEYS)
            saved = os.environ.pop("JW_B5_SYNTHETIC_ONLY", None)
            try:
                for over in ({"git_dir": cc.CANONICAL_ROOT}, {"output_root": base["custody_root"] + "/out"},
                             {"output_root": "/Users/edr/night-custody/x"}, {"hold_standing_fence": "yes"},
                             {"poll_live_s": 2}, {"accept_mock_verdicts": True}):
                    path.write_text(json.dumps({**base, **over}))
                    with self.assertRaises(cc.ConfigError, msg=over):
                        cc.load_config(path)
            finally:
                if saved is not None:
                    os.environ["JW_B5_SYNTHETIC_ONLY"] = saved

    def test_launchd_template_is_a_keepalive_loop(self):
        plist = plistlib.loads((ROOT / "configs/launchd/com.joulewise.cadence-controller.plist.template").read_bytes())
        self.assertIs(plist["KeepAlive"], True)
        self.assertNotIn("StartInterval", plist)
        self.assertNotEqual(plist.get("ProcessType"), "Background")
        self.assertEqual(plist["ProgramArguments"][-3:], ["loop", "--config", "@@CONFIG@@"])

    def test_prompt_names_the_controller_and_its_heartbeat_within_twenty_five_lines(self):   # Mythos F15
        prompt = (ROOT / "docs/process/MAGISTRATE_RELAUNCH_PROMPT.md").read_text()
        self.assertLessEqual(len(prompt.splitlines()), 25)
        self.assertIn("com.joulewise.cadence-controller", prompt)
        self.assertIn("cadence_controller.py ack", prompt)
        self.assertIn("check-heartbeat", prompt)

    def test_heartbeat_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {"state_dir": tmp}
            args = type("A", (), {"max_age": 300})
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cc.cmd_check_heartbeat(cfg, args), 1)
                cc.atomic_json(Path(tmp) / "heartbeat.json", {"pid": 1, "epoch": time.time(), "state": "WAIT"})
                self.assertEqual(cc.cmd_check_heartbeat(cfg, args), 0)


if __name__ == "__main__":
    unittest.main()
