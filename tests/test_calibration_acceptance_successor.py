from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import joulewise.calibration_bracketing as bracketing
from joulewise.calibration_ledger import (
    LEDGER_SCHEMA,
    CalibrationBracketSession,
    CalibrationLedgerSnapshot,
    LedgerObservation,
)
from scripts import build_calibration_acceptance_successor as successor


REPO_ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE_PATH = (
    REPO_ROOT / "configs" / "calibration" / "calibration_acceptance_d079_v2.json"
)
REGISTRY_PATH = bracketing.DEFAULT_ACCEPTANCE_REGISTRY_PATH
PARENT_HEAD = "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _parent_artifact() -> dict:
    return json.loads(ACCEPTANCE_PATH.read_bytes())


def _parent_observations() -> list[LedgerObservation]:
    artifact = _parent_artifact()
    corpus_by_attempt = {
        member["member_id"]: member
        for member in artifact["derivation_corpus"]["members"]
    }
    systematic_bounds = {
        "20260726T000039-491995f3": "0.035435840879704805",
        "20260801T064830-c76f5d1c": "0.0350400833260715",
    }
    observations: list[LedgerObservation] = []
    for index, row in enumerate(
        artifact["prior_observation_set"]["observations"], start=1
    ):
        member = corpus_by_attempt.get(row["attempt_id"])
        manifest_sha = (
            member["manifest_sha256"] if member is not None else _digest(f"m-{index}")
        )
        evidence_sha = (
            member["instrument_evidence_sha256"]
            if member is not None
            else _digest(f"e-{index}")
        )
        bound = (
            member["b_fiducial_s"]
            if member is not None
            else systematic_bounds.get(row["attempt_id"], "0.027000000000000001")
        )
        sequence = index * 2
        observations.append(
            LedgerObservation(
                sequence=sequence,
                receipt_digest=(PARENT_HEAD if sequence == 76 else _digest(f"r-{sequence}")),
                attempt_id=row["attempt_id"],
                content_id=row["content_id"],
                artifact_sha256={
                    "manifest.json": manifest_sha,
                    "instrument_evidence.json": evidence_sha,
                },
                identity_epoch=dict(artifact["identity_epoch"]),
                t1_bindings={},
                capture_wall_time_s=str(sequence),
                exact_bound_lexeme_s=bound,
                disposition=row["disposition"],
                custody_locator=f"/authenticated/parent/{row['attempt_id']}",
                observation_kind="historical-import",
            )
        )
    return observations


def _new_observation(
    index: int,
    *,
    bound: str = "0.0200000000000000001",
    disposition: str = "valid",
    content_id: str | None = None,
    epoch: dict | None = None,
    artifacts: dict | None = None,
) -> LedgerObservation:
    attempt_id = f"live-{index:02d}"
    return LedgerObservation(
        sequence=77 + index,
        receipt_digest=_digest(f"live-receipt-{index}"),
        attempt_id=attempt_id,
        content_id=content_id if content_id is not None else _digest(f"live-content-{index}"),
        artifact_sha256=artifacts
        or {
            "manifest.json": _digest(f"live-manifest-{index}"),
            "instrument_evidence.json": _digest(f"live-evidence-{index}"),
        },
        identity_epoch=epoch or dict(_parent_artifact()["identity_epoch"]),
        t1_bindings={},
        capture_wall_time_s=str(1000 + index),
        exact_bound_lexeme_s=bound,
        disposition=disposition,
        custody_locator=f"/authenticated/live/{attempt_id}",
        observation_kind="live-capture",
    )


