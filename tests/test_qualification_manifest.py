"""Synthetic registration and finalization checks for RL-181 §1.0."""

import hashlib
import json
from pathlib import Path
import re
import unittest

from joulewise.cadence_looks.qualification_manifest import (
    ManifestError,
    validate_final,
    validate_registration,
)


ROOT = Path(__file__).resolve().parents[1]
LOOKS = ROOT / "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks"
MANIFEST = LOOKS / "lm-qual-01.manifest.json"
LEDGER = ROOT / "docs/process/cadence/looks/LOOKS.json"
KIT_COMMITMENTS = LEDGER.with_name("qualification-kit-commitments.json")
OBSOLETE_KIT_PINS = ROOT / "docs/run_reports/2026-11-18-lm-qual-01-audit-1-obsolete-kit-pins.json"
PLACEHOLDER = b'"PENDING:CODE"'


def _final_bytes(registration):
    def synthetic_digest(match):
        digest = hashlib.sha256(str(match.start()).encode()).hexdigest()
        return f'"{digest}"'.encode()

    return re.sub(PLACEHOLDER, synthetic_digest, registration)


def _digest_slots(value, path=()):
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str) and (key == "sha256" or key.endswith("_sha256")):
                yield (*path, key), item
            yield from _digest_slots(item, (*path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _digest_slots(item, (*path, index))


class QualificationRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.registered = MANIFEST.read_bytes()
        self.final = _final_bytes(self.registered)

    def test_registered_manifest_parses_and_matches_ledger(self):
        document = validate_registration(self.registered)
        self.assertEqual(document["look_kind"], "qualification")
        self.assertEqual(document["status"], "registered")
        self.assertEqual(document["registration"]["ledger_path"], LEDGER.relative_to(ROOT).as_posix())
        ledger = json.loads(LEDGER.read_bytes())
        self.assertEqual(ledger["looks"], [{
            "look_id": document["look_id"],
            "manifest_path": MANIFEST.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(self.registered).hexdigest(),
            "status": "registered",
        }])

    def test_registered_kit_pins_match_independent_source(self):
        registered = validate_registration(self.registered)
        source = json.loads(KIT_COMMITMENTS.read_bytes())[registered["look_id"]]
        blocks = registered["reads"]["blocks"]
        self.assertEqual(len(blocks), len(source["kit_sha256_by_block"]))
        self.assertEqual(
            {block["block_id"]: block["kit_sha256"] for block in blocks},
            source["kit_sha256_by_block"],
        )

    def test_each_obsolete_kit_refuses_registration_and_finalization(self):
        registered = json.loads(self.registered)
        obsolete = json.loads(OBSOLETE_KIT_PINS.read_bytes())["kit_sha256_by_block"]
        for block in registered["reads"]["blocks"]:
            block_id = block["block_id"]
            with self.subTest(block_id=block_id):
                current_digest = block["kit_sha256"].encode()
                bad_digest = obsolete[block_id].encode()
                self.assertNotEqual(current_digest, bad_digest)
                stale = self.registered.replace(current_digest, bad_digest, 1)
                with self.assertRaisesRegex(ManifestError, rf"{block_id}.*kit SHA-256"):
                    validate_registration(stale)
                with self.assertRaisesRegex(ManifestError, rf"{block_id}.*kit SHA-256"):
                    validate_final(stale, _final_bytes(stale))
                with self.assertRaisesRegex(ManifestError, "differs outside"):
                    validate_final(self.registered, self.final.replace(current_digest, bad_digest, 1))

    def test_kit_commitments_are_bound_to_the_exact_block_set_and_id(self):
        registered = json.loads(self.registered)
        first, second, _ = registered["reads"]["blocks"]

        for source, replacement, message in (
            (first["kit_sha256"], second["kit_sha256"], "qual-01.*kit SHA-256"),
            ('"block_id": "qual-02"', '"block_id": "qual-01"', "duplicate qualification block"),
            ('"block_id": "qual-02"', '"block_id": "qual-04"', "qualification block set"),
            ('"look_id": "lm-qual-01"', '"look_id": "lm-qual-02"', "no independent qualification kit commitments"),
        ):
            with self.subTest(replacement=replacement):
                changed = self.registered.replace(source.encode(), replacement.encode(), 1)
                with self.assertRaisesRegex(ManifestError, message):
                    validate_registration(changed)

    def test_first_span_hand_read_covers_checks_and_prior_read(self):
        hand_read = validate_registration(self.registered)["reads"]["first_span_hand_read"]
        for clause in (
            "capture leg's G0 record",
            "each consumer's release against the span reference and its wait",
            "each leg's decode count against its own cap (4096, 3724 or 3151)",
            "hand-read from an earlier filler or pilot",
            "both leg types at q0 on this pin",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, hand_read)

    def test_registered_hash_slots_and_complete_synthetic_final(self):
        registered = validate_registration(self.registered)
        final = validate_final(self.registered, self.final)
        registered_digests = dict(_digest_slots(registered))
        final_digests = dict(_digest_slots(final))
        self.assertEqual(registered_digests.keys(), final_digests.keys())
        self.assertEqual(
            {path for path, value in registered_digests.items() if value != "PENDING:CODE"},
            {("reads", "blocks", i, "kit_sha256") for i in range(3)},
        )
        self.assertEqual(len(registered_digests), self.registered.count(PLACEHOLDER) + 3)
        for path, value in registered_digests.items():
            with self.subTest(path=path):
                self.assertRegex(final_digests[path], r"\A[0-9a-f]{64}\Z")
                if value == "PENDING:CODE":
                    self.assertNotEqual(final_digests[path], value)
                else:
                    self.assertEqual(final_digests[path], value)
        with self.assertRaisesRegex(ManifestError, "registered code and schema hash"):
            validate_registration(self.final)

    def test_final_rejects_changes_outside_hash_slots(self):
        kit_hash = json.loads(self.registered)["reads"]["blocks"][0]["kit_sha256"].encode()
        edits = (
            (b'"short_own_prefix_tokens": 3724', b'"short_own_prefix_tokens": 3723'),
            (b'"gaps": 140', b'"gaps": 139'),
            (b'"min_days": 3', b'"min_days": 2'),
            (b'"lower": -0.1,', b'"lower": -0.10,'),
            (kit_hash, b"0" * 64),
            (b'cadence_looks/fit_interim.py', b'cadence_looks/fit_other.py'),
            (b'"status": "registered",\n  "title":', b'"status":"registered",\n  "title":'),
            (b'"twin": false', b'"twin": true'),
            (b'"stage2_error",', b'"other_error",'),
            (b'Qualification of the frozen predictor', b'Qualification of the frozen model'),
            (b'Qualification of the frozen predictor', b'Qualificatio\\u006e of the frozen predictor'),
        )
        for original, replacement in edits:
            with self.subTest(original=original):
                self.assertIn(original, self.final)
                with self.assertRaises(ManifestError):
                    validate_final(self.registered, self.final.replace(original, replacement, 1))

        with self.assertRaisesRegex(ManifestError, "differs outside"):
            validate_final(self.registered, self.final + b"\n")
        with self.assertRaisesRegex(ManifestError, "differs outside"):
            reordered = json.dumps(json.loads(self.final), indent=2, sort_keys=True, ensure_ascii=False)
            validate_final(self.registered, (reordered + "\n").encode())

    def test_final_rejects_unfilled_or_malformed_hash_slots(self):
        scorer_hash = json.loads(self.final)["pins"]["scorer"]["sha256"]
        digest = json.dumps(scorer_hash).encode()
        for invalid in (PLACEHOLDER, b'"OPEN-2"', b'"' + b"A" * 64 + b'"', b'"abc"'):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ManifestError):
                    validate_final(self.registered, self.final.replace(digest, invalid, 1))

    def test_validator_rejects_placeholders_elsewhere_and_duplicate_keys(self):
        for invalid in (b'"OPEN-4"', PLACEHOLDER, b'"PENDING\\u003aCODE"'):
            with self.subTest(invalid=invalid):
                title = re.search(rb'"title": (".*?")', self.final)[1]
                with self.assertRaisesRegex(ManifestError, "placeholder outside"):
                    validate_final(self.registered, self.final.replace(title, invalid, 1))

        with self.assertRaisesRegex(ManifestError, "duplicate JSON key"):
            validate_final(self.registered, self.final.replace(
                b'"status": "registered",', b'"status": "draft", "status": "registered",', 1
            ))


if __name__ == "__main__":
    unittest.main()
