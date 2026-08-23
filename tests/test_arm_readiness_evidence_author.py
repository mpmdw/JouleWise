from __future__ import annotations

import copy
import hashlib
import io
import inspect
import json
import os
import shlex
import shutil
import time
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
import joulewise.arm_readiness_evidence as evidence
from joulewise.arm_readiness_evidence import (
    EvidenceAuthoringError,
    author_arm_readiness_evidence,
)
from joulewise.receipt_oracle import derive_bracket_session_receipt_oracle
from scripts import author_arm_readiness_evidence as evidence_author_cli
from scripts import generate_arm_readiness as arm_readiness_cli
from tests.test_arm_readiness_lifecycle import (
    git,
    make_go_fixture,
    predecessor_pack_root,
)
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID


ROOT = Path(__file__).resolve().parents[1]
OTHER_BOOT_SESSION_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"


def _cli_stdout(buffer: io.BytesIO) -> mock.Mock:
    """Stand-in for sys.stdout that survives argparse's 3.14 colorize probe."""
    return mock.Mock(
        buffer=buffer,
        fileno=mock.Mock(side_effect=io.UnsupportedOperation("fileno")),
        isatty=mock.Mock(return_value=False),
    )


def passing_suites(
    repository: Path, test_ids: list[str] | tuple[str, ...]
) -> evidence._SuiteResult:
    executed = []
    loaded_ids = []
    for test_id in test_ids:
        module = ".".join(test_id.split(".")[:2])
        relative = f"{module.replace('.', '/')}.py"
        raw = (repository / relative).read_bytes()
        executed.append(
            evidence._ExecutedFile(module, relative, hashlib.sha256(raw).hexdigest())
        )
        loaded_ids.append(test_id)
    return evidence._SuiteResult(
        tuple(loaded_ids),
        len(test_ids),
        0,
        0,
        0,
        0,
        0,
        tuple(executed),
    )


def _copy_primary(repository: Path, relative: str) -> None:
    target = repository / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((ROOT / relative).read_bytes())


def _identity_unit(arm: str, model: str) -> dict:
    return {
        "declared_identity": {
            "hardware_target": "synthetic-mac",
            "model_name": model,
            "model_revision": f"{model}-revision",
            "model_source": f"/synthetic/{model}",
            "quantization": {"bits": 4, "group_size": None, "name": "int4"},
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "workload_profile": {
                "dataset_ref": None,
                "name": "df_ph_decode",
                "output_tokens": 8,
                "prompt_text": None,
                "prompt_tokens": 8,
                "repetitions": 1,
                "warmup_runs": 1,
            },
        },
        "consumer_bindings": [
            {"arm": arm, "family": f"synthetic-{arm}", "measurement_arm": "decode"}
        ],
    }