def _snapshot(
    extras: tuple[LedgerObservation, ...] = (),
    *,
    reasons: tuple[str, ...] = (),
) -> CalibrationLedgerSnapshot:
    receipts = [
        {
            "sequence": index,
            "event": (
                "historical-import-v1-finalization"
                if index == 76
                else "historical-import-v1-reservation"
            ),
            "receipt_digest": PARENT_HEAD if index == 76 else _digest(f"r-{index}"),
        }
        for index in range(1, 77)
    ]
    observations = _parent_observations()
    for extra in sorted(extras, key=lambda item: item.sequence):
        while len(receipts) < extra.sequence - 1:
            sequence = len(receipts) + 1
            receipts.append(
                {
                    "sequence": sequence,
                    "event": "reservation",
                    "receipt_digest": _digest(f"padding-{sequence}"),
                }
            )
        receipt = {
            "sequence": extra.sequence,
            "event": "finalization",
            "receipt_digest": extra.receipt_digest,
        }
        if extra.disposition == "abandoned":
            receipt.update(
                {
                    "attempt_id": extra.attempt_id,
                    "disposition": extra.disposition,
                    "content_id": extra.content_id,
                    "artifact_sha256": dict(extra.artifact_sha256),
                    "exact_bound_lexeme_s": extra.exact_bound_lexeme_s,
                }
            )
        receipts.append(receipt)
        observations.append(extra)
    head_digest = receipts[-1]["receipt_digest"]
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=Path("/authenticated/ledger.jsonl"),
        head_sequence=len(receipts),
        head_digest=head_digest,
        receipts=tuple(receipts),
        observations=tuple(observations),
        refusal_reasons=reasons,
        baseline_sequence=76,
        baseline_digest=PARENT_HEAD,
        committed_head_sequence=len(receipts),
        committed_head_digest=head_digest,
    )


def _probe(snapshot: CalibrationLedgerSnapshot) -> dict:
    return bracketing.probe_calibration_acceptance_trigger(
        snapshot,
        observed_identity_epoch=_parent_artifact()["identity_epoch"],
        require_committed_registry=False,
        verify_custody=False,
    )


def _init_publication_repo(root: Path) -> tuple[Path, Path]:
    config = root / "configs/calibration"
    config.mkdir(parents=True)
    (config / ACCEPTANCE_PATH.name).write_bytes(ACCEPTANCE_PATH.read_bytes())
    registry = config / REGISTRY_PATH.name
    registry.write_bytes(REGISTRY_PATH.read_bytes())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "anchor"], cwd=root, check=True)
    return registry, config


def _open_pre_snapshot() -> CalibrationLedgerSnapshot:
    base = _snapshot()
    pre = _new_observation(2, bound="0.02")
    pre = replace(
        pre,
        sequence=79,
        bracket_session_id="session-1",
        bracket_slot="pre",
        bracket_window_id="window-1",
        bracket_plan_id="plan-1",
        bracket_plan_sha256="1" * 64,
        bracket_evidence_root_id="evidence-1",
        bracket_runs_root="/runs/window-1",
        observation_kind="bracket-session-finalized",
    )
    open_digest = _digest("session-open")
    claim_digest = _digest("session-pre-claim")
    receipts = (
        *base.receipts,
        {
            "sequence": 77,
            "event": "bracket-session-open",
            "session_id": "session-1",
            "predecessor_digest": PARENT_HEAD,
            "receipt_digest": open_digest,
        },
        {
            "sequence": 78,
            "event": "bracket-session-slot-claim",
            "session_id": "session-1",
            "receipt_digest": claim_digest,
        },
        {
            "sequence": 79,
            "event": "bracket-session-slot-finalization",
            "session_id": "session-1",
            "receipt_digest": pre.receipt_digest,
        },
    )
    session = CalibrationBracketSession(
        session_id="session-1",
        window_id="window-1",
        plan_id="plan-1",
        plan_sha256="1" * 64,
        evidence_root_id="evidence-1",
        runs_root="/runs/window-1",
        capability_receipt_digest=open_digest,
        capability_sequence=77,
        slot_attempt_ids={"pre": pre.attempt_id, "post": "post-attempt"},
        state="open",
        finalized_slots={"pre": pre},
    )
    return replace(
        base,
        head_sequence=79,
        head_digest=pre.receipt_digest,
        receipts=receipts,
        refusal_reasons=(
            "calibration_ledger_bracket_session_open",
            "calibration_ledger_head_mismatch",
        ),
        bracket_sessions=(session,),
        committed_head_sequence=76,
        committed_head_digest=PARENT_HEAD,
    )


