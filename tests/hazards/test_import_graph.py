"""Plan §2.1 and §2.4: the hazard path cannot reach the retired path.

``joulewise/hazards`` (and ``joulewise/flags`` once that package exists) must
not import, directly or through anything they import, the retired
TRANSACTION_PACK route (``arm_readiness*``, ``capture_t0_step``,
``launch_window``, ``t0_rehearsal``, ``v5_qualification`` and the rest of
plan §7's retired list); and the arm imports no flag code.

Two proofs: a static graph over every import that runs when a module is
imported (module and class bodies), plus every import inside the hazard
modules' own functions; and a dynamic run of a complete arm and monitor in a
fresh interpreter, whose ``sys.modules`` must hold none of them.  The one
deliberate exception is ``instrument._child_main``, which imports the
production powermetrics adapter (and so the measurement core) only inside the
cadence probe's child process.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import unittest
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIRED = (
    "joulewise.arm_readiness",  # also arm_readiness_evidence, arm_readiness_evidence_t0
    "joulewise.t0_rehearsal", "joulewise.v5_qualification", "joulewise.network_time_off",
    "joulewise.dwell", "joulewise.arm_retry",
    "scripts.capture_t0_step", "scripts.launch_window", "scripts.author_arm_evidence_t0",
    "scripts.author_arm_readiness_evidence", "scripts.generate_arm_readiness",
    "scripts.write_v5_qualification_plan", "scripts.harvest_v5_qualification",
    "scripts.harvest_v5_g2b_window", "scripts.v5_s1_desk_closeout", "scripts.check_v5_arm_abort",
    "scripts.produce_t0_rehearsal_bundle", "scripts.rehearse_t0_unattended",
    "scripts.restore_v5_null_reservation", "scripts.assemble_v5_battery_boundaries",
    "scripts.ed_session",
)
FLAG_CODE = ("joulewise.flags",)
CHILD_ONLY = {("joulewise.hazards.instrument", "_child_main")}


def is_retired(name: str) -> bool:
    return any(name == item or name.startswith(item + ".") or
               (item == "joulewise.arm_readiness" and name.startswith(item))
               for item in RETIRED)


def module_path(name: str) -> Path | None:
    base = ROOT.joinpath(*name.split("."))
    if base.with_suffix(".py").is_file():
        return base.with_suffix(".py")
    if (base / "__init__.py").is_file():
        return base / "__init__.py"
    return None


def first_party(name: str) -> bool:
    return name.split(".")[0] in ("joulewise", "scripts") and module_path(name) is not None


def _resolve(node: ast.AST, module: str, is_package: bool) -> list[str]:
    names = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            names.append(alias.name)
    elif isinstance(node, ast.ImportFrom):
        if node.level:
            parts = module.split(".")
            base = parts if is_package else parts[:-1]
            base = base[:len(base) - (node.level - 1)]
            prefix = ".".join(base + ([node.module] if node.module else []))
        else:
            prefix = node.module or ""
        names.append(prefix)
        for alias in node.names:
            names.append(f"{prefix}.{alias.name}")
    out = []
    for name in names:
        parts = name.split(".")
        for end in range(1, len(parts) + 1):  # importing a.b.c runs a and a.b first
            candidate = ".".join(parts[:end])
            if first_party(candidate):
                out.append(candidate)
    return out


@lru_cache(maxsize=None)
def imports(module: str, *, functions: bool = False) -> tuple[tuple[str, str | None], ...]:
    """(imported module, enclosing function or None) for one first-party module."""

    path = module_path(module)
    tree = ast.parse(path.read_text())
    is_package = path.name == "__init__.py"
    found: list[tuple[str, str | None]] = []

    def walk(node: ast.AST, function: str | None) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                if functions:
                    walk(child, getattr(child, "name", "<lambda>") if function is None else function)
                continue
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                found.extend((name, function) for name in _resolve(child, module, is_package))
            walk(child, function)

    walk(tree, None)
    return tuple(found)


def reachable(roots: list[str], *, own_functions: set[str]) -> dict[str, list[str]]:
    """Module -> path from a root, following import-time imports everywhere and
    function-level imports inside ``own_functions`` modules (except CHILD_ONLY)."""

    paths = {root: [root] for root in roots}
    queue = list(roots)
    while queue:
        current = queue.pop()
        edges = imports(current, functions=current in own_functions)
        for name, function in edges:
            if (current, function) in CHILD_ONLY:
                continue
            if name not in paths:
                paths[name] = paths[current] + [name]
                queue.append(name)
    return paths


def package_modules(package: str) -> list[str]:
    directory = ROOT.joinpath(*package.split("."))
    return [package] + [f"{package}.{path.stem}" for path in sorted(directory.glob("*.py"))
                        if path.stem != "__init__"]


class ImportGraphTests(unittest.TestCase):
    def assert_clean(self, roots, forbidden):
        own = set(roots)
        paths = reachable(roots, own_functions=own)
        bad = {name: path for name, path in paths.items() if forbidden(name)}
        self.assertEqual(bad, {}, "\n".join(" -> ".join(path) for path in bad.values()))
        return paths

    def test_hazard_modules_reach_no_retired_module(self):
        paths = self.assert_clean(package_modules("joulewise.hazards") + ["scripts.hazard_monitor"],
                                  is_retired)
        # the reused measurement helpers are reached, as the plan intends
        for reused in ("joulewise.kernel_clock", "joulewise.clock_reference", "joulewise.battery_float",
                       "joulewise.quiet_admission", "joulewise.prewindow"):
            self.assertIn(reused, paths)

    def test_the_analyzer_sees_the_measurement_core_reach_arm_readiness(self):
        # Positive control: bundle.py imports arm_readiness at module level, so a
        # hazard module importing the core directly would be caught.
        paths = reachable(["joulewise.bundle"], own_functions=set())
        self.assertIn("joulewise.arm_readiness", paths)
        paths = reachable(["joulewise.hazards.instrument"], own_functions={"joulewise.hazards.instrument"})
        self.assertNotIn("joulewise.adapters.powermetrics", paths)
        child = imports("joulewise.hazards.instrument", functions=True)
        self.assertIn(("joulewise.adapters.powermetrics", "_child_main"), child)

    def test_hazard_modules_import_no_flag_code(self):
        self.assert_clean(package_modules("joulewise.hazards") + ["scripts.hazard_monitor"],
                          lambda name: any(name == item or name.startswith(item + ".")
                                           for item in FLAG_CODE))

    def test_flags_package_reaches_no_retired_module(self):
        if module_path("joulewise.flags") is None:
            self.skipTest("joulewise/flags (lane L4) is not in this tree yet")
        self.assert_clean(package_modules("joulewise.flags"), is_retired)

    def test_the_adapter_import_is_confined_to_the_capture_child(self):
        tree = ast.parse((ROOT / "joulewise/hazards/instrument.py").read_text())
        importers = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.ImportFrom) and (inner.module or "").startswith("joulewise.adapters"):
                        importers.add(node.name)
        self.assertEqual(importers, {"_child_main"})
        for path in (ROOT / "joulewise" / "hazards").glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Name) and node.id == "_child_main":
                    self.fail(f"{path.name} calls _child_main in process")
                if isinstance(node, ast.Attribute) and node.attr == "_child_main":
                    self.fail(f"{path.name} calls _child_main in process")
        from joulewise.hazards import instrument
        self.assertIn("_child_main", instrument.CHILD_BOOTSTRAP)

    def test_a_complete_arm_and_monitor_run_load_no_retired_module(self):
        """Run the real arm (fakes at the hardware seams; the cadence probe's real
        child) and the real monitor in a fresh interpreter; list what was loaded."""

        script = r"""
import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from joulewise.hazards import arm, base, monitor
from tests.hazards.test_arm import Rig
from tests.hazards.test_monitor import FakeMac
root = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
rig = Rig(root / "arm")
result = rig.run()
mac = FakeMac(root / "monitor")
instance = mac.monitor()
instance.open_session()
instance.run(max_seconds=120)
instance.close_session("done")
print(json.dumps({"decision": result.decision, "modules": sorted(sys.modules)}))
"""
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        completed = subprocess.run([sys.executable, "-B", "-c", script, str(ROOT)], cwd=str(ROOT),
                                   capture_output=True, text=True, timeout=300, env=env)
        self.assertEqual(completed.returncode, 0, completed.stderr[-3000:])
        report = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(report["decision"], "GO")
        loaded = [name for name in report["modules"] if is_retired(name)
                  or any(name == item or name.startswith(item + ".") for item in FLAG_CODE)]
        self.assertEqual(loaded, [])
        # the instrument probe really ran its child (the adapter is not loaded here)
        self.assertNotIn("joulewise.adapters.powermetrics", report["modules"])
        self.assertNotIn("joulewise.bundle", report["modules"])


if __name__ == "__main__":
    unittest.main()
