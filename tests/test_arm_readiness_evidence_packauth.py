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
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import joulewise.arm_readiness as readiness  # noqa: E402
import joulewise.arm_readiness_evidence as evidence  # noqa: E402
from joulewise import identity_pins  # noqa: E402
from test_arm_readiness_evidence_author import (  # noqa: E402
    commit_u11_projection,
    make_author_fixture,
)
from test_arm_readiness_lifecycle import git  # noqa: E402

RECORDED_FREEZE = ROOT / "tests/fixtures/packauth_recorded_freeze"
RECEIPT_RELATIVE = "identity_pin_projection.receipts/projection-0001.json"
SIDECAR_RELATIVE = "identity_pin_projection.receipts/projection-0001.sha256"


class ProjectedPackAuthenticationTests(unittest.TestCase):
    maxDiff = None

    # ---- helpers ---------------------------------------------------------

    def fixture(self):
        temporary, repository, pack, _custody, _arm = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        repository = repository.resolve(strict=True)
        pack_relative = pack.resolve(strict=True).relative_to(repository).as_posix()
        receipt = json.loads((pack / RECEIPT_RELATIVE).read_bytes())
        anchor = receipt["pack"]["reviewed_git_commit"]
        git(repository, "checkout", anchor, "--", pack_relative)
        shutil.rmtree(pack / "identity_pin_projection.receipts")

        # The shared author fixture also declares the explicit two-way flag,
        # but it defaults to preserve=False; these PACKAUTH tests model the
        # modern _v4 path and need an anchor whose default is overridden
        # explicitly on the command line, so they rebuild the generator here.
        # Either way the synthetic digest is never added to the production
        # allowlist: that list stays closed to the reviewed historical
        # anchors, and a synthetic fixture earns admission by CAPABILITY.
        generator_raw = (
            "import argparse\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--check', action='store_true')\n"
            "parser.add_argument('--preserve-current-frozen-bytes', "
            "action=argparse.BooleanOptionalAction, default=True)\n"
            "args = parser.parse_args()\n"
            "if not args.check:\n"
            "    raise SystemExit(2)\n"
            "print('synthetic pack check passed')\n"
        ).encode("utf-8")
        (pack / "generate_configs.py").write_bytes(generator_raw)
        tree = json.loads((pack / "plan_tree.json").read_bytes())
        tree["generator"]["sha256"] = hashlib.sha256(generator_raw).hexdigest()
        tree_raw = readiness.render_json(tree)
        (pack / "plan_tree.json").write_bytes(tree_raw)
        (pack / "plan_tree.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json"
            )
        )
        git(repository, "add", "-A", ".")
        git(repository, "commit", "-qm", "install explicit PACKAUTH generator")
        commit_u11_projection(repository, pack, ("alpha",))
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        return repository, pack

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

    def committed_clone(self) -> tuple[Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repository = Path(temporary.name) / "repository"
        subprocess.run(
            ("git", "clone", "-q", "--shared", str(ROOT), str(repository)),
            check=True,
            capture_output=True,
        )
        git(repository, "config", "user.name", "packauth test")
        git(repository, "config", "user.email", "packauth@invalid")
        return repository, repository / "configs/campaigns/d117_floor_qwen25_1p5b_v1"

    def derivation_context(self, repository: Path, pack: Path):
        tree, _raw = readiness._plan_tree(pack)
        return evidence._DerivationContext(
            pack_root=pack,
            repository=repository.resolve(strict=True),
            tree=tree,
            pack_sha256=readiness.committed_pack_tree_sha256(pack),
            head_commit=subprocess.run(
                ("git", "rev-parse", "HEAD"),
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip(),
        )

    def modern_projected_fixture(self) -> tuple[Path, Path, str]:
        repository, pack = self.fixture()
        pack_relative = pack.resolve(strict=True).relative_to(repository).as_posix()
        receipt = json.loads((pack / RECEIPT_RELATIVE).read_bytes())
        anchor = receipt["pack"]["reviewed_git_commit"]
        git(repository, "checkout", anchor, "--", pack_relative)
        shutil.rmtree(pack / "identity_pin_projection.receipts")

        predecessor_digest = "a" * 64
        generator_raw = (
            "import argparse\n"
            f"CURRENT_FROZEN_RECEIPT_SHA256 = {predecessor_digest!r}\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--check', action='store_true')\n"
            "parser.add_argument('--preserve-current-frozen-bytes', "
            "action=argparse.BooleanOptionalAction, default=True)\n"
            "args = parser.parse_args()\n"
            "if not args.check:\n"
            "    raise SystemExit(2)\n"
            "print('synthetic pack check passed')\n"
        ).encode("utf-8")
        (pack / "generate_configs.py").write_bytes(generator_raw)
        tree = json.loads((pack / "plan_tree.json").read_bytes())
        tree["generator"]["sha256"] = hashlib.sha256(generator_raw).hexdigest()
        tree_raw = readiness.render_json(tree)
        (pack / "plan_tree.json").write_bytes(tree_raw)
        (pack / "plan_tree.sha256").write_bytes(
            readiness.gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
        )
        self.recommit(repository, "install modern predecessor-naming generator")
        commit_u11_projection(repository, pack, ("alpha",))
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        return repository, pack, predecessor_digest

    def recorded_generator(
        self, repository: Path, pack: Path, *, preserve_current_frozen_bytes: bool
    ):
        context = self.derivation_context(repository, pack)
        generator = context.tree["generator"]
        artifact, raw = evidence._committed_artifact(
            context.repository,
            generator["path"],
            kind="PACK_AUTHENTICATION",
        )
        return evidence._recorded_generator_check(
            context,
            artifact["path"],
            raw,
            kind="PACK_AUTHENTICATION",
            preserve_current_frozen_bytes=preserve_current_frozen_bytes,
        )

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
        self.assertEqual(
            checks,
            {
                "frozen_receipt_constant_relation",
                "pack_generator_check",
                "manifest_validator",
            },
        )

    def test_preserve_authentication_refuses_canonical_committed_freeze_receipt_tamper_with_regenerated_sidecar(
        self,
    ) -> None:
        repository, pack = self.committed_clone()
        receipt = pack / "arm_readiness.freeze.receipts/freeze-0001.json"
        value = json.loads(receipt.read_bytes())
        value["pack_identity"]["pack_root"] += "-tampered"
        raw = readiness.render_json(value)
        receipt.write_bytes(raw)
        receipt.with_name(f"{receipt.name}.sha256").write_bytes(
            readiness.gnu_sidecar(hashlib.sha256(raw).hexdigest(), receipt.name)
        )
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "tamper current freeze receipt")

        with self.assertRaises(evidence.EvidenceAuthoringError) as caught:
            self.recorded_generator(
                repository, pack, preserve_current_frozen_bytes=True
            )
        self.assertIn(
            "committed freeze receipt is not the receipt the plan pins",
            str(caught.exception),
        )

    def test_stale_current_frozen_receipt_constant_is_detected_but_not_an_authentication_dependency(
        self,
    ) -> None:
        # A current v2 pack has the exact imminent-v4 shape: U11 projected,
        # D-134 frozen, and a compiled constant that names freeze-0001.
        pack = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v2"
        context = self.derivation_context(ROOT, pack)
        _artifact, generator_raw = evidence._pinned_artifact(
            context,
            context.tree["generator"],
            kind="PACK_AUTHENTICATION",
            label="pack generator",
        )
        relation, _primaries = evidence._frozen_receipt_constant_relation(
            context, generator_raw, kind="PACK_AUTHENTICATION"
        )
        self.assertEqual(relation["relation"], "names_predecessor")
        self.assertFalse(relation["authentication_dependency"])
        with self.assertRaises(evidence.EvidenceAuthoringError) as caught:
            self.derive(ROOT, pack)
        self.assertIn("pack subtree adds files", str(caught.exception))
        self.assertNotIn("CURRENT_FROZEN_RECEIPT_SHA256", str(caught.exception))

    def test_frozen_receipt_constant_variants_do_not_change_the_authentication_verdict(
        self,
    ) -> None:
        pack = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v2"
        context = self.derivation_context(ROOT, pack)
        generator = context.tree["generator"]
        _artifact, recorded_raw = evidence._pinned_artifact(
            context,
            generator,
            kind="PACK_AUTHENTICATION",
            label="pack generator",
        )
        recorded_relation, _primaries = evidence._frozen_receipt_constant_relation(
            context, recorded_raw, kind="PACK_AUTHENTICATION"
        )
        current = recorded_relation["current_freeze_receipt_sha256"]
        predecessor = recorded_relation["predecessor_freeze_receipt_sha256"]
        self.assertRegex(current, r"^[0-9a-f]{64}$")
        self.assertRegex(predecessor, r"^[0-9a-f]{64}$")
        unrelated = "b" * 64
        self.assertNotIn(unrelated, (current, predecessor))

        fixed_generator = (
            "import argparse\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--check', action='store_true')\n"
            "parser.add_argument('--preserve-current-frozen-bytes', "
            "action=argparse.BooleanOptionalAction, default=True)\n"
            "args = parser.parse_args()\n"
            "if not args.check:\n"
            "    raise SystemExit(2)\n"
            "print('fixed derivation passed')\n"
        )
        variants = {
            "absent": ("", "absent", "absent"),
            "matching_current": (
                f"CURRENT_FROZEN_RECEIPT_SHA256 = {current!r}\n",
                "matches_current",
                "readable",
            ),
            "names_predecessor": (
                f"CURRENT_FROZEN_RECEIPT_SHA256 = {predecessor!r}\n",
                "names_predecessor",
                "readable",
            ),
            "unrelated": (
                f"CURRENT_FROZEN_RECEIPT_SHA256 = {unrelated!r}\n",
                "unrelated",
                "readable",
            ),
            "computed": (
                "CURRENT_FROZEN_RECEIPT_SHA256 = 'a' * 64\n",
                "unreadable",
                "non_literal",
            ),
            "duplicated": (
                f"CURRENT_FROZEN_RECEIPT_SHA256 = {current!r}\n"
                f"CURRENT_FROZEN_RECEIPT_SHA256 = {predecessor!r}\n",
                "unreadable",
                "duplicated",
            ),
            "syntactically_malformed": (
                "CURRENT_FROZEN_RECEIPT_SHA256: str\n",
                "unreadable",
                "malformed",
            ),
        }
        verdicts: list[dict[str, object]] = []
        for name, (constant_source, expected_relation, expected_status) in variants.items():
            with self.subTest(name=name):
                raw = (constant_source + fixed_generator).encode("utf-8")
                completed = subprocess.CompletedProcess(
                    args=[], returncode=0, stdout=b"fixed derivation passed\n", stderr=b""
                )
                with mock.patch.object(
                    evidence.subprocess, "run", return_value=completed
                ):
                    result = evidence._recorded_generator_check(
                        context,
                        generator["path"],
                        raw,
                        kind="PACK_AUTHENTICATION",
                        preserve_current_frozen_bytes=False,
                    )
                evidence._require_regenerated_generator_result(
                    result, kind="PACK_AUTHENTICATION"
                )
                verdicts.append(result)
                relation, _primaries = evidence._frozen_receipt_constant_relation(
                    context, raw, kind="PACK_AUTHENTICATION"
                )
                self.assertEqual(relation["relation"], expected_relation)
                self.assertEqual(
                    relation["constant_extraction_status"], expected_status
                )
                self.assertFalse(relation["authentication_dependency"])
        self.assertTrue(verdicts)
        self.assertTrue(all(verdict == verdicts[0] for verdict in verdicts[1:]))
        implicit_preserve = b"preserve_current_frozen_bytes = True\n"
        with self.assertRaises(evidence.EvidenceAuthoringError) as caught:
            evidence._generator_invocation(
                generator["path"],
                implicit_preserve,
                kind="PACK_AUTHENTICATION",
                preserve_current_frozen_bytes=False,
            )
        self.assertIn("closed reviewed historical allowlist", str(caught.exception))

    def test_unrelated_frozen_receipt_constant_has_its_own_relation(self) -> None:
        pack = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v2"
        context = self.derivation_context(ROOT, pack)
        raw = (
            "CURRENT_FROZEN_RECEIPT_SHA256 = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'\n"
        ).encode("utf-8")
        relation, _primaries = evidence._frozen_receipt_constant_relation(
            context, raw, kind="PACK_AUTHENTICATION"
        )
        self.assertEqual(relation["relation"], "unrelated")
        self.assertEqual(relation["constant_extraction_status"], "readable")
        self.assertFalse(relation["constant_matches_predecessor"])

    def test_preserve_echo_accepts_science_row_tamper_but_cannot_set_generator_pass(
        self,
    ) -> None:
        repository, pack = self.committed_clone()
        science = (
            pack
            / "01_phase_decode_absolute/d117f15-df-ph-decode-abs-r01.json"
        )
        science.write_bytes(science.read_bytes() + b"\n")
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "tamper committed science row")

        command = evidence._generator_command(str(pack / "generate_configs.py"))
        command.append("--preserve-current-frozen-bytes")
        completed = subprocess.run(
            command,
            cwd=repository,
            check=False,
            capture_output=True,
            env=evidence._generator_environment(),
        )
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        recorded = self.recorded_generator(
            repository, pack, preserve_current_frozen_bytes=True
        )
        self.assertEqual(recorded["derivation_mode"], "echo")
        with self.assertRaises(evidence.EvidenceAuthoringError) as caught:
            evidence._require_regenerated_generator_result(
                recorded, kind="PACK_AUTHENTICATION"
            )
        self.assertIn("echo", str(caught.exception))

    def test_external_pinned_input_drift_is_checked_in_derivation_mode(self) -> None:
        repository, pack = self.committed_clone()
        successor = repository / "configs/campaigns/d117_floor_qwen25_1p5b_v4"
        emit = evidence._generator_command(str(pack / "generate_configs.py"))[:-1]
        emit.extend(
            (
                "--pack-id",
                successor.name,
                "--family-suffix",
                "_v4",
                "--no-preserve-current-frozen-bytes",
            )
        )
        emitted = subprocess.run(
            emit,
            cwd=repository,
            check=False,
            capture_output=True,
            env=evidence._generator_environment(),
        )
        self.assertEqual(emitted.returncode, 0, emitted.stderr.decode())
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "emit unfrozen successor")

        acceptance = repository / "configs/calibration/calibration_acceptance_d079_v2_r2.json"
        acceptance.write_bytes(acceptance.read_bytes() + b"\n")
        git(repository, "add", "-A")
        git(repository, "commit", "-qm", "drift pinned acceptance")

        base = evidence._generator_command(str(successor / "generate_configs.py"))
        preserve = subprocess.run(
            [*base, "--preserve-current-frozen-bytes"],
            cwd=repository,
            check=False,
            capture_output=True,
            env=evidence._generator_environment(),
        )
        regenerate = subprocess.run(
            [*base, "--no-preserve-current-frozen-bytes"],
            cwd=repository,
            check=False,
            capture_output=True,
            env=evidence._generator_environment(),
        )
        self.assertEqual(preserve.returncode, 0, preserve.stderr.decode())
        self.assertNotEqual(regenerate.returncode, 0)
        self.assertIn(b"pinned input drifted", regenerate.stderr)
        recorded = self.recorded_generator(
            repository, successor, preserve_current_frozen_bytes=True
        )
        self.assertEqual(recorded["derivation_mode"], "echo")
        with self.assertRaises(evidence.EvidenceAuthoringError):
            evidence._require_regenerated_generator_result(
                recorded, kind="PACK_AUTHENTICATION"
            )

    def test_projected_pack_authentication_uses_no_preserve_anchor_when_constant_is_stale(
        self,
    ) -> None:
        repository, pack, predecessor_digest = self.modern_projected_fixture()
        derived = self.derive(repository, pack)
        checks = {item["check_id"]: item["evidence"] for item in derived.checks}
        command = checks["pack_generator_check"]["command"]
        self.assertEqual(command[-1], "--no-preserve-current-frozen-bytes")
        self.assertEqual(checks["pack_generator_check"]["derivation_mode"], "regenerated")
        self.assertEqual(
            checks["frozen_receipt_constant_relation"]["relation"],
            "no_current_receipt",
        )
        self.assertEqual(
            checks["frozen_receipt_constant_relation"][
                "compiled_current_frozen_receipt_sha256"
            ],
            predecessor_digest,
        )
        self.assertFalse(
            checks["frozen_receipt_constant_relation"]["authentication_dependency"]
        )
        self.assertTrue(checks["projected_pack_authentication"]["replayed_files"])


    # ---- the subprocess boundary ----------------------------------------

    def test_generator_child_cannot_see_the_invoking_environment(self) -> None:
        """A fake `mlx` on an inherited PYTHONPATH flipped a PASS (PR #178)."""

        scratch = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, scratch, True)
        site = scratch / "site"
        (site / "packauth_marker").mkdir(parents=True)
        (site / "packauth_marker" / "__init__.py").write_text("MARKER = 'HOSTILE'\n")
        probe = scratch / "probe.py"
        probe.write_text(
            "import json, os, sys\n"
            "try:\n"
            "    import packauth_marker\n"
            "    marker = packauth_marker.MARKER\n"
            "except ImportError:\n"
            "    marker = None\n"
            "print(json.dumps({'marker': marker,\n"
            "                  'pythonpath': os.environ.get('PYTHONPATH'),\n"
            "                  'virtual_env': os.environ.get('VIRTUAL_ENV'),\n"
            "                  'sys_path_0': sys.path[0],\n"
            "                  'dont_write_bytecode': sys.dont_write_bytecode}))\n"
        )
        with unittest.mock.patch.dict(
            os.environ,
            {"PYTHONPATH": str(site), "VIRTUAL_ENV": str(scratch / "venv")},
        ):
            # The parent really can import it, so the child's failure is the
            # isolation working and not a broken marker package.
            control = subprocess.run(
                [sys.executable, str(probe)],
                capture_output=True,
                env=dict(os.environ),
                check=True,
            )
            self.assertEqual(
                json.loads(control.stdout)["marker"], "HOSTILE", "marker is not importable at all"
            )
            completed = subprocess.run(
                evidence._generator_command(str(probe)),
                capture_output=True,
                env=evidence._generator_environment(),
                check=True,
            )
        observed = json.loads(completed.stdout)
        self.assertIsNone(observed["marker"])
        self.assertIsNone(observed["pythonpath"])
        self.assertIsNone(observed["virtual_env"])
        # -P keeps the pack's own directory off sys.path, so a committed pack
        # file cannot shadow a stdlib or joulewise module.
        self.assertNotEqual(Path(observed["sys_path_0"]), probe.parent)
        # -B survives -E discarding PYTHONDONTWRITEBYTECODE.
        self.assertTrue(observed["dont_write_bytecode"])
        self.assertNotIn("PYTHONPATH", evidence._generator_environment())
        self.assertNotIn("VIRTUAL_ENV", evidence._generator_environment())

    # ---- a RECORDED real freeze -----------------------------------------

    def test_replay_reproduces_a_recorded_real_freeze_projection(self) -> None:
        """Replay a write set the real `freeze_projection` actually produced.

        Every other fixture here is built by `apply_freeze_projection`, which
        mirrors the real code; if that mirror were wrong in the same way as the
        replay, those tests would still pass.  These bytes were recorded from
        the live D-117 estate, so nothing under test authored them.
        """

        manifest = json.loads((RECORDED_FREEZE / "manifest.json").read_bytes())
        scratch = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, scratch, True)
        with tarfile.open(RECORDED_FREEZE / "pre_projection.tar.gz") as tar:
            tar.extractall(scratch)
        recorded = scratch / "pre"
        receipt = json.loads((recorded / "receipt.json").read_bytes())
        self.assertEqual(
            hashlib.sha256((recorded / "receipt.json").read_bytes()).hexdigest(),
            manifest["receipt_sha256"],
        )
        pack = scratch / manifest["pack_id"]
        pack.mkdir()
        for name in ("plan_tree.json", "plan_tree.sha256", "producer_contract.json"):
            (pack / name).write_bytes((recorded / name).read_bytes())

        writes = evidence._replay_projection_write_set(
            pack,
            receipt,
            manifest["receipt_relative"],
            manifest["receipt_sha256"],
            kind="PACK_AUTHENTICATION",
        )

        self.assertEqual(sorted(writes), sorted(manifest["expected_sha256"]))
        for name, expected in sorted(manifest["expected_sha256"].items()):
            self.assertEqual(
                hashlib.sha256(writes[name]).hexdigest(),
                expected,
                f"replay diverges from the recorded real freeze: {name}",
            )

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

    def test_refuses_an_unlicensed_extra_file_before_executing_anything(self) -> None:
        """The fence runs BEFORE the generator: step 6 starts an interpreter
        whose working directory is the materialised tree, so a pack file the
        projection does not license must be refused first, not after it has
        had a chance to run."""

        repository, pack = self.fixture()
        (pack / "EXTRA.json").write_bytes(readiness.render_json({"extra": True}))
        self.recommit(repository)
        with unittest.mock.patch.object(
            evidence, "_generator_command", wraps=evidence._generator_command
        ) as spy:
            self.assert_refuses(repository, pack, "does not license")
        spy.assert_not_called()

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

    def test_refuses_a_frozen_state_with_no_receipt(self) -> None:
        """The state ALONE selects the composed path; no receipt is a refusal."""

        repository, pack = self.fixture()
        shutil.rmtree(pack / "identity_pin_projection.receipts")
        self.rewrite_tree(
            pack,
            lambda tree: tree["arm_attachments"]["identity_pin_projection"].__setitem__(
                "projection_receipt", None
            ),
        )
        self.recommit(repository)
        self.assert_refuses(repository, pack, "carries no receipt reference")

    def test_replay_refuses_a_superseded_anchored_projection(self) -> None:
        """`freeze_projection` (identity_pins.py:1831) refuses a superseded pack.

        No lawful projection can have been derived from one, so a replay that
        accepted it would manufacture a lineage the real freeze would have
        rejected.  A superseded projection is schema-required to carry real
        pins and a receipt reference (identity_pins.py:520-541), so the
        state is flipped on a copy of the FROZEN pack rather than the
        pre-projection one, and the replay is called directly.
        """

        repository, pack = self.fixture()
        scratch = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, scratch, True)
        candidate = scratch / pack.name
        shutil.copytree(pack, candidate)

        def supersede(value: dict) -> None:
            value["arm_attachments"]["identity_pin_projection"]["state"] = "superseded"

        tree = json.loads((candidate / "plan_tree.json").read_bytes())
        supersede(tree)
        producer = json.loads((candidate / "producer_contract.json").read_bytes())
        producer["identity_pin_projection"] = copy.deepcopy(
            tree["arm_attachments"]["identity_pin_projection"]
        )
        producer_raw = identity_pins._render_json(producer)
        (candidate / "producer_contract.json").write_bytes(producer_raw)
        tree["downstream_contract"]["producer_contract"]["sha256"] = hashlib.sha256(
            producer_raw
        ).hexdigest()
        tree_raw = identity_pins._render_json(tree)
        (candidate / "plan_tree.json").write_bytes(tree_raw)
        (candidate / "plan_tree.sha256").write_bytes(
            identity_pins._gnu_sidecar(
                hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json"
            )
        )
        # The candidate is a lawful superseded pack, so it LOADS ...
        _tree, projection, _producer = identity_pins._load_pack_projection(candidate)
        self.assertEqual(projection["state"], "superseded")

        receipt = json.loads((pack / RECEIPT_RELATIVE).read_bytes())
        digest = hashlib.sha256((pack / RECEIPT_RELATIVE).read_bytes()).hexdigest()
        # ... and the replay still refuses it.
        with self.assertRaises(evidence.EvidenceAuthoringError) as caught:
            evidence._replay_projection_write_set(
                candidate, receipt, RECEIPT_RELATIVE, digest, kind="PACK_AUTHENTICATION"
            )
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_pack_authentication_underivable",
        )
        self.assertIn("superseded", str(caught.exception))

    def test_refuses_a_mode_bit_flip(self) -> None:
        """The content census cannot see the executable bit; the fence must."""

        repository, pack = self.fixture()
        pack_relative = pack.resolve(strict=True).relative_to(repository).as_posix()
        os.chmod(pack / "config.json", 0o755)
        self.recommit(repository, "flip a mode bit")
        self.assertEqual(
            subprocess.run(
                ["git", "ls-tree", "HEAD", "--", f"{pack_relative}/config.json"],
                cwd=repository,
                capture_output=True,
                check=True,
            ).stdout.decode().split()[0],
            "100755",
            "the fixture did not actually record an executable bit",
        )
        self.assert_refuses(repository, pack, "changes file modes")

    def test_refuses_a_mode_bit_flip_on_a_licensed_addition(self) -> None:
        """The receipt and sidecar exist only at the head.

        The anchor-vs-head comparison spans shared paths only, so their modes
        are never reached by it and need a check of their own.
        """

        for relative in (RECEIPT_RELATIVE, SIDECAR_RELATIVE):
            with self.subTest(relative=relative):
                repository, pack = self.fixture()
                os.chmod(pack / relative, 0o755)
                self.recommit(repository, "flip a projection artifact mode")
                self.assert_refuses(
                    repository, pack, "not a plain committed file"
                )

    def test_refuses_a_receipt_carrying_an_extra_identity_unit(self) -> None:
        repository, pack = self.fixture()

        def add_unit(value: dict) -> None:
            extra = copy.deepcopy(value["identity_units"][0])
            extra["identity_unit_id"] = "smuggled/unit"
            value["identity_units"].append(extra)
            # The receipt schema pins the unit count, so a smuggled unit that
            # did not also correct it would be refused by validation instead.
            value["observations"]["identity_unit_count"] = len(value["identity_units"])

        self.rewrite_receipt(pack, add_unit)
        self.recommit(repository)
        self.assert_refuses(repository, pack, "identity units differ from the pack")


if __name__ == "__main__":
    unittest.main()
