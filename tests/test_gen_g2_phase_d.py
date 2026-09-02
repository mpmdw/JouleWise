"""Regression tests for the executable G2-a night-chain emitter."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gen_g2_phase_d.py"
RUNSHEET_PATH = REPO_ROOT / "docs" / "process_traces" / "2026-08-28-live-smoke" / "SHAKEDOWN-G2-RUNSHEET.md"


def _load_generator():
    spec = importlib.util.spec_from_file_location("gen_g2_phase_d_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _section(source: str, heading: str) -> str:
    start = source.index(heading)
    following = re.search(r"^## ", source[start + len(heading) :], re.MULTILINE)
    return source[start:] if following is None else source[start : start + len(heading) + following.start()]


def _independent_fence_inventory(source: str) -> list[tuple[int, int, str]]:
    """Fence parser intentionally independent of the production emitter."""

    result: list[tuple[int, int, str]] = []
    for heading in ("## Tree and fixed variables", "## G2-a — first machine evening"):
        section = _section(source, heading)
        offset = source.index(section)
        for match in re.finditer(r"^```(?:sh|zsh)\n(.*?)^```$", section, re.MULTILINE | re.DOTALL):
            start = source.count("\n", 0, offset + match.start()) + 1
            end = source.count("\n", 0, offset + match.end()) + 1
            result.append((start, end, match.group(1)))
    return result


class G2aNightChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = _load_generator()
        self.runsheet = RUNSHEET_PATH.read_text(encoding="utf-8")

    def test_inventory_has_every_shell_block_in_the_two_target_sections(self) -> None:
        independent = _independent_fence_inventory(self.runsheet)
        self.assertEqual(
            [(start, end) for start, end, _body in independent],
            [(161, 213), (237, 260), (283, 294), (298, 473), (484, 496)],
        )
        self.assertEqual(self.generator.inventory_g2a_shell_blocks(self.runsheet), independent)

    def test_identity_date_equals_the_full_reviewed_reconstruction(self) -> None:
        blocks = _independent_fence_inventory(self.runsheet)
        chain = self.generator.render_g2a_night_chain(self.runsheet, "20260830")
        required_inputs = (
            "# The desk producer runs while agents are present; require its outputs here.\n"
            'test -f "$G2A_INPUT_INVENTORY"\n'
            'test -f "$G2A_FROZEN_PLAN"\n'
            'test -f "$G2A_PROMPT_LADDER"\n'
        )
        expected = "#!/bin/zsh\nset -euo pipefail\n"
        for start, end, body in (blocks[0], blocks[1]):
            expected += f"\n# runsheet L{start}-{end}\n{body}"
        expected += "\n# arm-time input assertions\n" + required_inputs
        for start, end, body in (blocks[3], blocks[4]):
            expected += f"\n# runsheet L{start}-{end}\n{body}"
        self.assertEqual(chain, expected)
        self.assertNotEqual(chain + "# mutant line\n", expected)

    def test_date_substitution_is_confined_to_g2a_exports(self) -> None:
        blocks = _independent_fence_inventory(self.runsheet)
        replacement = "20300102"
        chain = self.generator.render_g2a_night_chain(self.runsheet, replacement)
        self.assertIn(blocks[1][2].replace("20260830", replacement), chain)
        for start, end, body in (blocks[0], blocks[3], blocks[4]):
            self.assertIn(f"# runsheet L{start}-{end}\n{body}", chain)
        self.assertNotIn("20260830", chain)

    def test_emit_writes_gnu_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "night-chain.zsh"
            self.generator.emit_g2a_night_chain(output, "20260830")
            contents = output.read_bytes()
            sidecar = output.with_name("night-chain.zsh.sha256").read_text(encoding="utf-8")
            self.assertEqual(
                sidecar,
                f"{hashlib.sha256(contents).hexdigest()}  night-chain.zsh\n",
            )
            self.assertTrue(output.stat().st_mode & 0o111)


if __name__ == "__main__":
    unittest.main()
