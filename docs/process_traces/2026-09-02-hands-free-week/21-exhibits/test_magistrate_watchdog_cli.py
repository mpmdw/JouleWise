"""Production-shaped CLI coverage for the magistrate plan fence."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Callable

from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan
from scripts import magistrate_watchdog as wd


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "magistrate_watchdog.py"
RETIRED_V1 = REPO_ROOT / "tests" / "fixtures" / "night_plan_v1_retired.json"


def _git_head(root: Path) -> str:
    return subprocess.check_output(
        ["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def _init_repo(root: Path) -> str:
    root.mkdir(parents=True)
    subprocess.run(["/usr/bin/git", "init", "-q", str(root)], check=True)
    (root / "marker.txt").write_text("initial\n", encoding="utf-8")
    subprocess.run(
        ["/usr/bin/git", "-C", str(root), "add", "marker.txt"], check=True
    )
    subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(root),
            "-c",
            "user.name=JouleWise Test",
            "-c",
            "user.email=joulewise-test@example.invalid",
            "commit",
            "-qm",
            "initial",
        ],
        check=True,
    )
    return _git_head(root)


def _truncate(path: Path, fraction: float) -> None:
    payload = path.read_bytes()
    path.write_bytes(payload[: max(1, int(len(payload) * fraction))])


def _drop_field(path: Path, field: str) -> None:
    mapping = json.loads(path.read_text(encoding="utf-8"))
    del mapping[field]
    path.write_text(json.dumps(mapping, sort_keys=True) + "\n", encoding="utf-8")


class MagistrateWatchdogCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.measurement_root = self.root / "measurement"
        self.measurement_head = _init_repo(self.measurement_root)
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        session_target = self.bin_dir / "session-target"
        session_target.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        session_target.chmod(0o755)
        self.session_bin = self.bin_dir / "claude"
        self.session_bin.symlink_to(session_target)
        git_stub = self.bin_dir / "git"
        git_stub.write_text(
            "#!/bin/sh\n"
            "case \"$*\" in\n"
            "  *refs/heads/main*) echo '0123456789abcdef refs/heads/main'; exit 0 ;;\n"
            "  *refs/heads/ops/stop*) exit 2 ;;\n"
            "esac\n"
            "exec /usr/bin/git \"$@\"\n",
            encoding="utf-8",
        )
        git_stub.chmod(0o755)
        self.environment = os.environ.copy()
        self.environment["MAGISTRATE_SESSION_BIN"] = str(self.session_bin)
        self.environment["PATH"] = (
            f"{self.bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin"
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _plan(
        self, custody_root: Path, *, plan_id: str, t0_offset_s: float = 60
    ) -> NightPlan:
        now = time.time()
        return NightPlan(
            plan_id=plan_id,
            receipt_class="TRANSACTION_PACK",
            t0_epoch_s=now + t0_offset_s,
            window_max_s=600,
            authored_epoch_s=now,
            repo_head=_git_head(REPO_ROOT),
            measurement_root=str(self.measurement_root),
            measurement_head=self.measurement_head,
            chain_path="/bin/true",
            chain_sha256_path=str(self.root / "chain.sha256"),
            custody_root=str(custody_root),
            registration_path=None,
        )

    def _write_valid(
        self, custody_parent: Path, name: str, *, t0_offset_s: float = 60
    ) -> Path:
        plan_root = custody_parent / name
        path = plan_root / "night_plan.json"
        write_night_plan(
            path, self._plan(plan_root, plan_id=name, t0_offset_s=t0_offset_s)
        )
        return path

    @staticmethod
    def _wait_for(predicate: Callable[[], object], *, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.05)
        return bool(predicate())

    def _run(
        self, custody_parent: Path, *, dry_run: bool = False
    ) -> subprocess.CompletedProcess[str]:
        argv = [
            sys.executable,
            str(SCRIPT_PATH),
            "tick",
            "--custody-root",
            str(custody_parent / "magistrate"),
        ]
        if dry_run:
            argv.append("--dry-run")
        return subprocess.run(
            argv,
            env=self.environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_real_cli_consumes_production_plan_set_and_fails_closed(self) -> None:
        custody_parent = self.root / "four-plan-custody"
        valid_path = self._write_valid(custody_parent, "valid-v2")
        retired_path = custody_parent / "retired-v1" / "night_plan.json"
        retired_path.parent.mkdir(parents=True)
        shutil.copyfile(RETIRED_V1, retired_path)
        torn_path = custody_parent / "torn" / "night_plan.json"
        torn_path.parent.mkdir(parents=True)
        shutil.copyfile(valid_path, torn_path)
        _truncate(torn_path, 0.4)
        missing_path = custody_parent / "missing-field" / "night_plan.json"
        missing_path.parent.mkdir(parents=True)
        shutil.copyfile(valid_path, missing_path)
        _drop_field(missing_path, "measurement_head")

        completed = self._run(custody_parent)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)
        watchdog_root = custody_parent / "magistrate"
        state = json.loads((watchdog_root / "state.json").read_text(encoding="utf-8"))
        self.assertEqual("HOLD_UNSAFE", state["state"])
        self.assertIn(str(torn_path), state["reason"])
        self.assertIn(str(missing_path), state["reason"])
        self.assertNotIn("joulewise.night_plan.v1", state["reason"])
        self.assertFalse(state.get("launch", False))
        self.assertFalse((watchdog_root / "attempts").exists())
        events = [
            json.loads(line)
            for line in (watchdog_root / "events.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
        ]
        retired_events = [event for event in events if event["kind"] == "plan_retired_v1"]
        self.assertEqual(1, len(retired_events))
        self.assertEqual(
            str(retired_path.parent.resolve()), retired_events[0]["plan_dir"]
        )

        positive_parent = self.root / "positive-control-custody"
        self._write_valid(positive_parent, "valid-v2")
        positive = self._run(positive_parent, dry_run=True)
        self.assertEqual(0, positive.returncode, positive.stderr)
        self.assertNotIn("Traceback", positive.stderr)
        decision_line = next(
            line for line in positive.stdout.splitlines() if line.startswith("decision=")
        )
        self.assertRegex(decision_line, r"^decision=(?:FENCED|HOLD_CENSUS)\b")
        self.assertNotIn("decision=LAUNCHING", positive.stdout)
        self.assertNotIn("decision=HOLD_UNSAFE", positive.stdout)

    def test_real_cli_resident_records_drain_after_plan_is_truncated(self) -> None:
        custody_parent = self.root / "resident-drain-custody"
        plan_path = self._write_valid(
            custody_parent, "resident-plan", t0_offset_s=2 * 60 * 60
        )
        watchdog_root = custody_parent / "magistrate"
        request_path = watchdog_root / "standdown.request"
        resident_source = (
            "import datetime as dt, json, os, sys, time\n"
            "from pathlib import Path\n"
            "from scripts import magistrate_watchdog as wd\n"
            "root=Path(sys.argv[1])\n"
            "storage=wd.Storage(root)\n"
            "class Table:\n"
            " def snapshot(self): return [wd.ProcessInfo(os.getpid(), os.getppid(), 'stub-start', 'stub resident')]\n"
            " def send_signal(self, pid, signum): pass\n"
            "class Child:\n"
            " pid=os.getpid()\n"
            " def poll(self): return None\n"
            "state=wd.initial_state()\n"
            "spawn_epoch=time.time()\n"
            "state.update({'state':'ACTIVE','activation_id':'cli-resident-activation','activation_spawn_epoch_s':spawn_epoch})\n"
            "lock={'schema':wd.LOCK_SCHEMA,'activation_id':state['activation_id'],'activation_spawn_epoch_s':spawn_epoch,'pid':os.getpid(),'start_time':'stub-start','supervisor_pid':os.getpid(),'launch_epoch_s':spawn_epoch,'binary_symlink':'stub','binary_version':'stub','status':'ACTIVE'}\n"
            "storage.atomic_json(root/'magistrate.lock', lock)\n"
            "deps=wd.Dependencies(wall_now=lambda:dt.datetime.now().astimezone(),monotonic=time.monotonic,census=lambda:wd.CensusObservation(True,1,'',''),git_probe=lambda:wd.StopObservation('CLEAR','clear'),processes=Table(),spawn=lambda *args:Child(),version_probe=lambda path:'stub',sleep=time.sleep)\n"
            "supervisor=wd.ResidentSupervisor(storage,deps,state,Child(),lock,root/'stdout',root/'stderr')\n"
            "storage.atomic_bytes(root/'resident.ready', b'ready\\n')\n"
            "supervisor.run()\n"
        )
        resident = subprocess.Popen(
            [
                sys.executable,
                "-c",
                resident_source,
                str(watchdog_root),
            ],
            start_new_session=True,
        )
        try:
            self.assertTrue(
                self._wait_for(
                    (watchdog_root / "resident.ready").exists, timeout=2
                ),
                "stub resident did not start",
            )
            _truncate(plan_path, 0.4)
            started = time.monotonic()
            self.assertTrue(
                self._wait_for(request_path.exists, timeout=wd.SUPERVISOR_POLL_S + 2),
                "resident did not request cooperative stop within one poll",
            )

            def drain_events() -> list[dict[str, object]]:
                events_path = watchdog_root / "events.jsonl"
                if not events_path.exists():
                    return []
                return [
                    event
                    for event in (
                        json.loads(line)
                        for line in events_path.read_text(encoding="utf-8").splitlines()
                    )
                    if event.get("kind") == "resident_drain_started"
                ]

            self.assertTrue(
                self._wait_for(lambda: bool(drain_events()), timeout=1),
                "resident_drain_started was not recorded",
            )
            self.assertLessEqual(
                time.monotonic() - started, wd.SUPERVISOR_POLL_S + 3
            )
            self.assertIn("night_plan_unreadable", str(drain_events()[0]["reason"]))
        finally:
            if resident.poll() is None:
                resident.terminate()
                try:
                    resident.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    resident.kill()
                    resident.wait(timeout=2)

    def test_real_cli_adopts_recorded_resident_on_unsafe_replacement_tick(self) -> None:
        custody_parent = self.root / "replacement-drain-custody"
        plan_path = self._write_valid(
            custody_parent, "replacement-plan", t0_offset_s=2 * 60 * 60
        )
        watchdog_root = custody_parent / "magistrate"
        stub = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            start_new_session=True,
        )
        try:
            start_time = "cli-stub-start"
            activation = "cli-replacement-activation"
            spawn_epoch = time.time()
            session = {
                "schema": wd.LOCK_SCHEMA,
                "activation_id": activation,
                "activation_spawn_epoch_s": spawn_epoch,
                "pid": stub.pid,
                "start_time": start_time,
                "supervisor_pid": stub.pid + 1,
                "launch_epoch_s": spawn_epoch,
                "binary_symlink": "stub",
                "binary_version": "stub",
                "status": "ACTIVE",
            }
            state = wd.initial_state()
            state.update(
                {
                    "state": "ACTIVE",
                    "activation_id": activation,
                    "activation_spawn_epoch_s": spawn_epoch,
                    "resident_session": session,
                }
            )
            storage = wd.Storage(watchdog_root)
            storage.atomic_json(watchdog_root / "state.json", state)
            storage.atomic_json(watchdog_root / "magistrate.lock", session)
            _truncate(plan_path, 0.4)

            cli_source = (
                "import os, sys\n"
                "from scripts import magistrate_watchdog as wd\n"
                "pid=int(sys.argv[1]); start=sys.argv[2]\n"
                "class Table:\n"
                " def snapshot(self): return [wd.ProcessInfo(pid, 1, start, 'stub resident')]\n"
                " def send_signal(self, target, signum): os.kill(target, signum)\n"
                "deps=wd.real_dependencies(); deps.processes=Table()\n"
                "wd.real_dependencies=lambda:deps\n"
                "raise SystemExit(wd.main(sys.argv[3:]))\n"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    cli_source,
                    str(stub.pid),
                    start_time,
                    "tick",
                    "--custody-root",
                    str(watchdog_root),
                ],
                cwd=REPO_ROOT,
                env=self.environment,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)
            self.assertIsNone(stub.poll(), "first ladder event must remain cooperative")
            self.assertTrue((watchdog_root / "standdown.request").exists())
            events = [
                json.loads(line)
                for line in (watchdog_root / "events.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            adopted = [event for event in events if event["kind"] == "resident_adopted"]
            self.assertEqual(1, len(adopted))
            self.assertEqual(stub.pid, adopted[0]["pid"])
            self.assertEqual(start_time, adopted[0]["start_time"])
            self.assertEqual(activation, adopted[0]["activation"])
            self.assertEqual(
                1,
                sum(event["kind"] == "resident_drain_started" for event in events),
            )
        finally:
            if stub.poll() is None:
                stub.terminate()
                try:
                    stub.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    stub.kill()
                    stub.wait(timeout=2)


if __name__ == "__main__":
    unittest.main()
