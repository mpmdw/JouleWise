"""The standing-queue controller (scripts/cadence_controller.py): the synthetic launch-to-close run (RL-172 (i)
row 5), restart idempotence, the network guard, the close's stops, the arm child's fence handoff, the host
readback parsing, the config and the launchd template. Synthetic only: no host command, no run bundle."""
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
import unittest

from joulewise.cadence import standing as law
from scripts import cadence_controller as cc, cadence_controller_synthetic as synth, cadence_legs_runner as runner

ROOT = Path(__file__).resolve().parents[2]
HAVE_TOOLS = shutil.which("git") is not None and shutil.which("ssh-keygen") is not None


def quiet(*_a, **_k):
    pass


@unittest.skipUnless(HAVE_TOOLS, "git and ssh-keygen are needed for the synthetic origin")
class SyntheticLaunchToClose(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_full_run_with_consumer_span(self):
        result = synth.run(Path(self.tmp.name) / "w", log=quiet)
        self.assertTrue(result["ok"])
        world = result["world"]
        state = Path(world.cfg["state_dir"])
        for plan_id in ("cq-dev-04-s01-a1", "cq-dev-04-s02-a1", "cq-dev-05-s01-a1"):
            intent = json.loads((state / "spans" / plan_id / "intent.json").read_text())
            arm = json.loads((state / "spans" / plan_id / "arm.json").read_text())
            close = json.loads((state / "spans" / plan_id / "close.json").read_text())
            # condition 8: every transition's record names the queue digest, plan, proofs and decision
            self.assertEqual(arm["queue_sha256"], intent["queue"]["sha256"])
            self.assertTrue(close["pushed"] and close["status"] == "CLOSED_OK")
            self.assertEqual(close["manifest"]["arm_proof_sha256"], intent["arm_proof_sha256"])
            self.assertLessEqual(intent["network_end_epoch"], arm["launch_epoch"])
            # RL-171 at this pin: the launch deadline is worst + one soak retry + 560 s reserves (+ grace)
            plan = runner.legsmod.plan_span(json.loads(Path(intent["kit"]["path"]).read_text()),
                                            t0_epoch=intent["t0_epoch"], windows=[], leg_ids=intent["span"]["legs"],
                                            max_span_s=runner.max_span_s())
            self.assertAlmostEqual(intent["deadline"] - intent["t0_epoch"],
                                   plan["worst_case_s"] + plan["soak_s"] + 560 + cc.LAUNCH_GRACE_S, places=3)
        retried = json.loads((state / "spans/cq-dev-04-s02-a1/close.json").read_text())["manifest"]["soak_attempts"]
        self.assertEqual([a["attempt"] for a in retried], [1, 2])

    def test_restart_adopts_a_launched_span_and_never_relaunches(self):
        world = synth.World(Path(self.tmp.name) / "w")
        ctl = world.controller()
        self.assertEqual(ctl.tick()["state"], "LIVE")
        (Path(world.cfg["state_dir"]) / "spans/cq-dev-04-s01-a1/arm.json").unlink()   # crash before the record
        calls = []
        world.launcher.launch = lambda req: calls.append(req)
        ctl2 = world.controller()
        ctl2.launcher = world.launcher
        status = ctl2.tick()
        self.assertEqual(calls, [])
        self.assertEqual(status["state"], "LIVE")
        self.assertEqual(ctl2.tick()["state"], "LIVE")      # the fence is still the LaunchAgent's
        world.launcher.finish()
        self.assertEqual(ctl2.tick()["state"], "CLOSED")    # the adopted span closes on its receipt
        self.assertEqual(calls, [])

    def test_restart_with_no_trace_of_a_launch_halts(self):
        world = synth.World(Path(self.tmp.name) / "w")
        ctl = world.controller()
        world.launcher.launch = lambda req: (_ for _ in ()).throw(SystemExit("crash inside the launch"))
        with self.assertRaises(SystemExit):
            ctl.tick()
        calls = []
        world.launcher.launch = lambda req: calls.append(req)
        status = world.controller().tick()
        self.assertEqual(calls, [])
        self.assertEqual(status["state"], "HALTED")
        self.assertIn("arm-indeterminate", json.dumps(world.controller().unacked_pages()).replace("ARM_INDETERMINATE",
                                                                                                    "arm-indeterminate"))

    def test_no_network_while_live(self):
        world = synth.World(Path(self.tmp.name) / "w")
        ctl = world.controller()
        ctl.tick()
        with self.assertRaises(cc.NetworkClosed):
            ctl.guard("anything")
        ctl.git.fetch_audit = lambda: self.fail("the live tick fetched")
        ctl.issues = lambda: self.fail("the live tick read issues")
        self.assertEqual(ctl.tick()["state"], "LIVE")

    def test_zero_leg_rows_through_the_close_is_a_stop(self):
        world = synth.World(Path(self.tmp.name) / "w")
        ctl = world.controller()
        ctl.tick()
        live = world.launcher.finish()
        shutil.rmtree(live["output"] / "desk-bundle" / "legs")
        receipt = json.loads((live["output"] / runner.RECEIPT_NAME).read_text())
        receipt["legs"] = []
        (live["output"] / runner.RECEIPT_NAME).write_text(json.dumps(receipt))
        os.utime(live["output"] / runner.RECEIPT_NAME, (live["ended"], live["ended"]))
        status = ctl.tick()
        self.assertEqual(status["state"], "HALTED")
        close = json.loads((Path(world.cfg["state_dir"]) / "spans/cq-dev-04-s01-a1/close.json").read_text())
        self.assertIn("NO_LEG_ROWS", {r["code"] for r in close["reasons"]})
        self.assertTrue(close["pushed"], "a negative result is still an authenticated receipt")
        world.env.t += 3600
        self.assertEqual(ctl.tick()["state"], "PAGED", "nothing arms until the halt is acknowledged")

    def test_unproven_restore_at_the_close_halts(self):
        world = synth.World(Path(self.tmp.name) / "w")
        ctl = world.controller()
        ctl.tick()
        world.launcher.finish()

        def proof(kind, allowed=()):
            p = synth.clean_proof(kind)
            p["lines"]["network_time"] = {"ok": False, "detail": "Network Time: On"}
            return p
        ctl.proof = proof
        self.assertEqual(ctl.tick()["state"], "HALTED")
        close = json.loads((Path(world.cfg["state_dir"]) / "spans/cq-dev-04-s01-a1/close.json").read_text())
        self.assertEqual(close["status"], "CLOSE_UNPROVEN")

    def test_veto_read_fresh_at_the_arm(self):
        world = synth.World(Path(self.tmp.name) / "w")
        world.issues = [{"number": 7, "title": "STOP the campaign", "labels": [{"name": "directive"}],
                         "author": {"login": "mpmdw"}, "state": "OPEN"}]
        ctl = world.controller()
        self.assertEqual(ctl.tick()["state"], "PAGED")
        self.assertIsNone(cc.fence.read_fence(Path(world.cfg["custody_root"])))
        world.issues = None    # a failed read is never "no veto"
        ctl.issues = lambda: None
        for p in ctl.unacked_pages():
            cc.cmd_ack(world.cfg, type("A", (), {"page_id": p["page_id"], "by": "t", "note": "seen"}))
        status = ctl.tick()      # no arm: the read failed; the long wait since the last close pages once
        self.assertIn(status["state"], ("WAIT", "PAGED"))
        self.assertIn("ISSUES_UNREADABLE", json.dumps(status))


    def test_a_foreign_run_is_waited_for_and_its_close_floored(self):
        world = synth.World(Path(self.tmp.name) / "w")
        ctl = world.controller()
        custody = Path(world.cfg["custody_root"])
        custody.mkdir(parents=True, exist_ok=True)
        cc.fence.write_fence(custody, {"purpose": "align-r0:f0", "pid": os.getpid(), "deadline": world.env.t + 9000})
        ctl.git.fetch_audit = lambda: self.fail("no network while another run holds the host")
        self.assertEqual(ctl.tick()["detail"]["reason"], "SPAN_LIVE")
        cc.fence.clear_owned(custody, "align-r0:f0")
        del ctl.git.fetch_audit
        world.env.t += 60
        status = ctl.tick()
        self.assertEqual(status["state"], "WAIT")
        self.assertIn("GAP", status["detail"]["codes"])
        world.env.t += law.GAP_AFTER_OTHER_S
        self.assertEqual(ctl.tick()["state"], "LIVE")


class ArmChild(unittest.TestCase):
    """The arm child clears only the controller's own standing fence, then calls the frozen launcher in-process
    with its own PID as the handoff PID."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "repo/scripts").mkdir(parents=True)
        shutil.copy(ROOT / "scripts/launch_align_r0.py", self.tmp / "repo/scripts/launch_align_r0.py")
        (self.tmp / "repo/scripts/launch_cadence_span.py").write_text(
            "import json, os, sys\nfrom pathlib import Path\nfrom scripts import launch_align_r0 as base\n"
            "def cadence_plan(kit, legs=None, batch_window=None, t0=None):\n    return {}\n"
            "def main(argv):\n"
            "    root = Path(argv[argv.index('--custody-root') + 1]); pid = int(argv[argv.index('--magistrate-pid') + 1])\n"
            "    with base.fence_lock(root):\n"
            "        cur = base.read_fence(root)\n"
            "        if cur and base.pid_alive(cur['pid']):\n"
            "            print('active fence', file=sys.stderr); return 2\n"
            "        base.write_fence(root, {'purpose': 'align-r0:t', 'pid': pid, 'deadline': 4e9})\n"
            "    Path(os.environ.get('ARGV_OUT', root / 'argv.json')).write_text(json.dumps(argv))\n"
            "    print(json.dumps({'fence': {'purpose': 'align-r0:t'}, 'next': 'exit the magistrate session now'}))\n"
            "    return 0\n")
        self.custody = self.tmp / "custody"
        self.custody.mkdir()

    def run_child(self, standing_pid):
        req = {"repo": str(self.tmp / "repo"), "python": sys.executable, "kit": "/k.json", "legs": "L001,L002",
               "batch_window": None, "output": "/o", "custody_root": str(self.custody), "deadline": 4e9,
               "standing_purpose": "cadence-controller:abc", "controller_pid": standing_pid}
        return subprocess.run([sys.executable, "-I", "-B", "-c", cc.ARM_CHILD, json.dumps(req)], capture_output=True,
                              text=True, cwd=self.tmp / "repo")

    def test_clears_the_controller_fence_and_launches(self):
        cc.fence.write_fence(self.custody, {"purpose": "cadence-controller:abc", "pid": os.getpid(), "deadline": 4e9})
        done = self.run_child(os.getpid())
        self.assertEqual(done.returncode, 0, done.stderr)
        argv = json.loads((self.custody / "argv.json").read_text())
        child = json.loads(done.stdout.splitlines()[-1])["arm_child_pid"]
        self.assertEqual(argv[argv.index("--magistrate-pid") + 1], str(child))
        self.assertNotIn("--batch-window", argv)
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "align-r0:t")

    def test_refuses_a_foreign_fence(self):
        cc.fence.write_fence(self.custody, {"purpose": "align-r0:other", "pid": os.getpid(), "deadline": 4e9})
        done = self.run_child(os.getpid())
        self.assertEqual(done.returncode, 3)
        self.assertEqual(cc.fence.read_fence(self.custody)["purpose"], "align-r0:other")
        self.assertFalse((self.custody / "argv.json").exists())


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

    def test_clean_host(self):
        with tempfile.TemporaryDirectory() as tmp:
            proof = cc.host_proof(self.cfg(tmp), FakeRunEnv(dict(self.GOOD)), "arm")
        self.assertEqual(law.proof_reasons(proof["lines"], "arm"), [])

    def test_each_bad_readback(self):
        cases = {"/usr/bin/sudo -n /usr/sbin/systemsetup": cc.Result(0, "Network Time: On\n", ""),
                 "/usr/bin/pmset -g batt": cc.Result(0, "Now drawing from 'Battery Power'\n", ""),
                 "/bin/launchctl list": cc.Result(0, "123\t0\tcom.joulewise.night.plan\n", ""),
                 "/usr/bin/pgrep -u root -x powermetrics": cc.Result(0, "4242\n", ""),
                 "/usr/bin/pgrep -fl km003c": cc.Result(2, "", "pgrep: error"),
                 "/bin/zsh": cc.Result(1, "FAIL spotlight agent loaded\nFAIL agent process present\n", "")}
        for key, result in cases.items():
            table = {key: result, **{k: v for k, v in self.GOOD.items() if k != key}}
            with tempfile.TemporaryDirectory() as tmp:
                proof = cc.host_proof(self.cfg(tmp), FakeRunEnv(table), "close")
            self.assertEqual(law.category(law.proof_reasons(proof["lines"], "close")), "halt", key)

    def test_frequency_word_and_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            proof = cc.host_proof(self.cfg(tmp), FakeRunEnv(dict(self.GOOD), freq=397), "close")
            self.assertFalse(proof["lines"]["kernel_frequency"]["ok"])
            Path(self.cfg(tmp)["high_power_marker"]).write_text("")
            proof = cc.host_proof(self.cfg(tmp), FakeRunEnv(dict(self.GOOD)), "close")
            self.assertFalse(proof["lines"]["high_power_marker"]["ok"])

    def test_an_agent_at_the_arm_is_a_wait(self):
        table = {"/usr/bin/pgrep -x claude": cc.Result(0, "777\n", ""), **self.GOOD}
        with tempfile.TemporaryDirectory() as tmp:
            proof = cc.host_proof(self.cfg(tmp), FakeRunEnv(table), "arm")
        self.assertEqual(law.category(law.proof_reasons(proof["lines"], "arm")), "wait")


class ConfigAndInstall(unittest.TestCase):
    def test_config_refusals(self):
        with tempfile.TemporaryDirectory() as tmp:
            world_cfg = synth.World(Path(tmp) / "w").cfg
            for over in ({"git_dir": cc.CANONICAL_ROOT}, {"output_root": world_cfg["custody_root"] + "/out"},
                         {"output_root": "/Users/edr/night-custody/x"}, {"hold_standing_fence": "yes"}):
                path = Path(tmp) / "c.json"
                path.write_text(json.dumps({**world_cfg, **over}))
                with self.assertRaises(cc.ConfigError, msg=over):
                    cc.load_config(path)
            path.write_text(json.dumps(world_cfg))
            self.assertEqual(cc.load_config(path)["schema"], cc.CONFIG_SCHEMA)

    def test_config_template_is_complete(self):
        text = (ROOT / "configs/launchd/cadence-controller.config.json.template").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.json"
            path.write_text(text.replace("@@MEASUREMENT_PYTHON@@", "/opt/venv/bin/python3.13"))
            cfg = cc.load_config(path)
        self.assertEqual(set(cfg), cc.CONFIG_KEYS)
        self.assertNotEqual(cfg["git_dir"], cc.CANONICAL_ROOT)

    def test_prompt_names_the_controller_within_twenty_five_lines(self):
        prompt = (ROOT / "docs/process/MAGISTRATE_RELAUNCH_PROMPT.md").read_text()
        self.assertLessEqual(len(prompt.splitlines()), 25)
        self.assertIn("com.joulewise.cadence-controller", prompt)
        self.assertIn("cadence_controller.py ack", prompt)

    def test_launchd_template_is_a_keepalive_loop(self):
        raw = (ROOT / "configs/launchd/com.joulewise.cadence-controller.plist.template").read_bytes()
        plist = plistlib.loads(raw)
        self.assertIs(plist["KeepAlive"], True)
        self.assertNotIn("StartInterval", plist)
        self.assertNotEqual(plist.get("ProcessType"), "Background")
        self.assertEqual(plist["ProgramArguments"][-3:], ["loop", "--config", "@@CONFIG@@"])

    def test_heartbeat_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {"state_dir": tmp}
            args = type("A", (), {"max_age": 300})
            self.assertEqual(cc.cmd_check_heartbeat(cfg, args), 1)
            cc.atomic_json(Path(tmp) / "heartbeat.json", {"pid": 1, "epoch": __import__("time").time(), "state": "WAIT"})
            self.assertEqual(cc.cmd_check_heartbeat(cfg, args), 0)


if __name__ == "__main__":
    unittest.main()
