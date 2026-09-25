"""Guard the pre-registration against silent derivation-chain drift.

The D-079 pre-registration fixes the rules for collecting a new identity
epoch's calibration acceptance corpus before capture; the chain is the tracked
shell script that runs one such derivation night. Its "digest in force" is the
SHA-256 authorized for subsequent nights by revision 3, superseding only the
sealed revision-1 chain digest. These tests bind that digest to the script's
bytes and compare the registration's own timing and receipt-class text with
the wrapper generator, while preserving the issuer's unique epoch pins. The
next acceptance issuance must pass this amended pre-registration's NEW SHA-256
via --preregistration-sha256; the r6 artifact does not record that digest.
"""

import hashlib
from pathlib import Path
import re
import unittest

from scripts import gen_derivation_night as generator
from scripts import issue_calibration_acceptance_generation as issuer


ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = ROOT / "configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
CHAIN = ROOT / "scripts/night_chains/calibration_derivation_only.zsh"
REVISION_3_DIGEST = re.compile(
    r"^Chain digest in force \(revision 3\): ([0-9a-f]{64})$", re.MULTILINE
)


def _one_match(pattern, text, label):
    matches = re.findall(pattern, text)
    if len(matches) != 1:
        raise AssertionError(
            f"{label}: expected exactly one match; found {len(matches)}"
        )
    return matches[0]


def _digest_in_force(text):
    sealed = _one_match(
        r"\bchain digest\s+([0-9a-f]{64})\b", text, "sealed_chain_digest_unique"
    )
    # Only text predating revision 3 may fall back to the sealed sentence.
    # A missing/malformed line in an existing revision must refuse, not fall back.
    if re.search(r"(?im)^# Revision 3\b|^Chain digest in force", text):
        return _one_match(REVISION_3_DIGEST, text, "revision_3_chain_digest_unique")
    return sealed


class PreregistrationChainDigestTests(unittest.TestCase):
    def test_digest_in_force_matches_tracked_chain(self):
        registered = _digest_in_force(PREREGISTRATION.read_text(encoding="utf-8"))
        actual = hashlib.sha256(CHAIN.read_bytes()).hexdigest()
        self.assertEqual(
            registered, actual,
            f"chain_digest_drift: registered={registered}; tracked={actual}",
        )

    def test_generator_matches_registered_timing_and_receipt_class(self):
        text = PREREGISTRATION.read_text(encoding="utf-8")
        receipt, settle, slots, cadence = _one_match(
            r"Sample\. Three[^\n]+, ([A-Z_]+) class, chain digest\s+"
            r"[0-9a-f]{64}\. Each window: one (\d+) s settle[^\n]+, "
            r"then (\d+) slots at a (\d+) s start-to-start\s+cadence,",
            text, "registered_sample_unique",
        )
        budget = _one_match(
            r"then one (\d+) s capture budget", text, "registered_capture_budget_unique"
        )
        for name, registered in (
            ("DEFAULT_SETTLE_S", int(settle)),
            ("PRE_REGISTERED_SLOT_COUNT", int(slots)),
            ("DEFAULT_SLOT_CADENCE_S", int(cadence)),
            ("DEFAULT_SLOT_CAPTURE_BUDGET_S", int(budget)),
            ("DERIVATION_RECEIPT_CLASS", receipt),
        ):
            with self.subTest(constant=name):
                self.assertEqual(
                    registered, getattr(generator, name),
                    f"registered_generator_drift: {name}",
                )

    def test_chain_preserves_derivation_capture_mode(self):
        text = CHAIN.read_text(encoding="utf-8")
        self.assertIn("--derivation-only", text)
        # Comment lines are excluded on the lead's ruling (2026-09-17): the chain explains in a

        # comment that the flag is absent, and the sealed rule is about the invocation, not prose.

        invocation_lines = [line for line in text.splitlines() if not line.lstrip().startswith("#")]

        self.assertNotIn("--sleep-display-before-capture", "\n".join(invocation_lines))

    def test_issuer_epoch_pins_remain_unique(self):
        text = PREREGISTRATION.read_text(encoding="utf-8")
        # Import and call the production parser; no regexes are copied here.
        # It deduplicates values, so also count its raw matches to reject even
        # a second identical pin rather than silently accepting repeated text.
        os_build = _one_match(
            issuer._PREREGISTRATION_OS_BUILD, text, "preregistration_os_build_unique"
        )
        powermetrics = _one_match(
            issuer._PREREGISTRATION_POWERMETRICS, text,
            "preregistration_powermetrics_digest_unique",
        )
        self.assertEqual(issuer.preregistration_epoch_pins(text), (os_build, powermetrics))


class DigestSelectionTests(unittest.TestCase):
    def setUp(self):
        self.text = PREREGISTRATION.read_text(encoding="utf-8")

    def test_pre_revision_3_text_uses_unique_sealed_digest(self):
        historical = self.text.split("# Revision 3", 1)[0]
        sealed = re.search(r"chain digest\s+([0-9a-f]{64})", historical).group(1)
        self.assertEqual(_digest_in_force(historical), sealed)

    def test_revision_3_missing_line_refuses_fallback(self):
        text = REVISION_3_DIGEST.sub("", self.text)
        with self.assertRaisesRegex(AssertionError, "revision_3_chain_digest_unique.*found 0"):
            _digest_in_force(text)

    def test_revision_3_duplicate_line_refuses(self):
        line = REVISION_3_DIGEST.search(self.text).group(0)
        with self.assertRaisesRegex(AssertionError, "revision_3_chain_digest_unique.*found 2"):
            _digest_in_force(self.text + "\n" + line + "\n")

    def test_sealed_digest_must_stay_unique(self):
        phrase = re.search(r"chain digest\s+[0-9a-f]{64}", self.text).group(0)
        for text, count in (
            (self.text.replace(phrase, "chain digest elided"), 0),
            (self.text + "\n" + phrase, 2),
        ):
            with self.subTest(matches=count):
                with self.assertRaisesRegex(
                    AssertionError, f"sealed_chain_digest_unique.*found {count}"
                ):
                    _digest_in_force(text)


if __name__ == "__main__":
    unittest.main()
