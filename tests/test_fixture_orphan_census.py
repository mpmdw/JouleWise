from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest import mock

from scripts import fixture_orphan_census as sentinel
from scripts import magistrate_watchdog as watchdog


VLLM = (
    "/usr/bin/python3 /private/tmp/tmpfixture/bin/vllm serve /fake/model "
    "--host 127.0.0.1 --port 43210 --served-model-name nv5-fake-model "
    "--revision test --tensor-parallel-size 1 --gpu-memory-utilization 0.1"
)
WORKER = (
    "/usr/bin/python3 /private/tmp/tmpfixture/remote/node_worker.py "
    "--task /private/tmp/tmpfixture/remote/nv5-localhost-contract/tasks/task-runtime-prepare.json "
    "--artifacts /private/tmp/tmpfixture/remote/nv5-localhost-contract/artifacts/task-runtime-prepare "
    "--work-root /private/tmp/tmpfixture/remote"
)
START = "Thu Sep  3 10:20:30 2026"


def row(command: str, *, pid: int = 200, ppid: int = 1) -> str:
    return f"  {pid} {ppid} {START} 12345 {command}\n"


class FixtureOrphanCensusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.signatures = sentinel.load_signatures()

    def test_required_fixture_signatures(self) -> None:
        # Independent expected names/commands ensure deleting either registry
        # entry cannot quietly remove its corresponding coverage.
        for command, expected in ((VLLM, "nv5-fake-vllm"), (WORKER, "nv5-fake-node-worker")):
            with self.subTest(signature=expected):
                matches = sentinel.census(row(command), self.signatures)
                self.assertEqual([item["signature"] for item in matches], [expected])

    def test_pid_one_filter(self) -> None:
        for command in (VLLM, WORKER):
            for parent in (0, 2, 199):
                with self.subTest(command=command, parent=parent):
                    self.assertEqual(sentinel.census(row(command, ppid=parent), self.signatures), [])

    def test_nonfixtures_do_not_match(self) -> None:
        for command in (
            "/usr/bin/sleep 30",
            VLLM.replace("/fake/model", "/models/real"),
            VLLM.replace("nv5-fake-model", "nv5-fake-model-production"),
            VLLM.replace("/bin/vllm", "/bin/not-vllm"),
            WORKER.replace("nv5-localhost-contract", "production-run"),
            WORKER.replace("node_worker.py", "other_node_worker.py"),
        ):
            with self.subTest(command=command):
                self.assertEqual(sentinel.census(row(command), self.signatures), [])

    def test_age_start_rss_and_json_schema(self) -> None:
        start = time.mktime(time.strptime(START, "%a %b %d %H:%M:%S %Y"))
        matches = sentinel.census(row(VLLM), self.signatures, now=start + 13 * 86400 + 5.5)
        actual = json.loads(json.dumps(matches))
        self.assertEqual(actual, [{
            "pid": 200, "ppid": 1,
            "start": dt.datetime.fromtimestamp(start, dt.timezone.utc).isoformat(),
            "age_s": 1123205.5, "rss_kb": 12345, "signature": "nv5-fake-vllm",
        }])
        self.assertEqual(sentinel.census(row(VLLM), self.signatures, now=start - 1)[0]["age_s"], 0)

    def test_sorted_one_row_per_pid(self) -> None:
        signatures = self.signatures + [("overlap", self.signatures[0][1])]
        actual = sentinel.census(row(VLLM, pid=300) + row(WORKER, pid=100), signatures)
        self.assertEqual([item["pid"] for item in actual], [100, 300])
        self.assertEqual(actual[1]["signature"], "nv5-fake-vllm")

    def test_empty_registry_refused_before_inventory(self) -> None:
        with mock.patch.object(Path, "read_text", return_value="[]"), mock.patch.object(
            sentinel, "process_inventory"
        ) as inventory, contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(sentinel.main([]), 2)
        inventory.assert_not_called()
        self.assertIn("non-empty list", json.loads(errors.getvalue())["error"])
        with self.assertRaises(ValueError):
            sentinel.census("", [])

    def test_invalid_registry_refused(self) -> None:
        for value in ({}, [None], [{"id": "x", "command_regex": ""}],
                      [{"id": "x", "command_regex": ".*"}],
                      [{"id": "x", "command_regex": "["}],
                      [{"id": "x", "command_regex": "x"}] * 2):
            with self.subTest(value=value), mock.patch.object(Path, "read_text", return_value=json.dumps(value)):
                with self.assertRaises((ValueError, sentinel.re.error)):
                    sentinel.load_signatures()

    def test_cli_json_and_exit_codes(self) -> None:
        for inventory, argv, expected in (
            (row("/usr/bin/sleep 30"), [], 0),
            (row("/usr/bin/sleep 30"), ["--fail-on-orphans"], 0),
            (row(VLLM), [], 0), (row(VLLM), ["--fail-on-orphans"], 1),
        ):
            with self.subTest(argv=argv, expected=expected), mock.patch.object(
                sentinel, "process_inventory", return_value=inventory
            ), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(sentinel.main(argv), expected)
            self.assertIsInstance(json.loads(output.getvalue()), list)

    def test_inventory_failures_are_not_clean(self) -> None:
        for error in (OSError("denied"), subprocess.TimeoutExpired(sentinel.PS_ARGV, 10),
                      subprocess.CalledProcessError(1, sentinel.PS_ARGV)):
            with self.subTest(error=error), mock.patch.object(sentinel.subprocess, "run", side_effect=error):
                observation = sentinel.launch_observation()
                self.assertIsNone(observation["count"])
                self.assertIsNone(observation["rows"])
                self.assertTrue(observation["error"])
                with contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(sentinel.main([]), 2)
                self.assertEqual(output.getvalue(), "")
        with mock.patch.object(sentinel.subprocess, "run", return_value=mock.Mock(stdout="")):
            with self.assertRaises(ValueError):
                sentinel.process_inventory()
        with self.assertRaises(ValueError):
            sentinel.census("broken inventory", self.signatures)

    def test_ps_uses_untruncated_command_and_bounded_observation(self) -> None:
        with mock.patch.object(sentinel.subprocess, "run", return_value=mock.Mock(stdout=row(VLLM))) as run:
            sentinel.process_inventory()
        self.assertIn("-axww", run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs["timeout"], 10)
        self.assertEqual(run.call_args.kwargs["env"]["LC_ALL"], "C")

    def test_launch_record_is_informational(self) -> None:
        storage = mock.Mock(root=Path("/unused-custody"))
        child = mock.Mock(pid=300)
        processes = mock.Mock()
        processes.snapshot.return_value = [watchdog.ProcessInfo(300, os.getpid(), "start", "fake")]
        deps = watchdog.Dependencies(
            wall_now=lambda: dt.datetime(2026, 9, 15, tzinfo=dt.timezone.utc),
            monotonic=lambda: 1.0, census=mock.Mock(), git_probe=mock.Mock(),
            processes=processes, spawn=mock.Mock(return_value=child),
            version_probe=lambda _: "fixture", sleep=mock.Mock(),
            fixture_census=watchdog.real_dependencies().fixture_census,
        )
        for inventory in (row(VLLM), row("/usr/bin/sleep 30")):
            with self.subTest(inventory=inventory), mock.patch.object(sentinel, "process_inventory", return_value=inventory), mock.patch.object(
                watchdog, "resolve_session_binary", return_value=Path("/fake/claude")
            ), mock.patch.object(watchdog, "render_prompt", return_value="fixture"), mock.patch.object(watchdog, "ResidentSupervisor"):
                watchdog.start_session(storage, deps, {})
            events = [call.args[1] for call in storage.append_jsonl.call_args_list
                      if call.args[1].get("kind") == "fixture_orphan_census"]
            expected = sentinel.census(inventory, self.signatures)
            self.assertEqual(events[-1]["fixture_orphans"]["count"], len(expected))
            self.assertEqual([r["pid"] for r in events[-1]["fixture_orphans"]["rows"]], [r["pid"] for r in expected])
        self.assertEqual(deps.spawn.call_count, 2)
        deps.census.assert_not_called()
        processes.send_signal.assert_not_called()

    def test_live_cli_smoke(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(Path(sentinel.__file__).resolve())],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 2:
            error = json.loads(result.stderr).get("error", "")
            if error.startswith("PermissionError:") and "Operation not permitted: 'ps'" in error:
                self.skipTest("PROVISIONAL: sandbox denies ps; lead must run the live census smoke")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = json.loads(result.stdout)
        self.assertIsInstance(rows, list)
        for item in rows:
            self.assertEqual(set(item), {"pid", "ppid", "start", "age_s", "rss_kb", "signature"})
            self.assertEqual(item["ppid"], 1)


if __name__ == "__main__":
    unittest.main()
