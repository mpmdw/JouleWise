"""Defect-shaped regressions for the operator pre-window process census."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "scripts/prewindow_check.sh"


class PrewindowCheckTests(unittest.TestCase):
    def test_check_8_refuses_agent_processes_missed_by_old_pattern(self) -> None:
        process_lines = (
            "edr 101 0.0 0.0 0 0 ?? S 0:00.00 claude daemon",
            "edr 102 0.0 0.0 0 0 ?? S 0:00.00 codex app-server",
            "edr 103 0.0 0.0 0 0 ?? S 0:00.00 t3 worker",
            "edr 104 0.0 0.0 0 0 ?? S 0:00.00 mcp-server",
            "edr 105 0.0 0.0 0 0 ?? S 0:00.00 run_campaign",
            "edr 106 0.0 0.0 0 0 ?? S 0:00.00 window-chain",
        )
        old_pattern = re.compile(
            r"codex exec|codex-run|run_campaign|window-chain"
        )
        for process_line in process_lines[:4]:
            self.assertIsNone(old_pattern.search(process_line))

        completed = self._check_lines(process_lines)
        self.assertEqual(
            completed.returncode, 1, completed.stdout + completed.stderr
        )
        self.assertIn(
            "6 agent/measurement process(es) already running",
            completed.stdout,
        )
        self.assertIn("NOT READY.", completed.stdout)
        # Counterfactual: removing the six offending lines admits readiness.
        self.assertEqual(self._check_lines([]).returncode, 0)

    def _check_lines(self, process_lines, *args):
        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory)
            commands = {
                "ps": "\n".join(
                    ["#!/bin/sh"]
                    + [f"printf '%s\\n' '{line}'" for line in process_lines]
                ),
                "uptime": (
                    "#!/bin/sh\nprintf '%s\\n' "
                    "'12:00 up 1 day, load averages: 0.10 0.20 0.30'"
                ),
                "pmset": (
                    "#!/bin/sh\nprintf \"%s\\n\" \"Now drawing from 'AC Power'\""
                ),
                "df": (
                    "#!/bin/sh\nprintf '%s\\n' "
                    "'Filesystem blocks Used Available Capacity Mounted' "
                    "'/dev/disk 1 1 100 1% /'"
                ),
            }
            for name, source in commands.items():
                path = fake_bin / name
                path.write_text(source + "\n", encoding="utf-8")
                path.chmod(0o755)

            completed = subprocess.run(
                ["/bin/bash", str(SCRIPT), *args],
                cwd=REPOSITORY,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:/usr/bin:/bin:/usr/sbin:/sbin",
                },
                text=True,
                capture_output=True,
                check=False,
            )

        return completed

    def test_wait_seconds_cap_refuses_without_a_full_dwell(self):
        refused = self._check_lines([], "--wait", "--timeout-s", "1")
        self.assertEqual(refused.returncode, 1)
        self.assertIn("TIMED OUT after 1s without 600s", refused.stdout)
        self.assertNotIn("READY after", refused.stdout)
        # Counterfactual: the same clean probes pass the one-shot check.
        self.assertEqual(self._check_lines([]).returncode, 0)

    def test_wait_seconds_cap_requires_a_positive_integer(self):
        for args in (("--timeout-s", "0"), ("--timeout-s", "-1"),
                     ("--timeout-s", "oops"), ("--timeout-s",)):
            with self.subTest(args=args):
                self.assertEqual(self._check_lines([], *args).returncode, 2)
        self.assertEqual(self._check_lines([], "--timeout-s", "600").returncode, 0)

    def test_real_driver_command_and_census_grep_do_not_match(self):
        # The actual interpreter and driver paths, with the driver's CLI argv;
        # no exemption hides a match in either paths or arguments.
        driver_command = (
            f"edr 201 0.0 0.0 0 0 ?? S 0:00.00 {sys.executable} -B "
            f"{REPOSITORY / 'scripts/run_night.py'} run --plan /tmp/window/plan.json"
        )
        grep_command = (
            "edr 202 0.0 0.0 0 0 ?? S 0:00.00 grep -cE "
            "[c]odex|[c]laude|[t]3|[m]cp-server|[r]un_campaign|[w]indow-chain"
        )
        completed = self._check_lines([driver_command, grep_command])
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("no agent or measurement process running", completed.stdout)
        # A real agent with a grep argument must still be seen. The former
        # grep -v grep erased this entire offending process line.
        refused = self._check_lines([driver_command, grep_command,
            "edr 203 0.0 0.0 0 0 ?? S 0:00.00 claude --grep needle"])
        self.assertEqual(refused.returncode, 1)
        self.assertIn("1 agent/measurement process(es) already running", refused.stdout)

    def test_driver_path_containing_agent_string_is_not_exempt(self):
        driver_command = (
            f"edr 201 0.0 0.0 0 0 ?? S 0:00.00 {sys.executable} "
            "/tmp/.claude/checkout/scripts/run_night.py run --plan /tmp/window/plan.json"
        )
        refused = self._check_lines([driver_command])
        self.assertEqual(refused.returncode, 1)
        self.assertIn("1 agent/measurement process(es) already running", refused.stdout)
        admitted = self._check_lines([driver_command.replace("/.claude/", "/measurement/")])
        self.assertEqual(admitted.returncode, 0, admitted.stdout + admitted.stderr)


if __name__ == "__main__":
    unittest.main()
