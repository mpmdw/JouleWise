"""Guard the mint lane's one-home generation policy resolver."""

from __future__ import annotations

from pathlib import Path
import unittest


class MintPolicyResolverGuardTests(unittest.TestCase):
    def test_mint_lane_has_no_copied_bracket_screen_literals(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        kernel_sources = (
            "joulewise/floor_mint_estimator.py",
            "joulewise/detection_floor.py",
            "scripts/mint_floor_artifact_generalized.py",
        )
        for relative in kernel_sources:
            with self.subTest(relative=relative):
                source = (repository / relative).read_text(encoding="utf-8")
                self.assertNotIn("0.010818", source)
                self.assertNotIn("0.009724", source)

