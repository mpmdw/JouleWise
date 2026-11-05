"""Source-only proof of the main closure, including lazy import edges."""
from __future__ import annotations

import ast
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
RETIRED = {
    "joulewise.arm_readiness", "joulewise.arm_readiness_evidence",
    "joulewise.arm_readiness_evidence_t0", "joulewise.arm_retry",
    "joulewise.dwell", "joulewise.network_time_off", "joulewise.scheduler_gates",
    "joulewise.t0_rehearsal", "joulewise.v5_qualification",
    "scripts.assemble_v5_battery_boundaries", "scripts.author_arm_evidence_t0",
    "scripts.author_arm_readiness_evidence", "scripts.capture_t0_step",
    "scripts.check_v5_arm_abort", "scripts.generate_arm_readiness",
    "scripts.harvest_v5_g2b_window", "scripts.harvest_v5_qualification",
    "scripts.launch_window", "scripts.produce_t0_rehearsal_bundle",
    "scripts.rehearse_t0_unattended", "scripts.restore_v5_null_reservation",
    "scripts.v5_s1_desk_closeout", "scripts.write_v5_qualification_plan",
    "scripts.ed_session.capture_t0_anchor_positive_control",
}


def source_modules():
    paths = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard",
         "joulewise", "scripts"], cwd=ROOT,
        env=dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1"),
        text=True,
    ).splitlines()
    return {
        p.removesuffix(".py").replace("/", ".").removesuffix(".__init__"): ROOT / p
        for p in paths if p.endswith(".py") and "restricted" not in Path(p).parts
        and (ROOT / p).is_file()
    }


def import_edges(tree, module, package=False):
    """All lexical imports plus literal dynamic imports; no provenance strings."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = node.module or ""
            if node.level:
                base = module.split(".") if package else module.split(".")[:-1]
                prefix = ".".join(base[:len(base) - node.level + 1] + ([prefix] if prefix else []))
            found.add(prefix)
            found.update(prefix + "." + a.name for a in node.names)
        elif isinstance(node, ast.Call) and node.args:
            name = ast.unparse(node.func)
            if name == "__import__" or name.endswith(".import_module"):
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found.add(arg.value)
    return {name for name in found if name.split(".")[0] in {"joulewise", "scripts"}}


class MainClosureTests(unittest.TestCase):
    def test_every_remaining_production_module_excludes_retired_imports(self):
        modules = source_modules()
        failures = []
        for name, path in sorted(modules.items()):
            if name in RETIRED:
                continue  # Removed in the subsequent deletion commit.
            edges = import_edges(ast.parse(path.read_text(), filename=str(path)), name,
                                 path.name == "__init__.py")
            for edge in edges:
                # Test missing targets too: deleting a module must not hide an edge.
                if any(edge == retired or edge.startswith(retired + ".") for retired in RETIRED):
                    failures.append(f"{name} -> {edge}")
        self.assertEqual(failures, [], "\n".join(failures))

    def test_analyzer_sees_lazy_relative_and_dynamic_imports(self):
        tree = ast.parse('''
def lazy():
    from . import arm_readiness
    import joulewise.arm_readiness_evidence_t0
    importlib.import_module("scripts.launch_window")
''')
        edges = import_edges(tree, "joulewise.example")
        self.assertTrue({"joulewise.arm_readiness", "joulewise.arm_readiness_evidence_t0",
                         "scripts.launch_window"} <= edges)


if __name__ == "__main__":
    unittest.main()
