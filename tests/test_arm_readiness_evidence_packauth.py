"""PACK_AUTHENTICATION over a U11-projected pack (PACKAUTH).

A projected pack cannot be authenticated by the pack generator's bare
``--check``: ``identity_pins.freeze_projection`` ADDS the projection receipt and
its sidecar -- which the generator then reports as inventory extras -- and
REWRITES ``plan_tree.json`` / ``plan_tree.sha256`` / ``producer_contract.json``
through ``_render_json`` (sorted keys) while the generator emits
insertion-order bytes.  The cure composes two authentications:

    1. the generator's own derivation of the PRE-projection pack, materialised
       from the commit the projection receipt anchors, and
    2. a byte-exact replay of the projection's write set from those
       pre-projection bytes plus the committed receipt.

The receipt's ``reviewed_git_commit`` is a repo-wide HEAD rather than a
pack-scoped pin, so it is treated as an UNTRUSTED source of candidate bytes:
these tests exercise each independent binding that makes it sufficient anyway.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import joulewise.arm_readiness as readiness  # noqa: E402
import joulewise.arm_readiness_evidence as evidence  # noqa: E402
from joulewise import identity_pins  # noqa: E402
from test_arm_readiness_evidence_author import make_author_fixture  # noqa: E402
from test_arm_readiness_lifecycle import git  # noqa: E402

RECEIPT_RELATIVE = "identity_pin_projection.receipts/projection-0001.json"
SIDECAR_RELATIVE = "identity_pin_projection.receipts/projection-0001.sha256"


class ProjectedPackAuthenticationTests(unittest.TestCase):
    maxDiff = None

    # ---- helpers ---------------------------------------------------------

    def fixture(self):
        temporary, repository, pack, _custody, _arm = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        return repository.resolve(strict=True), pack

    def derive(self, repository: Path, pack: Path):
        tree, _raw = readiness._plan_tree(pack)
        context = evidence._DerivationContext(
            pack_root=pack,
            repository=repository,
            tree=tree,
            pack_sha256=readiness.committed_pack_tree_sha256(pack),
            head_commit=readiness.reviewed_main(pack)["head_commit"],
        )
        return evidence._DERIVERS["PACK_AUTHENTICATION"](context)

    def recommit(self, repository: Path, message: str = "tamper") -> None:
        git(repository, "add", "-A", ".")
        git(repository, "commit", "-qm", message)
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

    def assert_refuses(self, repository: Path, pack: Path, needle: str) -> None:
        with self.assertRaises(evidence.EvidenceAuthoringError) as caught:
            self.derive(repository, pack)
        self.assertEqual(caught.exception.kind, "PACK_AUTHENTICATION")
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_pack_authentication_underivable",
        )
        # Each refusal must be told apart from the other five, or a single
        # eager check could pass every one of these tests by itself.
        self.assertIn(needle, str(caught.exception))

    def rewrite_receipt(self, pack: Path, mutate) -> str:
        """Rewrite the receipt, its sidecar and the plan tree's pin."""

        receipt = json.loads((pack / RECEIPT_RELATIVE).read_bytes())
        mutate(receipt)
        raw = identity_pins._render_json(receipt)
        digest = hashlib.sha256(raw).hexdigest()
        (pack / RECEIPT_RELATIVE).write_bytes(raw)
        (pack / SIDECAR_RELATIVE).write_bytes(
            identity_pins._gnu_sidecar(digest, Path(RECEIPT_RELATIVE).name)
        )
        self.rewrite_tree(
            pack,
            lambda tree: tree["arm_attachments"]["identity_pin_projection"][
                "projection_receipt"
            ].__setitem__("sha256", digest),
        )
        return digest

    def rewrite_tree(self, pack: Path, mutate) -> None:
        """Rewrite plan_tree.json AND its sidecar, so only the replay can tell."""

        tree = json.loads((pack / "plan_tree.json").read_bytes())
        mutate(tree)
        raw = identity_pins._render_json(tree)
        (pack / "plan_tree.json").write_bytes(raw)
        (pack / "plan_tree.sha256").write_bytes(
            identity_pins._gnu_sidecar(
                hashlib.sha256(raw).hexdigest(), "plan_tree.json"
            )
        )

    # ---- the passing composition ----------------------------------------

    def test_projected_pack_authenticates_through_the_composed_check(self) -> None:
        repository, pack = self.fixture()
        tree, _raw = readiness._plan_tree(pack)
        projection = tree["arm_attachments"]["identity_pin_projection"]
        self.assertEqual(projection["state"], "frozen")
        self.assertIsNotNone(projection["projection_receipt"])

        derived = self.derive(repository, pack)

        checks = {item["check_id"]: item["evidence"] for item in derived.checks}
        self.assertIn("projected_pack_authentication", checks)
        composed = checks["projected_pack_authentication"]
        receipt = json.loads((pack / RECEIPT_RELATIVE).read_bytes())
        # The generator ran against the ANCHORED pre-projection pack ...
        self.assertEqual(
            composed["reviewed_git_commit"], receipt["pack"]["reviewed_git_commit"]
        )
        self.assertEqual(checks["pack_generator_check"]["exit_code"], 0)
        # ... and the projection replayed byte-for-byte onto the committed pack.
        self.assertEqual(
            sorted(composed["replayed_files"]),
            ["plan_tree.json", "plan_tree.sha256", "producer_contract.json"],
        )
        self.assertEqual(composed["licensed_additions"], [RECEIPT_RELATIVE, SIDECAR_RELATIVE])
        for relative, digest in composed["replayed_files"].items():
            self.assertEqual(
                hashlib.sha256((pack / relative).read_bytes()).hexdigest(), digest
            )
        # The receipt and its sidecar are authenticated primaries, so the
        # author re-gates them like every other primary artifact.
        primary = {item["path"] for item in derived.primary_artifacts}
        pack_relative = pack.resolve(strict=True).relative_to(repository).as_posix()
        self.assertIn(f"{pack_relative}/{RECEIPT_RELATIVE}", primary)
        self.assertIn(f"{pack_relative}/{SIDECAR_RELATIVE}", primary)

    def test_facts_are_unchanged_by_the_projected_path(self) -> None:
        """The R1 validator compares facts for exact equality."""

        repository, pack = self.fixture()
        derived = self.derive(repository, pack)
        self.assertEqual(
            derived.facts,
            {
                "desk.current_pack.v1": {
                    "attempt_policy_status": "PASS",
                    "committed_pack_digest_status": "PASS",
                    "extraction_specification_status": "PASS",
                    "manifest_validator_status": "PASS",
                    "pack_generator_check_status": "PASS",
                    "plan_validator_status": "PASS",
                }
            },
        )
        for check in derived.checks:
            self.assertEqual(set(check), {"check_id", "status", "evidence"})

    def test_derivation_is_deterministic(self) -> None:
        """Re-derivation compares checks for equality, so nothing may vary."""

        repository, pack = self.fixture()
        first = self.derive(repository, pack)
        second = self.derive(repository, pack)
        self.assertEqual(first.checks, second.checks)
        self.assertEqual(first.facts, second.facts)
        self.assertEqual(first.derivation, second.derivation)

    def test_unprojected_pack_keeps_the_bare_generator_check(self) -> None:
        """Rewinding the projection must restore the ORIGINAL path exactly."""

        repository, pack = self.fixture()
        pack_relative = pack.resolve(strict=True).relative_to(repository).as_posix()
        receipt = json.loads((pack / RECEIPT_RELATIVE).read_bytes())
        anchor = receipt["pack"]["reviewed_git_commit"]
        git(repository, "checkout", anchor, "--", pack_relative)
        shutil.rmtree(pack / "identity_pin_projection.receipts")
        self.recommit(repository, "rewind the projection")

        tree, _raw = readiness._plan_tree(pack)
        self.assertEqual(
            tree["arm_attachments"]["identity_pin_projection"]["state"], "unprojected"
        )
        derived = self.derive(repository, pack)
        checks = {item["check_id"] for item in derived.checks}
        self.assertNotIn("projected_pack_authentication", checks)
        self.assertEqual(checks, {"pack_generator_check", "manifest_validator"})

    # ---- the refusals ----------------------------------------------------

    def test_refuses_pack_subtree_divergence_at_the_anchor(self) -> None:
        repository, pack = self.fixture()
        (pack / "config.json").write_bytes(
            readiness.render_json({"run_id": "synthetic-member-1", "tamper": True})
        )
        self.recommit(repository)
        self.assert_refuses(repository, pack, "diverges at the anchored commit")

    def test_refuses_projection_receipt_digest_mismatch(self) -> None:
        repository, pack = self.fixture()
        self.rewrite_tree(
            pack,
            lambda tree: tree["arm_attachments"]["identity_pin_projection"][
                "projection_receipt"
            ].__setitem__("sha256", "0" * 64),
        )
        self.recommit(repository)
        self.assert_refuses(
            repository, pack, "differs from the plan tree reference"
        )

    def test_refuses_post_projection_plan_tree_edit(self) -> None:
        """The sidecar is updated to match, so ONLY the replay can catch it."""

        repository, pack = self.fixture()
        self.rewrite_tree(
            pack,
            lambda tree: tree["closeout_attachments"].__setitem__(
                "required_successful_backups", 0
            ),
        )
        self.recommit(repository)
        self.assert_refuses(
            repository, pack, "does not reproduce the committed bytes"
        )

    def test_refuses_an_unlicensed_extra_file(self) -> None:
        repository, pack = self.fixture()
        (pack / "EXTRA.json").write_bytes(readiness.render_json({"extra": True}))
        self.recommit(repository)
        self.assert_refuses(repository, pack, "does not license")

    def test_refuses_a_removed_anchored_file(self) -> None:
        repository, pack = self.fixture()
        (pack / "config.json").unlink()
        self.recommit(repository)
        self.assert_refuses(repository, pack, "removes anchored files")

    def test_refuses_an_anchor_that_does_not_resolve(self) -> None:
        repository, pack = self.fixture()
        self.rewrite_receipt(
            pack,
            lambda receipt: receipt["pack"].__setitem__(
                "reviewed_git_commit", "b" * 40
            ),
        )
        self.recommit(repository)
        self.assert_refuses(repository, pack, "does not resolve to a commit")

    def test_refuses_an_anchor_outside_the_derivation_history(self) -> None:
        repository, pack = self.fixture()
        # A real commit on an unrelated root: resolvable, but no ancestor of
        # the derivation head, so it is outside the audited history.
        orphan = repository / "orphan.txt"
        git(repository, "checkout", "-q", "--orphan", "detached-history")
        orphan.write_text("orphan\n")
        git(repository, "add", "orphan.txt")
        git(repository, "commit", "-qm", "orphan")
        stray = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repository, capture_output=True, check=True
        ).stdout.decode().strip()
        git(repository, "checkout", "-q", "main")
        orphan.unlink(missing_ok=True)
        self.rewrite_receipt(
            pack,
            lambda receipt: receipt["pack"].__setitem__(
                "reviewed_git_commit", stray
            ),
        )
        self.recommit(repository)
        self.assert_refuses(repository, pack, "not an ancestor of the derivation head")

    def test_refuses_a_receipt_sidecar_that_does_not_match(self) -> None:
        repository, pack = self.fixture()
        (pack / SIDECAR_RELATIVE).write_bytes(
            identity_pins._gnu_sidecar("0" * 64, Path(RECEIPT_RELATIVE).name)
        )
        self.recommit(repository)
        self.assert_refuses(repository, pack, "sidecar does not authenticate")

    def test_refuses_a_non_passing_projection_receipt(self) -> None:
        repository, pack = self.fixture()
        def refuse(receipt: dict) -> None:
            receipt["status"] = "REFUSE"
            receipt["reason_codes"] = ["readiness_identity_environment_dirty"]
        self.rewrite_receipt(pack, refuse)
        self.recommit(repository)
        self.assert_refuses(repository, pack, "not a passing freeze receipt")


if __name__ == "__main__":
    unittest.main()
