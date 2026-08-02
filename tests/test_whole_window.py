"""Two-scope authenticated whole-window consumption regressions."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.floor_extraction import extract_absolute_cell
from joulewise.whole_window import AuthenticatedConsumptionSession
from joulewise.whole_window import (
    ADAPTER_CONTINUITY_SCHEMA,
    IDLE_ADMISSION_CORE_SCHEMA,
    NEG8_BRACKET_SCHEMA,
    WHOLE_WINDOW_SCHEMA,
    _validate_row,
    build_row_provenance,
)
from joulewise.campaign_provenance import (
    campaign_provenance_attestation,
    load_authenticated_campaign_catalog,
)


LOCAL_CROSSING = "clock_bound_exceeds_quarter_window"
UNRECORDED_ENVELOPE = "anchor_energy_envelope_unrecorded"
SENTINEL_J = 987_654_321.125


class CampaignManifestVerdictAuthenticationTests(unittest.TestCase):
    POLICY_SHA = "a" * 64
    BRACKET_POLICY = {"require_bracket": True}

    def _verdict_fixture(
        self,
        root: Path,
        *,
        schema_version: str,
        attest: bool,
        relabel: bool = False,
        poisoned_sibling: bool = False,
    ) -> dict:
        manifest_dir = root / "campaign_manifests"
        manifest_dir.mkdir(parents=True)
        manifest_path = manifest_dir / "source.json"
        manifest = {
            "schema_version": (
                "joulewise.campaign_provenance.v1"
                if relabel
                else schema_version
            ),
            "session_id": "source-session",
            "campaign_policy": {"sha256": self.POLICY_SHA},
            "members": [
                {
                    "execution": "invoked",
                    "run_id": "member",
                    "bundle_ids": ["member"],
                }
            ],
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if relabel:
            raw = manifest_path.read_bytes()
            v1 = b'"schema_version": "joulewise.campaign_provenance.v1"'
            v2 = b'"schema_version": "joulewise.campaign_provenance.v2"'
            self.assertEqual(raw.count(v1), 1)
            manifest_path.write_bytes(raw.replace(v1, v2, 1))
            manifest["schema_version"] = schema_version

        raw = manifest_path.read_bytes()
        if poisoned_sibling:
            sibling = {
                **manifest,
                "session_id": "unattested-sibling-session",
                "members": [
                    {
                        "execution": "invoked",
                        "run_id": "unattested-sibling",
                        "bundle_ids": ["unattested-sibling"],
                    }
                ],
            }
            (manifest_dir / "unattested-sibling.json").write_text(
                json.dumps(sibling, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if attest:
            attestation = campaign_provenance_attestation(
                manifest_path=manifest_path,
                raw_manifest_bytes=raw,
                manifest=manifest,
                timestamp="2026-08-01T12:00:00Z",
            )
            (root / "campaign_log.jsonl").write_text(
                json.dumps(attestation) + "\n",
                encoding="utf-8",
            )
        row = {
            "schema_version": WHOLE_WINDOW_SCHEMA,
            "status": "passed",
            "campaign_policy": {"sha256": self.POLICY_SHA},
            "bundle_ids": ["member"],
            "idle_admission_core": {
                "schema_version": IDLE_ADMISSION_CORE_SCHEMA,
                "policy_sha256": self.POLICY_SHA,
                "members": [
                    {
                        "bundle_id": "member",
                        "cpu_admission": {"decision": "admitted"},
                    }
                ],
                "adapter_wattage_continuity": {
                    "schema_version": ADAPTER_CONTINUITY_SCHEMA,
                    "decision": "stable",
                },
                "neg8_bracket": {
                    "schema_version": NEG8_BRACKET_SCHEMA,
                    "decision": "passed",
                    "policy": dict(self.BRACKET_POLICY),
                },
            },
        }
        row["row_provenance"] = build_row_provenance(
            policy_sha256=self.POLICY_SHA,
            bundle_ids=["member"],
            source_manifests=[
                {
                    "path": "campaign_manifests/source.json",
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            ],
        )
        return row

    def _validate(self, row: dict, root: Path) -> tuple[bool, tuple[str, ...]]:
        with (
            patch(
                "joulewise.whole_window._current_core_rederivation_reasons",
                return_value=set(),
            ),
            patch(
                "joulewise.whole_window._registered_bracket_policy",
                return_value=self.BRACKET_POLICY,
            ),
            patch(
                "joulewise.whole_window._derived_neg8_decision",
                return_value=("passed", None),
            ),
        ):
            return _validate_row(row, root, {"member"})

    def test_attested_v2_source_passes_beside_poisoned_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = self._verdict_fixture(
                root,
                schema_version="joulewise.campaign_provenance.v2",
                attest=True,
                poisoned_sibling=True,
            )
            ok, reasons = self._validate(row, root)
            catalog = load_authenticated_campaign_catalog(root)

        self.assertTrue(ok, reasons)
        self.assertEqual(reasons, ())
        self.assertIsNone(catalog)

    def test_unattested_and_relabelled_v2_sources_refuse_verdict(self) -> None:
        for relabel in (False, True):
            with self.subTest(relabel=relabel), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                row = self._verdict_fixture(
                    root,
                    schema_version="joulewise.campaign_provenance.v2",
                    attest=False,
                    relabel=relabel,
                )
                ok, reasons = self._validate(row, root)

                self.assertFalse(ok)
                self.assertIn(
                    "whole_window_verdict_provenance_invalid",
                    reasons,
                )


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
        tokenize_reasons: tuple[str, ...] = (),
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
                "tokenize": SENTINEL_J,
                "decode": decode_j,
            },
            "energy_bound_terms_j": {
                "E_interpolation_joint_edge_bound_j": 0.0,
                "E_drift_bound_j": 0.0,
            },
            "energy_anchor_shift_envelopes": {
                "/phase_energy_j/tokenize": cls._envelope(
                    SENTINEL_J, bound_s, half_width_j
                ),
                "/phase_energy_j/decode": cls._envelope(
                    decode_j, bound_s, half_width_j
                ),
            },
            "window_evidence_precheck": {
                "phase": {
                    "tokenize": gate(tokenize_reasons),
                    "decode": gate(()),
                }
            },
        }

    def _prepare_session(
        self,
        root: Path,
        widened_by_bundle: dict[str, dict],
        *,
        include_minted_envelopes: bool = True,
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
            if not include_minted_envelopes:
                del minted["energy_anchor_shift_envelopes"]
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

    def test_local_microphase_refusals_preserve_decode_and_cannot_leak(
        self,
    ) -> None:
        for local_reason in (LOCAL_CROSSING, UNRECORDED_ENVELOPE):
            with self.subTest(local_reason=local_reason):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    bundle_ids = [
                        f"member-{index}" for index in range(5)
                    ]
                    widened = {
                        bundle_id: self._summary(
                            10.0 + index * 0.01,
                            bound_s=0.03,
                            half_width_j=0.2,
                            tokenize_reasons=(local_reason,),
                        )
                        for index, bundle_id in enumerate(bundle_ids)
                    }
                    session = self._prepare_session(root, widened)
                    cooldowns = {
                        bundle_id: {
                            "verified": True,
                            "result": "recovered",
                        }
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
                    tokenize = extract_absolute_cell(
                        cell_id="tokenize",
                        metric="phase_energy_j.tokenize",
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
                            del summary["phase_energy_j"]["tokenize"]
                            del summary[
                                "window_evidence_precheck"
                            ]["phase"]["tokenize"]
                            del summary[
                                "energy_anchor_shift_envelopes"
                            ]["/phase_energy_j/tokenize"]
                            return summary

                        def provenance_for(
                            self, bundle_id: str
                        ) -> dict:
                            return dict(
                                session.provenance_for(bundle_id) or {}
                            )

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

                self.assertTrue(
                    session.ready, session.refusal_reasons
                )
                self.assertEqual(session.refusal_reasons, ())
                self.assertEqual(
                    {
                        bundle_id: reasons[("phase", "tokenize")]
                        for bundle_id, reasons in (
                            session.path_refusal_reasons.items()
                        )
                    },
                    {
                        bundle_id: (local_reason,)
                        for bundle_id in bundle_ids
                    },
                )
                self.assertTrue(
                    decode.extractable, decode.refusal_reasons
                )
                self.assertFalse(tokenize.extractable)
                self.assertIn(
                    local_reason, tokenize.refusal_reasons
                )
                self.assertTrue(
                    baseline.extractable, baseline.refusal_reasons
                )
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
                self.assertEqual(
                    decode_floor_bytes, baseline_floor_bytes
                )
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
                self.assertEqual(
                    decode_floor_inputs, baseline_floor_inputs
                )
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
            for child in ("tokenize", "decode"):
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

    def test_pre_anchor_summary_without_envelope_map_refuses_globally(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            widened = self._summary(
                10.0,
                bound_s=0.03,
                half_width_j=0.2,
            )
            session = self._prepare_session(
                root,
                {"member": widened},
                include_minted_envelopes=False,
            )

        self.assertFalse(session.ready)
        self.assertEqual(
            session.refusal_reasons, (UNRECORDED_ENVELOPE,)
        )
        self.assertEqual(session.path_refusal_reasons, {})
        self.assertEqual(session._summaries, {})
        self.assertEqual(session._provenance, {})

    def test_unrecorded_anchor_envelope_reason_is_local_and_child_refuses(
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
            decode["reasons"] = [UNRECORDED_ENVELOPE]
            session = self._prepare_session(
                root, {"member": widened}
            )
            report = extract_absolute_cell(
                cell_id="decode",
                metric="phase_energy_j.decode",
                window_class="phase",
                members=[
                    {"slot": "decode-member", "bundle_id": "member"}
                ],
                runs_root=root,
                cooldowns={
                    "member": {
                        "verified": True,
                        "result": "recovered",
                    }
                },
                strict_validator=lambda _path, _strict: (),
                consumption_session=session,
            )

        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertEqual(session.refusal_reasons, ())
        self.assertEqual(
            session.path_refusal_reasons,
            {"member": {("phase", "decode"): (UNRECORDED_ENVELOPE,)}},
        )
        self.assertFalse(report.extractable)
        self.assertIsNone(report.floor)
        self.assertEqual(report.n_admitted, 0)
        self.assertIn(UNRECORDED_ENVELOPE, report.refusal_reasons)
        self.assertEqual(len(report.members), 1)
        self.assertIn(
            UNRECORDED_ENVELOPE, report.members[0].reasons
        )

    def test_unrecorded_anchor_envelope_at_unknown_path_refuses_globally(
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
                "reasons": [UNRECORDED_ENVELOPE],
            }
            session = self._prepare_session(
                root, {"member": widened}
            )

        self.assertFalse(session.ready)
        self.assertEqual(
            session.refusal_reasons, (UNRECORDED_ENVELOPE,)
        )
        self.assertEqual(session.path_refusal_reasons, {})
        self.assertEqual(session._summaries, {})
        self.assertEqual(session._provenance, {})


if __name__ == "__main__":
    unittest.main()
