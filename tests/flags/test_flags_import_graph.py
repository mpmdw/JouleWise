"""Import graph: the flag package stays off the retired arm path, and the arm stays off it.

Three facts are checked:

1. No module in ``joulewise/flags`` imports a retired-path module, at module
   level or inside a function.
2. Importing any flag module in a fresh interpreter loads no retired-path
   module and none of the core modules a collector reaches only lazily
   (those run in the collector's own subprocess).
3. The arm decision (``joulewise/hazards/arm.py``, lane L1) imports nothing
   from ``joulewise.flags``: no collector can change the arm decision.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FLAGS = REPO / "joulewise" / "flags"
RETIRED_MODULES = frozenset({
    "joulewise.arm_readiness", "joulewise.arm_readiness_evidence", "joulewise.arm_readiness_evidence_t0",
    "joulewise.t0_rehearsal", "joulewise.v5_qualification", "joulewise.network_time_off", "joulewise.dwell",
})
RETIRED_SCRIPTS = ("capture_t0_step", "launch_window", "author_arm_evidence_t0", "author_arm_readiness_evidence",
                   "generate_arm_readiness", "write_v5_qualification_plan", "harvest_v5_qualification",
                   "harvest_v5_g2b_window")


def imported_names(path: Path, package: str = "joulewise.flags") -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".")[: len(package.split(".")) - (node.level - 1)]
                module = ".".join(base + ([node.module] if node.module else []))
            else:
                module = node.module or ""
            names.add(module)
            names.update(f"{module}.{alias.name}" for alias in node.names)
    return names


class FlagImportGraphTests(unittest.TestCase):
    def test_flag_modules_import_nothing_on_the_retired_path(self) -> None:
        for path in sorted(FLAGS.glob("*.py")) + [REPO / "scripts" / "collect_window_flags.py"]:
            names = imported_names(path)
            with self.subTest(module=path.name):
                self.assertEqual(sorted(names & RETIRED_MODULES), [])
                self.assertEqual(sorted(n for n in names if any(s in n for s in RETIRED_SCRIPTS)), [])
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("import_module(", text)
                self.assertNotIn("spec_from_file_location", text)

    def test_importing_flag_modules_loads_no_retired_or_lazy_core_module(self) -> None:
        probe = (
            "import json, sys\n"
            "import joulewise\n"
            "baseline = set(m for m in sys.modules if m.startswith('joulewise'))\n"
            "import joulewise.flags, joulewise.flags.schema, joulewise.flags.catalog, joulewise.flags.sink\n"
            "import joulewise.flags.exclusions, joulewise.flags.collect\n"
            "print(json.dumps(sorted(m for m in sys.modules if m.startswith('joulewise') and m not in baseline)))\n"
        )
        completed = subprocess.run([sys.executable, "-B", "-c", probe], cwd=REPO, capture_output=True, text=True,
                                   check=True)
        loaded = set(json.loads(completed.stdout))
        self.assertEqual(sorted(loaded & RETIRED_MODULES), [])
        self.assertEqual(sorted(loaded - {"joulewise.flags", "joulewise.flags.schema",
                                          "joulewise.flags.catalog", "joulewise.flags.sink",
                                          "joulewise.flags.exclusions", "joulewise.flags.collect"}), [])

    def test_arm_decision_imports_no_flag_code(self) -> None:
        hazards = REPO / "joulewise" / "hazards"
        if not (hazards / "arm.py").exists():
            self.skipTest("joulewise/hazards/arm.py not in this tree yet (lane L1)")
        for path in sorted(hazards.glob("*.py")):
            if path.name == "monitor.py":
                continue
            names = imported_names(path, "joulewise.hazards")
            with self.subTest(module=path.name):
                self.assertEqual(sorted(n for n in names if n.startswith("joulewise.flags")), [])


if __name__ == "__main__":
    unittest.main()
