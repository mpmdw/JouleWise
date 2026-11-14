"""scripts/launch_cadence_span.py: fence, claim, LaunchAgent wrapper, outer run, blackout (PR #775 row-1 delta).

The LaunchAgent fixture is ported from tests/test_magistrate_desk_fence.LaunchAgentTests (fake launchctl that
spawns the plist through a fake launchd, fake pmset and pgrep, the REAL run_align_r0_launchagent.sh) and drives
the REAL module file, so a mutant of it is what runs. Safety: the fake ``kill`` signals a PID only when that
process's command line lies inside this fixture's private temporary root; any other PID (a live process of the
host, a recycled PID, a uid passed by a swapped argv) is refused and logged, never signalled. Spotlight PIDs are
synthetic (900000001, 900000002) and only logged. Nothing here contacts launchd, pmset or a real process.
"""
from __future__ import annotations

from datetime import datetime, timedelta
import fcntl
import io
import json
import os
from pathlib import Path
import plistlib
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from joulewise.cadence import legs as legsmod
from scripts import launch_align_r0 as base, launch_cadence_span as cadence_launch
from tests.cadence.test_legs_runner import campaign_kit

SCRIPT = Path(cadence_launch.__file__).resolve()
REPO = SCRIPT.parents[1]
TMP = os.environ.get("TMPDIR")
ZONE = legsmod.LOCAL_ZONE

FAKE_KILL = '''
import os, signal, subprocess, sys
from pathlib import Path
root = Path(os.environ["WP10_FIXTURE_ROOT"])
with (root / "signals.log").open("a") as f: f.write(" ".join(sys.argv[1:]) + "\\n")
if len(sys.argv) != 3 or not sys.argv[1].startswith("-") or not sys.argv[2].isdigit():
    sys.exit(2)
pid = int(sys.argv[2])
if pid in (900000001, 900000002):       # synthetic Spotlight PIDs: log only
    sys.exit(1 if sys.argv[1] == "-CONT" and (root / "cont-fail").exists() else 0)
command = subprocess.run(["/bin/ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True).stdout
if str(root) not in command or pid in (os.getpid(), int(os.environ.get("FIXTURE_TEST_PID", "0"))):
    with (root / "refused-signals.log").open("a") as f: f.write(" ".join(sys.argv[1:]) + "\\n")
    sys.exit(1)                          # never a process outside this fixture
name = sys.argv[1][1:]
os.kill(pid, getattr(signal, "SIG" + name) if not name.isdigit() else int(name))
'''


def epoch(text):
    return datetime.fromisoformat(text).replace(tzinfo=ZONE).timestamp()


def far_window(now=None):
    """A one-off blackout about 12 h from now, so the fixture's span never meets it whatever the wall clock."""
    start = datetime.fromtimestamp(now or time.time(), ZONE) + timedelta(hours=12)
    h = min(start.hour, 22)
    return f"{h:02d}:00-{h:02d}:35"