class RegistryTrustAnchorTests(unittest.TestCase):
    def test_current_registry_authenticates_exact_issued_state(self) -> None:
        registry = bracketing.load_calibration_acceptance_registry(
            require_committed=False
        )
        self.assertIsNotNone(registry)
        active = bracketing._active_registry_entry(registry)
        self.assertEqual(active["acceptance_id"], "d079_calibration_acceptance_v2_n19")
        self.assertEqual(
            active["artifact_sha256"],
            "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
        )
        artifact = bracketing.load_calibration_acceptance_bound()
        counts = {
            disposition: sum(
                row["disposition"] == disposition
                for row in artifact["prior_observation_set"]["observations"]
            )
            for disposition in ("valid", "systematic-invalid", "ordinary-invalid")
        }
        self.assertEqual(counts, {"valid": 30, "systematic-invalid": 2, "ordinary-invalid": 6})
        self.assertEqual(active["ledger_cutoff"]["sequence"], 76)

    def test_registry_rejects_multiple_active_duplicate_and_cycle(self) -> None:
        registry = json.loads(REGISTRY_PATH.read_bytes())
        duplicate = json.loads(json.dumps(registry["entries"][0]))
        duplicate["generation"] = 2
        duplicate["acceptance_id"] = "duplicate"
        duplicate["artifact_path"] = "configs/calibration/duplicate.json"
        duplicate["parent_acceptance_id"] = duplicate["acceptance_id"]
        duplicate["parent_artifact_sha256"] = duplicate["artifact_sha256"]
        registry["entries"].append(duplicate)
        self.assertFalse(bracketing._valid_registry(registry))
        registry["entries"][0]["active"] = False
        self.assertFalse(bracketing._valid_registry(registry))

    def test_registry_rejects_traversal_absolute_and_duplicate_paths(self) -> None:
        registry = json.loads(REGISTRY_PATH.read_bytes())
        for path in ("../escape.json", "/tmp/escape.json", "configs/calibration/../x.json"):
            with self.subTest(path=path):
                changed = json.loads(json.dumps(registry))
                changed["entries"][0]["artifact_path"] = path
                self.assertFalse(bracketing._valid_registry(changed))

    def test_registry_requires_committed_bytes_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact_path = root / "configs/calibration/calibration_acceptance_d079_v2.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_bytes(ACCEPTANCE_PATH.read_bytes())
            registry_path = artifact_path.parent / "calibration_acceptance_registry.json"
            registry_path.write_bytes(REGISTRY_PATH.read_bytes())
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "anchor"], cwd=root, check=True)
            self.assertIsNotNone(
                bracketing.load_calibration_acceptance_registry(
                    registry_path, repo_root=root, require_committed=True
                )
            )
            registry_path.write_bytes(registry_path.read_bytes() + b" ")
            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceRegistryRefusal,
                "acceptance_registry_missing_commit",
            ):
                bracketing.load_calibration_acceptance_registry(
                    registry_path, repo_root=root, require_committed=True
                )

    def test_registry_rejects_symlink_artifact_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "configs/calibration"
            config.mkdir(parents=True)
            target = root / "target.json"
            target.write_bytes(ACCEPTANCE_PATH.read_bytes())
            (config / "calibration_acceptance_d079_v2.json").symlink_to(target)
            registry_path = config / "calibration_acceptance_registry.json"
            registry_path.write_bytes(REGISTRY_PATH.read_bytes())
            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceRegistryRefusal,
                "acceptance_registry_artifact_path_substituted",
            ):
                bracketing.load_calibration_acceptance_registry(
                    registry_path, repo_root=root, require_committed=False
                )


