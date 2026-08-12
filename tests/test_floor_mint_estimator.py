from __future__ import annotations

import copy
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import detection_floor
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.detection_floor import (
    COMMON_MODE_ESTIMATOR_ID,
    METHOD_ID,
    comparative_false_effect_floor,
    two_shared_edge_common_mode_registration,
)
from joulewise import floor_mint_estimator as estimator
from scripts import mint_floor_artifact as mint1
from tests.test_mint_floor_artifact_generalized import seven_b_components


ACCEPTANCE_SHA256 = "a" * 64
ALLOWANCE = {
    "observed_drift_s": "0.001000",
    "allowance_rule": "max(observed_drift_s,0.010818)",
    "bracket_screen_s": "0.010818",
    "applied_allowance_s": "0.010818",
    "allowance_embedding_count": 1,
}
ACCEPTANCE = {
    "acceptance_id": "d079_calibration_acceptance_v2_n19",
    "derivation_sha256": "d" * 64,
    "schema_version": "joulewise.calibration_acceptance_bound.v2",
}


def calibration_basis() -> dict:
    return {
        "calibration_scope": "production_window",
        "acceptance_selection": "issued_d116_artifact_only",
        "issued_acceptance": {
            "acceptance_id": ACCEPTANCE["acceptance_id"],
            "path": "configs/calibration/calibration_acceptance_d079_v2.json",
            "artifact_sha256": ACCEPTANCE_SHA256,
            "derivation_sha256": ACCEPTANCE["derivation_sha256"],
            "schema_version": ACCEPTANCE["schema_version"],
        },
        "allowance_rule": "max(observed_drift_s,0.010818)",
        "allowance_embedding_count": 1,
        "component_composition": "componentwise_max_never_sum.v1",
    }


def selection(spec_cell: dict) -> str:
    return estimator.selection_from_authenticated_spec(
        spec_cell,
        calibration_acceptance=ACCEPTANCE,
        calibration_acceptance_sha256=ACCEPTANCE_SHA256,
        calibration_allowance_projection=ALLOWANCE,
        declared_calibration_scope="production_window",
    )


def registered_component():
    _plan, _absolute, comparative = seven_b_components()
    spec_cell = copy.deepcopy(comparative.spec_cell)
    spec_cell.update(
        {
            "estimator": COMMON_MODE_ESTIMATOR_ID,
            "estimator_registration": (
                two_shared_edge_common_mode_registration()
            ),
            "calibration_basis": calibration_basis(),
        }
    )
    spec = copy.deepcopy(comparative.spec)
    target = next(
        index
        for index, cell in enumerate(spec["cells"])
        if cell["cell_id"] == spec_cell["cell_id"]
    )
    spec["cells"][target] = spec_cell
    return replace(comparative, spec_cell=spec_cell, spec=spec)


def recompute_kwargs(component, root: Path = Path("/authenticated/root")) -> dict:
    return {
        "core": mint1,
        "comparative_component": component,
        "runs_root": root,
        "calibration_acceptance": ACCEPTANCE,
        "calibration_acceptance_sha256": ACCEPTANCE_SHA256,
        "calibration_allowance_projection": ALLOWANCE,
        "declared_calibration_scope": "production_window",
        "calibration_ledger_snapshot": SimpleNamespace(valid=True),
        "calibration_bracket_binding": {"binding": "authenticated"},
    }