class Fixture(unittest.TestCase):
    """Per test: a private root with fakes, a stand-in magistrate, a fixture repo whose runner records its argv."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="jw-cadence-launch-fixture-", dir=TMP)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.custody = self.root / "magistrate"
        self.repo = self.root / "measurement"
        (self.repo / "scripts").mkdir(parents=True)
        self.output = self.root / "campaign-out" / "span"
        self.env = {**os.environ, "WP10_FIXTURE_ROOT": str(self.root), "FIXTURE_TEST_PID": str(os.getpid())}
        self.owner = subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(120)"])
        self.addCleanup(self.stop, self.owner)
        self.addCleanup(self.stop_fixture_processes)
        self.launchctl = self.script("launchctl", '''
import json, os, plistlib, signal, subprocess, sys
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
with (root/'launchctl.log').open('a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')
if sys.argv[1]=='bootstrap':
    if (root/'fail-bootstrap').exists(): sys.exit(19)
    job=plistlib.loads(Path(sys.argv[3]).read_bytes())
    (root/'job.json').write_text(json.dumps(job, default=str))
    (root/'service.loaded').write_text(sys.argv[2]+'/'+job['Label'])
    if (root/'no-start').exists(): sys.exit(0)        # loaded, never runs: nobody claims the fence
    subprocess.Popen([sys.executable, str(root/'fake-launchd'), sys.argv[3]],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
else:
    if (root/'fail-bootout').exists():
        print('fixture bootout denied', file=sys.stderr); sys.exit(5)
    if not (root/'service.loaded').exists():
        print('Could not find service', file=sys.stderr); sys.exit(113)
    if (root/'service.loaded').read_text()!=sys.argv[2]:
        print('fixture: wrong service target '+sys.argv[2], file=sys.stderr); sys.exit(6)
    (root/'service.loaded').unlink()
''')
        self.script("fake-launchd", '''
import os, plistlib, subprocess, sys
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
job=plistlib.loads(Path(sys.argv[1]).read_bytes())
with open(job['StandardOutPath'],'w') as out, open(job['StandardErrorPath'],'w') as err:
    p=subprocess.Popen(job['ProgramArguments'], cwd=job['WorkingDirectory'],
                       env={**os.environ, **job['EnvironmentVariables']},
                       stdout=out, stderr=err, start_new_session=True)
(root/'worker.pid').write_text(str(p.pid))
(root/'worker.done').write_text(str(p.wait()))
''')
        self.pmset = self.script("pmset", '''
import os, sys
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
(root/'pmset.argv').write_text(' '.join(sys.argv[1:]))
print("Now drawing from 'AC Power'")
''')
        self.pgrep = self.script("pgrep", '''
import json, os, sys
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
with (root/'pgrep.log').open('a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')
print(900000001 if sys.argv[-1]=='corespotlightd' else 900000002)
''')
        self.kill = self.script("kill", FAKE_KILL)
        (self.repo / "scripts/cadence_legs_runner.py").write_text('''
import json, os, sys, time
from pathlib import Path
root=Path(os.environ['WP10_FIXTURE_ROOT'])
(root/'runner-called.json').write_text(json.dumps({'argv': sys.argv[1:], 'pid': os.getpid()}))
sys.exit(0)
''')
        kit = campaign_kit(legs_per_span=3, end_by_local="18:00", soak_s=60, fixed_overhead_s=60,
                           leg_worst_case_s=1300, redo_quota=0)
        self.kit = self.root / "kit.json"
        self.kit.write_text(json.dumps(kit, indent=1))

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

    def fixture_pids(self):
        out = subprocess.run(["/bin/ps", "-A", "-o", "pid=,command="], capture_output=True, text=True).stdout
        pids = []
        for line in out.splitlines():
            pid, _, command = line.strip().partition(" ")
            if str(self.root) in command and int(pid) != os.getpid():
                pids.append(int(pid))
        return pids

    def stop_fixture_processes(self):
        """Only processes whose command line lies inside this fixture's private root."""
        for pid in self.fixture_pids():
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass

    def script(self, name, code):
        path = self.root / name
        path.write_text(f"#!{sys.executable}\n" + code)
        path.chmod(0o755)
        return path

    def wait_for(self, predicate, timeout=15):
        until = time.monotonic() + timeout
        while time.monotonic() < until:
            if predicate():
                return
            time.sleep(0.03)
        self.fail("timed out waiting for the synthetic LaunchAgent; " + self.logs())

    def logs(self):
        return "\n".join(p.read_text() for p in self.custody.glob("r0-launches/*/stderr.log"))

    def argv(self, *extra, deadline=None, window=None, magistrate=None, output=None):
        return ["launch", "--repo", str(self.repo), "--kit", str(self.kit), "--legs", "L001,L002,L003",
                "--batch-window", window or far_window(), "--output", str(output or self.output),
                "--python-bin", sys.executable, "--custody-root", str(self.custody), "--disk-path", str(self.root),
                "--magistrate-pid", str(magistrate or self.owner.pid),
                "--deadline", str(deadline if deadline is not None else time.time() + 5000),
                "--start-wait-seconds", "3", "--exit-wait-seconds", "30",
                "--launchctl-bin", str(self.launchctl), "--pmset-bin", str(self.pmset),
                "--pgrep-bin", str(self.pgrep), "--kill-bin", str(self.kill), *extra]

    def launch(self, *extra, **kw):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *self.argv(*extra, **kw)], cwd=REPO, env=self.env,
                              capture_output=True, text=True, timeout=60)

    def fence(self):
        return base.read_fence(self.custody)

    def write_fence(self, record):
        self.custody.mkdir(parents=True, exist_ok=True)
        base.write_fence(self.custody, record)