class TriggerProbeTests(unittest.TestCase):
    def test_pre_probe_accepts_only_governed_open_u1_extension_shape(self) -> None:
        result = _probe(_open_pre_snapshot())
        self.assertEqual(result["outcome"], "successor_required")
        malformed = replace(
            _open_pre_snapshot(),
            refusal_reasons=("calibration_ledger_head_mismatch",),
        )
        self.assertEqual(
            _probe(malformed)["outcome"], "authentication_or_epoch_refusal"
        )

    def test_range_expansion_below_and_above_require_successor(self) -> None:
        for index, bound in enumerate(
            ("0.0200000000000000001", "0.033558756679899995")
        ):
            with self.subTest(bound=bound):
                result = _probe(_snapshot((_new_observation(index, bound=bound),)))
                self.assertEqual(result["outcome"], "successor_required")
                self.assertEqual(
                    result["observed_triggers"],
                    ["new_valid_same_identity_capture_expands_observed_range"],
                )

    def test_in_range_observation_does_not_trigger_before_boundary(self) -> None:
        result = _probe(_snapshot((_new_observation(0, bound="0.0271"),)))
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
        self.assertEqual(result["observed_triggers"], [])

    def test_counts_37_and_38_are_distinct(self) -> None:
        seven = tuple(_new_observation(index, bound="0.0271") for index in range(7))
        eight = tuple(_new_observation(index, bound="0.0271") for index in range(8))
        self.assertEqual(_probe(_snapshot(seven))["outcome"], "accepted_under_active_artifact")
        result = _probe(_snapshot(eight))
        self.assertEqual(result["outcome"], "successor_required")
        self.assertEqual(
            result["observed_triggers"],
            ["content_distinct_valid_same_epoch_count_boundary"],
        )

    def test_systematic_classification_and_above_screen_both_refuse(self) -> None:
        cases = (
            _new_observation(0, disposition="systematic-invalid", bound="0.02"),
            _new_observation(0, disposition="valid", bound="0.04"),
        )
        for observation in cases:
            with self.subTest(disposition=observation.disposition, bound=observation.exact_bound_lexeme_s):
                result = _probe(_snapshot((observation,)))
                self.assertEqual(result["outcome"], "systematic_refusal")
                self.assertEqual(
                    result["refusal_reasons"],
                    [bracketing.SUCCESSOR_SYSTEMATIC_POLICY],
                )

    def test_ordinary_invalid_is_recorded_but_does_not_trigger(self) -> None:
        result = _probe(
            _snapshot((_new_observation(0, disposition="ordinary-invalid", bound="0.04"),))
        )
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
        self.assertEqual(len(result["new_content_ids"]), 1)

    def test_authenticated_terminal_no_content_is_excluded_without_refusal(self) -> None:
        observation = replace(
            _new_observation(0, disposition="abandoned"),
            content_id=None,
            artifact_sha256={},
            exact_bound_lexeme_s=None,
        )
        result = _probe(_snapshot((observation,)))
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
        self.assertEqual(result["new_content_ids"], [])
        self.assertEqual(result["refusal_reasons"], [])

    def test_terminal_no_content_receipt_variation_has_named_refusal(self) -> None:
        observation = replace(
            _new_observation(0, disposition="abandoned"),
            content_id=None,
            artifact_sha256={},
            exact_bound_lexeme_s=None,
        )
        snapshot = _snapshot((observation,))
        malformed_receipt = dict(snapshot.receipts[-1])
        malformed_receipt.pop("attempt_id")
        result = _probe(
            replace(snapshot, receipts=(*snapshot.receipts[:-1], malformed_receipt))
        )
        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
        self.assertEqual(
            result["refusal_reasons"],
            ["successor_terminal_no_content_receipt_malformed"],
        )

    def test_same_content_alias_does_not_increment_count(self) -> None:
        original = _parent_observations()[0]
        alias = replace(
            original,
            sequence=77,
            receipt_digest=_digest("alias-receipt"),
            attempt_id="live-alias",
            observation_kind="live-capture",
        )
        result = _probe(_snapshot((alias,)))
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
        self.assertEqual(result["new_content_ids"], [])

    def test_same_content_conflicting_disposition_epoch_bound_or_hash_refuses(self) -> None:
        base = _new_observation(0, bound="0.0271")
        changed_epoch = dict(base.identity_epoch)
        changed_epoch["os_build"] = "different"
        variants = (
            replace(base, sequence=78, attempt_id="alias", receipt_digest=_digest("a"), disposition="ordinary-invalid"),
            replace(base, sequence=78, attempt_id="alias", receipt_digest=_digest("b"), identity_epoch=changed_epoch),
            replace(base, sequence=78, attempt_id="alias", receipt_digest=_digest("c"), exact_bound_lexeme_s="0.0272"),
            replace(base, sequence=78, attempt_id="alias", receipt_digest=_digest("d"), artifact_sha256={"manifest.json": "1" * 64, "instrument_evidence.json": "2" * 64}),
        )
        for variant in variants:
            with self.subTest(receipt=variant.receipt_digest):
                result = _probe(_snapshot((base, variant)))
                self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
                self.assertIn("conflicting_content_classification_or_bytes", result["refusal_reasons"])

    def test_other_epoch_valid_is_excluded_without_self_fit(self) -> None:
        epoch = dict(_parent_artifact()["identity_epoch"])
        epoch["os_build"] = "25F85"
        result = _probe(_snapshot((_new_observation(0, epoch=epoch, bound="0.01"),)))
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")

    def test_observed_epoch_and_estimator_bytes_refuse_before_science(self) -> None:
        epoch = dict(_parent_artifact()["identity_epoch"])
        epoch["hardware_model"] = "Other"
        result = bracketing.probe_calibration_acceptance_trigger(
            _snapshot(),
            observed_identity_epoch=epoch,
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
        with patch.object(bracketing, "_current_estimator_code_sha256", return_value={"x": "0" * 64}):
            result = _probe(_snapshot())
        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
        self.assertEqual(result["observed_triggers"], ["protocol_or_estimator_byte_change"])

    def test_probe_does_not_consult_writer_copied_scalar(self) -> None:
        import scripts.validate_powermetrics_fiducial as writer

        snapshot = _snapshot((_new_observation(0, bound="0.034"),))
        expected = _probe(snapshot)
        with patch.object(writer, "PREFLIGHT_SYSTEMATIC_SCREEN_S", Decimal("999")):
            actual = _probe(snapshot)
        self.assertEqual(actual, expected)

    def test_prefix_omission_and_physical_pin_mismatch_refuse(self) -> None:
        omitted = replace(_snapshot(), observations=tuple(_parent_observations()[1:]))
        self.assertEqual(_probe(omitted)["outcome"], "authentication_or_epoch_refusal")
        mismatched = replace(
            _snapshot(),
            refusal_reasons=("calibration_ledger_head_mismatch",),
        )
        self.assertEqual(_probe(mismatched)["outcome"], "authentication_or_epoch_refusal")

    def test_missing_custody_refuses_when_reauthentication_enabled(self) -> None:
        result = bracketing.probe_calibration_acceptance_trigger(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=True,
        )
        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
        self.assertIn("new_observation_custody_or_physics_invalid", result["refusal_reasons"])


class DecimalDerivationTests(unittest.TestCase):
    def test_n19_golden_reproduces_predictions_and_operatives(self) -> None:
        artifact = _parent_artifact()
        content_by_attempt = {
            row["attempt_id"]: row["content_id"]
            for row in artifact["prior_observation_set"]["observations"]
        }
        members = sorted(
            (
                {
                    "content_id": content_by_attempt[member["member_id"]],
                    "b_fiducial_s": member["b_fiducial_s"],
                }
                for member in artifact["derivation_corpus"]["members"]
            ),
            key=lambda member: member["content_id"],
        )
        derived = bracketing.derive_successor_decimal_derivation(members)
        stats = derived["source_statistics"]
        operatives = derived["ratified_operatives"]
        self.assertEqual(stats["prediction_95_two_draw_s"], "0.008826584887500717")
        self.assertEqual(stats["prediction_99_two_draw_s"], "0.012093166090593858")
        self.assertEqual(operatives["bracket_screen_s"], "0.010818")
        self.assertEqual(operatives["preflight_level_screen_s"], "0.033558756679900")
        self.assertEqual(operatives["max_budgetable_excess_s"], "0.001275166090593858")

    def test_preflight_screen_equals_half_even_quantized_observed_maximum(self) -> None:
        members = [
            {
                "content_id": f"{index:064x}",
                "b_fiducial_s": (
                    "0.0000000000000000"
                    if index <= 9
                    else "0.0000000000000005"
                ),
            }
            for index in range(1, 20)
        ]
        derived = bracketing.derive_successor_decimal_derivation(members)
        self.assertEqual(derived["ratified_operatives"]["bracket_screen_s"], "0.000000")
        self.assertEqual(
            derived["rounding"]["preflight_level_screen"]["source_rule"],
            bracketing.SUCCESSOR_PREFLIGHT_SCREEN_RULE,
        )
        quantized_maximum = Decimal(
            derived["source_statistics"]["maximum_s"]
        ).quantize(Decimal("0.000000000000001"), rounding=bracketing.ROUND_HALF_EVEN)
        self.assertGreater(
            Decimal(derived["source_statistics"]["prediction_95_two_draw_s"]),
            Decimal(derived["source_statistics"]["maximum_s"]),
        )
        self.assertEqual(
            Decimal(derived["ratified_operatives"]["preflight_level_screen_s"]),
            quantized_maximum,
        )

    def test_negative_nonfinite_and_binary_float_inputs_refuse(self) -> None:
        for invalid in ("-0.1", "NaN", "Infinity", 0.1):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    bracketing.derive_successor_decimal_derivation(
                        [
                            {"content_id": "1" * 64, "b_fiducial_s": invalid},
                            {"content_id": "2" * 64, "b_fiducial_s": "0.2"},
                        ]
                    )

    def test_quantile_algorithm_and_d102_pin_are_stable(self) -> None:
        self.assertEqual(
            bracketing.SUCCESSOR_QUANTILE_METHOD,
            "decimal_incomplete_beta_bisection_v1",
        )
        self.assertEqual(
            bracketing.decimal_student_t_quantile("0.995", 18),
            Decimal(
                "2.8784404727135853941939366597008136821841052811738896572381901955286218320347263"
            ),
        )
        bypassed = bracketing.decimal_student_t_quantile(
            "0.995", 18, use_compatibility_pin=False
        )
        self.assertLess(
            abs(
                bypassed
                - Decimal(
                    "2.8784404727386081178058787265646316079030323608869115266837277466388674896049174"
                )
            ),
            Decimal("1e-60"),
        )

    def test_nonpinned_df37_matches_checked_in_independent_reference(self) -> None:
        self.assertLess(
            abs(
                bracketing.decimal_student_t_quantile(
                    "0.995", 37, use_compatibility_pin=False
                )
                - Decimal(
                    "2.71540872154998830130830201963737496013944012008966094097330087289823817193540197518371053830804074116858911770212594477"
                )
            ),
            Decimal("1e-60"),
        )

    def test_quantile_continued_fraction_nonconvergence_is_governed(self) -> None:
        with patch.object(
            bracketing, "SUCCESSOR_CONTINUED_FRACTION_MAX_ITERATIONS", 0
        ):
            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceNumericalRefusal,
                "successor_quantile_continued_fraction_nonconvergence",
            ):
                bracketing.decimal_student_t_quantile(
                    "0.995", 17, use_compatibility_pin=False
                )

    def test_q13_pending_minimum_refuses_n_below_19(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "successor_corpus_below_pending_q13_minimum_19"
        ):
            bracketing.derive_successor_decimal_derivation(
                [
                    {"content_id": "1" * 64, "b_fiducial_s": "0"},
                    {"content_id": "2" * 64, "b_fiducial_s": "0.1"},
                ]
            )


