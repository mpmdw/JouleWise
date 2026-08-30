from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "paper_renumber_refs.py"
REAL_DRAFT = ROOT / "docs" / "paper" / "draft-v1.md"
REAL_DRAFT_SHA256 = "939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab"
EXPECTED_ORPHANS = {4, 9, 11, 14, 16, 17, 18, 21, 24, 25}
EXPECTED_MAP = {
    1: 1,
    2: 2,
    3: 3,
    5: 4,
    6: 5,
    7: 6,
    8: 7,
    10: 8,
    12: 9,
    13: 10,
    15: 11,
    19: 12,
    20: 13,
    22: 14,
    23: 15,
    26: 16,
    27: 17,
    28: 18,
    29: 19,
    30: 20,
    31: 21,
}


FIXTURE = r"""# Fixture

Citations [1] [3] and a comma group [1, 3].
Placeholders [PENDING], [PENDING, PENDING], [RESULT PENDING NOW], and
[REPOSITORY AND ARCHIVE LOCATORS PENDING] stay put, as do
[[NEEDS-VALUE: fixture]], [TERM_A_FIXTURE], and [2](https://example.invalid).
An unknown-range group [1, 4] is not partly rewritten.
Inline code `[2]` is protected.
\[
[2]
\]

```text
[2]
```

## 11. References

1. A. Able. “Kept one.”
2. B. Baker. “Uncited orphan.”
3. C. Charlie. “Kept three.”

## Appendix A. Fixture suffix

The suffix can cite [3].
"""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(*arguments: object, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *(str(argument) for argument in arguments)],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _parse_report(stdout: str) -> tuple[set[int], dict[int, int]]:
    orphan_line = next(line for line in stdout.splitlines() if line.startswith("ORPHANS:"))
    orphans = {int(value) for value in re.findall(r"\d+", orphan_line)}
    mapping = {
        int(old): int(new)
        for old, new in re.findall(r"^  (\d+) -> (\d+)$", stdout, flags=re.MULTILINE)
    }
    return orphans, mapping


class PaperRenumberRefsTests(unittest.TestCase):
    def test_fixture_dry_run_apply_exclusions_and_idempotence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            draft = Path(tmp_dir) / "fixture.md"
            draft.write_text(FIXTURE, encoding="utf-8")
            original = draft.read_bytes()

            dry_run = _run(draft)
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertIn("MODE: dry-run", dry_run.stdout)
            self.assertEqual(_parse_report(dry_run.stdout), ({2}, {1: 1, 3: 2}))
            self.assertEqual(draft.read_bytes(), original)

            applied = _run(draft, "--apply")
            self.assertEqual(applied.returncode, 0, applied.stderr)
            rewritten = draft.read_text(encoding="utf-8")
            self.assertIn("Citations [1] [2] and a comma group [1, 2].", rewritten)
            self.assertIn("The suffix can cite [2].", rewritten)
            self.assertIn("2. C. Charlie. “Kept three.”", rewritten)
            self.assertNotIn("B. Baker", rewritten)
            for protected in (
                "[PENDING]",
                "[PENDING, PENDING]",
                "[RESULT PENDING NOW]",
                "[REPOSITORY AND ARCHIVE LOCATORS PENDING]",
                "[[NEEDS-VALUE: fixture]]",
                "[TERM_A_FIXTURE]",
                "[2](https://example.invalid)",
                "[1, 4]",
                "Inline code `[2]`",
                "\\[\n[2]\n\\]",
                "```text\n[2]\n```",
            ):
                self.assertIn(protected, rewritten)

            first_application = draft.read_bytes()
            second = _run(draft, "--apply")
            self.assertEqual(second.returncode, 3)
            self.assertIn("ALREADY RENUMBERED", second.stderr)
            self.assertEqual(draft.read_bytes(), first_application)

    def test_real_draft_default_dry_run_has_ruled_orphans_and_map(self) -> None:
        self.assertEqual(_sha256(REAL_DRAFT), REAL_DRAFT_SHA256)
        result = _run(REAL_DRAFT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MODE: dry-run", result.stdout)
        self.assertEqual(_parse_report(result.stdout), (EXPECTED_ORPHANS, EXPECTED_MAP))
        self.assertEqual(_sha256(REAL_DRAFT), REAL_DRAFT_SHA256)

    def test_real_draft_apply_requires_round_7_guard_and_preserves_bytes(self) -> None:
        before = REAL_DRAFT.read_bytes()
        self.assertEqual(hashlib.sha256(before).hexdigest(), REAL_DRAFT_SHA256)
        result = _run(REAL_DRAFT, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --i-am-round-7", result.stderr)
        after = REAL_DRAFT.read_bytes()
        self.assertEqual(after, before)
        self.assertEqual(hashlib.sha256(after).hexdigest(), REAL_DRAFT_SHA256)


if __name__ == "__main__":
    unittest.main()