class LaunchAgentTests(Fixture):
    def test_handoff_claim_run_and_clean_close_through_the_real_wrapper(self):
        window, deadline = far_window(), time.time() + 5000
        result = self.launch(window=window, deadline=deadline)
        self.assertEqual(result.returncode, 0, result.stderr + self.logs())
        printed = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(printed["next"], "exit the magistrate session now")
        fence = self.fence()
        # Claimed by the wrapper (F3, F4, F5, F6): another pid, this launch's purpose and deadline.
        self.assertEqual(set(fence), {"purpose", "pid", "deadline"})
        self.assertNotEqual(fence["pid"], self.owner.pid)
        self.assertEqual(fence["purpose"], printed["fence"]["purpose"])
        self.assertEqual(fence["deadline"], float(str(deadline)))                    # F6: the launch deadline
        self.assertFalse((self.root / "runner-called.json").exists(), "runner before the magistrate exited")
        self.owner.terminate(); self.owner.wait(timeout=5)
        self.wait_for(lambda: (self.root / "worker.done").exists())
        self.assertEqual((self.root / "worker.done").read_text(), "0", self.logs())
        called = json.loads((self.root / "runner-called.json").read_text())["argv"]
        self.assertEqual(called[:1], ["run"])
        for flag, value in (("--kit", str(self.kit)), ("--legs", "L001,L002,L003"), ("--batch-window", window),
                            ("--output", str(self.output)), ("--pmset-bin", str(self.pmset))):
            self.assertEqual(called[called.index(flag) + 1], value)
        # Spotlight paused and resumed through the configured pgrep and kill (W2, W3).
        pgrep = [json.loads(x) for x in (self.root / "pgrep.log").read_text().splitlines()]
        self.assertEqual([p[-1] for p in pgrep], ["corespotlightd", "spotlightknowledged"])
        self.assertEqual([p[:2] for p in pgrep], [["-U", str(os.getuid())]] * 2)
        signals = (self.root / "signals.log").read_text().split("\n")
        for pid in ("900000001", "900000002"):
            self.assertIn(f"-STOP {pid}", signals)
            self.assertIn(f"-CONT {pid}", signals)
        self.assertFalse((self.root / "refused-signals.log").exists())
        # Close: the fence is cleared and the wrapper booted out its own service target (W4).
        self.assertIsNone(self.fence())
        self.assertFalse((self.root / "service.loaded").exists(), self.logs())
        self.assertEqual(json.loads((self.root / "job.json").read_text())["ProgramArguments"][2], str(SCRIPT))

    def test_the_job_spec(self):
        (self.root / "no-start").touch()
        self.launch()
        job = json.loads((self.root / "job.json").read_text())
        self.assertEqual(job["ExitTimeOut"], 400)                                    # W5: exactly 2 x 180 + 40
        self.assertEqual(job["ProcessType"], "Interactive")
        self.assertEqual(job["EnvironmentVariables"],                                # W9
                         {"PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin", "LC_ALL": "C"})
        self.assertTrue(job["Label"].startswith("com.joulewise.align-r0."))
        args = job["ProgramArguments"]
        # The wrapper's positional contract (run_align_r0_launchagent.sh): helper python custody purpose
        # magistrate deadline exit_wait pmset disk pgrep kill runner_spec launchctl service_target.
        self.assertEqual(args[:2], ["/bin/bash", str(REPO / "scripts/run_align_r0_launchagent.sh")])
        self.assertEqual(args[2], str(SCRIPT))
        self.assertEqual(args[3], sys.executable)
        self.assertEqual(args[4], str(self.custody))
        self.assertTrue(args[5].startswith("align-r0:"))
        self.assertEqual(args[6], str(self.owner.pid))
        self.assertEqual(args[8], "30.0")
        self.assertEqual(args[9:14], [str(self.pmset), str(self.root), str(self.pgrep), str(self.kill), args[13]])
        self.assertTrue(args[13].endswith("/runner.json"))
        self.assertEqual(args[14], str(self.launchctl))
        self.assertEqual(args[15], f"gui/{os.getuid()}/{job['Label']}")
        spec = json.loads(Path(args[13]).read_text())
        self.assertEqual(spec["kind"], "cadence-legs-v1")

    def test_an_unclaimed_fence_is_a_refusal_and_is_cleared(self):
        # Loaded but never started: nobody but the magistrate holds the fence (F3, F4).
        (self.root / "no-start").touch()
        result = self.launch()
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("did not claim", result.stderr)
        self.assertNotIn("exit the magistrate session now", result.stdout)
        self.assertIsNone(self.fence())
        self.assertFalse((self.root / "service.loaded").exists())

    def test_a_live_fence_refuses_and_is_left_as_found(self):
        other = subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(60)"])
        self.addCleanup(self.stop, other)
        record = {"purpose": "align-r0:someone-else", "pid": other.pid, "deadline": time.time() + 600}
        self.write_fence(record)
        result = self.launch()
        self.assertEqual(result.returncode, 2)
        self.assertIn("active desk fence", result.stderr)                             # F1, F2
        self.assertEqual(self.fence(), record)
        self.assertFalse((self.root / "launchctl.log").exists())

    def test_the_fence_is_published_under_the_fence_lock(self):
        # F7: while another holder has the lock, no fence may appear.
        self.custody.mkdir(parents=True)
        fd = os.open(self.custody / ".desk-fence.lock", os.O_CREAT | os.O_RDWR, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        (self.root / "no-start").touch()
        process = subprocess.Popen([sys.executable, "-B", str(SCRIPT), *self.argv()], cwd=REPO, env=self.env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            until = time.monotonic() + 3
            while time.monotonic() < until:
                self.assertFalse((self.custody / base.FENCE_NAME).exists(), "fence published outside the lock")
                time.sleep(0.05)
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        process.communicate(timeout=30)

    def test_a_failed_bootstrap_clears_the_fence_only_when_bootout_is_proven(self):
        (self.root / "fail-bootstrap").touch()
        result = self.launch()
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(self.fence())                                              # F8: bootout 113 -> cleared
        (self.root / "fail-bootout").touch()
        result = self.launch(output=self.root / "campaign-out" / "span2")
        self.assertEqual(result.returncode, 2)
        fence = self.fence()                                                         # F9: indeterminate -> kept
        self.assertIsNotNone(fence)
        self.assertEqual(fence["pid"], self.owner.pid)

    def test_setup_refusals_publish_nothing(self):
        dead = subprocess.Popen([sys.executable, "-B", "-c", "pass"]); dead.wait()
        bad_kit = self.root / "bad-kit.json"
        kit = json.loads(self.kit.read_text())
        kit["model"] = "benign-only build"                                           # a label the validator refuses
        bad_kit.write_text(json.dumps(kit))
        self.output.mkdir(parents=True)
        cases = (
            ({"output": self.output}, "new record directory"),                                     # F12
            ({"magistrate": dead.pid, "output": self.root / "o1"}, "live magistrate PID"),         # F11
            ({"deadline": time.time() - 5, "output": self.root / "o2"}, "live magistrate PID"),    # F11
            ({"deadline": time.time() + base.MAX_DESK_SECONDS + 600, "output": self.root / "o3"},
             "more than"),                                                                         # F10
        )
        for kw, why in cases:
            with self.subTest(why=why):
                result = self.launch(**kw)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn(why, result.stderr)
        argv = self.argv(output=self.root / "o4")
        argv[argv.index("--kit") + 1] = str(bad_kit)
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *argv], cwd=REPO, env=self.env,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 2)                                       # K3: the kit is validated
        self.assertIn("condition label", result.stderr)
        self.assertFalse((self.root / "launchctl.log").exists())
        self.assertFalse(self.custody.exists() and any(self.custody.iterdir()))