class SuccessorBuilderTests(unittest.TestCase):
    def test_first_range_successor_contains_all_30_plus_trigger(self) -> None:
        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
        build = successor.build_calibration_acceptance_successor(
            snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(build.artifact["derivation_corpus"]["n"], 31)
        self.assertEqual(build.artifact["prospective_rederivation"]["count_trigger"]["next_boundary"], 38)
        self.assertTrue(bracketing._valid_acceptance_bound(build.artifact))
        self.assertEqual(build.successor_probe["outcome"], "accepted_under_active_artifact")
        self.assertEqual(build.successor_probe["refusal_reasons"], [])
        self.assertNotIn("parent_judgment_policy", build.successor_probe)
        self.assertEqual(build.artifact["lineage"]["parent_acceptance_id"], "d079_calibration_acceptance_v2_n19")
        self.assertIn(_digest("live-content-0"), build.artifact["lineage"]["trigger_judgment"]["new_content_ids"])

    def test_repeated_and_shuffled_builds_are_byte_identical(self) -> None:
        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
        first = successor.build_calibration_acceptance_successor(
            snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        shuffled = replace(snapshot, observations=tuple(reversed(snapshot.observations)))
        second = successor.build_calibration_acceptance_successor(
            shuffled,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(first.artifact_bytes, second.artifact_bytes)
        self.assertEqual(first.registry_bytes, second.registry_bytes)
        self.assertEqual(first.head_pin, second.head_pin)

    def test_count_boundary_advances_only_after_crossing(self) -> None:
        extras = tuple(_new_observation(index, bound="0.0271") for index in range(8))
        build = successor.build_calibration_acceptance_successor(
            _snapshot(extras),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(build.artifact["derivation_corpus"]["n"], 38)
        self.assertEqual(build.artifact["prospective_rederivation"]["count_trigger"]["next_boundary"], 76)

    def test_ancestor_boundary_rule_is_validated_from_its_entry(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0, bound="0.02"),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for entry in build.registry["entries"]:
                destination = root / entry["artifact_path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(
                    build.artifact_bytes
                    if entry["acceptance_id"] == build.artifact["acceptance_id"]
                    else (REPO_ROOT / entry["artifact_path"]).read_bytes()
                )
            registry = root / "configs/calibration/calibration_acceptance_registry.json"
            registry.write_bytes(build.registry_bytes)
            with patch.object(
                bracketing,
                "SUCCESSOR_COUNT_BOUNDARY_RULE",
                "future_rule_not_applied_to_ancestors",
            ):
                loaded = bracketing.load_calibration_acceptance_registry(
                    registry, repo_root=root, require_committed=False
                )
            self.assertEqual(
                loaded["entries"][0]["count_boundary_rule"],
                bracketing.GENESIS_COUNT_BOUNDARY_RULE,
            )

    def test_systematic_and_unresolved_never_build(self) -> None:
        cases = (
            _snapshot((_new_observation(0, disposition="systematic-invalid"),)),
            _snapshot((replace(_new_observation(0, disposition="abandoned"), content_id=None, artifact_sha256={}, exact_bound_lexeme_s=None),)),
        )
        for snapshot in cases:
            with self.subTest(head=snapshot.head_digest):
                with self.assertRaisesRegex(ValueError, "does not require a successor"):
                    successor.build_calibration_acceptance_successor(
                        snapshot,
                        observed_identity_epoch=_parent_artifact()["identity_epoch"],
                        require_committed_registry=False,
                        verify_custody=False,
                    )

    def test_no_content_closure_does_not_brick_range_successor(self) -> None:
        abandoned = replace(
            _new_observation(0, disposition="abandoned"),
            content_id=None,
            artifact_sha256={},
            exact_bound_lexeme_s=None,
        )
        build = successor.build_calibration_acceptance_successor(
            _snapshot((abandoned, _new_observation(1, bound="0.02"))),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(
            build.artifact["prior_observation_set"]["noncontent_attempts"],
            [
                {
                    "attempt_id": abandoned.attempt_id,
                    "closure_sequence": abandoned.sequence,
                    "receipt_digest": abandoned.receipt_digest,
                    "disposition": "abandoned",
                    "custody_locator": abandoned.custody_locator,
                }
            ],
        )
        self.assertEqual(
            build.successor_probe["outcome"], "accepted_under_active_artifact"
        )

    def test_real_successor_probe_rejection_blocks_build(self) -> None:
        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
        parent_probe = _probe(snapshot)
        rejected = {
            "outcome": "authentication_or_epoch_refusal",
            "refusal_reasons": ["synthetic_real_probe_rejection"],
        }
        with patch.object(
            successor,
            "probe_calibration_acceptance_trigger",
            side_effect=(parent_probe, rejected),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "successor_real_probe_refused:authentication_or_epoch_refusal",
            ):
                successor.build_calibration_acceptance_successor(
                    snapshot,
                    observed_identity_epoch=_parent_artifact()["identity_epoch"],
                    require_committed_registry=False,
                    verify_custody=False,
                )

    def test_nonterminal_or_uncommitted_head_refuses(self) -> None:
        snapshot = _snapshot((_new_observation(0),))
        for changed in (
            replace(snapshot, committed_head_digest="0" * 64),
            replace(snapshot, refusal_reasons=("calibration_ledger_pending",)),
            replace(snapshot, receipts=(*snapshot.receipts[:-1], {**snapshot.receipts[-1], "event": "reservation"})),
        ):
            with self.subTest(changed=changed.refusal_reasons):
                with self.assertRaisesRegex(ValueError, "committed terminal"):
                    successor.build_calibration_acceptance_successor(
                        changed,
                        observed_identity_epoch=_parent_artifact()["identity_epoch"],
                        require_committed_registry=False,
                        verify_custody=False,
                    )

    def test_failed_publication_precondition_mutates_neither_destination(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry, _ = _init_publication_repo(root)
            artifact = root / build.artifact_path
            artifact.write_text("occupied", encoding="utf-8")
            before = registry.read_bytes()
            with self.assertRaises(ValueError):
                successor.publish_successor(
                    build,
                    artifact_destination=artifact,
                    registry_destination=registry,
                    expected_registry_bytes=before,
                    repo_root=root,
                )
            self.assertEqual(artifact.read_text(encoding="utf-8"), "occupied")
            self.assertEqual(registry.read_bytes(), before)

    def test_publication_co_lands_both_paths_and_verifies_committed_mode(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        for prepublish_artifact in (False, True):
            with self.subTest(prepublish_artifact=prepublish_artifact):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    registry, _ = _init_publication_repo(root)
                    artifact = root / build.artifact_path
                    if prepublish_artifact:
                        artifact.write_bytes(build.artifact_bytes)
                    before = registry.read_bytes()
                    verification = successor.publish_successor(
                        build,
                        artifact_destination=artifact,
                        registry_destination=registry,
                        expected_registry_bytes=before,
                        repo_root=root,
                    )
                    self.assertEqual(artifact.read_bytes(), build.artifact_bytes)
                    self.assertEqual(registry.read_bytes(), build.registry_bytes)
                    self.assertTrue(verification["committed_mode_verified"])
                    committed_paths = subprocess.run(
                        [
                            "git",
                            "diff-tree",
                            "--no-commit-id",
                            "--name-only",
                            "-r",
                            "HEAD",
                        ],
                        cwd=root,
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.splitlines()
                    self.assertEqual(
                        set(committed_paths),
                        {
                            build.artifact_path,
                            "configs/calibration/calibration_acceptance_registry.json",
                        },
                    )
                    loaded = bracketing.load_calibration_acceptance_registry(
                        registry, repo_root=root, require_committed=True
                    )
                    self.assertIsNotNone(loaded)
                    self.assertEqual(
                        bracketing._active_registry_entry(loaded)["acceptance_id"],
                        build.artifact["acceptance_id"],
                    )

    def test_uncommitted_registry_replacement_names_missing_commit_everywhere(self) -> None:
        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
        build = successor.build_calibration_acceptance_successor(
            snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry, _ = _init_publication_repo(root)
            artifact = root / build.artifact_path
            artifact.write_bytes(build.artifact_bytes)
            registry.write_bytes(build.registry_bytes)

            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceRegistryRefusal,
                "acceptance_registry_missing_commit",
            ):
                bracketing.load_calibration_acceptance_registry(
                    registry, repo_root=root, require_committed=True
                )
            probe = bracketing.probe_calibration_acceptance_trigger(
                snapshot,
                observed_identity_epoch=_parent_artifact()["identity_epoch"],
                registry_path=registry,
                repo_root=root,
                require_committed_registry=True,
                verify_custody=False,
            )
            self.assertEqual(
                probe["refusal_reasons"], ["acceptance_registry_missing_commit"]
            )
            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceRegistryRefusal,
                "acceptance_registry_missing_commit",
            ):
                successor.build_calibration_acceptance_successor(
                    snapshot,
                    observed_identity_epoch=_parent_artifact()["identity_epoch"],
                    registry_path=registry,
                    repo_root=root,
                    require_committed_registry=True,
                    verify_custody=False,
                )

    def test_dry_run_build_writes_nothing(self) -> None:
        before = {path: path.read_bytes() for path in (ACCEPTANCE_PATH, REGISTRY_PATH)}
        successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(before, {path: path.read_bytes() for path in before})


if __name__ == "__main__":
    unittest.main()
