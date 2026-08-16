"""Two-scope authenticated whole-window consumption regressions."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import joulewise.arm_readiness as arm_readiness
from joulewise.arm_readiness import LaunchLineageError
from joulewise.floor_extraction import extract_absolute_cell
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
)
from joulewise.whole_window import AuthenticatedConsumptionSession
from joulewise.whole_window import (
    ADAPTER_CONTINUITY_SCHEMA,
    IDLE_ADMISSION_CORE_SCHEMA,
    MEMBER_FAILURE_DETAIL_MAX_CHARS,
    NEG8_BRACKET_SCHEMA,
    WHOLE_WINDOW_SCHEMA,
    WHOLE_WINDOW_SEMANTIC_IDENTITY_KEYS,
    _authenticate_whole_window_launch_sources,
    _calibration_launch_lineages,
    _validate_row,
    _validated_member_failures,
    _whole_window_semantic_identity,
    build_evaluation_basis,
    build_row_provenance,
    canonical_sha256,
    launch_lineage_refusal_reasons,
    mint_neg8_drift_bound_artifact,
    whole_window_refusal_reasons,
)
from joulewise.campaign_provenance import (
    campaign_provenance_attestation,
    load_authenticated_campaign_catalog,
)
from tests.test_calibration_bracketing import _fixture_snapshot
from tests.test_arm_readiness import LaunchConsumptionV2Tests
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID


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
        session = AuthenticatedConsumptionSession(
            root,
            {"member"},
            calibration_ledger_snapshot=CalibrationLedgerSnapshot(
                ledger_schema=LEDGER_SCHEMA,
                ledger_path=Path("fixture-ledger.jsonl"),
                head_sequence=0,
                head_digest=GENESIS_DIGEST,
                receipts=(),
                observations=(),
                refusal_reasons=(),
            ),
        )
        session._prepared = True
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
            return _validate_row(
                row,
                root,
                {"member"},
                consumption_session=session,
            )

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

    def test_present_empty_member_failures_validates_but_absent_is_legacy(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = self._verdict_fixture(
                root,
                schema_version="joulewise.campaign_provenance.v2",
                attest=True,
            )
            self.assertIsNone(_validated_member_failures(legacy))
            enriched = copy.deepcopy(legacy)
            enriched["member_failures"] = []
            self.assertEqual(_validated_member_failures(enriched), [])
            ok, reasons = self._validate(enriched, root)

        self.assertTrue(ok, reasons)
        self.assertEqual(reasons, ())

    def test_malformed_present_member_failures_invalidates_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = self._verdict_fixture(
                root,
                schema_version="joulewise.campaign_provenance.v2",
                attest=True,
            )
            row["member_failures"] = [
                {
                    "member_id": "foreign-member",
                    "reason_code": "cpu_busy_ratio_p95_exceeded",
                    "detail": "foreign member",
                }
            ]
            ok, reasons = self._validate(row, root)

        self.assertFalse(ok)
        self.assertIn("whole_window_verdict_provenance_invalid", reasons)


class ProspectiveMemberFailureValidationTests(unittest.TestCase):
    @staticmethod
    def _row() -> dict:
        return {
            "bundle_ids": ["included-member"],
            "excluded_bundles": [{"bundle_id": "excluded-member"}],
            "waived_bundles": [{"bundle_id": "waived-member"}],
        }

    @staticmethod
    def _failure(member_id: str, reason_code: str, detail: str) -> dict:
        return {
            "member_id": member_id,
            "reason_code": reason_code,
            "detail": detail,
        }

    def test_six_key_semantic_identity_projection_is_frozen(self) -> None:
        self.assertEqual(
            WHOLE_WINDOW_SEMANTIC_IDENTITY_KEYS,
            (
                "status",
                "bundle_ids",
                "campaign_policy",
                "idle_admission_core",
                "row_provenance",
                "evaluation_basis",
            ),
        )
        row = {
            key: {"fixture": key}
            for key in WHOLE_WINDOW_SEMANTIC_IDENTITY_KEYS
        }
        row["bundle_ids"] = ["z", "a"]
        row["member_failures"] = []
        projection = _whole_window_semantic_identity(row)
        self.assertEqual(tuple(projection), WHOLE_WINDOW_SEMANTIC_IDENTITY_KEYS)
        self.assertEqual(projection["bundle_ids"], ["a", "z"])
        self.assertNotIn("member_failures", projection)

    def test_valid_member_failures_cover_included_excluded_and_waived_ids(
        self,
    ) -> None:
        row = self._row()
        row["member_failures"] = [
            self._failure(
                "excluded-member",
                "whole_window_bundle_invalid",
                "strict validation failed",
            ),
            self._failure(
                "included-member",
                "cpu_busy_ratio_p95_exceeded",
                "cpu p95 exceeded",
            ),
            self._failure(
                "waived-member",
                "environment_admission_failed",
                "environment validation failed",
            ),
        ]

        self.assertEqual(
            _validated_member_failures(row), row["member_failures"]
        )

    def test_malformed_present_member_failure_shapes_are_rejected(self) -> None:
        valid = self._failure(
            "included-member",
            "cpu_busy_ratio_p95_exceeded",
            "cpu p95 exceeded",
        )
        cases = {
            "wrong_type": "not-a-list",
            "missing_key": [
                {
                    "member_id": "included-member",
                    "reason_code": "cpu_busy_ratio_p95_exceeded",
                }
            ],
            "duplicate_pair": [valid, dict(valid)],
            "foreign_member": [
                {**valid, "member_id": "foreign-member"}
            ],
            "invalid_reason_spelling": [
                {**valid, "reason_code": "CPU-Busy"}
            ],
            "undeclared_reason": [
                {**valid, "reason_code": "future_reason"}
            ],
            "unsorted": [
                self._failure(
                    "waived-member",
                    "environment_admission_failed",
                    "environment validation failed",
                ),
                valid,
            ],
            "empty_detail": [{**valid, "detail": ""}],
            "oversized_detail": [
                {
                    **valid,
                    "detail": "x" * (MEMBER_FAILURE_DETAIL_MAX_CHARS + 1),
                }
            ],
        }
        for name, member_failures in cases.items():
            with self.subTest(case=name):
                row = self._row()
                row["member_failures"] = member_failures
                self.assertIsNone(_validated_member_failures(row))

    def test_same_basis_legacy_and_enriched_rows_do_not_conflict(self) -> None:
        legacy = {
            "record_type": "idle_admission_whole_window_verdict",
            "status": "passed",
            "bundle_ids": ["member"],
            "campaign_policy": {"sha256": "a" * 64},
            "idle_admission_core": {"same": True},
            "row_provenance": {"same": True},
            "evaluation_basis": None,
        }
        enriched = copy.deepcopy(legacy)
        enriched["member_failures"] = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "campaign_log.jsonl").write_text(
                json.dumps(legacy) + "\n" + json.dumps(enriched) + "\n",
                encoding="utf-8",
            )
            with patch(
                "joulewise.whole_window._validate_row",
                return_value=(True, ()),
            ):
                reasons = whole_window_refusal_reasons(root, {"member"})

        self.assertEqual(reasons, ())


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

        calibration_snapshot, _candidates = _fixture_snapshot([])
        session = AuthenticatedConsumptionSession(
            root,
            set(widened_by_bundle),
            calibration_ledger_snapshot=calibration_snapshot,
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


class LaunchLineageWholeWindowTests(unittest.TestCase):
    @staticmethod
    def _lineage(*, plan_id: str = "plan-1") -> dict:
        return {
            "schema_version": "joulewise.launch_lineage.v1",
            "collection_boot_session_id": (
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
            ),
            "pack_id": "pack-1",
            "plan_id": plan_id,
            "window_id": "window-1",
            "bracket_session_id": "bracket-1",
            "consumption": {"path": "/consume.json", "sha256": "a" * 64},
            "start": {"path": "/start.json", "sha256": "b" * 64},
            "settle": {"path": "/settle.json", "sha256": "c" * 64},
            "completion": None,
        }

    @staticmethod
    def _write_bundle(root: Path, bundle_id: str, *, marker: bool) -> Path:
        path = root / bundle_id
        path.mkdir()
        tags = ["launch_lineage_required"] if marker else []
        (path / "config.json").write_text(
            json.dumps({"run_metadata": {"tags": tags}}) + "\n",
            encoding="utf-8",
        )
        (path / "metadata.json").write_text("{}\n", encoding="utf-8")
        return path

    def _completed_launch(self) -> tuple[LaunchConsumptionV2Tests, dict]:
        launch = LaunchConsumptionV2Tests()
        launch.setUp()
        self.addCleanup(launch.doCleanups)
        consumption_path, settled = launch._settle()
        with patch.object(
            arm_readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            arm_readiness.record_launch_lifecycle_event(
                launch.pack,
                consumption_path,
                "completion",
            )
        return launch, settled["launch_lineage"]

    @staticmethod
    def _write_authenticated_marker_bundle(
        launch: LaunchConsumptionV2Tests,
        lineage: dict,
        bundle_id: str,
    ) -> tuple[Path, dict]:
        runs_root = Path(launch.arm["arm_context"]["claim_runs_root"])
        bundle = runs_root / bundle_id
        bundle.mkdir()
        (bundle / "config.json").write_text(
            json.dumps(
                {"run_metadata": {"tags": ["launch_lineage_required"]}}
            )
            + "\n",
            encoding="utf-8",
        )
        locator_path = runs_root / arm_readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        (bundle / "metadata.json").write_text(
            json.dumps(
                {
                    "extra": {
                        "launch_lineage": lineage,
                        "launch_lineage_locator_sha256": hashlib.sha256(
                            locator_path.read_bytes()
                        ).hexdigest(),
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return runs_root, {
            "bundle_id": bundle_id,
            "bundle_path": bundle_id,
        }

    @staticmethod
    def _write_calibration_bracket(
        root: Path,
        lineage: dict,
    ) -> dict:
        bracket: dict[str, dict] = {}
        for role in ("pre", "post"):
            custody = root / f"calibration-{role}"
            custody.mkdir()
            raw = json.dumps({"launch_lineage": lineage}).encode("utf-8")
            (custody / "instrument_evidence.json").write_bytes(raw)
            bracket[role] = {
                "relative_path": str(custody),
                "evidence_sha256": hashlib.sha256(raw).hexdigest(),
            }
        bracket["pre"]["bracket_runs_root"] = str(root)
        return bracket

    @classmethod
    def _write_neg8_corpus(
        cls,
        root: Path,
        *,
        mixed: bool = False,
    ) -> tuple[Path, dict]:
        lineage = cls._lineage()
        members = []
        for index in range(10):
            bundle_id = f"member-{index}"
            path = cls._write_bundle(root, bundle_id, marker=True)
            stamped = (
                cls._lineage(plan_id="plan-2")
                if mixed and index == 9
                else lineage
            )
            (path / "metadata.json").write_text(
                json.dumps({"extra": {"launch_lineage": stamped}}) + "\n",
                encoding="utf-8",
            )
            (path / "summary_metrics.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            members.append(
                {"bundle_id": bundle_id, "bundle_path": bundle_id}
            )
        manifest_path = root / "neg8-corpus.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.neg8_reference_corpus.v1",
                    "corpus_id": "launch-lineage-corpus",
                    "freeze_status": "settled_reference",
                    "condition_id": "df-rq-mid",
                    "members": members,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return manifest_path, lineage

    @staticmethod
    def _neg8_patches():
        def reference(path: Path):
            value = 10.0 + float(path.name.rsplit("-", 1)[1])
            return (
                {"point_j": value, "lower_j": value, "upper_j": value},
                value - 1.0,
                None,
            )

        return (
            patch(
                "joulewise.whole_window.authenticate_bundle_launch_lineage",
                return_value={"authenticated": True},
            ),
            patch(
                "joulewise.whole_window._custody_strict_invalid",
                return_value=False,
            ),
            patch(
                "joulewise.whole_window._current_strict_summary",
                return_value=True,
            ),
            patch(
                "joulewise.whole_window._scientific_config_identity",
                return_value=("d" * 64, True),
            ),
            patch(
                "joulewise.whole_window._reference_energy_evidence",
                side_effect=reference,
            ),
            patch(
                "joulewise.whole_window.neg8_freshness_bindings_from_metadata",
                return_value={
                    "os_build": "fixture-os",
                    "power_supply_identity_sha256": "e" * 64,
                    "calibration_identity_sha256": "f" * 64,
                },
            ),
            patch(
                "joulewise.whole_window._bundle_evidence_sha256",
                return_value="1" * 64,
            ),
        )

    def test_neg8_bound_refuses_marker_without_direct_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _lineage = self._write_neg8_corpus(root)
            (root / "member-0" / "metadata.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "launch_consumption_missing",
            ):
                mint_neg8_drift_bound_artifact(root, manifest_path)

    def test_neg8_bound_authenticates_every_member_and_seals_full_lineage(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, lineage = self._write_neg8_corpus(root)
            patches = self._neg8_patches()
            with ExitStack() as stack:
                authenticate = stack.enter_context(patches[0])
                for candidate in patches[1:]:
                    stack.enter_context(candidate)
                artifact = mint_neg8_drift_bound_artifact(root, manifest_path)

        self.assertEqual(authenticate.call_count, 10)
        self.assertEqual(artifact["launch_lineage"], lineage)

    def test_neg8_bound_refuses_mixed_full_lineages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _lineage = self._write_neg8_corpus(
                root,
                mixed=True,
            )
            patches = self._neg8_patches()
            with ExitStack() as stack:
                for candidate in patches:
                    stack.enter_context(candidate)
                with self.assertRaisesRegex(
                    ValueError,
                    "launch_lineage_conflict",
                ):
                    mint_neg8_drift_bound_artifact(root, manifest_path)

    def test_member_set_refuses_marker_legacy_mix(self) -> None:
        lineage = self._lineage()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_bundle(root, "marker", marker=True)
            self._write_bundle(root, "legacy", marker=False)

            def authenticate(_path, *, config, **_kwargs):
                tags = config.get("run_metadata", {}).get("tags", [])
                return (
                    {"launch_lineage": lineage}
                    if "launch_lineage_required" in tags
                    else None
                )

            with patch(
                "joulewise.whole_window.authenticate_bundle_launch_lineage",
                side_effect=authenticate,
            ):
                reasons = launch_lineage_refusal_reasons(
                    root,
                    {"marker", "legacy"},
                    require_completion=False,
                )

        self.assertEqual(reasons, ("launch_lineage_conflict",))

    def test_completion_required_boundary_preserves_registered_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_bundle(root, "marker", marker=True)
            with patch(
                "joulewise.whole_window.authenticate_bundle_launch_lineage",
                side_effect=LaunchLineageError(
                    "launch_lifecycle_incomplete",
                    "completion absent",
                ),
            ):
                reasons = launch_lineage_refusal_reasons(
                    root,
                    {"marker"},
                    require_completion=True,
                )

        self.assertEqual(reasons, ("launch_lifecycle_incomplete",))

    def test_verdict_sources_require_members_calibrations_and_bound_to_match(
        self,
    ) -> None:
        lineage = self._lineage()
        with (
            patch(
                "joulewise.whole_window._calibration_launch_lineages",
                return_value=(lineage, lineage),
            ),
            patch(
                "joulewise.whole_window.authenticate_launch_lineage",
                side_effect=lambda value, **_kwargs: {
                    "launch_lineage": value
                },
            ),
        ):
            common = _authenticate_whole_window_launch_sources(
                lineage,
                calibration_bracket={"pre": {}, "post": {}},
                drift_bound_artifact={"launch_lineage": lineage},
                require_completion=True,
                require_bound=True,
            )
            with self.assertRaisesRegex(
                LaunchLineageError,
                "members, calibrations, and bound",
            ):
                _authenticate_whole_window_launch_sources(
                    lineage,
                    calibration_bracket={"pre": {}, "post": {}},
                    drift_bound_artifact={
                        "launch_lineage": self._lineage(plan_id="plan-2")
                    },
                    require_completion=True,
                    require_bound=True,
                )

        self.assertEqual(common, lineage)

    def test_verdict_reopens_both_calibration_receipts_with_completion(self) -> None:
        lineage = self._lineage()
        bracket = {}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for role in ("pre", "post"):
                custody = root / role
                custody.mkdir()
                raw = json.dumps({"launch_lineage": lineage}).encode("utf-8")
                (custody / "instrument_evidence.json").write_bytes(raw)
                bracket[role] = {
                    "relative_path": str(custody),
                    "evidence_sha256": hashlib.sha256(raw).hexdigest(),
                }
            with patch(
                "joulewise.whole_window.authenticate_launch_lineage",
                side_effect=lambda value, **_kwargs: {
                    "launch_lineage": value
                },
            ) as authenticate:
                observed = _calibration_launch_lineages(
                    bracket,
                    require_completion=True,
                )

        self.assertEqual(observed, (lineage, lineage))
        self.assertEqual(authenticate.call_count, 2)
        self.assertTrue(
            all(
                call.kwargs["require_completion"] is True
                for call in authenticate.call_args_list
            )
        )

    def test_evaluation_basis_carries_full_lineage_only_when_authenticated(
        self,
    ) -> None:
        lineage = self._lineage()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "member").mkdir()
            occurrences = [{"bundle_id": "member", "bundle_path": "member"}]
            bracket = {
                "pre": {"bracket_runs_root": str(root)},
                "post": {"bracket_runs_root": str(root)},
            }
            with (
                patch(
                    "joulewise.whole_window._authenticated_bundle_launch_lineage_set",
                    return_value=lineage,
                ),
                patch(
                    "joulewise.whole_window._authenticate_whole_window_launch_sources",
                    return_value=lineage,
                ),
            ):
                basis = build_evaluation_basis(
                    policy_sha256="d" * 64,
                    member_occurrences=occurrences,
                    calibration_bracket=bracket,
                )
            legacy = build_evaluation_basis(
                policy_sha256="d" * 64,
                member_occurrences=occurrences,
                calibration_bracket=None,
            )

        self.assertEqual(basis["launch_lineage"], lineage)
        self.assertEqual(
            basis["sha256"],
            canonical_sha256(
                {key: value for key, value in basis.items() if key != "sha256"}
            ),
        )
        self.assertNotIn("launch_lineage", legacy)

    def test_verdict_issuance_refuses_real_mismatched_bound_lineage(self) -> None:
        launch, lineage = self._completed_launch()
        runs_root, occurrence = self._write_authenticated_marker_bundle(
            launch,
            lineage,
            "member",
        )
        bracket = self._write_calibration_bracket(runs_root, lineage)
        other_launch, other_lineage = self._completed_launch()
        pack_records = {
            launch.pack.resolve(): launch.arm["pack"],
            other_launch.pack.resolve(): other_launch.arm["pack"],
        }
        with patch.object(
            arm_readiness,
            "_pack_record",
            side_effect=lambda root: pack_records[Path(root).resolve()],
        ):
            matching = build_evaluation_basis(
                policy_sha256="d" * 64,
                member_occurrences=[occurrence],
                calibration_bracket=bracket,
                drift_bound_artifact={"launch_lineage": lineage},
            )
            self.assertEqual(matching["launch_lineage"], lineage)

            with self.assertRaisesRegex(
                LaunchLineageError,
                "members, calibrations, and bound",
            ):
                build_evaluation_basis(
                    policy_sha256="d" * 64,
                    member_occurrences=[occurrence],
                    calibration_bracket=bracket,
                    drift_bound_artifact={"launch_lineage": other_lineage},
                )


if __name__ == "__main__":
    unittest.main()
