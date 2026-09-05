"""Regression tests for the S-0 immutable-line-audit runsheet block.

The production guard is intentionally inline in the operator runsheet.  These
tests execute that exact fenced shell block, replacing only the pinned specs
when a small counterfactual repository is needed.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.git_fixture import init_git_fixture


ROOT = Path(__file__).resolve().parents[1]
RUNSHEET = ROOT / "docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md"
EXECUTED_S0_HEAD = "f125ae70c5a57403d9543c197f9b4e41db581881"


def _line_audit_block() -> str:
    text = RUNSHEET.read_text(encoding="utf-8")
    marker = "**Immutable line audit.**"
    try:
        section = text.split(marker, 1)[1]
    except IndexError as exc:
        raise AssertionError("immutable line-audit section is missing") from exc
    match = re.search(r"```zsh\n(.*?)\n```", section, flags=re.DOTALL)
    if match is None:
        raise AssertionError("immutable line-audit zsh block is missing")
    return match.group(1)


def _block_specs(block: str) -> list[str]:
    match = re.search(
        r"^for spec in \\\n(?P<body>.*?)^do$",
        block,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError("line-audit spec list is missing")
    body = match.group("body").replace("\\\n", "\n")
    specs = shlex.split(body)
    if not specs:
        raise AssertionError("line-audit spec list is empty")
    return specs


def _replace_specs(block: str, specs: list[str]) -> str:
    rendered = "for spec in \\\n"
    for index, spec in enumerate(specs):
        continuation = " \\\n" if index < len(specs) - 1 else "\n"
        rendered += f"  {shlex.quote(spec)}{continuation}"
    rendered += "do"
    replaced, count = re.subn(
        r"^for spec in \\\n.*?^do$",
        rendered,
        block,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    if count != 1:
        raise AssertionError(f"expected one line-audit spec list, replaced {count}")
    return replaced


def _legacy_transcript(repository: Path, head: str, specs: list[str]) -> bytes:
    """Reproduce the former successful-path bytes for contract comparison."""

    transcript = bytearray()
    for spec in specs:
        source_file, line_ranges = spec.split(" ", 1)
        source = subprocess.run(
            ["git", "-C", str(repository), "show", f"{head}:{source_file}"],
            check=True,
            capture_output=True,
        ).stdout
        numbered = subprocess.run(
            ["nl", "-ba"], check=True, input=source, capture_output=True
        ).stdout
        selected = subprocess.run(
            ["sed", "-n", line_ranges],
            check=True,
            input=numbered,
            capture_output=True,
        ).stdout
        transcript.extend(selected)
    return bytes(transcript)


class S0LineAuditGuardTests(unittest.TestCase):
    maxDiff = None

    def _init_repository(
        self, root: Path, files: dict[str, str]
    ) -> tuple[Path, str]:
        repository = root / "repo"
        repository.mkdir()
        init_git_fixture(repository, "-q")
        subprocess.run(
            ["git", "config", "user.name", "line-audit fixture"],
            cwd=repository,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "line-audit@example.invalid"],
            cwd=repository,
            check=True,
        )
        for relative, contents in files.items():
            path = repository / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repository, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "line-audit fixture"],
            cwd=repository,
            check=True,
        )
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return repository, head

    def _run(
        self,
        block: str,
        repository: Path,
        head: str,
        root: Path,
    ) -> tuple[subprocess.CompletedProcess[str], Path]:
        proof = root / "proof"
        transcripts = proof / "transcripts"
        transcripts.mkdir(parents=True)
        environment_file = root / "env.sh"
        environment_file.write_text(
            "\n".join(
                (
                    "set -euo pipefail",
                    f"export CLONE={shlex.quote(str(repository))}",
                    f"export BASE={shlex.quote(head)}",
                    f"export PROOF={shlex.quote(str(proof))}",
                    f"export TRANS={shlex.quote(str(transcripts))}",
                    f"export PY={shlex.quote(sys.executable)}",
                    "die() { printf 'S-0 STOP: %s\\n' \"$*\" >&2; exit 1; }",
                    "",
                )
            ),
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["S0_ENV"] = str(environment_file)
        completed = subprocess.run(
            ["zsh", "-c", block],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        return completed, transcripts / "006-pinned-line-audit.txt"

    def test_unchanged_pin_set_passes_at_the_executed_s0_head(self) -> None:
        """The issued estate-10 head still yields the established transcript."""

        block = _line_audit_block()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            completed, transcript = self._run(
                block, ROOT, EXECUTED_S0_HEAD, root
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(transcript.is_file())
            self.assertEqual(
                transcript.read_bytes(),
                _legacy_transcript(ROOT, EXECUTED_S0_HEAD, _block_specs(block)),
            )

    def test_same_length_shifted_range_refuses(self) -> None:
        """The refuter's exact 165-line coordinate shift must fail closed."""

        block = _line_audit_block()
        specs = _block_specs(block)
        original = "scripts/generate_arm_readiness.py 28,192p"
        shifted = "scripts/generate_arm_readiness.py 27,191p"
        specs[specs.index(original)] = shifted
        block = _replace_specs(block, specs)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            completed, _transcript = self._run(
                block, ROOT, EXECUTED_S0_HEAD, root
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "line audit coordinate/content mismatch for "
            "scripts/generate_arm_readiness.py",
            completed.stderr,
        )

    def test_short_first_extract_refuses_despite_a_later_valid_spec(self) -> None:
        """Removing the count check recreates the concatenated-nonempty bypass."""

        block = _replace_specs(
            _line_audit_block(),
            ["short.txt 1,4p", "valid.txt 1,2p"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, head = self._init_repository(
                root,
                {"short.txt": "one\ntwo\n", "valid.txt": "one\ntwo\n"},
            )
            completed, _transcript = self._run(block, repository, head, root)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "line audit count mismatch for short.txt: expected 4 lines, emitted 2",
            completed.stderr,
        )

    def test_past_end_first_extract_refuses_despite_a_later_valid_spec(self) -> None:
        """A zero-line file contribution cannot hide behind another spec's bytes."""

        block = _replace_specs(
            _line_audit_block(),
            ["short.txt 5,7p", "valid.txt 1,2p"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, head = self._init_repository(
                root,
                {"short.txt": "one\ntwo\n", "valid.txt": "one\ntwo\n"},
            )
            completed, _transcript = self._run(block, repository, head, root)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("line audit extract is empty for short.txt", completed.stderr)

    def test_malformed_or_descending_ranges_refuse_before_extraction(self) -> None:
        """The count is derived only from the documented inclusive range grammar."""

        for line_ranges in ("1p", "4,2p"):
            with self.subTest(line_ranges=line_ranges):
                block = _replace_specs(
                    _line_audit_block(), [f"fixture.txt {line_ranges}"]
                )
                with tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    repository, head = self._init_repository(
                        root, {"fixture.txt": "one\ntwo\nthree\nfour\n"}
                    )
                    completed, _transcript = self._run(
                        block, repository, head, root
                    )

                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(
                    f"invalid line-audit ranges for fixture.txt: {line_ranges}",
                    completed.stderr,
                )


if __name__ == "__main__":
    unittest.main()
