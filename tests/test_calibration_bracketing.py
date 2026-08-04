"""Defect-shaped regressions for claim-bearing calibration bracketing."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import tempfile
from types import MappingProxyType
import unittest
from unittest.mock import patch

from joulewise.calibration_bracketing import (
    CalibrationCandidate,
    _canonical_sha256,
    _valid_acceptance_bound,
    evaluate_calibration_bracket as _evaluate_calibration_bracket,
    load_calibration_acceptance_bound,
    load_calibration_candidate,
)
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    content_id_from_artifact_hashes,
)
from joulewise.powermetrics_fiducial import (
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    PROTOCOL_V3_SHA256,
    PULSE_COUNT,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
)
from joulewise.schemas import CalibrationBracketingPolicy


def _fixture_snapshot(
    candidates: list[CalibrationCandidate],
    *,
    extra_observations: tuple[LedgerObservation, ...] = (),
) -> tuple[CalibrationLedgerSnapshot, list[CalibrationCandidate]]:
    """Build an explicitly synthetic authenticated snapshot for unit tests."""

    normalized: list[CalibrationCandidate] = []
    observations: list[LedgerObservation] = []
    for index, candidate in enumerate(candidates):
        attempt_id = candidate.attempt_id or f"fixture-attempt-{index}-{candidate.relative_path}"
        hashes = {
            "manifest.json": candidate.manifest_sha256,
            "instrument_evidence.json": candidate.evidence_sha256,
        }
        content_id = candidate.content_id or content_id_from_artifact_hashes(hashes)
        assert content_id is not None
        digest = candidate.ledger_receipt_digest or hashlib.sha256(
            attempt_id.encode("utf-8")
        ).hexdigest()
        bound = str(candidate.b_fiducial_s)
        normalized_candidate = replace(
            candidate,
            attempt_id=attempt_id,
            content_id=content_id,
            ledger_receipt_digest=digest,
        )
        normalized.append(normalized_candidate)
        observations.append(
            LedgerObservation(
                sequence=index + 2,
                receipt_digest=digest,
                attempt_id=attempt_id,
                content_id=content_id,
                artifact_sha256=MappingProxyType(hashes),
                identity_epoch=MappingProxyType(
                    {
                        field: candidate.bindings.get(field)
                        for field in (
                            "os_build",
                            "hardware_model",
                            "power_policy",
                            "sampling_interval_ms",
                            "estimator_revision",
                            "pulse_protocol_id",
                        )
                    }
                ),
                t1_bindings=MappingProxyType(
                    {field: candidate.bindings.get(field) for field in V2_BINDING_FIELDS}
                ),
                capture_wall_time_s=str(candidate.capture_wall_time_s),
                exact_bound_lexeme_s=bound,
                disposition="valid",
                custody_locator=candidate.relative_path,
            )
        )
    all_observations = (*observations, *extra_observations)
    return (
        CalibrationLedgerSnapshot(
            ledger_schema=LEDGER_SCHEMA,
            ledger_path=Path("fixture-ledger.jsonl"),
            head_sequence=len(all_observations) * 2,
            head_digest=(
                all_observations[-1].receipt_digest
                if all_observations
                else GENESIS_DIGEST
            ),
            receipts=(),
            observations=tuple(all_observations),
            refusal_reasons=(),
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
        ),
        normalized,
    )


def evaluate_calibration_bracket(
    candidates: list[CalibrationCandidate], **kwargs: object
) -> tuple[dict, tuple[str, ...]]:
    snapshot, normalized = _fixture_snapshot(list(candidates))
    return _evaluate_calibration_bracket(
        normalized,
        ledger_snapshot=snapshot,
        _allow_unissued_fixture=True,
        **kwargs,
    )


class CalibrationBracketingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bindings = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        self.bindings.update(
            {
                "hardware_model": "Mac15,9",
                "os_build": "25F84",
                "sampling_interval_ms": 100,
                "pulse_protocol_id": PROTOCOL_ID,
                "power_policy": "ac_high_power",
                "estimator_revision": RESIDUAL_REGION_METHOD,
                "protocol_sha256": PROTOCOL_V3_SHA256,
            }
        )
        self.policy = CalibrationBracketingPolicy(
            require_bracket=True,
            calibration_bracket_max_drift_s=0.010,
        )

    def test_unissued_fixture_cannot_license_default_claim_evaluation(self) -> None:
        snapshot, candidates = _fixture_snapshot(
            [
                self.candidate("pre", 99.0, "0.025"),
                self.candidate("post", 111.0, "0.026"),
            ]
        )
        result, reasons = _evaluate_calibration_bracket(
            candidates,
            window_start_s=1_000.0,
            window_end_s=1_100.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
        )

        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(
            result["acceptance"]["freshness"]["reason"],
            "acceptance_artifact_unissued_fixture",
        )

    def candidate(
        self,
        name: str,
        capture_s: float,
        bound_s: Decimal | str | float,
        *,
        protocol_id: str = PROTOCOL_ID,
        bindings: dict | None = None,
    ) -> CalibrationCandidate:
        corpus_alias = {
            "pre": "20260722T145535-e941c821",
            "post": "20260722T194118-9dc0749d",
            "pre-v3": "20260722T214220-1acdbbc0",
            "post-v3": "20260722T215127-eeef661a",
        }
        new_observation = name in {
            "range-expander",
            "current-pre",
            "current-post",
            "window-b-new-systematic-pre",
            "window-b-post",
        }
        manifest_sha256 = (
            hashlib.sha256(f"manifest:{name}".encode()).hexdigest()
            if new_observation
            else "ab" * 32
        )
        evidence_sha256 = (
            hashlib.sha256(f"evidence:{name}".encode()).hexdigest()
            if new_observation
            else "cd" * 32
        )
        return CalibrationCandidate(
            relative_path=(
                f"instrument_validation/{corpus_alias.get(name, name)}"
            ),
            manifest_sha256=manifest_sha256,
            evidence_sha256=evidence_sha256,
            protocol_id=protocol_id,
            capture_wall_time_s=capture_s,
            b_fiducial_s=bound_s,
            bindings=self.bindings if bindings is None else bindings,
        )

    def test_claim_window_passes_and_embeds_never_zero_allowance_once(self) -> None:
        # Exact H2 defect shape: a single sample maximum used to stand in for
        # temporal instrument stability. Two causal endpoints now bracket it.
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.027)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["endpoint_max_b_fiducial_s"], 0.027)
        self.assertEqual(result["calibration_drift_allowance_s"], 0.010818)
        self.assertEqual(result["b_fiducial_s"], 0.037818)

    def test_missing_post_bracket_refuses_claim(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))

    def test_claim_bracket_refuses_v2_only_candidates_but_accepts_v3_pair(self) -> None:
        # K4 defect shape: fresh, binding-matched v2 validation artifacts are
        # still reduction evidence, but do not carry v3's governed 95/95
        # claim calibration. Replacing only the protocol with v3 passes.
        v2 = [
            self.candidate("pre-v2", 99.0, 0.020, protocol_id=PROTOCOL_V2_ID),
            self.candidate("post-v2", 111.0, 0.027, protocol_id=PROTOCOL_V2_ID),
        ]
        result, reasons = evaluate_calibration_bracket(
            v2,
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))

        v3 = [
            self.candidate("pre-v3", 99.0, 0.020),
            self.candidate("post-v3", 111.0, 0.027),
        ]
        result, reasons = evaluate_calibration_bracket(
            v3,
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")

    def test_bracket_drift_over_d079_budget_refuses_claim(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.035)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertAlmostEqual(result["drift_s"], 0.015)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))

    def test_d079_budgeted_drift_above_obsolete_cliff_passes_with_allowance(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.031)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(
            result["acceptance"]["drift"]["status"], "passed_budgeted"
        )
        self.assertEqual(result["calibration_drift_allowance_s"], 0.011)
        self.assertEqual(result["b_fiducial_s"], 0.042)
        self.assertEqual(
            result["policy"]["calibration_bracket_max_drift_s_role"],
            "legacy_obsolete_not_an_acceptance_comparator",
        )

    def test_d079_drift_beyond_budget_refuses_with_recorded_basis(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.020), self.candidate("post", 111.0, 0.035)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))
        self.assertEqual(
            result["acceptance"]["drift"]["status"], "budget_exceeded"
        )

    def test_d102_decimal_boundary_sweep_is_exact_and_inclusive(self) -> None:
        cases = (
            ("exact-screen", "0.030818", "passed", "0.010818"),
            (
                "exact-ceiling",
                "0.032093166090593858",
                "passed",
                "0.012093166090593858",
            ),
            (
                "one-decimal-unit-beyond",
                "0.032093166090593859",
                "failed",
                "0.012093166090593859",
            ),
        )
        for name, post, status, observed in cases:
            with self.subTest(name=name):
                result, reasons = evaluate_calibration_bracket(
                    [
                        self.candidate("pre", 99.0, "0.020"),
                        self.candidate("post", 111.0, post),
                    ],
                    window_start_s=100.0,
                    window_end_s=110.0,
                    bindings=self.bindings,
                    policy=self.policy,
                )
                self.assertEqual(result["status"], status)
                self.assertEqual(
                    result["acceptance"]["drift"]["observed_s"], observed
                )
                self.assertEqual(
                    reasons,
                    ()
                    if status == "passed"
                    else ("instrument_calibration_mismatch",),
                )

        exact_ceiling = float(Decimal("0.032093166090593858"))
        one_binary64_ulp_beyond = math.nextafter(exact_ceiling, math.inf)
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, 0.020),
                self.candidate("post", 111.0, one_binary64_ulp_beyond),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))
        self.assertGreater(
            Decimal(result["acceptance"]["drift"]["observed_s"]),
            Decimal("0.012093166090593858"),
        )

        zero, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.025"),
                self.candidate("post", 111.0, "0.025"),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(zero["acceptance"]["drift"]["observed_s"], "0.000")
        self.assertEqual(zero["acceptance"]["allowance"]["value_s"], "0.010818")

    def test_t1_mismatched_candidate_remains_ineligible_under_d079_v2(self) -> None:
        mismatched = dict(self.bindings)
        mismatched["power_policy"] = "configs/campaign_policies/quiet_mac.json"
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, 0.020),
                self.candidate("post-mismatch", 111.0, 0.020, bindings=mismatched),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(result["pre"])
        self.assertIsNone(result["post"])
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))
        self.assertEqual(result["acceptance"]["freshness"]["status"], "fresh")

    def test_window_a_t1_mismatch_shape_still_cannot_form_bracket(self) -> None:
        window_a_post_bindings = dict(self.bindings)
        window_a_post_bindings["power_policy"] = (
            "configs/campaign_policies/quiet_mac_p2_production.json"
        )
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("window-a-pre", 99.0, 0.022),
                self.candidate(
                    "window-a-deviation-post",
                    111.0,
                    0.024,
                    bindings=window_a_post_bindings,
                ),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(result["pre"])
        self.assertIsNone(result["post"])
        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))

    def test_identity_epoch_violation_refuses_stale_acceptance_bound(self) -> None:
        changed_epoch = dict(self.bindings)
        changed_epoch["os_build"] = "25F85"
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, 0.020, bindings=changed_epoch),
                self.candidate("post", 111.0, 0.021, bindings=changed_epoch),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=changed_epoch,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(
            reasons, ("calibration_acceptance_bound_stale",)
        )
        self.assertEqual(result["acceptance"]["freshness"]["status"], "stale")

    def test_f1_freshness_uses_six_field_epoch_not_full_t1(self) -> None:
        changed = dict(self.bindings)
        changed["mlx_version"] = "different-but-exactly-t1-matched"
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.025", bindings=changed),
                self.candidate("post", 111.0, "0.026", bindings=changed),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=changed,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["acceptance"]["freshness"]["stale_fields"], [])

    def test_f2_estimator_digest_closure_is_exactly_four_modules(self) -> None:
        artifact = load_calibration_acceptance_bound()
        self.assertIsNotNone(artifact)
        self.assertEqual(
            set(artifact["prospective_rederivation"]["estimator_code_sha256"]),
            {
                "joulewise/powermetrics_fiducial.py",
                "joulewise/uncertainty_evidence.py",
                "joulewise/adapters/powermetrics.py",
                "joulewise/reduce.py",
            },
        )

    def test_systematic_preflight_level_failure_is_never_budgeted(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [self.candidate("pre", 99.0, 0.034), self.candidate("post", 111.0, 0.023)],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))
        self.assertEqual(result["acceptance"]["preflight"]["status"], "failed")
        self.assertEqual(
            result["acceptance"]["preflight"]["failure_class"],
            "systematic_not_budgetable",
        )
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            ["new_systematic_failure_challenges_preflight_screen"],
        )
        self.assertIsNone(result["calibration_drift_allowance_s"])

    def test_window_b_systematic_failure_precedes_rederivation_staleness(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate(
                    "window-b-new-systematic-pre",
                    99.0,
                    "0.035435840879704805",
                ),
                self.candidate("window-b-post", 111.0, "0.023"),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("instrument_calibration_mismatch",))
        self.assertEqual(result["acceptance"]["preflight"]["status"], "failed")
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            [
                "new_valid_same_identity_capture_expands_observed_range",
                "new_systematic_failure_challenges_preflight_screen",
            ],
        )

    def test_unselected_same_identity_range_expander_stales_artifact(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [
                replace(
                    self.candidate("range-expander", 99.0, "0.022"),
                    relative_path=(
                        "/authenticated-custody/another-root/"
                        "instrument_validation/range-expander"
                    ),
                ),
                self.candidate("current-pre", 199.0, "0.025"),
                self.candidate("current-post", 211.0, "0.026"),
            ],
            window_start_s=200.0,
            window_end_s=210.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(result["acceptance"]["freshness"]["status"], "stale")
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "candidate_set_boundary"
            ],
            "authenticated_calibration_ledger_snapshot_only",
        )
        self.assertFalse(
            result["acceptance"]["prospective_rederivation"][
                "global_runs_root_scan"
            ]
        )
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            ["new_valid_same_identity_capture_expands_observed_range"],
        )
        self.assertTrue(
            result["pre"]["relative_path"].endswith("current-pre")
        )
        self.assertTrue(
            result["post"]["relative_path"].endswith("current-post")
        )

    def test_off_ledger_candidate_refuses_even_beside_registered_pair(self) -> None:
        candidates = [
            self.candidate("pre", 99.0, "0.025"),
            self.candidate("post", 111.0, "0.026"),
        ]
        snapshot, registered = _fixture_snapshot(candidates)
        off_ledger = replace(
            self.candidate("unregistered-copy", 105.0, "0.0255"),
            attempt_id="off-ledger",
            content_id="f" * 64,
            ledger_receipt_digest="e" * 64,
        )
        result, reasons = _evaluate_calibration_bracket(
            [*registered, off_ledger],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))

        _result, omitted_reasons = _evaluate_calibration_bracket(
            registered[:1],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(
            omitted_reasons,
            ("calibration_ledger_off_ledger_artifact",),
        )

    def test_prior_set_subtraction_does_not_treat_known_holdout_as_new(self) -> None:
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.021"),
                self.candidate("post", 111.0, "0.026"),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
        )
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            [],
        )

    def test_corpus_doubling_counts_38_total_valid_distinct_observations(self) -> None:
        candidates = [
            self.candidate("current-pre", 99.0, "0.025"),
            self.candidate("current-post", 111.0, "0.026"),
        ]
        for index in range(36):
            candidates.append(
                replace(
                    self.candidate(
                        f"extra-{index}", 120.0 + index, "0.025"
                    ),
                    manifest_sha256=hashlib.sha256(
                        f"extra-manifest-{index}".encode()
                    ).hexdigest(),
                    evidence_sha256=hashlib.sha256(
                        f"extra-evidence-{index}".encode()
                    ).hexdigest(),
                )
            )
        snapshot, registered = _fixture_snapshot(candidates)
        result, reasons = _evaluate_calibration_bracket(
            registered,
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
            ["corpus_doubles_from_19_to_38"],
        )

    def test_acceptance_artifact_rederives_from_decimal_member_table(self) -> None:
        artifact = load_calibration_acceptance_bound()
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact["derivation_corpus"]["n"], 19)
        self.assertEqual(
            artifact["decimal_derivation"]["source_statistics"]["range_s"],
            "0.010817749309353528",
        )
        tampered = json.loads(json.dumps(artifact))
        tampered["derivation_corpus"]["members"][0]["b_fiducial_s"] = "0.030"
        tampered["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in tampered.items()
                if key != "derivation_sha256"
            }
        )
        self.assertFalse(_valid_acceptance_bound(tampered))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tampered.json"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            self.assertIsNone(load_calibration_acceptance_bound(path))

    def test_rekeyed_self_consistent_artifact_is_not_authenticated(self) -> None:
        artifact = load_calibration_acceptance_bound()
        self.assertIsNotNone(artifact)
        rekeyed = json.loads(json.dumps(artifact))
        rekeyed["identity_epoch"]["os_build"] = "25F85"
        rekeyed["prior_observation_set"]["epoch_catalog"]["d079_epoch"][
            "os_build"
        ] = "25F85"
        rekeyed["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in rekeyed.items()
                if key != "derivation_sha256"
            }
        )
        # The arithmetic document remains self-consistent; only the checked-in
        # byte pin supplies the missing authority and must reject it.
        self.assertTrue(_valid_acceptance_bound(rekeyed))
        changed = dict(self.bindings)
        changed["os_build"] = "25F85"
        result, reasons = evaluate_calibration_bracket(
            [
                self.candidate("pre", 99.0, "0.025", bindings=changed),
                self.candidate("post", 111.0, "0.026", bindings=changed),
            ],
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=changed,
            policy=self.policy,
            acceptance_bound=rekeyed,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(result["acceptance"]["freshness"]["status"], "stale")

    def test_estimator_module_byte_change_stales_artifact_at_load(self) -> None:
        with patch(
            "joulewise.calibration_bracketing._current_estimator_code_sha256",
            return_value={
                "joulewise/powermetrics_fiducial.py": "0" * 64,
                "joulewise/uncertainty_evidence.py": "1" * 64,
                "joulewise/adapters/powermetrics.py": "2" * 64,
                "joulewise/reduce.py": "3" * 64,
            },
        ):
            self.assertIsNotNone(load_calibration_acceptance_bound())
            result, reasons = evaluate_calibration_bracket(
                [
                    self.candidate("pre", 99.0, "0.025"),
                    self.candidate("post", 111.0, "0.026"),
                ],
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
            )
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertIn(
            "protocol_or_estimator_byte_change",
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
        )

    def test_hash_rekeyed_candidate_cannot_bypass_binding_authentication(self) -> None:
        # H2 validity defect shape: rewriting a binding and then rehashing the
        # evidence/manifest must not create an authenticated bracket endpoint.
        bindings = dict(self.bindings)
        bindings.update(
            {
                "anchor_method_version": (
                    "powermetrics_native_second_censored_intersection_v1"
                ),
                "pulse_protocol_id": PROTOCOL_ID,
                "protocol_sha256": PROTOCOL_V3_SHA256,
                "estimator_revision": RESIDUAL_REGION_METHOD,
            }
        )
        canonical = json.dumps(
            bindings,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        events = b'{"timestamp_s":99.0}\n'
        raw = b"authenticated-by-patched-physics"
        evidence = {
            "schema_version": "joulewise.instrument_evidence.v1",
            "protocol_id": PROTOCOL_ID,
            "pulse_count": PULSE_COUNT,
            "anchor_method_version": bindings["anchor_method_version"],
            "residual_region_method": RESIDUAL_REGION_METHOD,
            "residual_region_coverage_assumption": "complete accepted region",
            "residual_region_coverage_resolution_s": (
                REGION_COVERAGE_RESOLUTION_S
            ),
            "capture_wall_time_s": 99.0,
            "b_fiducial_s": 0.02,
            "max_age_s": MAX_AGE_S,
            "bindings": bindings,
            "binding_evidence": {
                "schema_version": "joulewise.instrument_binding_evidence.v1",
                "binding_vector_sha256": hashlib.sha256(canonical).hexdigest(),
                "powermetrics_binary": {
                    "path": "/usr/bin/powermetrics",
                    "sha256": bindings["powermetrics_sha256"],
                },
                "power_policy": {"id": bindings["power_policy"]},
            },
            "artifact_sha256": {
                "events.jsonl": hashlib.sha256(events).hexdigest(),
                "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "instrument_validation" / "candidate"
            (directory / "raw").mkdir(parents=True)
            (directory / "events.jsonl").write_bytes(events)
            (directory / "raw/powermetrics.plist").write_bytes(raw)

            def write_evidence_and_manifest() -> None:
                evidence_raw = json.dumps(evidence, sort_keys=True).encode()
                (directory / "instrument_evidence.json").write_bytes(evidence_raw)
                artifacts = {
                    "events.jsonl": hashlib.sha256(events).hexdigest(),
                    "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
                    "instrument_evidence.json": hashlib.sha256(
                        evidence_raw
                    ).hexdigest(),
                }
                (directory / "manifest.json").write_text(
                    json.dumps(
                        {
                            "schema_version": (
                                "joulewise.instrument_validation_manifest.v1"
                            ),
                            "protocol_id": PROTOCOL_ID,
                            "pulse_count": PULSE_COUNT,
                            "artifacts": artifacts,
                        }
                    )
                )

            write_evidence_and_manifest()
            with patch(
                "joulewise.calibration_bracketing.verify_stored_evidence_physics",
                return_value=0.02,
            ):
                candidate = load_calibration_candidate(
                    directory, runs_root=root
                )
                self.assertIsNotNone(candidate)
                self.assertEqual(candidate.b_fiducial_s, "0.02")
                evidence["bindings"]["hardware_model"] = "tampered-model"
                write_evidence_and_manifest()
                self.assertIsNone(
                    load_calibration_candidate(directory, runs_root=root)
                )


if __name__ == "__main__":
    unittest.main()
