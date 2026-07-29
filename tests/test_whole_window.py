"""Two-scope authenticated whole-window consumption regressions."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.floor_extraction import extract_absolute_cell
from joulewise.whole_window import AuthenticatedConsumptionSession


LOCAL_CROSSING = "clock_bound_exceeds_quarter_window"
SENTINEL_J = 987_654_321.125


class TwoScopeRefusalTests(unittest.TestCase):
    @staticmethod
    def _bracket(bound_s: float = 0.03) -> dict:
        return {
            "schema_version": (
                "joulewise.instrument_calibration_bracket.v1"
            ),
            "status": "passed",
            "b_fiducial_s": bound_s,
            "pre": {
                "manifest_sha256": "a" * 64,
                "evidence_sha256": "b" * 64,
                "b_fiducial_s": 0.02,
            },
            "post": {
                "manifest_sha256": "c" * 64,
                "evidence_sha256": "d" * 64,
                "b_fiducial_s": bound_s,
            },
        }

    @staticmethod
    def _envelope(point_j: float, bound_s: float, half_width_j: float) -> dict:
        return {
            "method": (
                "common_trace_shift_plus_independent_edge_corners_v3"
            ),
            "anchor_bound_s": bound_s,
            "point_j": point_j,
            "lower_j": point_j - half_width_j,
            "upper_j": point_j + half_width_j,
            "max_abs_delta_j": half_width_j,
        }

    @classmethod
    def _summary(
        cls,
        decode_j: float,
        *,
        bound_s: float,
        half_width_j: float,
        prefill_reasons: tuple[str, ...] = (),
    ) -> dict:
        def gate(reasons: tuple[str, ...]) -> dict:
            return {
                "eligible": not reasons,
                "reasons": list(reasons),
                "windows": [
                    {
                        "eligible": not reasons,
                        "reasons": list(reasons),
                        "interpolation_joint_edge_bound_j": 0.0,
                    }
                ],
            }

        return {
            "status": "succeeded",
            "summary_provenance": {"reducer_version": "0.5.2"},
            "measurement_quality": {
                "cooldown_cap_hit": False,
                "idle_window_suspect": False,
                "telemetry_source": "powermetrics",
            },
            "phase_energy_j": {
                "prefill": SENTINEL_J,
                "decode": decode_j,
            },
            "energy_bound_terms_j": {
                "E_interpolation_joint_edge_bound_j": 0.0,
                "E_drift_bound_j": 0.0,
            },
            "energy_anchor_shift_envelopes": {
                "/phase_energy_j/prefill": cls._envelope(
                    SENTINEL_J, bound_s, half_width_j
                ),
                "/phase_energy_j/decode": cls._envelope(
                    decode_j, bound_s, half_width_j
                ),
            },
            "window_evidence_precheck": {
                "phase": {
                    "prefill": gate(prefill_reasons),
                    "decode": gate(()),
                }
            },
        }

    def _prepare_session(
        self,
        root: Path,
        widened_by_bundle: dict[str, dict],
    ) -> AuthenticatedConsumptionSession:
        bundle_paths: dict[str, Path] = {}
        for index, (bundle_id, widened) in enumerate(
            sorted(widened_by_bundle.items())
        ):
            bundle = root / bundle_id
            bundle.mkdir()
            minted = self._summary(
                10.0 + index * 0.01,
                bound_s=0.02,
                half_width_j=0.1,
            )
            (bundle / "summary_metrics.json").write_text(
                json.dumps(minted, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "instrument_calibration": {
                            "verified_effective_b_fiducial_s": 0.02
                        }
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            bundle_paths[bundle_id] = bundle

        session = AuthenticatedConsumptionSession(
            root, set(widened_by_bundle)
        )

        def rederive(path: Path, **_kwargs: object) -> dict:
            return widened_by_bundle[path.name]

        with (
            patch(
                "joulewise.whole_window.calibration_bracket_for_bundles",
                return_value=(self._bracket(), ()),
            ),
            patch(
                "joulewise.whole_window._current_strict_summary",
                return_value=True,
            ),
            patch(
                "joulewise.whole_window._verify_instrument_calibration",
                return_value=(0.02, None),
            ),
            patch(
                "joulewise.whole_window."
                "_rederive_summary_for_authenticated_fiducial_bound",
                side_effect=rederive,
            ),
        ):
            session._prepare(
                bundle_paths=bundle_paths,
                policy=SimpleNamespace(calibration_bracketing=object()),
            )
        return session

    def test_local_prefill_crossing_preserves_decode_and_cannot_leak(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle_ids = [f"member-{index}" for index in range(5)]
            widened = {
                bundle_id: self._summary(
                    10.0 + index * 0.01,
                    bound_s=0.03,
                    half_width_j=0.2,
                    prefill_reasons=(LOCAL_CROSSING,),
                )
                for index, bundle_id in enumerate(bundle_ids)
            }
            session = self._prepare_session(root, widened)
            cooldowns = {
                bundle_id: {"verified": True, "result": "recovered"}
                for bundle_id in bundle_ids
            }
            members = [
                {"slot": bundle_id, "bundle_id": bundle_id}
                for bundle_id in bundle_ids
            ]
            decode = extract_absolute_cell(
                cell_id="decode",
                metric="phase_energy_j.decode",
                window_class="phase",
                members=members,
                runs_root=root,
                cooldowns=cooldowns,
                strict_validator=lambda _path, _strict: (),
                consumption_session=session,
            )
            prefill = extract_absolute_cell(
                cell_id="prefill",
                metric="phase_energy_j.prefill",
                window_class="phase",
                members=members,
                runs_root=root,
                cooldowns=cooldowns,
                strict_validator=lambda _path, _strict: (),
                consumption_session=session,
            )

            class DecodeOnlySession:
                ready = True
                refusal_reasons: tuple[str, ...] = ()

                def summary_for(
                    self, bundle_id: str
                ) -> dict:
                    summary = copy.deepcopy(
                        session.summary_for(bundle_id)
                    )
                    del summary["phase_energy_j"]["prefill"]
                    del summary["window_evidence_precheck"]["phase"][
                        "prefill"
                    ]
                    del summary["energy_anchor_shift_envelopes"][
                        "/phase_energy_j/prefill"
                    ]
                    return summary

                def provenance_for(self, bundle_id: str) -> dict:
                    return dict(session.provenance_for(bundle_id) or {})

            baseline = extract_absolute_cell(
                cell_id="decode",
                metric="phase_energy_j.decode",
                window_class="phase",
                members=members,
                runs_root=root,
                cooldowns=cooldowns,
                strict_validator=lambda _path, _strict: (),
                consumption_session=DecodeOnlySession(),
            )

        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertEqual(session.refusal_reasons, ())
        self.assertEqual(
            {
                bundle_id: reasons[("phase", "prefill")]
                for bundle_id, reasons in (
                    session.path_refusal_reasons.items()
                )
            },
            {
                bundle_id: (LOCAL_CROSSING,)
                for bundle_id in bundle_ids
            },
        )
        self.assertTrue(decode.extractable, decode.refusal_reasons)
        self.assertFalse(prefill.extractable)
        self.assertIn(LOCAL_CROSSING, prefill.refusal_reasons)
        self.assertTrue(baseline.extractable, baseline.refusal_reasons)
        assert decode.floor is not None
        assert baseline.floor is not None
        decode_floor_bytes = json.dumps(
            decode.as_row()["floor"],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        baseline_floor_bytes = json.dumps(
            baseline.as_row()["floor"],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(decode_floor_bytes, baseline_floor_bytes)
        decode_floor_inputs = {
            "values_j": [
                member.value_j for member in decode.members
            ],
            "anchor_shift_bounds_j": [
                member.anchor_shift_bound_j
                for member in decode.members
            ],
            "operative_anchor_envelopes": [
                member.operative_anchor_envelope
                for member in decode.members
            ],
        }
        baseline_floor_inputs = {
            "values_j": [
                member.value_j for member in baseline.members
            ],
            "anchor_shift_bounds_j": [
                member.anchor_shift_bound_j
                for member in baseline.members
            ],
            "operative_anchor_envelopes": [
                member.operative_anchor_envelope
                for member in baseline.members
            ],
        }
        self.assertEqual(decode_floor_inputs, baseline_floor_inputs)
        self.assertNotIn(
            str(SENTINEL_J),
            json.dumps(
                decode_floor_inputs,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )

    def test_universal_reason_clears_all_authenticated_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            widened = self._summary(
                10.0,
                bound_s=0.03,
                half_width_j=0.2,
            )
            for child in ("prefill", "decode"):
                gate = widened["window_evidence_precheck"]["phase"][
                    child
                ]
                gate["eligible"] = False
                gate["reasons"] = ["negative_power_sample"]
                gate["windows"][0]["eligible"] = False
                gate["windows"][0]["reasons"] = [
                    "negative_power_sample"
                ]
            session = self._prepare_session(
                root, {"member": widened}
            )

        self.assertFalse(session.ready)
        self.assertEqual(
            session.refusal_reasons, ("negative_power_sample",)
        )
        self.assertEqual(session.path_refusal_reasons, {})
        self.assertEqual(session._summaries, {})
        self.assertEqual(session._provenance, {})
        self.assertIsNone(session.summary_for("member"))
        self.assertIsNone(session.provenance_for("member"))

    def test_unknown_code_under_recognized_child_defaults_global(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            widened = self._summary(
                10.0,
                bound_s=0.03,
                half_width_j=0.2,
            )
            decode = widened["window_evidence_precheck"]["phase"][
                "decode"
            ]
            decode["eligible"] = False
            decode["reasons"] = ["future_unclassified_reason"]
            session = self._prepare_session(
                root, {"member": widened}
            )

        self.assertFalse(session.ready)
        self.assertEqual(
            session.refusal_reasons,
            ("future_unclassified_reason",),
        )
        self.assertEqual(session.path_refusal_reasons, {})
        self.assertEqual(session._summaries, {})
        self.assertEqual(session._provenance, {})

    def test_known_code_under_unrecognized_child_defaults_global(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            widened = self._summary(
                10.0,
                bound_s=0.03,
                half_width_j=0.2,
            )
            widened["window_evidence_precheck"]["phase"][
                "unrecognized_child"
            ] = {
                "eligible": False,
                "reasons": [LOCAL_CROSSING],
            }
            session = self._prepare_session(
                root, {"member": widened}
            )

        self.assertFalse(session.ready)
        self.assertEqual(
            session.refusal_reasons, (LOCAL_CROSSING,)
        )
        self.assertEqual(session.path_refusal_reasons, {})
        self.assertEqual(session._summaries, {})
        self.assertEqual(session._provenance, {})

    def test_unrecorded_anchor_envelope_reason_remains_global(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            widened = self._summary(
                10.0,
                bound_s=0.03,
                half_width_j=0.2,
            )
            decode = widened["window_evidence_precheck"]["phase"][
                "decode"
            ]
            decode["eligible"] = False
            decode["reasons"] = [
                "anchor_energy_envelope_unrecorded"
            ]
            session = self._prepare_session(
                root, {"member": widened}
            )

        self.assertFalse(session.ready)
        self.assertEqual(
            session.refusal_reasons,
            ("anchor_energy_envelope_unrecorded",),
        )
        self.assertEqual(session.path_refusal_reasons, {})


if __name__ == "__main__":
    unittest.main()