def make_author_fixture(pack_name: str = "d117_floor_qwen25_1p5b_v1"):
    """Build an ALPHA authoring pack plus its two family siblings.

    PACK_FAMILY derivation reads the family named by
    ``evidence._PACKS_BY_PROFILE``, which is the IMMUTABLE HISTORICAL family, so
    the default fixture is that family's generation-1 ALPHA member and the
    siblings match its generation.  A caller may ask for a later generation to
    exercise successor-chain behaviour; it must then supply the family route for
    that generation (today: by patching ``_PACKS_BY_PROFILE``, which stands in
    for the registry-driven successor family route that does not exist yet).
    """

    generation_suffix = pack_name[pack_name.rindex("_v") :]
    temporary, repository, pack, custody, arm_path = make_go_fixture(
        pack_name, "ALPHA"
    )

    for relative in (
        # Every registered issued generation is available to the fixture:
        # historical `_v1`/`_v2` packs pin n19/n19_r2, and successor packs may
        # name any retained n17 r3-r6 issuance.
        "configs/calibration/calibration_acceptance_d079_v2.json",
        "configs/calibration/calibration_acceptance_d079_v2_r2.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r3.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r4.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r5.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json",
        "docs/decision_log.md",
        "docs/phase_2/window_runbook.md",
        "joulewise/analysis_manifest_v3.py",
        "joulewise/arm_readiness.py",
        "joulewise/calibration_bracketing.py",
        "joulewise/calibration_ledger.py",
        "joulewise/detection_floor.py",
        "joulewise/floor_extraction.py",
        "joulewise/floor_mint_estimator.py",
        "joulewise/identity_pins.py",
        "joulewise/receipt_oracle.py",
        "scripts/floor_mint_pinsets/schema_v2.json",
        "scripts/mint_floor_artifact_generalized.py",
        "scripts/recover_calibration_ledger.py",
        "tests/test_calibration_ledger.py",
        "tests/test_calibration_bracketing.py",
        "tests/test_calibration_live_three_window.py",
        "tests/receipt_corpus.py",
        "tests/test_arm_readiness_dry_run.py",
        "tests/test_arm_readiness_lifecycle.py",
        "tests/test_arm_readiness_schemas.py",
        "tests/test_arm_readiness_integration.py",
        "tests/test_mint_floor_artifact.py",
        "tests/test_mint_floor_artifact_generalized.py",
    ):
        _copy_primary(repository, relative)
    for source in (ROOT / "joulewise").rglob("*.py"):
        _copy_primary(repository, source.relative_to(ROOT).as_posix())
    for source in (ROOT / "scripts").rglob("*.py"):
        _copy_primary(repository, source.relative_to(ROOT).as_posix())
    fixture = ROOT / "tests/fixtures/calibration_live_three_window/scenario.json"
    fixture_target = repository / fixture.relative_to(ROOT)
    fixture_target.parent.mkdir(parents=True, exist_ok=True)
    fixture_target.write_bytes(fixture.read_bytes())
    seven_b = ROOT / "configs/campaigns/qwen25_7b_decode_floor_v1"
    shutil.copytree(
        seven_b,
        repository / seven_b.relative_to(ROOT),
        dirs_exist_ok=True,
    )

    plan_path = pack / "calibration_plan.json"
    plan_raw = readiness.render_json(
        {"plan_id": "plan-test", "analysis": {"estimator": "d054_false_effect_guard.v1"}}
    )
    plan_path.write_bytes(plan_raw)
    config_raw = readiness.render_json({"run_id": "synthetic-member-1"})
    (pack / "config.json").write_bytes(config_raw)
    manifest = {
        "schema_version": "joulewise.order_manifest.v1",
        "manifest_id": "synthetic-order-v1",
        "plan_id": "plan-test",
        "calibration_plan_sha256": hashlib.sha256(plan_raw).hexdigest(),
        "planned_n_bundles": 1,
        "executed_order": [
            {
                "index": 1,
                "config": "config.json",
                "config_sha256": hashlib.sha256(config_raw).hexdigest(),
                "run_id": "synthetic-member-1",
            }
        ],
    }
    (pack / "order_manifest.json").write_bytes(readiness.render_json(manifest))

    generator_relative = f"configs/campaigns/{pack.name}/generate_configs.py"
    generator_raw = (
        "import sys\n"
        "if '--check' not in sys.argv:\n"
        "    raise SystemExit(2)\n"
        "print('synthetic pack check passed')\n"
    ).encode("utf-8")
    (pack / "generate_configs.py").write_bytes(generator_raw)
    producer_raw = readiness.render_json({"schema_version": "synthetic-producer.v1"})
    (pack / "producer_contract.json").write_bytes(producer_raw)

    extraction_relative = "configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json"
    _copy_primary(repository, extraction_relative)
    extraction_raw = (repository / extraction_relative).read_bytes()
    acceptance_relative = "configs/calibration/calibration_acceptance_d079_v2.json"
    acceptance_raw = (repository / acceptance_relative).read_bytes()

    tree_path = pack / "plan_tree.json"
    tree = json.loads(tree_path.read_text())
    tree["plan"] = {"path": "calibration_plan.json", "plan_id": "plan-test"}
    tree["generator"] = {
        "path": generator_relative,
        "sha256": hashlib.sha256(generator_raw).hexdigest(),
    }
    tree["downstream_contract"] = {
        "extraction_spec": {
            "path": extraction_relative,
            "sha256": hashlib.sha256(extraction_raw).hexdigest(),
        },
        "producer_contract": {
            "path": f"configs/campaigns/{pack.name}/producer_contract.json",
            "sha256": hashlib.sha256(producer_raw).hexdigest(),
        },
    }
    tree["attempt_policy"] = {
        "policy": "abort_window_on_any_required_member_failure",
        "predeclared_before_data": True,
        "calibration_retries": 0,
        "science_member_replacements": 0,
        "outcome_dependent_top_up": "forbidden",
    }
    tree["acceptance_policy"] = {
        "selection": "issued_d116_artifact_only",
        "issued_acceptance": {
            "acceptance_id": "d079_calibration_acceptance_v2_n19",
            "path": acceptance_relative,
            "artifact_sha256": hashlib.sha256(acceptance_raw).hexdigest(),
        },
    }
    tree["stage_graph"] = [
        {
            "stage_id": "synthetic-verdict",
            "kind": "whole_window_verdict",
            "launch": {"commands": []},
        },
        {
            "stage_id": "synthetic-backup",
            "kind": "backup",
            "launch": {
                "commands": [
                    {"command_kind": "backup", "command_id": "backup.claim"},
                    {"command_kind": "backup", "command_id": "backup.bound"},
                ]
            },
        },
    ]
    tree["closeout_attachments"] = {
        "backup_requirements": {"required_successful_backups": 2}
    }
    tree["arm_attachments"]["launch"] = {
        "schema_version": "joulewise.stage_launch_bindings.v1",
        "bindings": [],
        "derived_path_rules": [],
    }
    tree["arm_attachments"]["receipt_oracle"] = (
        derive_bracket_session_receipt_oracle()
    )

    alpha_identity = _identity_unit("A", "alpha-model")
    tree["arm_attachments"]["identity_pin_projection"]["identity_units"][0][
        "declared_identity"
    ] = copy.deepcopy(alpha_identity["declared_identity"])
    tree["arm_attachments"]["identity_pin_projection"]["identity_units"][0][
        "consumer_bindings"
    ] = copy.deepcopy(alpha_identity["consumer_bindings"])
    tree_raw = readiness.render_json(tree)
    tree_path.write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_bytes(
        readiness.gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
    )

    beta_identity = _identity_unit("B", "beta-model")
    sibling_trees = {
        f"d117_floor_qwen25_7b{generation_suffix}": [beta_identity],
        f"d117_contrast_qwen25_1p5b_vs_7b{generation_suffix}": [
            alpha_identity,
            beta_identity,
        ],
    }
    for pack_name, units in sibling_trees.items():
        sibling = repository / "configs/campaigns" / pack_name
        sibling.mkdir(parents=True, exist_ok=True)
        (sibling / "plan_tree.json").write_bytes(
            readiness.render_json(
                {
                    "arm_attachments": {
                        "identity_pin_projection": {"identity_units": units}
                    }
                }
            )
        )

    git(repository, "add", ".")
    git(repository, "commit", "-qm", "author evidence inputs")
    git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
    return temporary, repository, pack, custody, arm_path


class ArmReadinessEvidenceAuthorTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        boot = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        utc = mock.patch.object(readiness, "_utc_now", return_value="2026-08-12T12:00:00Z")
        monotonic = mock.patch.object(evidence.time, "monotonic_ns", return_value=100)
        boot.start()
        utc.start()
        monotonic.start()
        self.addCleanup(boot.stop)
        self.addCleanup(utc.stop)
        self.addCleanup(monotonic.stop)

    def test_committed_fixture_derives_every_generic_kind_from_known_artifacts(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        repository = repository.resolve(strict=True)
        tree, _raw = readiness._plan_tree(pack)
        context = evidence._DerivationContext(
            pack_root=pack,
            repository=repository,
            tree=tree,
            pack_sha256=readiness.committed_pack_tree_sha256(pack),
            head_commit=readiness.reviewed_main(pack)["head_commit"],
        )
        rows, kinds = evidence._required_generic_rows(pack, tree)
        self.assertNotIn("ACCEPTANCE_SUCCESSOR", kinds)
        with self.assertRaisesRegex(
            EvidenceAuthoringError, "no ratified successor-acceptance"
        ):
            evidence._derive_acceptance_successor(context)
        by_kind = {
            kind: [row for row in rows if kind in row["required_evidence_kinds"]]
            for kind in kinds
        }
        with mock.patch.object(
            evidence,
            "_execute_unittest_suite_subprocess",
            side_effect=passing_suites,
        ):
            for kind in kinds:
                with self.subTest(kind=kind):
                    derived = evidence._DERIVERS[kind](context)
                    if kind == "DOCTRINE_PIN":
                        self.assertTrue(
                            {
                                "joulewise/arm_readiness_evidence.py",
                                "scripts/author_arm_readiness_evidence.py",
                            }
                            <= {
                                artifact["path"]
                                for artifact in derived.primary_artifacts
                            }
                        )
                    source = evidence._fact_source(context, derived)
                    receipt = evidence._assemble_receipt(
                        context,
                        derived,
                        source,
                        issued_at_utc="2026-08-12T12:00:00Z",
                        boot_session_id=TEST_BOOT_SESSION_ID,
                        valid_until_monotonic_ns=10**30,
                    )
                    readiness.validate_evidence_receipt(receipt)
                    for row in by_kind[kind]:
                        self.assertTrue(
                            readiness._predicate_passes(receipt, row["predicate_id"]),
                            row,
                        )

    def test_public_author_signature_has_no_execution_injection(self) -> None:
        # The cold-gate fence is that authoring admits no OUTCOME-BEARING seam:
        # boot identity, clocks, hashes, HEAD, facts, statuses and suite
        # outcomes are always derived here and can never be supplied.  The
        # S-1 step-6 threading widened this signature by exactly two
        # keyword-only CUSTODY INPUTS (a table path and Ed's out-of-band
        # digest), which carry no outcome and are defaulted to None so an
        # omitted table still fails closed rather than being derived.  The
        # library asserts the same tuple at import
        # (`_assert_public_author_signature`); this test mirrors it so the
        # fence cannot be relaxed on one side only.
        parameters = inspect.signature(author_arm_readiness_evidence).parameters
        self.assertEqual(
            tuple(parameters),
            ("pack_root", "step6_confirmation_table", "expected_confirmation_digest"),
        )
        for name in ("step6_confirmation_table", "expected_confirmation_digest"):
            with self.subTest(parameter=name):
                self.assertIs(
                    parameters[name].kind, inspect.Parameter.KEYWORD_ONLY
                )
                self.assertIsNone(parameters[name].default)
        for keyword in ("runner", "outcome", "_suite_runner"):
            with self.subTest(keyword=keyword), self.assertRaises(TypeError):
                author_arm_readiness_evidence(Path("unused"), **{keyword: object()})

    def test_public_namespace_has_exact_non_dispatch_census(self) -> None:
        self.assertEqual(
            evidence.__all__,
            [
                "EvidenceAuthoringError",
                "author_arm_readiness_evidence",
            ],
        )
        self.assertIs(type(evidence._DERIVERS), dict)
        self.assertFalse(hasattr(evidence, "DERIVERS"))
        with self.assertRaises(AttributeError):
            evidence.DERIVERS["DOCTRINE_PIN"] = lambda _context: object()
        # Cold-gate boundary (2026-08-12 synthesis): the module's ACTUAL
        # public (non-underscore) namespace admits no outcome-bearing seam —
        # no dispatch table, no deriver, no domain-module handle. Frozen
        # census; any new public name must be adjudicated here.
        self.assertEqual(
            sorted(name for name in vars(evidence) if not name.startswith("_")),
            [
                "Any",
                "Callable",
                "EvidenceAuthoringError",
                "Mapping",
                "Path",
                "PurePosixPath",
                "Sequence",
                "annotations",
                "author_arm_readiness_evidence",
                "copy",
                "dataclass",
                "inspect",
                "json",
                "os",
                "re",
                "shutil",
                "signal",
                "subprocess",
                "sys",
                "tempfile",
                "time",
            ],
        )
        for name in ("derive_doctrine_pin", "derive_three_window_regression",
                     "derive_bracket_session_receipt_oracle", "readiness",
                     "validate_extraction_spec", "SPECIALIZED_EVIDENCE_KINDS",
                     "EVIDENCE_VALIDITY_NS", "SOURCE_SCHEMA",
                     "SOURCE_DIRECTORY", "EVIDENCE_DIRECTORY",
                     "DerivationContext", "DerivedKind"):
            self.assertFalse(hasattr(evidence, name))

    def test_production_suite_runner_records_exact_three_window_counts(self) -> None:
        result = evidence._execute_unittest_suite_subprocess(
            ROOT, ("tests.test_calibration_live_three_window",)
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.tests_run, 23)
        self.assertEqual(result.skipped, 3)
        identities = {item.path: item.sha256 for item in result.executed_files}
        relative = "tests/test_calibration_live_three_window.py"
        self.assertEqual(
            identities[relative], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        )

    def test_authoring_is_deterministic_and_consumer_boot_primitive_pins(self) -> None:
        # Renamed per delta re-audit S1D-2: the boot leg exercises the
        # CONSUMER-side primitive (validate_r1_class_lifecycle, called only
        # from arm_readiness.py), not authoring-path boot binding — R1
        # authoring does not enforce boot binding; the arm path does, with
        # live boot context, failing closed without it. The end-to-end
        # boot-voiding obligation is recorded on row A84.
        temporary, _repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        with mock.patch.object(
            evidence,
            "_execute_unittest_suite_subprocess",
            side_effect=passing_suites,
        ):
            first = author_arm_readiness_evidence(pack)
            self.assertEqual(first["status"], "PASS")
            tree, _raw = readiness._plan_tree(pack)
            _rows, kinds = evidence._required_generic_rows(pack, tree)
            self.assertEqual(first["authored_kinds"], kinds)
            before = {
                path.relative_to(pack).as_posix(): path.read_bytes()
                for directory in (
                    pack / evidence._SOURCE_DIRECTORY,
                    pack / evidence._EVIDENCE_DIRECTORY,
                )
                for path in directory.iterdir()
            }
            for path in (pack / evidence._EVIDENCE_DIRECTORY).glob("*.json"):
                receipt = readiness.validate_evidence_receipt(
                    readiness.parse_json_bytes(path.read_bytes(), require_canonical=True)
                )
                # Exact-key schema validation above already owns the absence of
                # boot fields from content receipts.  Independently pin the
                # positive boot binding carried by every execution receipt.
                if (
                    receipt["schema_version"]
                    == readiness.EXECUTION_EVIDENCE_RECEIPT_SCHEMA
                ):
                    self.assertEqual(
                        receipt["boot_session_id"], TEST_BOOT_SESSION_ID
                    )
            git(_repository, "add", ".")
            git(_repository, "commit", "-qm", "authored evidence")
            git(_repository, "update-ref", "refs/remotes/origin/main", "HEAD")
            second = author_arm_readiness_evidence(pack)
            self.assertFalse(second["mutated"])
            after = {
                path.relative_to(pack).as_posix(): path.read_bytes()
                for directory in (
                    pack / evidence._SOURCE_DIRECTORY,
                    pack / evidence._EVIDENCE_DIRECTORY,
                )
                for path in directory.iterdir()
            }
            self.assertEqual(before, after)
            execution_receipt = next(
                readiness.validate_evidence_receipt(
                    readiness.parse_json_bytes(path.read_bytes(), require_canonical=True)
                )
                for path in (pack / evidence._EVIDENCE_DIRECTORY).glob("*.json")
                if readiness.parse_json_bytes(
                    path.read_bytes(), require_canonical=True
                )["schema_version"]
                == readiness.EXECUTION_EVIDENCE_RECEIPT_SCHEMA
            )
            with self.assertRaisesRegex(
                readiness.ArmReadinessError,
                "EXECUTION_BOUND evidence is outside its boot/horizon binding",
            ) as stale:
                readiness.validate_r1_class_lifecycle(
                    execution_receipt,
                    execution_receipt["kind"],
                    current_boot_session_id=OTHER_BOOT_SESSION_ID,
                    now_monotonic_ns=100,
                )
            self.assertEqual(stale.exception.reason_code, "readiness_record_expired")

    def test_uncommitted_authoring_file_refuses_before_writing_output(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        author_module = repository / "joulewise/arm_readiness_evidence.py"
        author_module.write_bytes(author_module.read_bytes() + b"\n# uncommitted probe\n")

        with self.assertRaises(EvidenceAuthoringError) as caught:
            author_arm_readiness_evidence(pack)
        self.assertEqual(caught.exception.kind, "DOCTRINE_PIN")
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_doctrine_pin_underivable",
        )
        self.assertIn("not byte-identical to HEAD", str(caught.exception))
        self.assertFalse((pack / evidence._SOURCE_DIRECTORY).exists())
        self.assertFalse((pack / evidence._EVIDENCE_DIRECTORY).exists())

    def test_cli_refuses_pack_from_a_different_repository_tree(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        self.assertNotEqual(repository.resolve(), evidence_author_cli.REPO_ROOT)
        output = io.BytesIO()
        stdout = _cli_stdout(output)

        with mock.patch.object(evidence_author_cli.sys, "stdout", stdout):
            return_code = evidence_author_cli.main(["--pack-root", str(pack)])

        self.assertEqual(return_code, 2)
        refused = readiness.parse_json_bytes(output.getvalue(), require_canonical=True)
        self.assertEqual(refused["status"], "REFUSE")
        self.assertEqual(
            refused["reason_codes"], ["evidence_author_repository_mismatch"]
        )
        self.assertFalse((pack / evidence._SOURCE_DIRECTORY).exists())
        self.assertFalse((pack / evidence._EVIDENCE_DIRECTORY).exists())

    def test_source_tamper_refuses_without_overwriting_any_receipt(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        suite_patch = mock.patch.object(
            evidence,
            "_execute_unittest_suite_subprocess",
            side_effect=passing_suites,
        )
        suite_patch.start()
        self.addCleanup(suite_patch.stop)
        author_arm_readiness_evidence(pack)
        receipt_before = {
            path.name: path.read_bytes()
            for path in (pack / evidence._EVIDENCE_DIRECTORY).iterdir()
        }
        source = pack / evidence._SOURCE_DIRECTORY / "doctrine-pin.json"
        source.write_bytes(source.read_bytes() + b" ")
        # Commit and review the tamper so pack custody admits the staged bytes.
        # The fixture registry's exact allowlist names this fixture generation,
        # so the authored-path commit reaches the source/receipt integrity check
        # instead of being misclassified as an unrelated changed dependency.
        git(repository, "add", ".")
        git(repository, "commit", "-qm", "authored evidence, tampered source")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        with self.assertRaisesRegex(EvidenceAuthoringError, "invalid"):
            author_arm_readiness_evidence(pack)
        self.assertEqual(
            receipt_before,
            {
                path.name: path.read_bytes()
                for path in (pack / evidence._EVIDENCE_DIRECTORY).iterdir()
            },
        )

    def test_coordinated_source_receipt_rewrite_refuses_without_overwrite(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        suite_patch = mock.patch.object(
            evidence,
            "_execute_unittest_suite_subprocess",
            side_effect=passing_suites,
        )
        suite_patch.start()
        self.addCleanup(suite_patch.stop)
        author_arm_readiness_evidence(pack)
        source_path = pack / evidence._SOURCE_DIRECTORY / "doctrine-pin.json"
        receipt_path = (
            pack
            / evidence._EVIDENCE_DIRECTORY
            / "evidence-doctrine-pin.json"
        )
        source = readiness.parse_json_bytes(
            source_path.read_bytes(), require_canonical=True
        )
        source["derivation"]["operator_supplied_conclusion"] = True
        source_raw = readiness.render_json(source)
        source_path.write_bytes(source_raw)
        receipt = readiness.parse_json_bytes(
            receipt_path.read_bytes(), require_canonical=True
        )
        receipt["dependency_manifest_sha256"] = hashlib.sha256(source_raw).hexdigest()
        for fact in receipt["facts"]:
            fact["source_sha256"] = hashlib.sha256(source_raw).hexdigest()
        receipt_raw = readiness.render_json(receipt)
        receipt_path.write_bytes(receipt_raw)
        receipt_path.with_name(f"{receipt_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(receipt_raw).hexdigest(), receipt_path.name
            )
        )
        # This is the COHERENT rewrite: source, receipt facts, and sidecar agree.
        # Committing it creates the authored-path changed set; the fixture's
        # pack-exact allowlist deliberately admits that set.  Semantic replay
        # must therefore reject the internally consistent lie.
        git(repository, "add", ".")
        git(repository, "commit", "-qm", "authored evidence, coordinated rewrite")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        tampered = {
            path.relative_to(pack).as_posix(): path.read_bytes()
            for directory in (
                pack / evidence._SOURCE_DIRECTORY,
                pack / evidence._EVIDENCE_DIRECTORY,
            )
            for path in directory.iterdir()
        }
        with self.assertRaisesRegex(
            EvidenceAuthoringError,
            "DOCTRINE_PIN ARM re-derivation differs from authored semantics",
        ):
            author_arm_readiness_evidence(pack)
        self.assertEqual(
            tampered,
            {
                path.relative_to(pack).as_posix(): path.read_bytes()
                for directory in (
                    pack / evidence._SOURCE_DIRECTORY,
                    pack / evidence._EVIDENCE_DIRECTORY,
                )
                for path in directory.iterdir()
            },
        )

    def test_first_authoring_refuses_when_restore_after_verdict_and_both_backups_is_removed(
        self,
    ) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        runbook = repository / "docs/phase_2/window_runbook.md"
        text = runbook.read_text(encoding="utf-8")
        text = text.replace(
            "whole-window verdict, and the backup, re-enable it:",
            "window close-out, re-enable it:",
        ).replace(
            "The restore comes last because re-enabling automatic network time permits",
            "Re-enabling automatic network time permits",
        )
        runbook.write_text(text, encoding="utf-8")
        git(repository, "add", "docs/phase_2/window_runbook.md")
        git(repository, "commit", "-qm", "tamper restore doctrine")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

        with self.assertRaises(EvidenceAuthoringError) as caught:
            author_arm_readiness_evidence(pack)
        self.assertEqual(caught.exception.kind, "DOCTRINE_PIN")
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_doctrine_pin_underivable",
        )
        self.assertFalse((pack / evidence._SOURCE_DIRECTORY).exists())
        self.assertFalse((pack / evidence._EVIDENCE_DIRECTORY).exists())

    def test_first_authoring_refuses_tampered_acceptance_owner_primary(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        acceptance_path = (
            repository / "configs/calibration/calibration_acceptance_d079_v2.json"
        )
        acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
        acceptance["unknown_evidence_author_probe"] = True
        acceptance_raw = readiness.render_json(acceptance)
        acceptance_path.write_bytes(acceptance_raw)
        tree_path = pack / "plan_tree.json"
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
        tree["acceptance_policy"]["issued_acceptance"]["artifact_sha256"] = (
            hashlib.sha256(acceptance_raw).hexdigest()
        )
        tree_raw = readiness.render_json(tree)
        tree_path.write_bytes(tree_raw)
        (pack / "plan_tree.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json"
            )
        )
        git(repository, "add", ".")
        git(repository, "commit", "-qm", "tamper acceptance primary")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

        with self.assertRaises(EvidenceAuthoringError) as caught:
            author_arm_readiness_evidence(pack)
        self.assertEqual(caught.exception.kind, "ACCEPTANCE_OWNER")
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_acceptance_owner_underivable",
        )
        self.assertFalse((pack / evidence._SOURCE_DIRECTORY).exists())
        self.assertFalse((pack / evidence._EVIDENCE_DIRECTORY).exists())

    def _install_target_sentinel_suite(
        self,
        repository: Path,
        *,
        marker: Path,
        marker_text: str,
        failing: bool,
    ) -> bytes:
        relative = "tests/test_calibration_ledger.py"
        failure = "self.fail('target sentinel failure')" if failing else "self.assertTrue(True)"
        raw = (
            "from pathlib import Path\n"
            "import unittest\n"
            "\n"
            "class TargetBytesTests(unittest.TestCase):\n"
            "    def test_executes(self):\n"
            f"        Path({str(marker)!r}).write_text({marker_text!r}, encoding='utf-8')\n"
            f"        {failure}\n"
        ).encode("utf-8")
        (repository / relative).write_bytes(raw)
        git(repository, "add", relative)
        git(repository, "commit", "-qm", "install target-only sentinel suite")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        return raw

    def _install_environment_sentinel_suite(
        self, repository: Path, *, marker: Path, poison_name: str
    ) -> None:
        relative = "tests/test_calibration_ledger.py"
        raw = (
            "import json\n"
            "import os\n"
            "from pathlib import Path\n"
            "import unittest\n"
            "\n"
            "class TargetBytesTests(unittest.TestCase):\n"
            "    def test_executes(self):\n"
            f"        observed = {{'poison': os.environ.get({poison_name!r}), "
            "'LC_ALL': os.environ.get('LC_ALL'), 'LANG': os.environ.get('LANG')}\n"
            f"        Path({str(marker)!r}).write_text(json.dumps(observed, sort_keys=True), encoding='utf-8')\n"
            f"        self.assertNotIn({poison_name!r}, os.environ)\n"
            "        self.assertEqual(os.environ.get('LC_ALL'), 'C')\n"
            "        self.assertEqual(os.environ.get('LANG'), 'C')\n"
        ).encode("utf-8")
        (repository / relative).write_bytes(raw)
        git(repository, "add", relative)
        git(repository, "commit", "-qm", "install hermetic environment sentinel")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

    def _install_grandchild_sentinel_suite(
        self, repository: Path, *, marker: Path, block_seconds: float
    ) -> None:
        relative = "tests/test_calibration_ledger.py"
        grandchild = (
            "import time\n"
            "from pathlib import Path\n"
            "time.sleep(0.75)\n"
            f"Path({str(marker)!r}).write_text('LEAKED', encoding='utf-8')\n"
        )
        raw = (
            "import subprocess\n"
            "import sys\n"
            "import time\n"
            "import unittest\n"
            "\n"
            "class TargetBytesTests(unittest.TestCase):\n"
            "    def test_executes(self):\n"
            f"        subprocess.Popen([sys.executable, '-I', '-B', '-c', {grandchild!r}])\n"
            f"        time.sleep({block_seconds!r})\n"
        ).encode("utf-8")
        (repository / relative).write_bytes(raw)
        git(repository, "add", relative)
        git(repository, "commit", "-qm", "install process-group sentinel")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

    def test_suite_child_does_not_inherit_parent_poison_or_hostile_locale(self) -> None:
        temporary, repository, _pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        marker = Path(temporary.name) / "environment.marker"
        poison_name = "JOULEWISE_AUTHOR_POISON"
        self._install_environment_sentinel_suite(
            repository, marker=marker, poison_name=poison_name
        )

        with mock.patch.dict(
            os.environ,
            {poison_name: "MUST_NOT_CROSS", "LC_ALL": "HOSTILE_LOCALE"},
        ):
            result = evidence._execute_unittest_suite_subprocess(
                repository,
                ("tests.test_calibration_ledger.TargetBytesTests.test_executes",),
            )

        self.assertTrue(result.passed)
        self.assertEqual(
            json.loads(marker.read_text(encoding="utf-8")),
            {"LANG": "C", "LC_ALL": "C", "poison": None},
        )

    def test_suite_completion_kills_delayed_grandchild_process_group(self) -> None:
        temporary, repository, _pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        marker = Path(temporary.name) / "completion-grandchild.marker"
        self._install_grandchild_sentinel_suite(
            repository, marker=marker, block_seconds=0.0
        )

        result = evidence._execute_unittest_suite_subprocess(
            repository,
            ("tests.test_calibration_ledger.TargetBytesTests.test_executes",),
        )
        self.assertTrue(result.passed)
        time.sleep(1.0)
        self.assertFalse(marker.exists())

    def test_suite_timeout_kills_delayed_grandchild_process_group(self) -> None:
        temporary, repository, _pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        marker = Path(temporary.name) / "timeout-grandchild.marker"
        self._install_grandchild_sentinel_suite(
            repository, marker=marker, block_seconds=5.0
        )

        with (
            mock.patch.object(evidence, "_SUITE_TIMEOUT_SECONDS", 0.1),
            self.assertRaisesRegex(ValueError, "timed out after 0.1 seconds"),
        ):
            evidence._execute_unittest_suite_subprocess(
                repository,
                ("tests.test_calibration_ledger.TargetBytesTests.test_executes",),
            )
        time.sleep(1.0)
        self.assertFalse(marker.exists())

    def _target_sentinel_deriver(self, context) -> evidence._DerivedKind:
        kind = "RECOVERY_LEDGER_TEST"
        result = evidence._run_suite(
            context,
            kind,
            ("tests.test_calibration_ledger.TargetBytesTests.test_executes",),
        )
        artifact, _raw = evidence._committed_artifact(
            context.repository, "tests/test_calibration_ledger.py", kind=kind
        )
        return evidence._DerivedKind(
            kind,
            {"desk.recovery_ledger_path.v1": {"target_sentinel_status": "PASS"}},
            (artifact,),
            (evidence._check("target_sentinel_suite", result.evidence()),),
            {"bound_head": context.head_commit},
        )

    def test_public_author_executes_target_bytes_and_binds_executed_file_sha(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        marker = Path(temporary.name) / "sentinel.marker"
        target_raw = self._install_target_sentinel_suite(
            repository,
            marker=marker,
            marker_text="TARGET-REPOSITORY-BYTES",
            failing=False,
        )
        self.assertNotEqual(
            hashlib.sha256(target_raw).hexdigest(),
            hashlib.sha256((ROOT / "tests/test_calibration_ledger.py").read_bytes()).hexdigest(),
        )
        with (
            mock.patch.object(
                evidence,
                "_required_generic_rows",
                return_value=([], ["RECOVERY_LEDGER_TEST"]),
            ),
            mock.patch.dict(
                evidence._DERIVERS,
                {"RECOVERY_LEDGER_TEST": self._target_sentinel_deriver},
                clear=True,
            ),
        ):
            result = author_arm_readiness_evidence(pack)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(marker.read_text(encoding="utf-8"), "TARGET-REPOSITORY-BYTES")
        source = readiness.parse_json_bytes(
            (
                pack
                / evidence._SOURCE_DIRECTORY
                / "recovery-ledger-test.json"
            ).read_bytes(),
            require_canonical=True,
        )
        executed = source["checks"][0]["evidence"]["executed_files"]
        identity = next(
            item for item in executed if item["path"] == "tests/test_calibration_ledger.py"
        )
        self.assertEqual(identity["sha256"], hashlib.sha256(target_raw).hexdigest())

    def test_public_derivation_refuses_failing_target_suite_after_fresh_execution(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        marker = Path(temporary.name) / "failing-sentinel.marker"
        self._install_target_sentinel_suite(
            repository,
            marker=marker,
            marker_text="FAILING-TARGET-EXECUTED",
            failing=True,
        )
        with (
            mock.patch.object(
                evidence,
                "_required_generic_rows",
                return_value=([], ["RECOVERY_LEDGER_TEST"]),
            ),
            mock.patch.dict(
                evidence._DERIVERS,
                {"RECOVERY_LEDGER_TEST": self._target_sentinel_deriver},
                clear=True,
            ),
        ):
            with self.assertRaisesRegex(EvidenceAuthoringError, "focused suite refused"):
                author_arm_readiness_evidence(pack)
        self.assertEqual(marker.read_text(encoding="utf-8"), "FAILING-TARGET-EXECUTED")
        self.assertFalse((pack / evidence._SOURCE_DIRECTORY).exists())
        self.assertFalse((pack / evidence._EVIDENCE_DIRECTORY).exists())

    def test_derivation_refuses_executed_file_sha_mismatch(self) -> None:
        temporary, repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        marker = Path(temporary.name) / "sha-mismatch.marker"
        self._install_target_sentinel_suite(
            repository,
            marker=marker,
            marker_text="SHA-MISMATCH-PROBE",
            failing=False,
        )
        tree, _raw = readiness._plan_tree(pack)
        context = evidence._DerivationContext(
            pack_root=pack,
            repository=repository,
            tree=tree,
            pack_sha256=readiness.committed_pack_tree_sha256(pack),
            head_commit=readiness.reviewed_main(pack)["head_commit"],
        )
        test_ids = ("tests.test_calibration_ledger.TargetBytesTests.test_executes",)
        observed = evidence._execute_unittest_suite_subprocess(repository, test_ids)
        target = next(
            item
            for item in observed.executed_files
            if item.path == "tests/test_calibration_ledger.py"
        )
        attacked_files = tuple(
            evidence._ExecutedFile(item.module, item.path, "0" * 64)
            if item == target
            else item
            for item in observed.executed_files
        )
        attacked = evidence._SuiteResult(
            observed.test_ids,
            observed.tests_run,
            observed.failures,
            observed.errors,
            observed.skipped,
            observed.expected_failures,
            observed.unexpected_successes,
            attacked_files,
        )
        with mock.patch.object(
            evidence, "_execute_unittest_suite_subprocess", return_value=attacked
        ):
            with self.assertRaisesRegex(
                EvidenceAuthoringError,
                "executed-file SHA differs from SHA-bound primary artifact",
            ):
                evidence._run_suite(context, "RECOVERY_LEDGER_TEST", test_ids)

    def test_assemble_receipt_owns_immediate_schema_validation(self) -> None:
        pack = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v1"
        tree, _raw = readiness._plan_tree(pack)
        context = evidence._DerivationContext(
            pack_root=pack,
            repository=ROOT,
            tree=tree,
            pack_sha256=readiness.committed_pack_tree_sha256(pack),
            head_commit=readiness.reviewed_main(pack)["head_commit"],
        )
        derived = evidence._DerivedKind(
            "DOCTRINE_PIN",
            {"clock.restore_recipe.v1": {"restore_after_verdict": True}},
            (),
            (evidence._check("schema_probe", {}),),
            {},
        )
        source = evidence._fact_source(context, derived)
        with mock.patch.object(evidence, "_evidence_id", return_value=""):
            with self.assertRaisesRegex(
                readiness.ArmReadinessError, "evidence receipt.evidence_id"
            ):
                evidence._assemble_receipt(
                    context,
                    derived,
                    source,
                    issued_at_utc="2026-08-12T12:00:00Z",
                    boot_session_id=TEST_BOOT_SESSION_ID,
                    valid_until_monotonic_ns=10**30,
                )

    def test_discovery_revalidation_catches_staged_source_digest_corruption(self) -> None:
        temporary, _repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        source_dir = pack / evidence._SOURCE_DIRECTORY
        real_replace = os.replace

        def replace_and_corrupt(source, destination):
            real_replace(source, destination)
            if Path(destination).resolve() == source_dir.resolve():
                path = next(source_dir.glob("*.json"))
                path.write_bytes(path.read_bytes() + b" ")

        with (
            mock.patch.object(
                evidence,
                "_execute_unittest_suite_subprocess",
                side_effect=passing_suites,
            ),
            mock.patch.object(evidence.os, "replace", side_effect=replace_and_corrupt),
        ):
            with self.assertRaisesRegex(
                EvidenceAuthoringError, "authored discovery refused"
            ):
                author_arm_readiness_evidence(pack)
        self.assertFalse((pack / evidence._SOURCE_DIRECTORY).exists())
        self.assertFalse((pack / evidence._EVIDENCE_DIRECTORY).exists())

    def test_final_receipt_validation_catches_invalid_discovery_object(self) -> None:
        temporary, _repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        real_discover = readiness._discover_evidence

        def discover_then_mutate(*args, **kwargs):
            items, discovered, refusals = real_discover(*args, **kwargs)
            attacked = copy.deepcopy(discovered)
            first = next(iter(attacked.values()))
            first["status"] = "INVALID"
            return items, attacked, refusals

        with (
            mock.patch.object(
                evidence,
                "_execute_unittest_suite_subprocess",
                side_effect=passing_suites,
            ),
            mock.patch.object(
                readiness, "_discover_evidence", side_effect=discover_then_mutate
            ),
        ):
            # Refusal CODES are the closed contract surface; detail MESSAGES
            # are diagnostic and code-authoritative.  Under R1 this mutation is
            # caught by the execution-receipt validator
            # (joulewise/arm_readiness.py:2259, "execution evidence receipt
            # status is invalid") rather than by the legacy generic validator
            # (:2143, "evidence status is invalid").  The message moved; the
            # governed code did not, so the code is what is asserted.
            with self.assertRaises(readiness.ArmReadinessError) as caught:
                author_arm_readiness_evidence(pack)
            self.assertEqual(
                caught.exception.reason_code, "readiness_schema_invalid"
            )
        self.assertFalse((pack / evidence._SOURCE_DIRECTORY).exists())
        self.assertFalse((pack / evidence._EVIDENCE_DIRECTORY).exists())

    def test_underivable_kind_writes_no_pack_output(self) -> None:
        temporary, _repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)

        def refuse(_context):
            raise evidence._underivable("DOCTRINE_PIN", "synthetic missing doctrine")

        with mock.patch.dict(evidence._DERIVERS, {"DOCTRINE_PIN": refuse}):
            with self.assertRaisesRegex(EvidenceAuthoringError, "missing doctrine"):
                author_arm_readiness_evidence(pack)
        self.assertFalse((pack / evidence._SOURCE_DIRECTORY).exists())
        self.assertFalse((pack / evidence._EVIDENCE_DIRECTORY).exists())

    def test_historical_pack_is_not_refused_by_the_author_registry_site(
        self,
    ) -> None:
        """The author's registry site resolves a historical v1 identity.

        The pack/profile map is immutable history, so this site must NEVER be
        the thing that refuses a v1 pack; prevention is layered onto the later
        governed gates (R2 frozen-plan resolution, freeze-receipt
        authentication, the R1 lifecycle once a registry installs it).
        """

        temporary, _repository, pack, _custody, _arm_path = make_go_fixture(
            "d117_floor_qwen25_1p5b_v1", "ALPHA"
        )
        self.addCleanup(temporary.cleanup)
        tree, _raw = readiness._plan_tree(pack)
        rows, kinds = evidence._required_generic_rows(pack, tree)
        self.assertTrue(rows)
        self.assertIn("PACK_FAMILY", kinds)
        self.assertEqual(readiness._plan_profile(pack), "ALPHA")

    def test_pack_family_evidence_binds_the_immutable_historical_family(
        self,
    ) -> None:
        temporary, _repository, pack, _custody, _arm_path = make_author_fixture()
        self.addCleanup(temporary.cleanup)
        tree, _raw = readiness._plan_tree(pack)
        context = evidence._DerivationContext(
            pack_root=pack,
            repository=readiness._repo_for_pack(pack),
            tree=tree,
            pack_sha256=readiness.committed_pack_tree_sha256(pack),
            head_commit=readiness.reviewed_main(pack)["head_commit"],
        )
        derived = evidence._derive_pack_family(context)
        self.assertEqual(
            [artifact["path"] for artifact in derived.primary_artifacts],
            [
                f"configs/campaigns/{pack_name}/plan_tree.json"
                for pack_name in evidence._PACKS_BY_PROFILE.values()
            ],
        )
        # The bound family is the historical one.  A registry-driven successor
        # route for PACK_FAMILY derivation does not exist yet: a _v2 pack would
        # still bind these three v1 plan trees.  Reported to the magistrate with
        # the R1 registry install rather than patched here.
        self.assertEqual(
            [artifact["path"] for artifact in derived.primary_artifacts],
            [
                "configs/campaigns/d117_floor_qwen25_1p5b_v1/plan_tree.json",
                "configs/campaigns/d117_floor_qwen25_7b_v1/plan_tree.json",
                "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/plan_tree.json",
            ],
        )

    def test_authored_evidence_makes_synthetic_pack_freeze_pass(self) -> None:
        # This one exercises the SUCCESSOR world end to end (freeze-0002 with a
        # predecessor root), so it needs the successor family route.  Patching
        # _PACKS_BY_PROFILE stands in for the registry-driven successor family
        # route that is not built yet: the code map itself is immutable history
        # and must not be edited to follow a supersession.
        family = mock.patch.dict(
            evidence._PACKS_BY_PROFILE,
            {
                # The ruled successor family (MAGISTRATE-RULING.md:124-131).
                "ALPHA": "d117_floor_qwen25_1p5b_v4",
                "BETA": "d117_floor_qwen25_7b_v4",
                "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v4",
            },
        )
        family.start()
        self.addCleanup(family.stop)
        temporary, repository, pack, _custody, _arm_path = make_author_fixture(
            "d117_floor_qwen25_1p5b_v4"
        )
        self.addCleanup(temporary.cleanup)
        author_output = io.BytesIO()
        author_stdout = _cli_stdout(author_output)
        with (
            mock.patch.object(evidence_author_cli, "REPO_ROOT", repository),
            mock.patch.object(evidence_author_cli.sys, "stdout", author_stdout),
        ):
            author_return_code = evidence_author_cli.main(["--pack-root", str(pack)])
        self.assertEqual(author_return_code, 0)
        authored = readiness.parse_json_bytes(
            author_output.getvalue(), require_canonical=True
        )
        self.assertEqual(authored["status"], "PASS")
        pack_relative = pack.relative_to(repository).as_posix()
        source_relative = f"{pack_relative}/{evidence._SOURCE_DIRECTORY}"
        evidence_relative = f"{pack_relative}/{evidence._EVIDENCE_DIRECTORY}"
        # D-139/F2: the fixture pack is a successor, so the emitted sequence
        # must carry the mechanically derived predecessor root or the operator
        # deadlocks on a command that always refuses.
        predecessor = predecessor_pack_root(repository, pack.name)
        predecessor_relative = predecessor.relative_to(repository).as_posix()
        self.assertEqual(
            authored["post_authoring"],
            {
                "sequence": [
                    f"git add -- {source_relative} {evidence_relative}",
                    "git commit",
                    "git push origin HEAD:main",
                    (
                        "python3 scripts/generate_arm_readiness.py freeze "
                        f"--pack-root {pack_relative} "
                        f"--predecessor-pack-root {predecessor_relative}"
                    ),
                ],
                "recovery": (
                    "A reboot or HEAD change voids all twelve receipts; run "
                    f"git rm -r -- {source_relative} {evidence_relative} "
                    "before re-authoring."
                ),
            },
        )
        git(repository, "add", "--", source_relative, evidence_relative)
        git(repository, "commit", "-qm", "authored freeze evidence")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        output = io.BytesIO()
        stdout = _cli_stdout(output)
        # Run the EMITTED command itself, from the repository root, so the
        # operator sequence is the thing under test rather than a hand-built
        # argv that happens to work.
        emitted = shlex.split(authored["post_authoring"]["sequence"][3])
        self.assertEqual(
            emitted[:2], ["python3", "scripts/generate_arm_readiness.py"]
        )
        previous_directory = Path.cwd()
        os.chdir(repository)
        try:
            with mock.patch.object(arm_readiness_cli.sys, "stdout", stdout):
                return_code = arm_readiness_cli.main(emitted[2:])
        finally:
            os.chdir(previous_directory)
        self.assertEqual(return_code, 0)
        result = readiness.parse_json_bytes(
            output.getvalue(), require_canonical=True
        )
        self.assertEqual(result["status"], "PASS", result)
        receipt = readiness.validate_freeze_receipt(
            json.loads(Path(result["receipt_path"]).read_text())
        )
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(len(receipt["rows"]), 14)
        self.assertEqual(
            len([row for row in receipt["rows"] if row["verdict"] == "PASS"]),
            13,
        )
        self.assertEqual(
            len(
                [
                    row
                    for row in receipt["rows"]
                    if row["verdict"] == "NOT_APPLICABLE"
                ]
            ),
            1,
        )
        self.assertEqual(receipt["receipt_id"], "freeze-0002")
        git(repository, "add", "--", pack_relative)
        git(repository, "commit", "-qm", "freeze synthetic successor")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        # F1 (delta-8): idempotent replay must re-authenticate the CURRENT
        # successor in full, not only its ancestry.  One appended byte in any
        # binding the receipt names must refuse instead of replaying PASS with
        # mutated: false; restoring the bytes must replay PASS again.
        receipt_path = Path(result["receipt_path"])
        replay = readiness.generate_freeze_receipt(
            pack, predecessor_pack_root=predecessor
        )
        self.assertEqual(
            (replay["status"], replay["mutated"], replay["receipt_sha256"]),
            ("PASS", False, result["receipt_sha256"]),
        )
        for label, target in (
            (
                "identity projection evidence",
                pack / "identity_pin_projection.receipts/projection-0001.json",
            ),
            ("freeze receipt", receipt_path),
            (
                "freeze receipt sidecar",
                receipt_path.with_name(f"{receipt_path.name}.sha256"),
            ),
        ):
            with self.subTest(tampered=label):
                original = target.read_bytes()
                target.write_bytes(original + b"\n")
                try:
                    with self.assertRaises(readiness.ArmReadinessError):
                        readiness.generate_freeze_receipt(
                            pack, predecessor_pack_root=predecessor
                        )
                finally:
                    target.write_bytes(original)
                restored = readiness.generate_freeze_receipt(
                    pack, predecessor_pack_root=predecessor
                )
                self.assertEqual(
                    (
                        restored["status"],
                        restored["mutated"],
                        restored["receipt_sha256"],
                    ),
                    ("PASS", False, result["receipt_sha256"]),
                )


if __name__ == "__main__":
    unittest.main()
