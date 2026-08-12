from __future__ import annotations

import copy
import inspect
import json
import math
import re
import tempfile
import unittest
from contextlib import ExitStack
from dataclasses import replace
from decimal import Decimal
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
        return SimpleNamespace(
            MintError=mint1.MintError,
            bind_floor_artifact_evidence=binder,
            validate_floor_artifact=mock.Mock(return_value=[]),
        )

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

    def actual_binder_fixture(
        self,
        tmp: str,
        *,
        width_delta: float = 1e-9,
        common_mode: bool = True,
    ):
        from tests.test_mint_floor_artifact import (
            BinderTests as CoreBinderTests,
            authenticated_components,
        )

        helper = CoreBinderTests("runTest")
        source_artifact, floor_path, roots = helper._tree(tmp)
        plan, absolute_component, comparative_component = (
            authenticated_components()
        )
        default_widths = tuple(comparative_component.widths_j)
        exact_widths_list = list(default_widths)
        exact_widths_list[0] += width_delta
        exact_widths = tuple(exact_widths_list)
        artifact = mint1.mint_authenticated_artifact(
            artifact_id="synthetic-common-mode",
            plan=plan,
            plan_sha256=mint1.PLAN_SHA256,
            calibration_plan_relative_path="calibration_plan.json",
            absolute=absolute_component,
            comparative=replace(
                comparative_component,
                widths_j=exact_widths,
            ),
            project_commit="0" * 40,
            project_tree_state="clean",
        )
        source_cell = source_artifact["cells"][0]
        target_cell = artifact["cells"][0]
        for component_name in ("absolute", "comparative"):
            source_rows = {
                row["bundle_id"]: row
                for row in mint1._record_rows(component_name, source_cell)
            }
            target_rows = mint1._record_rows(component_name, target_cell)
            for row in target_rows:
                installed = source_rows[row["bundle_id"]]
                row["bundle_sha256"] = installed["bundle_sha256"]
                row["config_sha256"] = installed["config_sha256"]
            target_cell["provenance"][component_name]["bundle_sha256s"] = [
                row["bundle_sha256"] for row in target_rows
            ]
            target_cell["provenance"][component_name]["campaign_log"] = (
                copy.deepcopy(
                    source_cell["provenance"][component_name]["campaign_log"]
                )
            )
        registered = registered_component()
        component = SimpleNamespace(
            spec_cell=(
                registered.spec_cell
                if common_mode
                else comparative_component.spec_cell
            ),
            widths_j=default_widths,
        )
        self.assertEqual(mint1.validate_floor_artifact(artifact), [])
        kwargs = self.binder_kwargs(mint1, component, artifact)
        kwargs.update(
            {
                "floor_path": floor_path,
                "evidence_roots": roots,
                "runs_root": roots["window_c"],
                "calibration_ledger_snapshot": None,
            }
        )
        return helper, artifact, kwargs, exact_widths

    @staticmethod
    def pre_fix_swallow_negative_control(kwargs):
        """The deleted pre-fix control, retained only as an attack oracle."""

        core = kwargs["core"]
        legacy_result = None
        try:
            legacy_result = core.bind_floor_artifact_evidence(
                kwargs["artifact"],
                kwargs["floor_path"],
                kwargs["evidence_roots"],
                strict_validator=kwargs["strict_validator"],
                calibration_ledger_snapshot=kwargs[
                    "calibration_ledger_snapshot"
                ],
                calibration_bracket_binding=kwargs[
                    "calibration_bracket_binding"
                ],
            )
        except core.MintError as exc:
            if not str(exc).endswith(
                "artifact widths differ from authenticated source bytes"
            ):
                raise
        if legacy_result is not None:
            return legacy_result
        provenance = kwargs["artifact"]["cells"][0]["provenance"]
        return {
            name: tuple(provenance[name]["bundle_sha256s"])
            for name in ("absolute", "comparative")
        }

    @staticmethod
    def tamper_absolute_width_consistently(artifact: dict) -> None:
        cell = artifact["cells"][0]
        original = cell["absolute"]
        widths = list(original["admissible_half_widths_j"])
        widths[0] += 1.0
        estimate = mint1.absolute_false_effect_floor(
            [row["metric_value_j"] for row in original["bundle_observations"]],
            admissible_half_widths_j=widths,
        )
        cell["absolute"] = mint1.build_absolute_record(
            estimate,
            original["bundle_observations"],
            consumption_semantics_id=original["consumption_semantics_id"],
            whole_window_drift_allowance=original[
                "whole_window_drift_allowance"
            ],
        )
        cell["floor_abs_j"] = cell["absolute"][
            "drift_widened_guarded_floor_j"
        ]
        cell["floor_gate_j"] = max(cell["floor_abs_j"], cell["floor_cmp_j"])
        diagnostics = {
            name: copy.deepcopy(record["point_floor_diagnostic"])
            for name, record in (
                ("absolute", cell["absolute"]),
                ("comparative", cell["comparative"]),
            )
            if "point_floor_diagnostic" in record
        }
        cell["point_floor_diagnostics"] = diagnostics
        group = artifact["transport_groups"][0]
        group["composed_floor_abs_j"] = cell["floor_abs_j"]
        group["composed_floor_cmp_j"] = cell["floor_cmp_j"]
        group["composed_floor_gate_j"] = cell["floor_gate_j"]
        group["point_floor_diagnostics"] = {cell["cell_id"]: diagnostics}

    def test_default_binding_is_exactly_the_pinned_binder(self) -> None:
        _plan, _absolute, component = seven_b_components()
        expected = {"absolute": ("a",), "comparative": ("b",)}
        core = self.core(return_value=expected)
        result = estimator.bind_v2_floor_artifact_evidence(
            **self.binder_kwargs(core, component, self.artifact(0.5))
        )
        self.assertEqual(result, expected)
        core.bind_floor_artifact_evidence.assert_called_once()

    def test_default_binding_retains_pinned_one_e_minus_twelve_tolerance(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            helper, _artifact, kwargs, _widths = self.actual_binder_fixture(
                tmp,
                width_delta=5e-13,
                common_mode=False,
            )
            stack = kwargs["artifact"]["cells"][0]["source_regime"][
                "stack_identity"
            ]
            with (
                mock.patch.object(mint1, "build_stack_identity", return_value=stack),
                mock.patch.object(
                    mint1,
                    "_authenticated_consumption_summaries",
                    side_effect=helper._synthetic_consumption,
                ),
            ):
                rebound = estimator.bind_v2_floor_artifact_evidence(**kwargs)
            self.assertEqual(set(rebound), {"absolute", "comparative"})

    def test_common_mode_binding_accepts_only_exact_rederived_width(self) -> None:
        component = registered_component()
        width = 0.10000000000000002
        artifact = self.artifact(width)
        verified = {"absolute": ("verified-a",), "comparative": ("verified-b",)}

        def verify_substituted_copy(candidate, *_args, **_kwargs):
            self.assertIsNot(candidate, artifact)
            expected = copy.deepcopy(artifact)
            expected["cells"][0]["comparative"][
                "admissible_half_widths_j"
            ] = list(component.widths_j)
            self.assertEqual(candidate, expected)
            return verified

        core = self.core(side_effect=verify_substituted_copy)
        recomputation = SimpleNamespace(exact_widths_j=(width,))
        with mock.patch.object(
            estimator,
            "recompute_comparative_estimate",
            return_value=recomputation,
        ):
            result = estimator.bind_v2_floor_artifact_evidence(
                **self.binder_kwargs(core, component, artifact)
            )
        self.assertEqual(result, verified)
        self.assertEqual(artifact, self.artifact(width))

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
            return_value={"absolute": ("a",), "comparative": ("b",)}
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

    def test_common_mode_string_width_refuses_after_full_binder(self) -> None:
        component = registered_component()
        for label, attacked in (("string", "0.1"), ("bool", True)):
            with self.subTest(label=label):
                artifact = self.artifact(0.1)
                artifact["cells"][0]["comparative"][
                    "admissible_half_widths_j"
                ] = [attacked]
                core = self.core(
                    return_value={"absolute": ("a",), "comparative": ("b",)}
                )
                with mock.patch.object(
                    estimator,
                    "recompute_comparative_estimate",
                    return_value=SimpleNamespace(exact_widths_j=(0.1,)),
                ):
                    with self.assertRaisesRegex(
                        ValueError, "common-mode widths differ"
                    ):
                        estimator.bind_v2_floor_artifact_evidence(
                            **self.binder_kwargs(core, component, artifact)
                        )
                core.bind_floor_artifact_evidence.assert_called_once()

    def test_common_mode_absolute_width_refusal_is_never_swallowed(self) -> None:
        component = registered_component()
        core = self.core(
            side_effect=mint1.MintError(
                "root: artifact widths differ from authenticated source bytes"
            )
        )
        with self.assertRaisesRegex(mint1.MintError, "artifact widths differ"):
            estimator.bind_v2_floor_artifact_evidence(
                **self.binder_kwargs(core, component, self.artifact(0.1))
            )

    def test_common_mode_comparative_hash_refusal_is_never_swallowed(self) -> None:
        component = registered_component()
        core = self.core(
            side_effect=mint1.MintError(
                "root: rebound bundle hashes differ from component provenance"
            )
        )
        with self.assertRaisesRegex(mint1.MintError, "rebound bundle hashes"):
            estimator.bind_v2_floor_artifact_evidence(
                **self.binder_kwargs(core, component, self.artifact(0.1))
            )

    def test_common_mode_multi_cell_artifact_refuses(self) -> None:
        component = registered_component()
        artifact = self.artifact(0.1)
        artifact["cells"].append(copy.deepcopy(artifact["cells"][0]))
        core = self.core(return_value={})
        with self.assertRaisesRegex(ValueError, "one isolated cell"):
            core.bind_floor_artifact_evidence(
                artifact,
                Path("/floor/artifact.json"),
                {"root": Path("/evidence")},
                strict_validator=lambda _path, _strict: [],
            )
            estimator._stored_comparative_widths(artifact)
        core.bind_floor_artifact_evidence.assert_called_once()
        core.bind_floor_artifact_evidence.reset_mock()
        with self.assertRaisesRegex(ValueError, "one isolated cell"):
            estimator.bind_v2_floor_artifact_evidence(
                **self.binder_kwargs(core, component, artifact)
            )
        core.bind_floor_artifact_evidence.assert_not_called()

    def test_binding_seam_has_no_swallow_or_provenance_fallback(self) -> None:
        source = inspect.getsource(estimator.bind_v2_floor_artifact_evidence)
        self.assertNotIn("except core.MintError", source)
        self.assertFalse(hasattr(estimator, "_binding_result_from_provenance"))

    def test_binding_copy_validator_patch_restores_on_return_and_raise(self) -> None:
        component = registered_component()
        for should_raise in (False, True):
            with self.subTest(should_raise=should_raise):
                core = self.core(
                    side_effect=(
                        mint1.MintError("fixture downstream refusal")
                        if should_raise
                        else None
                    ),
                    return_value={"absolute": ("a",), "comparative": ("b",)},
                )
                pinned_validator = core.validate_floor_artifact
                call = lambda: estimator.bind_v2_floor_artifact_evidence(
                    **self.binder_kwargs(core, component, self.artifact(0.1))
                )
                with mock.patch.object(
                    estimator,
                    "recompute_comparative_estimate",
                    return_value=SimpleNamespace(exact_widths_j=(0.1,)),
                ):
                    if should_raise:
                        with self.assertRaisesRegex(
                            mint1.MintError, "downstream refusal"
                        ):
                            call()
                    else:
                        call()
                self.assertIs(core.validate_floor_artifact, pinned_validator)

    def test_binding_crosswires_refuse_both_directions_and_controls_accept(
        self,
    ) -> None:
        registered = registered_component()
        common_spec_default_widths = self.artifact(0.5)
        default_only_core = self.core(
            return_value={"absolute": ("a",), "comparative": ("b",)}
        )
        # A site-limited default-only binder accepts these default-shaped
        # widths even though the authenticated selector is common-mode.
        self.assertEqual(
            default_only_core.bind_floor_artifact_evidence(
                common_spec_default_widths,
                Path("/floor/artifact.json"),
                {"root": Path("/evidence")},
                strict_validator=lambda _path, _strict: [],
            ),
            {"absolute": ("a",), "comparative": ("b",)},
        )
        with mock.patch.object(
            estimator,
            "recompute_comparative_estimate",
            return_value=SimpleNamespace(exact_widths_j=(0.6,)),
        ):
            with self.assertRaisesRegex(ValueError, "common-mode widths differ"):
                estimator.bind_v2_floor_artifact_evidence(
                    **self.binder_kwargs(
                        default_only_core,
                        registered,
                        common_spec_default_widths,
                    )
                )

        _plan, _absolute, default_component = seven_b_components()
        default_spec_common_widths = self.artifact(0.6)

        def pinned_default_binder(candidate, *_args, **_kwargs):
            if candidate["cells"][0]["comparative"][
                "admissible_half_widths_j"
            ] != [0.5]:
                raise mint1.MintError(
                    "root: artifact widths differ from authenticated source bytes"
                )
            return {"absolute": ("a",), "comparative": ("b",)}

        pinned_core = self.core(side_effect=pinned_default_binder)
        with self.assertRaisesRegex(mint1.MintError, "artifact widths differ"):
            estimator.bind_v2_floor_artifact_evidence(
                **self.binder_kwargs(
                    pinned_core,
                    default_component,
                    default_spec_common_widths,
                )
            )
        # A site-limited common-only comparison would accept the same attack,
        # proving the default-selector dispatch is the binding-site gate.
        def common_only_control(candidate, exact_widths):
            observed = candidate["cells"][0]["comparative"][
                "admissible_half_widths_j"
            ]
            if [Decimal(str(value)) for value in observed] != [
                Decimal(str(value)) for value in exact_widths
            ]:
                raise ValueError("common-only control refused")
            return {"absolute": ("self-certified",), "comparative": ("self-certified",)}

        self.assertEqual(
            set(common_only_control(default_spec_common_widths, (0.6,))),
            {"absolute", "comparative"},
        )

    def test_common_mode_binding_does_not_mask_an_earlier_legacy_check(self) -> None:
        component = registered_component()
        core = self.core(side_effect=mint1.MintError("campaign log sha256 mismatch"))
        with self.assertRaisesRegex(mint1.MintError, "campaign log"):
            estimator.bind_v2_floor_artifact_evidence(
                **self.binder_kwargs(core, component, self.artifact(0.1))
            )

    def test_actual_core_absolute_width_attack_fails_pre_fix_control(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            helper, artifact, kwargs, exact_widths = self.actual_binder_fixture(
                tmp
            )
            self.tamper_absolute_width_consistently(artifact)
            stack = artifact["cells"][0]["source_regime"]["stack_identity"]
            with (
                mock.patch.object(mint1, "build_stack_identity", return_value=stack),
                mock.patch.object(
                    mint1,
                    "_authenticated_consumption_summaries",
                    side_effect=helper._synthetic_consumption,
                ),
                mock.patch.object(
                    estimator,
                    "recompute_comparative_estimate",
                    return_value=SimpleNamespace(exact_widths_j=exact_widths),
                ) as recompute,
            ):
                accepted = self.pre_fix_swallow_negative_control(kwargs)
                self.assertEqual(set(accepted), {"absolute", "comparative"})
                with self.assertRaisesRegex(mint1.MintError, "artifact widths differ"):
                    estimator.bind_v2_floor_artifact_evidence(**kwargs)
            recompute.assert_not_called()
            self.assertFalse(kwargs["floor_path"].exists())

    def test_actual_core_comparative_hash_attack_fails_pre_fix_control(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            helper, artifact, kwargs, exact_widths = self.actual_binder_fixture(
                tmp
            )
            pre_absolute_attack = copy.deepcopy(artifact)
            self.tamper_absolute_width_consistently(artifact)
            artifact["cells"][0]["provenance"]["comparative"][
                "bundle_sha256s"
            ][0] = "f" * 64
            mint1._record_rows(
                "comparative", artifact["cells"][0]
            )[0]["bundle_sha256"] = "f" * 64
            stack = artifact["cells"][0]["source_regime"]["stack_identity"]
            with (
                mock.patch.object(mint1, "build_stack_identity", return_value=stack),
                mock.patch.object(
                    mint1,
                    "_authenticated_consumption_summaries",
                    side_effect=helper._synthetic_consumption,
                ),
                mock.patch.object(
                    estimator,
                    "recompute_comparative_estimate",
                    return_value=SimpleNamespace(exact_widths_j=exact_widths),
                ),
            ):
                accepted = self.pre_fix_swallow_negative_control(kwargs)
                self.assertEqual(
                    accepted["comparative"][0],
                    "f" * 64,
                    "pre-fix control self-certified the tampered provenance hash",
                )
                with self.assertRaisesRegex(mint1.MintError, "artifact widths differ"):
                    estimator.bind_v2_floor_artifact_evidence(**kwargs)

                artifact.clear()
                artifact.update(copy.deepcopy(pre_absolute_attack))
                artifact["cells"][0]["provenance"]["comparative"][
                    "bundle_sha256s"
                ][0] = "f" * 64
                mint1._record_rows(
                    "comparative", artifact["cells"][0]
                )[0]["bundle_sha256"] = "f" * 64
                with self.assertRaisesRegex(
                    mint1.MintError, "bundle_sha256 does not match source bytes"
                ):
                    estimator.bind_v2_floor_artifact_evidence(**kwargs)
            self.assertFalse(kwargs["floor_path"].exists())

    def test_actual_core_common_mode_bind_completes_and_returns_strict_hashes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            helper, artifact, kwargs, exact_widths = self.actual_binder_fixture(
                tmp
            )
            stack = artifact["cells"][0]["source_regime"]["stack_identity"]
            strict_hashes = []
            original_strict_bundle = mint1._strict_bundle
            original_binder = mint1.bind_floor_artifact_evidence
            binder_outcomes = []

            def track_strict_bundle(*args, **call_kwargs):
                member = original_strict_bundle(*args, **call_kwargs)
                strict_hashes.append(member.bundle_sha256)
                return member

            def track_binder_completion(*args, **call_kwargs):
                try:
                    result = original_binder(*args, **call_kwargs)
                except mint1.MintError:
                    binder_outcomes.append("raised")
                    raise
                binder_outcomes.append("completed")
                return result

            with (
                mock.patch.object(mint1, "build_stack_identity", return_value=stack),
                mock.patch.object(
                    mint1,
                    "_authenticated_consumption_summaries",
                    side_effect=helper._synthetic_consumption,
                ),
                mock.patch.object(
                    mint1, "_strict_bundle", side_effect=track_strict_bundle
                ),
                mock.patch.object(
                    mint1,
                    "bind_floor_artifact_evidence",
                    side_effect=track_binder_completion,
                ),
                mock.patch.object(
                    estimator,
                    "recompute_comparative_estimate",
                    return_value=SimpleNamespace(exact_widths_j=exact_widths),
                ),
            ):
                pre_fix_result = self.pre_fix_swallow_negative_control(kwargs)
                self.assertEqual(set(pre_fix_result), {"absolute", "comparative"})
                self.assertEqual(binder_outcomes, ["raised"])
                absolute_n = len(
                    mint1._record_rows("absolute", artifact["cells"][0])
                )
                strict_hashes.clear()
                rebound = estimator.bind_v2_floor_artifact_evidence(**kwargs)
            self.assertEqual(binder_outcomes, ["raised", "completed"])
            self.assertEqual(rebound["absolute"], tuple(strict_hashes[:absolute_n]))
            self.assertEqual(
                rebound["comparative"], tuple(strict_hashes[absolute_n:])
            )
            self.assertEqual(
                artifact["cells"][0]["comparative"][
                    "admissible_half_widths_j"
                ],
                list(exact_widths),
            )
            statement_path = Path(tmp) / "single-count.txt"
            mint1.write_outputs_exclusive(
                artifact,
                kwargs["floor_path"],
                statement_path,
            )
            written = json.loads(kwargs["floor_path"].read_text(encoding="utf-8"))
            self.assertEqual(
                written["cells"][0]["comparative"][
                    "admissible_half_widths_j"
                ],
                list(exact_widths),
            )
            self.assertTrue(statement_path.is_file())

    def test_post_131_stack_unavailable_and_both_roots_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            helper, artifact, kwargs, exact_widths = self.actual_binder_fixture(
                tmp
            )
            with (
                mock.patch.object(mint1, "build_stack_identity", return_value=None),
                mock.patch.object(
                    mint1,
                    "_authenticated_consumption_summaries",
                    side_effect=helper._synthetic_consumption,
                ),
                mock.patch.object(
                    estimator,
                    "recompute_comparative_estimate",
                    return_value=SimpleNamespace(exact_widths_j=exact_widths),
                ) as recompute,
            ):
                with self.assertRaisesRegex(
                    mint1.MintError,
                    "source stack identity fields are unavailable",
                ):
                    estimator.bind_v2_floor_artifact_evidence(**kwargs)
            recompute.assert_not_called()

        with tempfile.TemporaryDirectory() as tmp:
            helper, artifact, kwargs, exact_widths = self.actual_binder_fixture(
                tmp
            )
            artifact["cells"][0]["provenance"].pop("comparative")
            stack = artifact["cells"][0]["source_regime"]["stack_identity"]
            with (
                mock.patch.object(mint1, "validate_floor_artifact", return_value=[]),
                mock.patch.object(mint1, "build_stack_identity", return_value=stack),
                mock.patch.object(
                    mint1,
                    "_authenticated_consumption_summaries",
                    side_effect=helper._synthetic_consumption,
                ),
                mock.patch.object(
                    estimator,
                    "recompute_comparative_estimate",
                    return_value=SimpleNamespace(exact_widths_j=exact_widths),
                ) as recompute,
            ):
                with self.assertRaisesRegex(
                    mint1.MintError,
                    "claim-ready bind requires both component evidence roots",
                ):
                    estimator.bind_v2_floor_artifact_evidence(**kwargs)
            recompute.assert_not_called()

    def test_all_pinned_binder_refusal_classes_propagate_on_common_mode(self) -> None:
        binder_source = inspect.getsource(mint1.bind_floor_artifact_evidence)
        # This source inventory closes the list against the actual pinned
        # binder.  The per-message loop below then proves that the common-mode
        # wrapper propagates, rather than classifies or swallows, every class.
        for gate in (
            "validate_floor_artifact(artifact)",
            "_assert_path_independent(artifact)",
            "_validate_custody_store_provenance",
            "_resolve_plan_path",
            "calibration plan bytes do not match artifact sha256",
            "calibration plan bytes do not match declared provenance",
            "missing evidence-root mapping",
            "is not a directory",
            "campaign log sha256 mismatch",
            "component consumption wire is invalid",
            "artifact consumption semantics differ",
            "authenticated consumption omitted artifact members",
            "_strict_bundle(",
            "rebound bundle hashes differ",
            "source stack differs from artifact",
            "source stack identity fields are unavailable",
            "artifact widths differ from authenticated source bytes",
            "claim-ready bind requires both component evidence roots",
        ):
            with self.subTest(source_gate=gate):
                self.assertIn(gate, binder_source)
        component = registered_component()
        refusals = (
            "cannot bind invalid floor artifact: invalid",
            "artifact embeds machine-dependent paths",
            "artifact custody-store provenance differs",
            "calibration plan path does not resolve",
            "calibration plan bytes do not match artifact sha256",
            "calibration plan bytes do not match declared provenance",
            "missing evidence-root mapping for 'root'",
            "evidence root 'root' is not a directory",
            "root: campaign log sha256 mismatch",
            "root: component consumption wire is invalid",
            "root: artifact consumption semantics differ from authenticated source consumption",
            "root: authenticated consumption omitted artifact members",
            "root: strict bundle validation failed",
            "root: artifact widths differ from authenticated source bytes",
            "root: rebound bundle hashes differ from component provenance",
            "root: source stack differs from artifact",
            "source stack identity fields are unavailable",
            "claim-ready bind requires both component evidence roots",
        )
        for message in refusals:
            with self.subTest(message=message):
                core = self.core(side_effect=mint1.MintError(message))
                with self.assertRaisesRegex(mint1.MintError, re.escape(message)):
                    estimator.bind_v2_floor_artifact_evidence(
                        **self.binder_kwargs(core, component, self.artifact(0.1))
                    )
                core.bind_floor_artifact_evidence.assert_called_once()

    def test_actual_pinned_binder_refusal_gates_run_on_common_mode_copy(self) -> None:
        """Drive each F4 class inside the real post-#131 pinned binder."""

        cases = (
            ("invalid_artifact", "cannot bind invalid floor artifact"),
            ("path_dependence", "fixture path-dependence refusal"),
            ("custody", "fixture custody-store provenance refusal"),
            ("plan_resolution", "calibration plan"),
            ("plan_sha", "calibration plan bytes do not match artifact sha256"),
            ("plan_identity", "calibration plan bytes do not match declared provenance"),
            ("missing_root", "missing evidence-root mapping"),
            ("non_directory_root", "is not a directory"),
            ("campaign_sha", "campaign log sha256 mismatch"),
            ("component_wire", "component consumption wire is invalid"),
            ("semantics", "artifact consumption semantics differ"),
            ("omitted_members", "authenticated consumption omitted artifact members"),
            ("strict_bundle", "strict validation failed"),
            ("absolute_width", "artifact widths differ from authenticated source bytes"),
            ("rebound_hash", "rebound bundle hashes differ"),
            ("stack_mismatch", "source stack differs from artifact"),
            ("stack_unavailable", "source stack identity fields are unavailable"),
            ("both_roots", "claim-ready bind requires both component evidence roots"),
        )
        for case, message in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                helper, artifact, kwargs, exact_widths = self.actual_binder_fixture(
                    tmp
                )
                source_stack = artifact["cells"][0]["source_regime"][
                    "stack_identity"
                ]
                build_stack_result = source_stack
                consumption = helper._synthetic_consumption
                strict_validator = kwargs["strict_validator"]
                bypass_validator = False

                if case == "invalid_artifact":
                    artifact["schema_version"] = "forged.schema"
                elif case == "plan_resolution":
                    artifact["provenance"]["calibration_plan"][
                        "relative_path"
                    ] = "missing-plan.json"
                elif case == "plan_sha":
                    artifact["provenance"]["calibration_plan"]["sha256"] = "f" * 64
                    bypass_validator = True
                elif case == "plan_identity":
                    artifact["provenance"]["calibration_plan"]["plan_id"] = "forged"
                    bypass_validator = True
                elif case == "missing_root":
                    kwargs["evidence_roots"] = {
                        key: value
                        for key, value in kwargs["evidence_roots"].items()
                        if key != "a10"
                    }
                elif case == "non_directory_root":
                    kwargs["evidence_roots"] = {
                        **kwargs["evidence_roots"],
                        "a10": Path(tmp) / "not-a-directory",
                    }
                elif case == "campaign_sha":
                    artifact["cells"][0]["provenance"]["absolute"][
                        "campaign_log"
                    ]["sha256"] = "f" * 64
                elif case == "component_wire":
                    artifact["cells"][0]["absolute"][
                        "consumption_semantics_id"
                    ] = "forged.semantics"
                    bypass_validator = True
                elif case == "semantics":
                    def consumption(*args, **call_kwargs):
                        summaries, _semantics = helper._synthetic_consumption(
                            *args, **call_kwargs
                        )
                        return summaries, "forged.semantics"
                elif case == "omitted_members":
                    def consumption(*args, **call_kwargs):
                        summaries, semantics = helper._synthetic_consumption(
                            *args, **call_kwargs
                        )
                        summaries.pop(next(iter(summaries)))
                        return summaries, semantics
                elif case == "strict_bundle":
                    strict_validator = lambda _path, _strict: ("fixture",)
                elif case == "absolute_width":
                    self.tamper_absolute_width_consistently(artifact)
                elif case == "rebound_hash":
                    artifact["cells"][0]["provenance"]["comparative"][
                        "bundle_sha256s"
                    ][0] = "f" * 64
                    bypass_validator = True
                elif case == "stack_mismatch":
                    artifact["cells"][0]["provenance"]["comparative"][
                        "source_regime"
                    ]["stack_identity_sha256"] = "f" * 64
                    bypass_validator = True
                elif case == "stack_unavailable":
                    build_stack_result = None
                elif case == "both_roots":
                    artifact["cells"][0]["provenance"].pop("comparative")
                    bypass_validator = True

                kwargs["artifact"] = artifact
                kwargs["strict_validator"] = strict_validator
                mint1._BINDING_SUMMARY_CACHE.clear()
                with ExitStack() as patches:
                    patches.enter_context(
                        mock.patch.object(
                            mint1,
                            "build_stack_identity",
                            return_value=build_stack_result,
                        )
                    )
                    patches.enter_context(
                        mock.patch.object(
                            mint1,
                            "_authenticated_consumption_summaries",
                            side_effect=consumption,
                        )
                    )
                    patches.enter_context(
                        mock.patch.object(
                            estimator,
                            "recompute_comparative_estimate",
                            return_value=SimpleNamespace(
                                exact_widths_j=exact_widths
                            ),
                        )
                    )
                    if bypass_validator:
                        patches.enter_context(
                            mock.patch.object(
                                mint1,
                                "validate_floor_artifact",
                                return_value=[],
                            )
                        )
                    if case == "path_dependence":
                        patches.enter_context(
                            mock.patch.object(
                                mint1,
                                "_assert_path_independent",
                                side_effect=mint1.MintError(
                                    "fixture path-dependence refusal"
                                ),
                            )
                        )
                    if case == "custody":
                        patches.enter_context(
                            mock.patch.object(
                                mint1,
                                "_validate_custody_store_provenance",
                                side_effect=mint1.MintError(
                                    "fixture custody-store provenance refusal"
                                ),
                            )
                        )
                    with self.assertRaisesRegex(mint1.MintError, re.escape(message)):
                        estimator.bind_v2_floor_artifact_evidence(**kwargs)
                self.assertFalse(kwargs["floor_path"].exists())


if __name__ == "__main__":
    unittest.main()