class SelectionTests(unittest.TestCase):
    def test_public_surface_is_limited_to_three_functions(self) -> None:
        self.assertEqual(
            estimator.__all__,
            [
                "selection_from_authenticated_spec",
                "recompute_comparative_estimate",
                "bind_v2_floor_artifact_evidence",
            ],
        )

    def test_common_mode_private_helper_signatures_and_parameter_sha_are_pinned(
        self,
    ) -> None:
        estimator._assert_common_mode_contract()
        self.assertEqual(
            detection_floor.COMMON_MODE_PARAMETER_SHA256,
            estimator._CANONICAL_COMMON_MODE_PARAMETER_SHA256,
        )

    def test_absent_estimator_selects_default(self) -> None:
        self.assertEqual(selection({}), estimator._DEFAULT_PATH)

    def test_explicit_default_selects_default(self) -> None:
        self.assertEqual(
            selection({"estimator": METHOD_ID}), estimator._DEFAULT_PATH
        )

    def test_shipped_fallback_shape_basis_without_estimator_selects_default(
        self,
    ) -> None:
        self.assertEqual(
            selection({"calibration_basis": calibration_basis()}),
            estimator._DEFAULT_PATH,
        )

    def test_registered_common_mode_selects_only_registered_path(self) -> None:
        self.assertEqual(
            selection(
                {
                    "estimator": COMMON_MODE_ESTIMATOR_ID,
                    "estimator_registration": (
                        two_shared_edge_common_mode_registration()
                    ),
                    "calibration_basis": calibration_basis(),
                }
            ),
            estimator._COMMON_MODE_PATH,
        )

    def test_unknown_estimator_refuses(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported authenticated"):
            selection({"estimator": "attacker.estimator.v1"})

    def test_pending_candidate_refuses_at_mint_time(self) -> None:
        with self.assertRaisesRegex(ValueError, "pending common-mode"):
            selection(
                {
                    "estimator": COMMON_MODE_ESTIMATOR_ID,
                    "estimator_registration": {
                        "estimator_id": COMMON_MODE_ESTIMATOR_ID,
                        "status": "candidate_pending_floor_commonmode_01",
                    },
                    "calibration_basis": calibration_basis(),
                }
            )

    def test_malformed_full_registration_never_falls_back(self) -> None:
        registration = two_shared_edge_common_mode_registration()
        registration["parameter_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "not canonical"):
            selection(
                {
                    "estimator": COMMON_MODE_ESTIMATOR_ID,
                    "estimator_registration": registration,
                    "calibration_basis": calibration_basis(),
                }
            )

    def test_registration_without_common_mode_estimator_refuses(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot authorize"):
            selection(
                {
                    "estimator_registration": (
                        two_shared_edge_common_mode_registration()
                    )
                }
            )

    def test_malformed_basis_on_default_path_refuses_not_falls_back(self) -> None:
        basis = calibration_basis()
        basis["allowance_embedding_count"] = 2
        with self.assertRaisesRegex(ValueError, "policy literals"):
            selection({"calibration_basis": basis})

    def test_basis_must_match_authenticated_acceptance_fields(self) -> None:
        attacks = {
            "acceptance_id": "forged",
            "artifact_sha256": "f" * 64,
            "derivation_sha256": "e" * 64,
            "schema_version": "forged.schema",
        }
        for field, value in attacks.items():
            with self.subTest(field=field):
                basis = calibration_basis()
                basis["issued_acceptance"][field] = value
                with self.assertRaisesRegex(ValueError, "producer acceptance"):
                    selection({"calibration_basis": basis})

    def test_allowance_projection_must_equal_max_rule(self) -> None:
        attacked = {**ALLOWANCE, "applied_allowance_s": "0.010817"}
        with self.assertRaisesRegex(ValueError, r"max\(observed_drift_s"):
            estimator.selection_from_authenticated_spec(
                {"calibration_basis": calibration_basis()},
                calibration_acceptance=ACCEPTANCE,
                calibration_acceptance_sha256=ACCEPTANCE_SHA256,
                calibration_allowance_projection=attacked,
                declared_calibration_scope="production_window",
            )


class RecomputationTests(unittest.TestCase):
    def test_default_recomputation_preserves_pinned_core_result(self) -> None:
        _plan, _absolute, comparative = seven_b_components()
        result = estimator.recompute_comparative_estimate(
            **recompute_kwargs(comparative)
        )
        blocks, deltas = mint1._comparative_blocks(comparative)
        expected = mint1.comparative_false_effect_floor(
            deltas, admissible_half_widths_j=comparative.widths_j
        )
        self.assertEqual(result.estimator_path, estimator._DEFAULT_PATH)
        self.assertEqual(result.estimate, expected)
        self.assertEqual(result.comparative_blocks, tuple(blocks))
        self.assertEqual(result.exact_widths_j, comparative.widths_j)
        self.assertNotIn("estimator", result.comparative_record)
        self.assertNotIn("estimator_registration", result.comparative_record)

    def test_spec_blocks_must_flatten_to_authenticated_member_order(self) -> None:
        _plan, _absolute, comparative = seven_b_components()
        with self.assertRaisesRegex(ValueError, "flatten"):
            estimator.recompute_comparative_estimate(
                **recompute_kwargs(
                    replace(
                        comparative,
                        members=(
                            comparative.members[1],
                            comparative.members[0],
                            *comparative.members[2:],
                        ),
                    )
                )
            )

    def test_registered_recomputation_never_calls_default_floor(self) -> None:
        component = registered_component()
        bracket = {
            "status": "passed",
            "endpoint_max_b_fiducial_s": 0.02,
            "calibration_drift_allowance_s": 0.010818,
            "b_fiducial_s": 0.030818,
            "operative_b_fiducial_s": 0.030818,
            "acceptance": {
                "allowance": {
                    "rule": "max(observed_drift_s,bracket_screen_s)",
                    "value_s": "0.010818",
                    "embedding_count": 1,
                    "embedded_in": "b_fiducial_s",
                }
            },
        }
        session = SimpleNamespace(
            ready=True,
            refusal_reasons=(),
            calibration_bracket=bracket,
            operative_fiducial_bound_s=0.030818,
        )
        common_estimate = comparative_false_effect_floor(
            [member.metric_value_j for member in ()] or [0.0, 0.0],
            admissible_half_widths_j=[0.125, 0.125],
        )

        def common_floor(deltas, _inputs, **_kwargs):
            return comparative_false_effect_floor(
                deltas,
                admissible_half_widths_j=[0.125] * len(deltas),
            )

        with (
            V2AuthenticationReadSession(),
            mock.patch.object(
                estimator, "_assert_common_mode_contract", return_value=None
            ),
            mock.patch.object(
                estimator,
                "_authenticated_common_mode_session",
                return_value=session,
            ),
            mock.patch.object(
                estimator.floor_extraction,
                "_common_mode_block_inputs_from_evidence",
                side_effect=lambda members, **_kwargs: tuple(
                    member.position for member in members
                ),
            ) as builder,
            mock.patch.object(
                estimator.floor_extraction,
                "_common_mode_floor_from_block_inputs",
                side_effect=common_floor,
            ) as common,
            mock.patch.object(
                mint1,
                "comparative_false_effect_floor",
                side_effect=AssertionError("default floor called"),
            ) as default,
        ):
            result = estimator.recompute_comparative_estimate(
                **recompute_kwargs(component)
            )
        self.assertEqual(result.estimator_path, estimator._COMMON_MODE_PATH)
        self.assertEqual(result.exact_widths_j, (0.125,) * 10)
        self.assertEqual(builder.call_count, 10)
        common.assert_called_once()
        default.assert_not_called()
        self.assertNotEqual(result.estimate, common_estimate)
        self.assertNotIn("estimator", result.comparative_record)

    def test_registered_refusal_does_not_fall_back(self) -> None:
        component = registered_component()
        with (
            mock.patch.object(
                estimator, "_assert_common_mode_contract", return_value=None
            ),
            mock.patch.object(
                estimator,
                "_authenticated_common_mode_session",
                side_effect=ValueError("registered refusal"),
            ),
            mock.patch.object(
                mint1, "comparative_false_effect_floor", wraps=(
                    mint1.comparative_false_effect_floor
                )
            ) as default,
        ):
            with self.assertRaisesRegex(ValueError, "registered refusal"):
                estimator.recompute_comparative_estimate(
                    **recompute_kwargs(component)
                )
        default.assert_not_called()

    def test_common_mode_requires_active_authentication_session(self) -> None:
        component = registered_component()
        with self.assertRaisesRegex(ValueError, "active v2 authentication"):
            estimator._authenticated_common_mode_session(
                component,
                runs_root=Path("/not-read"),
                calibration_ledger_snapshot=SimpleNamespace(),
                calibration_bracket_binding={},
            )

    def test_common_mode_session_is_fresh_and_uses_full_spec_membership(
        self,
    ) -> None:
        component = registered_component()
        expected_ids = set(estimator._full_spec_member_ids(component.spec))
        bracket = {"status": "passed"}
        session = SimpleNamespace(
            ready=True,
            refusal_reasons=(),
            calibration_bracket=bracket,
            summary_for=lambda bundle_id: {"bundle_id": bundle_id},
        )
        ledger = SimpleNamespace(valid=True)
        binding = {"binding": "authenticated"}
        with (
            V2AuthenticationReadSession(),
            mock.patch.object(
                estimator,
                "AuthenticatedConsumptionSession",
                return_value=session,
            ) as constructor,
            mock.patch.object(
                estimator,
                "whole_window_refusal_reasons",
                return_value=(),
            ) as refusal_reasons,
        ):
            observed = estimator._authenticated_common_mode_session(
                component,
                runs_root=Path("/authenticated/root"),
                calibration_ledger_snapshot=ledger,
                calibration_bracket_binding=binding,
            )
        self.assertIs(observed, session)
        constructor.assert_called_once_with(
            Path("/authenticated/root"),
            expected_ids,
            evaluation_basis_sha256=(
                component.whole_window_evaluation_basis_sha256
            ),
            consumption_semantics_id=component.consumption_semantics_id,
            calibration_ledger_snapshot=ledger,
            calibration_bracket_binding=binding,
        )
        self.assertEqual(refusal_reasons.call_args.args[1], expected_ids)


class BinderTests(unittest.TestCase):
    @staticmethod
    def artifact(width: float) -> dict:
        return {
            "cells": [
                {
                    "comparative": {"admissible_half_widths_j": [width]},
                    "provenance": {
                        "absolute": {"bundle_sha256s": ["a" * 64]},
                        "comparative": {"bundle_sha256s": ["b" * 64]},
                    },
                }
            ]
        }

    @staticmethod
    def core(side_effect=None, return_value=None):
        binder = mock.Mock(side_effect=side_effect, return_value=return_value)
        return SimpleNamespace(MintError=mint1.MintError, bind_floor_artifact_evidence=binder)

    def binder_kwargs(self, core, component, artifact) -> dict:
        return {
            "core": core,
            "artifact": artifact,
            "floor_path": Path("/floor/artifact.json"),
            "evidence_roots": {"root": Path("/evidence")},
            "strict_validator": lambda _path, _strict: [],
            "comparative_component": component,
            "runs_root": Path("/evidence"),
            "calibration_acceptance": ACCEPTANCE,
            "calibration_acceptance_sha256": ACCEPTANCE_SHA256,
            "calibration_allowance_projection": ALLOWANCE,
            "declared_calibration_scope": "production_window",
            "calibration_ledger_snapshot": SimpleNamespace(),
            "calibration_bracket_binding": {},
        }

    def test_default_binding_is_exactly_the_pinned_binder(self) -> None:
        _plan, _absolute, component = seven_b_components()
        expected = {"absolute": ("a",), "comparative": ("b",)}
        core = self.core(return_value=expected)
        result = estimator.bind_v2_floor_artifact_evidence(
            **self.binder_kwargs(core, component, self.artifact(0.5))
        )
        self.assertEqual(result, expected)
        core.bind_floor_artifact_evidence.assert_called_once()

    def test_common_mode_binding_accepts_only_exact_rederived_width(self) -> None:
        component = registered_component()
        width = 0.10000000000000002
        core = self.core(
            side_effect=mint1.MintError(
                "root: artifact widths differ from authenticated source bytes"
            )
        )
        recomputation = SimpleNamespace(exact_widths_j=(width,))
        with mock.patch.object(
            estimator,
            "recompute_comparative_estimate",
            return_value=recomputation,
        ):
            result = estimator.bind_v2_floor_artifact_evidence(
                **self.binder_kwargs(core, component, self.artifact(width))
            )
        self.assertEqual(
            result,
            {"absolute": ("a" * 64,), "comparative": ("b" * 64,)},
        )

    def test_one_ulp_downward_common_mode_width_refuses(self) -> None:
        component = registered_component()
        exact = 0.10000000000000002
        attacked = math.nextafter(exact, -math.inf)
        artifact = self.artifact(attacked)
        # Repair every artifact-local headline which could be derived from
        # the attacked record. The evidence binder must still compare the
        # stored width to its independent authenticated recomputation.
        artifact["cells"][0].update(
            {
                "floor_cmp_j": attacked,
                "floor_gate_j": attacked,
            }
        )
        artifact["cells"][0]["comparative"].update(
            {
                "corner_widened_guarded_floor_j": attacked,
                "drift_widened_guarded_floor_j": attacked,
            }
        )
        core = self.core(
            side_effect=mint1.MintError(
                "root: artifact widths differ from authenticated source bytes"
            )
        )
        with mock.patch.object(
            estimator,
            "recompute_comparative_estimate",
            return_value=SimpleNamespace(exact_widths_j=(exact,)),
        ):
            with self.assertRaisesRegex(ValueError, "common-mode widths differ"):
                estimator.bind_v2_floor_artifact_evidence(
                    **self.binder_kwargs(core, component, artifact)
                )

    def test_common_mode_binding_does_not_mask_an_earlier_legacy_check(self) -> None:
        component = registered_component()
        core = self.core(side_effect=mint1.MintError("campaign log sha256 mismatch"))
        with self.assertRaisesRegex(mint1.MintError, "campaign log"):
            estimator.bind_v2_floor_artifact_evidence(
                **self.binder_kwargs(core, component, self.artifact(0.1))
            )


if __name__ == "__main__":
    unittest.main()
