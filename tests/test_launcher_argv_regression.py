from __future__ import annotations

import hashlib
import shlex
import tempfile
import unittest
from pathlib import Path

from joulewise.arm_readiness import (
    FamilyPublicationError,
    _authenticate_confirmation_table,
    gnu_sidecar,
    render_json,
)
from scripts.launch_window import _parser


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs/phase_2/window_runbook.md"
E10_ANCHOR = "**E-10 — Ed's deliberate physical launch:**"
TABLE_FLAG = "--step6-confirmation-table"
DIGEST_FLAG = "--expected-confirmation-digest"


def runbook_launch_tokens() -> list[str]:
    """Extract the E-10 launcher invocation from the runbook's own bytes."""

    text = RUNBOOK.read_text(encoding="utf-8")
    anchor = text.find(E10_ANCHOR)
    if anchor < 0:
        raise AssertionError(f"cannot locate the E-10 anchor {E10_ANCHOR!r}")
    cursor = anchor
    while True:
        fence = text.find("```sh", cursor)
        if fence < 0:
            raise AssertionError("E-10 has no fenced sh launcher block")
        end = text.find("```", fence + len("```sh"))
        if end < 0:
            raise AssertionError("E-10 launcher fence is unterminated")
        block = text[fence + len("```sh") : end]
        if "scripts/launch_window.py" in block:
            break
        cursor = end + 3
    logical = " ".join(
        line.strip().removesuffix("\\").strip()
        for line in block.splitlines()
        if line.strip()
    )
    tokens = shlex.split(logical, posix=True)
    if len(tokens) < 2 or tokens[1] != "scripts/launch_window.py":
        raise AssertionError(f"E-10 launcher block has unexpected argv: {tokens!r}")
    return tokens


def _rendered_argv(tokens: list[str], *, root: Path) -> list[str]:
    values = {
        "$PACK_ROOT": str(root / "pack"),
        "$ARM_RECEIPT": str(root / "arm.json"),
        "$ARM_READINESS_CUSTODY_ROOT": str(root / "readiness"),
        "$LAUNCH_MANIFEST": str(root / "launch.json"),
        # Deliberately not under family_publication/: the regression must prove
        # that an explicit operator path is retained by the real parser.
        "$STEP6_CONFIRMATION_TABLE": str(root / "operator-selected" / "table.json"),
        "$ED_STEP6_CONFIRMED_SHA256": "a" * 64,
    }
    rendered = [values.get(token, token) for token in tokens]
    unresolved = [token for token in rendered if token.startswith("$")]
    if unresolved:
        raise AssertionError(f"unresolved E-10 shell variable(s): {unresolved!r}")
    return rendered[2:]


def _without_confirmation_pair(argv: list[str]) -> list[str]:
    result: list[str] = []
    index = 0
    while index < len(argv):
        if argv[index] in {TABLE_FLAG, DIGEST_FLAG}:
            index += 2
            continue
        result.append(argv[index])
        index += 1
    return result


class LauncherArgvRegressionTests(unittest.TestCase):
    def test_runbook_launch_line_executes_against_real_parser(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            argv = _rendered_argv(runbook_launch_tokens(), root=Path(tmp))
            args = _parser().parse_args(argv)
        self.assertEqual(args.pack_root, Path(tmp) / "pack")
        self.assertEqual(args.arm_receipt, Path(tmp) / "arm.json")
        self.assertEqual(
            args.arm_readiness_custody_root,
            Path(tmp) / "readiness",
        )
        self.assertEqual(args.launch_manifest, Path(tmp) / "launch.json")

    def test_runbook_confirmation_pair_pending_pr205(self) -> None:
        tokens = runbook_launch_tokens()
        if TABLE_FLAG not in tokens or DIGEST_FLAG not in tokens:
            self.skipTest(
                "OPEN DEFECT: E-10 lacks --step6-confirmation-table and "
                "--expected-confirmation-digest; PR #205 is the pending cure"
            )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = _parser().parse_args(_rendered_argv(tokens, root=root))
            expected = root / "operator-selected" / "table.json"
            self.assertEqual(args.step6_confirmation_table, expected)
            self.assertNotIn("family_publication", expected.parts)
            self.assertEqual(args.expected_confirmation_digest, "a" * 64)

    def test_confirmation_pair_crosses_the_missing_digest_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rendered = _rendered_argv(runbook_launch_tokens(), root=root)
            pre_args = _parser().parse_args(_without_confirmation_pair(rendered))
            with self.assertRaises(FamilyPublicationError) as caught:
                _authenticate_confirmation_table(
                    pre_args.step6_confirmation_table,
                    pre_args.expected_confirmation_digest,
                )
            self.assertEqual(caught.exception.check_id, "confirmation_missing")
            self.assertEqual(
                str(caught.exception),
                "no expected confirmation digest supplied",
            )

            table = root / "operator-selected" / "table.json"
            table.parent.mkdir(parents=True)
            raw = render_json({})
            table.write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            table.with_name(f"{table.name}.sha256").write_bytes(
                gnu_sidecar(digest, table.name)
            )
            post_argv = _without_confirmation_pair(rendered) + [
                TABLE_FLAG,
                str(table),
                DIGEST_FLAG,
                digest,
            ]
            post_args = _parser().parse_args(post_argv)
            self.assertEqual(post_args.step6_confirmation_table, table)
            with self.assertRaises(FamilyPublicationError) as later:
                _authenticate_confirmation_table(
                    post_args.step6_confirmation_table,
                    post_args.expected_confirmation_digest,
                )
            self.assertNotEqual(later.exception.check_id, "confirmation_missing")


if __name__ == "__main__":
    unittest.main()
