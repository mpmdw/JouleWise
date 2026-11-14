"""Guard the mint lane's one-home generation policy resolver."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

from joulewise.calibration_bracketing import D125_SCREEN_FLOOR_S

# RL-144 addendum M1: two pinned Block 6 programs carry the registered s_bracket (registration section 3.3,
# 10.818 ms) by design; an independent recompute carries its own copy. Exempt by name only, and each literal
# must equal the registry constant. Nothing else may copy it.
PINNED_LITERAL_FILES = {
    "joulewise/b6_analysis_check.py": r"calibration_bracket\([^)]*?(\d+\.\d+)\)",
    "scripts/independent_recompute_b6.py": r"^S_BRACKET_S\s*=\s*(\d+\.\d+)\s*$",
}


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
                if relative.as_posix() not in PINNED_LITERAL_FILES:
                    self.assertNotIn("0.010818", source)
                self.assertNotIn("0.009724", source)

    def test_the_two_pinned_programs_carry_exactly_the_registry_constant(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        for relative, pattern in PINNED_LITERAL_FILES.items():
            with self.subTest(relative=relative):
                source = (repository / relative).read_text(encoding="utf-8")
                literals = re.findall(pattern, source, re.MULTILINE | re.DOTALL)
                self.assertEqual(len(literals), 1)
                self.assertEqual(source.count("0.010818"), 1)
                self.assertEqual(str(D125_SCREEN_FLOOR_S), literals[0])