class BlackoutTests(Fixture):
    """The launch-time plan judges the blackout on an injected clock (B1, B3, B7), with the committed
    cl-dev-01 kit and the pilot roster: worst case 16,650 s."""

    def main_at(self, when, window="02:00-02:35", tag="o"):
        now = epoch(when)
        argv = self.argv(deadline=now + 18110, window=window, output=self.root / f"out-{tag}")
        argv[argv.index("--kit") + 1] = str(REPO / "docs/process/cadence/kits/cl-dev-01.json")
        if window is None:
            i = argv.index("--batch-window"); del argv[i:i + 2]
        (self.root / "fail-bootstrap").touch()      # a plan that passes stops at a failed bootstrap
        err = io.StringIO()
        with patch.object(cadence_launch.time, "time", return_value=now), patch("sys.stderr", err), \
             patch("sys.stdout", io.StringIO()), patch.dict(os.environ, {"WP10_FIXTURE_ROOT": str(self.root)}):
            rc = cadence_launch.main(argv)
        return rc, err.getvalue()

    def test_a_2130_t0_meets_the_0200_blackout_and_refuses(self):
        rc, err = self.main_at("2026-11-15T21:30", tag="late")              # worst case to 02:07:30
        self.assertEqual(rc, 2)
        self.assertIn("meets a batch blackout (02:00-02:35)", err)
        self.assertNotIn("exit status", err)
        self.assertFalse((self.root / "launchctl.log").exists())
        rc, err = self.main_at("2026-11-15T13:20", tag="day")               # control: worst case ends 17:57:30
        self.assertEqual(rc, 2)
        self.assertIn("exit status 19", err)                                # the plan passed; bootstrap failed

    def test_no_flag_uses_the_r1_driver_window_and_a_1000_t0_refuses(self):
        rc, err = self.main_at("2026-11-15T10:00", window=None, tag="ten")  # worst case meets 11:45-13:15
        self.assertEqual(rc, 2)
        self.assertIn("meets a batch blackout (11:45-13:15)", err)
        self.assertFalse((self.root / "launchctl.log").exists())
        rc, err = self.main_at("2026-11-15T06:00", window=None, tag="six")  # control: ends 10:37:30
        self.assertIn("exit status 19", err)


