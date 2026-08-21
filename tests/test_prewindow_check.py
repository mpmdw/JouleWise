"""Defect-shaped regressions for the operator pre-window process census."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "scripts/prewindow_check.sh"


class PrewindowCheckTests(unittest.TestCase):
    def test_check_8_refuses_agent_processes_missed_by_old_pattern(self) -> None:
        process_lines = (
            "edr 101 0.0 0.0 0 0 ?? S 0:00.00 claude daemon",
            "edr 102 0.0 0.0 0 0 ?? S 0:00.00 codex mcp-server",
            "edr 103 0.0 0.0 0 0 ?? S 0:00.00 mcp-server",
        )
        old_pattern = re.compile(
            r"codex exec|codex-run|run_campaign|window-chain"
        )
        for process_line in process_lines:
            self.assertIsNone(old_pattern.search(process_line))

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
                ["/bin/bash", str(SCRIPT)],
                cwd=REPOSITORY,
                env={
                    **os.environ,
                    "PATH": f"{fake_bin}:/usr/bin:/bin:/usr/sbin:/sbin",
                },
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(
            completed.returncode, 1, completed.stdout + completed.stderr
        )
        self.assertIn(
            "3 agent/measurement process(es) already running",
            completed.stdout,
        )
        self.assertIn("NOT READY.", completed.stdout)


if __name__ == "__main__":
    unittest.main()
