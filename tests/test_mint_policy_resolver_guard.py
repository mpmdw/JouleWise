"""Guard the mint lane's one-home generation policy resolver."""

from __future__ import annotations

from pathlib import Path
import unittest


class MintPolicyResolverGuardTests(unittest.TestCase):
    def test_mint_lane_has_no_copied_bracket_screen_literals(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        policy_registry = repository / "joulewise/calibration_bracketing.py"
        mint_lane_sources = sorted(
            source
            for root in (repository / "joulewise", repository / "scripts")
            for source in root.rglob("*.py")
            if source != policy_registry
        )
        self.assertTrue(mint_lane_sources)
        for path in mint_lane_sources:
            relative = path.relative_to(repository)
            with self.subTest(relative=str(relative)):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("0.010818", source)
                self.assertNotIn("0.009724", source)
