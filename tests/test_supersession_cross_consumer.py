"""Cross-consumer supersession behavior on preserved counterfactual log bytes.

# PHASE-2 CURE — SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from joulewise.analysis_engine.inputs import (
    campaign_cooldown_evidence,
    supersession_visibility_scan,
)
from joulewise.campaign_provenance import campaign_provenance_attestation
from joulewise.whole_window import (
    OCCURRENCE_SUPERSESSION_SCHEMA,
    REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS,
    _basis_source_manifests,
    _supersession_is_logged,
    recognizable_occurrence_supersession_counts,
    supersession_entry_sha256,
    supersession_entry_validation_results,
    validate_occurrence_supersession_entry,
)
from scripts import run_campaign as run_campaign_module


BUNDLE_ID = "bundle-X"
POLICY_SHA256 = "a" * 64


@dataclass
class SupersessionFixture:
    temporary: tempfile.TemporaryDirectory
    root: Path
    log_path: Path
    attestation_rows: list[dict[str, Any]]
    manifests: list[dict[str, Any]]
    occurrences: list[dict[str, Any]]
    supersessions: dict[str, dict[str, Any]]


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True) + "\n").encode("utf-8")


def _write_log(fixture: SupersessionFixture, row_names: Sequence[str]) -> None:
    rows = fixture.attestation_rows + [
        fixture.supersessions[name] for name in row_names
    ]
    fixture.log_path.write_bytes(b"".join(_json_bytes(row) for row in rows))


def build_supersession_fixture(
    *,
    occurrence_count: int = 3,
    row_names: Sequence[str] = ("S1", "S2"),
) -> SupersessionFixture:
    """Write a hand-assembled log that the guarded recorder now refuses."""

    if occurrence_count not in {2, 3}:
        raise ValueError("the exhibition fixture supports two or three occurrences")
    temporary = tempfile.TemporaryDirectory(prefix="supersession-divergence-")
    fixture_root = Path(temporary.name)
    root = fixture_root / "runs"
    manifest_dir = root / "campaign_manifests"
    manifest_dir.mkdir(parents=True)
    log_path = root / "campaign_log.jsonl"

    canonical = root / BUNDLE_ID
    quarantine = fixture_root / "quarantine-bundle-X"
    canonical.mkdir()
    quarantine.mkdir()
    custody_hashes: dict[str, str] = {}
    for name, value in (
        ("config.json", {"run_id": BUNDLE_ID}),
        ("metadata.json", {"status": "failed"}),
        ("summary_metrics.json", {"status": "failed"}),
    ):
        raw = _json_bytes(value)
        (canonical / name).write_bytes(raw)
        (quarantine / name).write_bytes(raw)
        custody_hashes[name] = hashlib.sha256(raw).hexdigest()

    manifests: list[dict[str, Any]] = []
    occurrences: list[dict[str, Any]] = []
    attestations: list[dict[str, Any]] = []
    for index in range(1, occurrence_count + 1):
        manifest = {
            "schema_version": "joulewise.campaign_provenance.v2",
            "analysis_manifest_id": None,
            "session_id": f"session-{index}",
            "first_physical_run_id": BUNDLE_ID,
            "members": [
                {
                    "config": f"{BUNDLE_ID}.json",
                    "execution": "invoked",
                    "run_id": BUNDLE_ID,
                    "bundle_ids": [BUNDLE_ID],
                    "preceding_campaign_cooldown": {
                        "result": "first_run_exempt",
                        "session_id": f"session-{index}",
                        "following_run_id": BUNDLE_ID,
                    },
                }
            ],
        }
        manifest_path = manifest_dir / f"{index:02d}.json"
        raw = _json_bytes(manifest)
        manifest_path.write_bytes(raw)
        source = {
            "path": f"campaign_manifests/{manifest_path.name}",
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        manifests.append(manifest)
        occurrences.append(
            {
                "bundle_id": BUNDLE_ID,
                "source_manifest": source,
                "member_index": 0,
                "bundle_index": 0,
            }
        )
        attestations.append(
            campaign_provenance_attestation(
                manifest_path=manifest_path,
                raw_manifest_bytes=raw,
                manifest=manifest,
                timestamp=f"2026-09-01T12:00:0{index}Z",
            )
        )

    def supersession(
        selected_index: int,
        superseded_indices: Sequence[int],
        reason: str,
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "schema_version": OCCURRENCE_SUPERSESSION_SCHEMA,
            "record_type": "campaign_occurrence_supersession",
            "runs_root": str(root.resolve()),
            "bundle_id": BUNDLE_ID,
            "campaign_policy_sha256": POLICY_SHA256,
            "reason": reason,
            "selected_occurrence": occurrences[selected_index - 1],
            "superseded_occurrences": [
                occurrences[index - 1] for index in superseded_indices
            ],
            "quarantine": {
                "path": str(quarantine.resolve()),
                "config_sha256": custody_hashes["config.json"],
                "metadata_sha256": custody_hashes["metadata.json"],
                "summary_sha256": custody_hashes["summary_metrics.json"],
            },
        }
        entry["entry_sha256"] = supersession_entry_sha256(entry)
        return entry

    s1 = supersession(2, (1,), "o1 failed; operator selected o2")
    supersessions = {"S1": s1}
    if occurrence_count == 3:
        supersessions["S2"] = supersession(
            3, (1, 2), "o1 and o2 failed; operator selected o3"
        )
        supersessions["S2_NONCHAIN"] = supersession(
            3, (1,), "counterfactual non-chained selection of o3"
        )
    invalid = dict(s1)
    invalid["entry_sha256"] = "0" * 64
    supersessions["S1_INVALID"] = invalid

    fixture = SupersessionFixture(
        temporary=temporary,
        root=root,
        log_path=log_path,
        attestation_rows=attestations,
        manifests=manifests,
        occurrences=occurrences,
        supersessions=supersessions,
    )
    _write_log(fixture, row_names)
    return fixture


class SupersessionCrossConsumerExhibitionTests(unittest.TestCase):
    def fixture(self, **kwargs: Any) -> SupersessionFixture:
        fixture = build_supersession_fixture(**kwargs)
        self.addCleanup(fixture.temporary.cleanup)
        return fixture

    def membership_binding(
        self, fixture: SupersessionFixture, supplied_name: str
    ) -> tuple[list[dict[str, Any]] | None, tuple[str, ...]]:
        selected_occurrence = fixture.supersessions[supplied_name][
            "selected_occurrence"
        ]
        refusal_reasons: set[str] = set()
        selected = _basis_source_manifests(
            basis={"member_occurrences": [selected_occurrence]},
            verified_sources=[
                (occurrence["source_manifest"], manifest)
                for occurrence, manifest in zip(
                    fixture.occurrences, fixture.manifests, strict=True
                )
            ],
            row={
                "campaign_policy": {"sha256": POLICY_SHA256},
                "occurrence_supersessions": [
                    fixture.supersessions[supplied_name]
                ],
            },
            runs_root=fixture.root,
            refusal_reasons=refusal_reasons,
        )
        return selected, tuple(sorted(refusal_reasons))

    def audit(self, fixture: SupersessionFixture) -> dict[str, Any]:
        return supersession_visibility_scan(
            fixture.root,
            scope="analysis_corpus",
            evidence_root_id=None,
            authenticated_basis={
                "kind": "whole_window_evaluation_basis_sha256",
                "sha256": "b" * 64,
            },
        )

    def assert_multiple_row_refusal(
        self,
        fixture: SupersessionFixture,
        supplied_name: str,
    ) -> None:
        before = fixture.log_path.read_bytes()
        read = supersession_entry_validation_results(fixture.root)
        self.assertIsNotNone(read)
        assert read is not None

        cooldown = campaign_cooldown_evidence(fixture.root)[BUNDLE_ID]
        self.assertEqual(
            cooldown,
            {
                "result": "unknown",
                "verified": False,
                "session_id": None,
                "manifest": None,
                "raw_artifact": None,
            },
        )

        valid_entries = run_campaign_module._valid_supersession_entries(
            fixture.root
        )
        self.assertEqual(valid_entries, [])
        self.assertIsNone(
            run_campaign_module._matching_supersession(
                valid_entries,
                BUNDLE_ID,
                fixture.occurrences,
                POLICY_SHA256,
            )
        )
        resolution = run_campaign_module._resolve_ordinary_occurrence(
            fixture.root,
            BUNDLE_ID,
            fixture.occurrences,
            POLICY_SHA256,
            read,
        )
        self.assertEqual(resolution.status, "ambiguous")
        self.assertIn(
            REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS,
            resolution.refusal_reasons,
        )

        selected_manifests, binding_reasons = self.membership_binding(
            fixture, supplied_name
        )
        self.assertIsNone(selected_manifests)
        self.assertIn(
            REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS,
            binding_reasons,
        )

        audit = self.audit(fixture)
        self.assertEqual(audit["raw_count"], 2)
        self.assertEqual(audit["status"], "refused")
        self.assertEqual(
            audit["findings"],
            [
                {
                    "reason_code": (
                        REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS
                    ),
                    "bundle_ids": [BUNDLE_ID],
                }
            ],
        )
        self.assertEqual(fixture.log_path.read_bytes(), before)

    def test_truth_table_row_1_single_valid_selects_all_consumers(self) -> None:
        fixture = self.fixture(occurrence_count=2, row_names=("S1",))
        before = fixture.log_path.read_bytes()
        s1 = fixture.supersessions["S1"]
        self.assertTrue(validate_occurrence_supersession_entry(s1, fixture.root))

        cooldown = campaign_cooldown_evidence(fixture.root)[BUNDLE_ID]
        self.assertTrue(cooldown["verified"])
        self.assertEqual(cooldown["manifest"], "campaign_manifests/02.json")

        valid_entries = run_campaign_module._valid_supersession_entries(
            fixture.root
        )
        self.assertEqual(valid_entries, [s1])
        self.assertEqual(
            run_campaign_module._matching_supersession(
                valid_entries,
                BUNDLE_ID,
                fixture.occurrences,
                POLICY_SHA256,
            ),
            s1,
        )

        read = supersession_entry_validation_results(fixture.root)
        self.assertIsNotNone(read)
        assert read is not None
        resolution = run_campaign_module._resolve_ordinary_occurrence(
            fixture.root,
            BUNDLE_ID,
            fixture.occurrences,
            POLICY_SHA256,
            read,
        )
        self.assertEqual(resolution.status, "selected")
        self.assertEqual(resolution.selected_occurrence, fixture.occurrences[1])
        self.assertEqual(resolution.refusal_reasons, ())

        selected_manifests, binding_reasons = self.membership_binding(
            fixture, "S1"
        )
        self.assertIsNotNone(selected_manifests)
        assert selected_manifests is not None
        self.assertEqual(selected_manifests[0]["session_id"], "session-2")
        self.assertEqual(binding_reasons, ())
        audit = self.audit(fixture)
        self.assertEqual(audit["raw_count"], 1)
        self.assertEqual(audit["validated_count"], 1)
        self.assertEqual(audit["status"], "clean")
        self.assertNotIn("findings", audit)
        self.assertEqual(fixture.log_path.read_bytes(), before)

    def test_truth_table_row_2_two_valid_chained_refuses_all_consumers(self) -> None:
        self.assert_multiple_row_refusal(self.fixture(), "S2")

    def test_truth_table_row_3_valid_nonchain_refuses_all_consumers(self) -> None:
        self.assert_multiple_row_refusal(
            self.fixture(row_names=("S1", "S2_NONCHAIN")),
            "S2_NONCHAIN",
        )

    def test_truth_table_row_4_valid_plus_invalid_refuses_all_consumers(self) -> None:
        self.assert_multiple_row_refusal(
            self.fixture(
                occurrence_count=2,
                row_names=("S1", "S1_INVALID"),
            ),
            "S1",
        )

    def test_truth_table_row_5_identical_duplicates_refuse_all_consumers(self) -> None:
        self.assert_multiple_row_refusal(
            self.fixture(occurrence_count=2, row_names=("S1", "S1")),
            "S1",
        )

    def test_truth_table_row_6_reverse_order_refuses_all_consumers(self) -> None:
        self.assert_multiple_row_refusal(
            self.fixture(row_names=("S2", "S1")),
            "S2",
        )

    def test_mutation_m1_matching_never_restores_latest_wins(self) -> None:
        fixture = self.fixture()
        self.assertIsNone(
            run_campaign_module._matching_supersession(
                [fixture.supersessions["S1"], fixture.supersessions["S2"]],
                BUNDLE_ID,
                fixture.occurrences,
                POLICY_SHA256,
            )
        )

    def test_mutation_m2_binding_never_uses_existence_only_membership(self) -> None:
        fixture = self.fixture(occurrence_count=2, row_names=("S1", "S1"))
        refusal_reasons: set[str] = set()
        self.assertFalse(
            _supersession_is_logged(
                fixture.supersessions["S1"],
                fixture.root,
                refusal_reasons,
            )
        )
        self.assertEqual(
            refusal_reasons,
            {REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS},
        )

    def test_mutation_m3_d093_never_drops_multiple_row_finding(self) -> None:
        fixture = self.fixture()
        self.assertEqual(
            self.audit(fixture)["findings"][0]["reason_code"],
            REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS,
        )

    def test_mutation_m4_all_consumers_share_reason_constant(self) -> None:
        fixture = self.fixture()
        read = supersession_entry_validation_results(fixture.root)
        self.assertIsNotNone(read)
        assert read is not None
        resolution = run_campaign_module._resolve_ordinary_occurrence(
            fixture.root,
            BUNDLE_ID,
            fixture.occurrences,
            POLICY_SHA256,
            read,
        )
        _selected, binding_reasons = self.membership_binding(fixture, "S2")
        reported = self.audit(fixture)["findings"][0]["reason_code"]
        self.assertEqual(
            {
                *resolution.refusal_reasons,
                *binding_reasons,
                reported,
            },
            {REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS},
        )

    def test_mutation_m5_recognizable_count_includes_invalid_rows(self) -> None:
        fixture = self.fixture(
            occurrence_count=2,
            row_names=("S1", "S1_INVALID"),
        )
        self.assertEqual(
            recognizable_occurrence_supersession_counts(
                [
                    fixture.supersessions["S1"],
                    fixture.supersessions["S1_INVALID"],
                ]
            ),
            {BUNDLE_ID: 2},
        )

    def test_mutation_m6_recognizable_count_preserves_identical_rows(self) -> None:
        fixture = self.fixture(occurrence_count=2, row_names=("S1", "S1"))
        entry = fixture.supersessions["S1"]
        self.assertEqual(
            recognizable_occurrence_supersession_counts([entry, entry]),
            {BUNDLE_ID: 2},
        )


if __name__ == "__main__":
    unittest.main()
