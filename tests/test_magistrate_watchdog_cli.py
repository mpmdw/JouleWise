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

from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan


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

    def _plan(self, custody_root: Path, *, plan_id: str) -> NightPlan:
        now = time.time()
        return NightPlan(
            plan_id=plan_id,
            receipt_class="TRANSACTION_PACK",
            t0_epoch_s=now + 60,
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

    def _write_valid(self, custody_parent: Path, name: str) -> Path:
        plan_root = custody_parent / name
        path = plan_root / "night_plan.json"
        write_night_plan(path, self._plan(plan_root, plan_id=name))
        return path

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


if __name__ == "__main__":
    unittest.main()
