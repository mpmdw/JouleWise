"""PR #775 row-1 review: the runner's frozen-bytes preflight and its work reserve (mutants b and h2).

Tests only; no frozen path changes. No host, model or energy is touched."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.cadence import legs as legsmod
from scripts import cadence_legs_runner as runner
from tests.git_fixture import init_git_fixture
from tests.cadence.test_legs_runner import NEW_WINDOW, campaign_kit, local

TMP = os.environ.get("TMPDIR")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


class FrozenPreflightTests(unittest.TestCase):
    """``verify_frozen_production``: HEAD must be the kit's frozen commit and every frozen path's
    working-tree bytes must hash as the kit says."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.root = Path(self.tmp.name)
        init_git_fixture(self.root, "-q")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "user.name", "test")
        (self.root / "scripts").mkdir()
        self.files = {"scripts/cadence_legs_runner.py": b"runner bytes\n", "configs/r1_runtime.json": b"{}\n"}
        for rel, data in self.files.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_bytes(data)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "frozen")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.kit = {"frozen": {"commit": self.head,
                               "paths": {p: hashlib.sha256(d).hexdigest() for p, d in self.files.items()}}}
        patcher = patch.object(runner, "ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def test_matching_bytes_pass(self):
        result = runner.verify_frozen_production(self.kit)
        self.assertEqual((result["rc"], result["head"], result["paths"]), (0, self.head, 2))

    def test_a_flipped_frozen_file_refuses(self):
        (self.root / "configs/r1_runtime.json").write_bytes(b'{"flipped": true}\n')
        with self.assertRaisesRegex(runner.SpanRefusal, r"frozen paths differ.*configs/r1_runtime.json"):
            runner.verify_frozen_production(self.kit)

    def test_a_missing_frozen_file_refuses(self):
        (self.root / "scripts/cadence_legs_runner.py").unlink()
        with self.assertRaisesRegex(runner.SpanRefusal, "frozen paths differ"):
            runner.verify_frozen_production(self.kit)

    def test_head_other_than_the_frozen_commit_refuses(self):
        kit = {"frozen": {**self.kit["frozen"], "commit": "0" * 40}}
        with self.assertRaisesRegex(runner.SpanRefusal, "is not the kit's frozen commit"):
            runner.verify_frozen_production(kit)
        # A later commit whose frozen bytes are unchanged is still not the frozen commit.
        (self.root / "README").write_text("later\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "later")
        with self.assertRaisesRegex(runner.SpanRefusal, "is not the kit's frozen commit"):
            runner.verify_frozen_production(self.kit)

    def test_a_refused_preflight_runs_nothing_and_still_closes(self):
        (self.root / "configs/r1_runtime.json").write_bytes(b"changed\n")
        out = self.root / "span"
        clock = runner.FakeClock(local("2026-11-15T13:20"))
        deps = runner.mock_deps(out, clock)
        deps.verify_frozen, deps.max_span_s = runner.verify_frozen_production, runner.max_span_s()
        kit = {**campaign_kit(), "frozen": self.kit["frozen"]}
        plan = legsmod.plan_span(kit, t0_epoch=clock.time(), windows=NEW_WINDOW)
        rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, deadline=runner.launch_deadline(plan),
                             windows=NEW_WINDOW, deps=deps)
        receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
        self.assertEqual(rc, 2)
        self.assertEqual(next(s for s in receipt["steps"] if s["rc"])["name"], "frozen")
        self.assertEqual(deps.fake.calls, [])
        self.assertEqual(deps.host.calls[-1], "restore")


class WorkReserveTests(unittest.TestCase):
    """The work deadline is ``--deadline`` less WORK_RESERVE_S: the close must fit inside the reserve."""

    def span(self, deadline_offset):
        tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / "span"
        clock = runner.FakeClock(local("2026-11-15T13:20"))
        deps = runner.mock_deps(out, clock)
        deps.max_span_s = runner.max_span_s()
        rc = runner.run_span(kit=campaign_kit(), kit_sha256="f" * 64, output=out,
                             deadline=clock.time() + deadline_offset, windows=NEW_WINDOW, deps=deps)
        return rc, json.loads((out / runner.RECEIPT_NAME).read_text()), deps

    def test_a_deadline_inside_the_reserve_starts_nothing(self):
        self.assertGreater(runner.WORK_RESERVE_S, 0)
        rc, receipt, deps = self.span(runner.WORK_RESERVE_S - 1)
        self.assertEqual(rc, 3)
        self.assertEqual(receipt["steps"][0]["name"], "deadline")
        self.assertEqual(receipt["steps"][0]["rc"], 3)
        self.assertIn("work deadline reached; cleanup reserve retained", receipt["error"])
        self.assertEqual(deps.host.calls, ["restore"])          # nothing ran; the close still did

    def test_the_reserve_is_subtracted_from_the_remaining_time(self):
        rc, receipt, _ = self.span(runner.WORK_RESERVE_S + 50)
        self.assertEqual(receipt["steps"][0]["result"]["remaining_s"], 50)
        self.assertNotEqual(rc, 0)                               # 50 s cannot hold a span: the plan refuses

    def test_a_leg_whose_runtime_would_cross_the_reserve_is_not_run(self):
        # Enough for the dwell, the soak, L001 and all but 100 s of L002: L002 fits only if the
        # 370 s reserve is (wrongly) spent, so it must not start.
        kit = campaign_kit()
        clock = runner.FakeClock(local("2026-11-15T13:20"))
        spec, spec2 = legsmod.leg_specs(kit, ["L001", "L002"])
        tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / "span"
        deps = runner.mock_deps(out, clock)
        deps.max_span_s = runner.max_span_s()
        g0 = 90.0 + spec["seed"] % 240
        first_leg = legsmod.leg_expected_s(spec) - legsmod.TIME_MODEL["g0_s"] + g0
        second_leg = legsmod.leg_expected_s(spec2) - legsmod.TIME_MODEL["g0_s"] + 90.0 + spec2["seed"] % 240
        self.assertGreater(runner.WORK_RESERVE_S, 100)
        budget = 300 + 1830 + first_leg + second_leg - 100
        real_plan = legsmod.plan_span

        def roomy_plan(*a, **kw):
            value = real_plan(*a, **kw)
            return {**value, "soak_s": 0, "redo_quota": 0, "leg_cap_s": 0}    # let the span start
        with patch.object(legsmod, "plan_span", side_effect=roomy_plan):
            rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out,
                                 deadline=clock.time() + budget + runner.WORK_RESERVE_S, windows=NEW_WINDOW,
                                 deps=deps, leg_ids=["L001", "L002"])
        receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
        self.assertEqual(rc, 3)
        self.assertEqual(receipt["legs_finished"], 1)
        self.assertIn("L002: mock leg would overrun the work deadline", receipt["error"])
        self.assertFalse((out / "legs/L002/leg_summary.json").exists())


if __name__ == "__main__":
    unittest.main()
