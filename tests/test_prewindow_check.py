"""Defect-shaped regressions for the operator pre-window process census."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shlex
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

    def _check_lines(self, process_lines, *args, load="0.10", t0=False, fast_dwell=False):
        # Explicit (comm, args) pairs preserve executable names containing spaces.
        # Legacy fixtures use ps aux rows or a bare executable name.
        processes = []
        for line in process_lines:
            if isinstance(line, tuple):
                comm, arguments = line
                full_line = f"edr 201 0.0 0.0 0 0 ?? S 0:00.00 {arguments}"
            else:
                arguments = line.split(maxsplit=9)[9] if line.startswith("edr ") else line
                comm = arguments.split()[0]
                full_line = line
            processes.append((comm, arguments, full_line))

        def output(column):
            return "\n".join(f"printf '%s\\n' {shlex.quote(row[column])}" for row in processes) or ":"

        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory)
            commands = {
                "ps": (
                    '#!/bin/sh\ncase "$*" in\n'
                    f'  "-A -o comm=")\n{output(0)}\n;;\n'
                    f'  "-A -o args=")\n{output(1)}\n;;\n'
                    f'  aux)\n{output(2)}\n;;\n'
                    '  "-Ao pid=,pcpu=,args=")\n'
                    + ("\n".join(f"printf '%s\\n' {shlex.quote('201 ' + (row[2].split()[2] if row[2].startswith('edr ') else '0.0') + ' ' + row[1])}"
                                 for row in processes) or "printf '%s\\n' '1 0.0 launchd'") + "\n;;\n"
                    '  *) echo "unsupported fake ps columns: $*" >&2; exit 2;;\nesac'
                ),
                "uptime": (
                    "#!/bin/sh\nprintf '%s\\n' "
                    f"'12:00 up 1 day, load averages: {load} 0.20 0.30'"
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

            script = SCRIPT
            if fast_dwell:
                # Mock seam: advance only Bash's elapsed clock at sleep. All
                # 600-second dwell, reset and deadline logic stays production.
                script = fake_bin / "scripts/prewindow_check.sh"
                script.parent.mkdir()
                policy = fake_bin / "joulewise/prewindow.py"
                policy.parent.mkdir()
                policy.write_bytes((REPOSITORY / "joulewise/prewindow.py").read_bytes())
                script.write_text(SCRIPT.read_text().replace('sleep "$pause"', 'SECONDS=$((SECONDS + pause))'))
            completed = subprocess.run(
                ["/bin/bash", str(script), *args],
                cwd=REPOSITORY,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:/usr/bin:/bin:/usr/sbin:/sbin",
                    "JOULEWISE_PREWINDOW_T0_CPU_ADMISSION": "1" if t0 else "",
                },
                text=True,
                capture_output=True,
                check=False,
            )

        return completed

    def test_t0_high_load_is_report_only_and_does_not_reset_dwell(self):
        ordinary = self._check_lines([], load="2.10")
        self.assertEqual(ordinary.returncode, 1)
        self.assertIn("BLOCK", ordinary.stdout)
        native = self._check_lines([], load="2.10", t0=True)
        self.assertEqual(native.returncode, 0, native.stdout + native.stderr)
        self.assertIn("REPORT 1-minute load average 2.10; limit 2.0", native.stdout)
        self.assertNotIn("BLOCK", native.stdout)
        args = ("--wait", "--timeout-s", "630")
        native = self._check_lines([], *args, load="2.10", t0=True, fast_dwell=True)
        self.assertEqual(native.returncode, 0, native.stdout + native.stderr)
        self.assertRegex(native.stdout, r"continuous clean dwell 6[0-2][0-9]/600s")
        ordinary = self._check_lines([], *args, load="2.10", fast_dwell=True)
        self.assertEqual(ordinary.returncode, 1)
        self.assertIn("TIMED OUT", ordinary.stdout)
        self.assertNotIn("READY after", ordinary.stdout)

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

    def test_driver_arguments_containing_agent_strings_are_allowed(self):
        driver_command = (
            f"edr 201 0.0 0.0 0 0 ?? S 0:00.00 {sys.executable} "
            "/tmp/.claude/checkout/scripts/run_night.py run --plan /tmp/window/plan.json"
        )
        for argument in ("/tmp/claude/x.json", "/tmp/codex/x.json"):
            admitted = self._check_lines([driver_command + " " + argument])
            self.assertEqual(admitted.returncode, 0, admitted.stdout + admitted.stderr)
        self.assertEqual(self._check_lines(["/usr/local/bin/claude"]).returncode, 1)
        self.assertEqual(self._check_lines(["/usr/local/bin/codex"]).returncode, 1)
        admitted = self._check_lines([driver_command.replace("/.claude/", "/measurement/")])
        self.assertEqual(admitted.returncode, 0, admitted.stdout + admitted.stderr)

    def test_check_8_refuses_executable_names_containing_spaces(self):
        names = ("Codex (Service)", "T3 Code", "Claude Desktop", "mcp-server worker",
                 "run_campaign worker", "window-chain worker")
        for name in names:
            with self.subTest(comm=name):
                # Neutral args make this a comm-only match, including app paths.
                comm = f"/Applications/Worker.app/Contents/MacOS/{name}"
                refused = self._check_lines([(comm, "worker --plan /tmp/window/plan.json")])
                self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
                self.assertIn("1 agent/measurement process(es) already running", refused.stdout)
        refused = self._check_lines([(name, "worker") for name in names])
        self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
        self.assertIn("6 agent/measurement process(es) already running", refused.stdout)


if __name__ == "__main__":
    unittest.main()
