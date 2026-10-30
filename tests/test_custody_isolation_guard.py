"""Tests must never resolve the custody registry under the real home directory.

``custody_parent()`` defaults to ``~/night-custody`` when
``JOULEWISE_CUSTODY_PARENT`` is unset, and campaigns publish
``active-campaigns`` entries there that the liveness census, the quiet guard
and run_campaign's stale-lock reclaim read. CI and the local runners import
test files as top-level modules, so no package-level hook in tests/ can set the
variable for the whole suite; each module that can reach a custody writer or
reader isolates itself with ``tests.custody_isolation`` instead, and this
module keeps that from regressing.
"""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise import measurement_liveness
from tests.custody_isolation import (
    ADDITIONAL_PARENTS_ENV,
    CUSTODY_PARENT_ENV,
    isolate_custody_parent,
)

TESTS = Path(__file__).resolve().parent

# Modules observed reaching custody_parent() in a full-suite probe
# (CUSTODY-T1, 2026-10-30), plus the window_status.sh caller, which runs
# measurement_liveness.py as a script.
REACHING_MODULES = frozenset({
    "test_axi_controller_events.py",
    "test_axi_mock_spec.py",
    "test_collector_analysis_manifest_id.py",
    "test_measurement_liveness.py",
    "test_run_campaign.py",
    "test_run_campaign_hazard_flags.py",
    "test_run_campaign_max_blocks.py",
    "test_run_campaign_p2_rc.py",
    "test_window_status_guard.py",
})

# Source shapes that drive a real custody writer or reader. A module whose
# source matches one must isolate the custody parent.
REACH_MARKERS = {
    "axi spec campaign": re.compile(r"\brun_axi_spec_campaign\("),
    "registry publish": re.compile(r"\bpublish_campaign\("),
    "custody parent": re.compile(r"\bcustody_parent\(\)"),
    "run_campaign main": re.compile(r"\brun_campaign(?:_module)?\.main\("),
    "shared run_campaign runner": re.compile(
        r"from tests\.test_run_campaign import (?:\([^)]*|[^\n]*)\brun_campaign\b"),
    "run_campaign.py argv": re.compile(
        r"str\(\s*(?:ROOT|REPO_ROOT|REPOSITORY)\s*/\s*[\"']scripts/run_campaign\.py[\"']\s*\)"),
    "liveness script": re.compile(r"window_status\.sh|measurement_liveness\.py"),
}
ISOLATION = re.compile(r"\bisolate_custody_parent\(|JOULEWISE_CUSTODY_PARENT|\bCUSTODY_PARENT_ENV\b")


def _test_sources() -> dict[Path, str]:
    return {path: path.read_text(encoding="utf-8")
            for path in sorted(TESTS.rglob("test_*.py")) if path.resolve() != Path(__file__).resolve()}


def _reaching(source: str) -> list[str]:
    return [name for name, marker in REACH_MARKERS.items() if marker.search(source)]


class StaticCustodyIsolationTests(unittest.TestCase):
    def test_every_module_that_reaches_custody_isolates_it(self) -> None:
        bare = {str(path.relative_to(TESTS)): hits
                for path, source in _test_sources().items()
                if (hits := _reaching(source)) and not ISOLATION.search(source)}
        self.assertEqual(bare, {}, "these test modules can reach custody_parent() without "
                         "JOULEWISE_CUSTODY_PARENT; call tests.custody_isolation.isolate_custody_parent")

    def test_observed_reaching_modules_are_still_isolated_and_still_scanned(self) -> None:
        sources = {path.name: source for path, source in _test_sources().items() if path.parent == TESTS}
        for name in sorted(REACHING_MODULES):
            with self.subTest(module=name):
                self.assertIn(name, sources)
                self.assertRegex(sources[name], ISOLATION)
                # The markers must recognise every module the probe saw reach custody.
                self.assertTrue(_reaching(sources[name]), name)


class IsolationHelperTests(unittest.TestCase):
    def test_per_test_isolation_points_outside_home_and_restores_unset(self) -> None:
        clean = {key: value for key, value in os.environ.items()
                 if key not in (CUSTODY_PARENT_ENV, ADDITIONAL_PARENTS_ENV)}
        with patch.dict(os.environ, clean, clear=True):
            case = unittest.TestCase()
            parent = isolate_custody_parent(case)
            self.assertEqual(measurement_liveness.custody_parent(), parent)
            self.assertEqual(os.environ[ADDITIONAL_PARENTS_ENV], "[]")
            self.assertTrue(parent.is_relative_to(Path(tempfile.gettempdir()).resolve()))
            self.assertFalse(parent.is_relative_to(Path("~").expanduser().resolve() / "night-custody"))
            entry = measurement_liveness.publish_campaign(
                parent / "runs", "guard", observer=lambda pid: measurement_liveness.Identity("UNKNOWN"))
            self.assertEqual(entry.path.parent, parent / "active-campaigns")
            case.doCleanups()
            self.assertNotIn(CUSTODY_PARENT_ENV, os.environ)
            self.assertNotIn(ADDITIONAL_PARENTS_ENV, os.environ)
            self.assertFalse(parent.parent.exists())

    def test_per_test_isolation_restores_a_previous_value(self) -> None:
        with patch.dict(os.environ, {CUSTODY_PARENT_ENV: "/previous", ADDITIONAL_PARENTS_ENV: '["/x"]'}):
            case = unittest.TestCase()
            parent = isolate_custody_parent(case)
            self.assertEqual(os.environ[CUSTODY_PARENT_ENV], str(parent))
            case.doCleanups()
            self.assertEqual(os.environ[CUSTODY_PARENT_ENV], "/previous")
            self.assertEqual(os.environ[ADDITIONAL_PARENTS_ENV], '["/x"]')

    def test_module_scope_registers_module_cleanups(self) -> None:
        registered = []
        with patch.object(unittest, "addModuleCleanup",
                          side_effect=lambda function, *a, **k: registered.append(function)):
            with patch.dict(os.environ, {}):
                parent = isolate_custody_parent()
                self.assertEqual(os.environ[CUSTODY_PARENT_ENV], str(parent))
                for function in reversed(registered):
                    function()
        self.assertEqual(len(registered), 2)
        self.assertFalse(parent.parent.exists())


class ProductionDefaultTests(unittest.TestCase):
    def test_custody_parent_default_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            clean = {key: value for key, value in os.environ.items() if key != CUSTODY_PARENT_ENV}
            with patch.dict(os.environ, {**clean, "HOME": home}, clear=True):
                self.assertEqual(measurement_liveness.custody_parent(), Path(home) / "night-custody")
            with patch.dict(os.environ, {CUSTODY_PARENT_ENV: "~/elsewhere", "HOME": home}):
                self.assertEqual(measurement_liveness.custody_parent(), Path(home) / "elsewhere")
        self.assertEqual(measurement_liveness.CUSTODY_PARENT_ENV, CUSTODY_PARENT_ENV)
        self.assertEqual(measurement_liveness.ADDITIONAL_PARENTS_ENV, ADDITIONAL_PARENTS_ENV)


if __name__ == "__main__":
    unittest.main()