class OuterRunTests(Fixture):
    """``run``: the agent-free outer run the wrapper calls (A5, R2, R3, R4)."""

    def test_run_verb_routes_to_the_campaign_run_not_the_base(self):
        with patch.object(cadence_launch, "run_until_deadline", return_value=0) as ours, \
             patch.object(base, "main", return_value=9) as theirs:
            self.assertEqual(cadence_launch.main(["run", "--deadline", "1", "--runner-spec", "x"]), 0)
        ours.assert_called_once()
        theirs.assert_not_called()

    def test_term_reaches_a_slow_child_which_gets_its_cleanup_grace(self):
        child = self.root / "child.py"
        child.write_text(f'''
import os, signal, sys, time
from pathlib import Path
root = Path({str(self.root)!r})
def on_term(*_):
    (root / "child-term").write_text(str(time.time()))
    time.sleep(2.0)                          # its own Automatic restore, inside the grace
    (root / "child-cleaned").write_text("1")
    sys.exit(0)
signal.signal(signal.SIGTERM, on_term)
(root / "child.pid").write_text(str(os.getpid()))
time.sleep(60)
''')
        spec = self.root / "runner.json"
        spec.write_text(json.dumps({"kind": "cadence-legs-v1", "argv": [sys.executable, "-B", str(child)]}))
        outer = subprocess.Popen([sys.executable, "-B", str(SCRIPT), "run", "--deadline", str(time.time() + 3600),
                                  "--runner-spec", str(spec)], cwd=REPO, env=self.env)
        self.addCleanup(self.stop, outer)
        self.wait_for(lambda: (self.root / "child.pid").exists())
        child_pid = int((self.root / "child.pid").read_text())
        outer.send_signal(signal.SIGTERM)
        code = outer.wait(timeout=30)
        self.assertEqual(code, 128 + signal.SIGTERM)                         # R4: trapped, not a bare kill
        self.assertTrue((self.root / "child-term").exists(), "child never got TERM")       # R2
        self.assertTrue((self.root / "child-cleaned").exists(), "child killed inside its grace")   # R3
        with self.assertRaises(ProcessLookupError):
            os.kill(child_pid, 0)

    def test_the_fake_kill_never_signals_outside_the_fixture(self):
        victim = subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(30)"])
        self.addCleanup(self.stop, victim)
        result = subprocess.run([str(self.kill), "-TERM", str(victim.pid)], env=self.env, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(victim.poll())
        for argv in (["-U", str(os.getuid())], ["-x", "corespotlightd"]):
            self.assertNotEqual(subprocess.run([str(self.kill), *argv], env=self.env).returncode, 0)
        self.assertIn(f"-TERM {victim.pid}", (self.root / "refused-signals.log").read_text())


if __name__ == "__main__":
    unittest.main()
