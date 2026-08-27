from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.capture_t0_step import CaptureT0Error, _parse_window_environment


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs/phase_2/window_runbook.md"
EXAMPLE_ANCHOR = "Example next-generation ALPHA `window.env`"
ADDITIONAL_ANCHOR = "`window.env` must additionally"


def documented_window_env_keys() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Extract the example keys and additionally-bound keys from the runbook."""

    text = RUNBOOK.read_text(encoding="utf-8")
    example = text.find(EXAMPLE_ANCHOR)
    if example < 0:
        raise AssertionError(f"cannot locate {EXAMPLE_ANCHOR!r}")
    fence = text.find("```sh", example)
    end = text.find("```", fence + len("```sh")) if fence >= 0 else -1
    if fence < 0 or end < 0:
        raise AssertionError("window.env example sh fence is missing or unterminated")
    example_keys = tuple(
        re.findall(
            r"^([A-Z][A-Z0-9_]*)=",
            text[fence + len("```sh") : end],
            flags=re.MULTILINE,
        )
    )
    if not example_keys:
        raise AssertionError("window.env example block contains no assignments")

    additional = text.find(ADDITIONAL_ANCHOR)
    if additional < 0:
        raise AssertionError(f"cannot locate {ADDITIONAL_ANCHOR!r}")
    paragraph_end = text.find("\n\n", additional)
    paragraph = text[additional : paragraph_end if paragraph_end >= 0 else None]
    additional_keys = tuple(re.findall(r"`([A-Z][A-Z0-9_]*)`", paragraph))
    if additional_keys != (
        "ARM_RECEIPT",
        "ARM_READINESS_CUSTODY_ROOT",
        "LAUNCH_MANIFEST",
    ):
        raise AssertionError(
            "unexpected additional window.env binding sentence: "
            f"{additional_keys!r}"
        )
    return example_keys, additional_keys


def _environment_bytes(keys: set[str] | tuple[str, ...]) -> bytes:
    return "".join(f"{key}=/synthetic/{key.lower()}\n" for key in sorted(keys)).encode()


class WindowEnvAllowlistTests(unittest.TestCase):
    def test_example_block_only_is_accepted(self) -> None:
        example, _additional = documented_window_env_keys()
        parsed = _parse_window_environment(_environment_bytes(example))
        self.assertEqual(set(parsed), set(example))
        self.assertEqual(len(example), 25)

    def test_additionally_bound_runbook_keys_pending_ruling(self) -> None:
        example, additional = documented_window_env_keys()
        combined = set(example) | set(additional)
        try:
            parsed = _parse_window_environment(_environment_bytes(combined))
        except CaptureT0Error as exc:
            self.assertEqual(
                exc.reason_code,
                "evidence_author_t0_capture_environment_invalid",
            )
            self.assertEqual(
                str(exc),
                "window.env exact keys differ; missing=[], "
                "unknown=['ARM_RECEIPT', 'LAUNCH_MANIFEST']",
            )
            self.skipTest(
                "OPEN DEFECT: the runbook requires ARM_RECEIPT and "
                "LAUNCH_MANIFEST but _ENV_KEYS refuses both; PR #205 records "
                "the pending magistrate ruling"
            )
        self.assertEqual(set(parsed), combined)


if __name__ == "__main__":
    unittest.main()
