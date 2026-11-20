"""CI coverage for the frozen hp-02 item and occupancy contracts."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile


DRAFTS = (Path(__file__).resolve().parents[1]
          / "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-f2-0203")
FIXTURES = DRAFTS / "hp-02/fixtures"


class HP02SuccessorItemsTests(unittest.TestCase):
    def test_frozen_gate_vectors_and_timing(self):
        def check(script, *args, want=0):
            result = subprocess.run(
                [sys.executable, "-IB", str(script), *map(str, args)],
                capture_output=True, text=True, timeout=180,
            )
            self.assertEqual(result.returncode, want, result.stdout + result.stderr)
            return result.stdout

        with tempfile.TemporaryDirectory(prefix="hp02-acceptance-") as scratch:
            scratch = Path(scratch)
            with ZipFile(FIXTURES / "hp02-occupancy-fixture.zip") as archive:
                self.assertEqual(archive.read("fixtures/successor_regression.py"),
                                 (FIXTURES / "successor_regression.py").read_bytes())
                self.assertEqual(archive.read("fixtures/inputs/item-cases.json"),
                                 (FIXTURES / "item-cases.json").read_bytes())
                archive.extractall(scratch)
            fixture = scratch / "fixtures"
            output = check(DRAFTS / "tests/test_hp_gates.py", scratch, scratch)
            self.assertIn("60 original decisions, 54 timing decisions, 1764 clock cases, 11 dated pairs, "
                          "0 native command attempts", output)
            output = check(fixture / "clocked_occupancy.py")
            self.assertIn("1764 explicit clock plans, 43 clocked runner traces, 11 dated pairs, "
                          "60 inherited vector IDs; native attempts 0", output)
            self.assertIn("PASS 0 mismatches / 54 decisions",
                          check(fixture / "successor_regression.py", "--candidate", scratch / "timing-decisions.json"))
            self.assertIn("FAIL 27 mismatches / 54 decisions",
                          check(fixture / "successor_regression.py", want=1))
            self.assertIn("60 successor decisions specified", check(fixture / "replay_contract.py"))

    def test_legacy_held_items_replay(self):
        root = Path(__file__).resolve().parents[1]
        path = (DRAFTS / "hp-02").relative_to(root)
        with tempfile.TemporaryDirectory(prefix="hp02-held-") as scratch:
            seat = Path(scratch)
            (seat / "fixtures").mkdir()
            for name in ("replay_legacy.py", "item-cases.json"):
                (seat / "fixtures" / name).write_bytes((FIXTURES / name).read_bytes())
            (seat / "tmp/runtime").mkdir(parents=True)
            draft = seat / "tmp/drafts/hp-02"
            draft.mkdir(parents=True)
            for name in ("gates.sh", *(f"ITEM-hp-02-s{piece:02d}.md" for piece in (1, 2, 3))):
                data = subprocess.check_output(["git", "show", f"a32eb54ce:{path}/{name}"], cwd=root)
                (draft / name).write_bytes(data)
            result = subprocess.run(
                [sys.executable, "-IB", str(seat / "fixtures/replay_legacy.py")],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("60 cases x 3 items x 2 shells PASS (legacy only)", result.stdout)
            self.assertIn("clear-date-no-qualification legacy_rc=1 WAIT", result.stdout)
            self.assertIn("pair-plus-one legacy_rc=0 HP02 GATES PASS", result.stdout)
