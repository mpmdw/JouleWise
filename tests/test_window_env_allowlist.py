from __future__ import annotations

import re
import unittest
from pathlib import Path

from joulewise import arm_readiness_evidence_t0 as evidence_t0
from scripts import capture_t0_step as capture


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs/phase_2/window_runbook.md"
EXAMPLE_ANCHOR = "Example next-generation ALPHA `window.env`"
ADDITIONAL_ANCHOR = "`window.env` must additionally"
EVIDENCE_KIND = "LAUNCH_RECIPE"


def documented_window_env_keys() -> tuple[str, ...]:
    """Extract the exact example keys and prove the stale instruction is gone."""

    text = RUNBOOK.read_text(encoding="utf-8")
    if ADDITIONAL_ANCHOR in text:
        raise AssertionError(
            f"retired additional-binding instruction remains: {ADDITIONAL_ANCHOR!r}"
        )
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
    return example_keys


def _environment_bytes(keys: set[str] | tuple[str, ...] | frozenset[str]) -> bytes:
    return "".join(
        f"{key}=/synthetic/{key.lower()}\n" for key in sorted(keys)
    ).encode()


class WindowEnvAllowlistTests(unittest.TestCase):
    def _assert_refused_at_both_boundaries(
        self, raw: bytes, *, detail: str
    ) -> None:
        with self.assertRaises(capture.CaptureT0Error) as capture_caught:
            capture._parse_window_environment(raw)
        self.assertEqual(
            capture_caught.exception.reason_code,
            "evidence_author_t0_capture_environment_invalid",
        )
        self.assertEqual(str(capture_caught.exception), detail)

        with self.assertRaises(
            evidence_t0.T0EvidenceAuthoringError
        ) as author_caught:
            evidence_t0._parse_window_environment(raw, kind=EVIDENCE_KIND)
        self.assertEqual(author_caught.exception.kind, EVIDENCE_KIND)
        self.assertEqual(
            author_caught.exception.reason_code,
            "evidence_author_t0_launch_recipe_underivable",
        )
        self.assertEqual(str(author_caught.exception), detail)

    def test_example_block_only_is_accepted(self) -> None:
        example = documented_window_env_keys()
        raw = _environment_bytes(example)
        capture_parsed = capture._parse_window_environment(raw)
        author_parsed = evidence_t0._parse_window_environment(
            raw, kind=EVIDENCE_KIND
        )
        self.assertEqual(capture_parsed, author_parsed)
        self.assertEqual(set(capture_parsed), set(example))
        self.assertEqual(len(example), 25)

    def test_additionally_bound_runbook_keys_pending_ruling(self) -> None:
        example = documented_window_env_keys()
        combined = set(example) | {"ARM_RECEIPT", "LAUNCH_MANIFEST"}
        self._assert_refused_at_both_boundaries(
            _environment_bytes(combined),
            detail=(
                "window.env exact keys differ; missing=[], "
                "unknown=['ARM_RECEIPT', 'LAUNCH_MANIFEST']"
            ),
        )

    def test_shared_contract_is_identical_and_exact_at_both_boundaries(self) -> None:
        self.assertIs(capture.WINDOW_ENV_KEYS, evidence_t0.WINDOW_ENV_KEYS)
        self.assertIs(capture._ENV_KEYS, evidence_t0.WINDOW_ENV_KEYS)
        self.assertEqual(set(documented_window_env_keys()), evidence_t0.WINDOW_ENV_KEYS)

        for missing in evidence_t0.WINDOW_ENV_KEYS:
            with self.subTest(missing=missing):
                self._assert_refused_at_both_boundaries(
                    _environment_bytes(evidence_t0.WINDOW_ENV_KEYS - {missing}),
                    detail=(
                        "window.env exact keys differ; "
                        f"missing={[missing]!r}, unknown=[]"
                    ),
                )

        self._assert_refused_at_both_boundaries(
            _environment_bytes(
                evidence_t0.WINDOW_ENV_KEYS | {"SYNTHETIC_UNKNOWN"}
            ),
            detail=(
                "window.env exact keys differ; missing=[], "
                "unknown=['SYNTHETIC_UNKNOWN']"
            ),
        )

    def test_runbook_exports_post_arm_paths_and_chain_guards_them(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")
        arm = text.index("scripts/generate_arm_readiness.py arm")
        arm_export = text.index("export ARM_RECEIPT=", arm)
        manifest_export = text.index("export LAUNCH_MANIFEST=", arm_export)
        verify = text.index("scripts/generate_arm_readiness.py verify", manifest_export)
        e10 = text.index("**E-10 — Ed's deliberate physical launch:**", verify)
        self.assertLess(arm, arm_export)
        self.assertLess(arm_export, manifest_export)
        self.assertLess(manifest_export, verify)
        self.assertLess(verify, e10)
        self.assertIn("exact absolute `receipt_path`", text[arm:arm_export])
        self.assertIn('arm_readiness.t0.inputs/launch-manifest.json"', text)

        chain_start = text.index("```zsh", e10)
        chain_end = text.index("```", chain_start + len("```zsh"))
        chain = text[chain_start:chain_end]
        source = chain.index('source "$WINDOW_PLAN_ROOT/window.env"')
        arm_guard = chain.index(
            ': "${ARM_RECEIPT:?E-10 export step must export ARM_RECEIPT}"'
        )
        manifest_guard = chain.index(
            ': "${LAUNCH_MANIFEST:?E-10 export step must export LAUNCH_MANIFEST}"'
        )
        first_launch = chain.index('"$PY" "$REPO/scripts/launch_window.py"')
        self.assertLess(source, arm_guard)
        self.assertLess(arm_guard, manifest_guard)
        self.assertLess(manifest_guard, first_launch)


if __name__ == "__main__":
    unittest.main()
