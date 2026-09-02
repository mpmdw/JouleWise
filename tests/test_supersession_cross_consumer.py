"""Cross-consumer supersession behavior on preserved counterfactual log bytes.

# PRE-CURE EXHIBITION — SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01 phase 1
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
    _basis_source_manifests,
    supersession_entry_sha256,
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
    ) -> list[dict[str, Any]] | None:
        selected_occurrence = fixture.supersessions[supplied_name][
            "selected_occurrence"
        ]
        return _basis_source_manifests(
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
        )

    def test_legacy_log_selects_in_whole_window_while_cooldown_join_refuses(
        self,
    ) -> None:
        fixture = self.fixture()
        before = fixture.log_path.read_bytes()
        s1 = fixture.supersessions["S1"]
        s2 = fixture.supersessions["S2"]
        self.assertTrue(validate_occurrence_supersession_entry(s1, fixture.root))
        self.assertTrue(validate_occurrence_supersession_entry(s2, fixture.root))

        valid_entries = run_campaign_module._valid_supersession_entries(
            fixture.root
        )
        self.assertEqual(valid_entries, [s1, s2])
        selected = run_campaign_module._matching_supersession(
            valid_entries,
            BUNDLE_ID,
            fixture.occurrences,
            POLICY_SHA256,
        )
        self.assertEqual(selected, s2)
        self.assertEqual(selected["selected_occurrence"], fixture.occurrences[2])

        cooldown = campaign_cooldown_evidence(fixture.root)[BUNDLE_ID]
        self.assertEqual(cooldown["result"], "unknown")
        self.assertFalse(cooldown["verified"])
        self.assertIsNone(cooldown["manifest"])
        self.assertEqual(fixture.log_path.read_bytes(), before)

    def test_membership_binding_disposition_on_the_same_fixture(self) -> None:
        fixture = self.fixture()
        before = fixture.log_path.read_bytes()

        selected_manifests = self.membership_binding(fixture, "S2")

        self.assertIsNotNone(selected_manifests)
        assert selected_manifests is not None
        self.assertEqual(len(selected_manifests), 1)
        self.assertEqual(selected_manifests[0]["session_id"], "session-3")
        self.assertEqual(fixture.log_path.read_bytes(), before)

    def test_d093_totals_audit_reports_clean_for_two_valid_same_bundle_rows(
        self,
    ) -> None:
        fixture = self.fixture()

        audit = supersession_visibility_scan(
            fixture.root,
            scope="analysis_corpus",
            evidence_root_id=None,
            authenticated_basis={
                "kind": "whole_window_evaluation_basis_sha256",
                "sha256": "b" * 64,
            },
        )

        self.assertEqual(audit["raw_count"], 2)
        self.assertEqual(audit["validated_count"], 2)
        self.assertEqual(audit["status"], "clean")

    def test_single_valid_row_all_three_consumers_agree(self) -> None:
        fixture = self.fixture(occurrence_count=2, row_names=("S1",))
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

        selected_manifests = self.membership_binding(fixture, "S1")
        self.assertIsNotNone(selected_manifests)
        assert selected_manifests is not None
        self.assertEqual(selected_manifests[0]["session_id"], "session-2")

    def test_truth_table_additional_multiple_row_shapes(self) -> None:
        cases = (
            # name, occurrence count, log rows, governing row, C2 match, C3 session
            ("chained_reverse_order", 3, ("S2", "S1"), "S2", "S2", "session-3"),
            (
                "valid_nonchain",
                3,
                ("S1", "S2_NONCHAIN"),
                "S2_NONCHAIN",
                None,
                None,
            ),
            ("valid_plus_invalid", 2, ("S1", "S1_INVALID"), "S1", "S1", "session-2"),
            ("duplicate_identical", 2, ("S1", "S1"), "S1", None, "session-2"),
        )
        for name, occurrence_count, row_names, supplied, c2_match, c3_session in cases:
            with self.subTest(shape=name):
                fixture = self.fixture(
                    occurrence_count=occurrence_count,
                    row_names=row_names,
                )
                cooldown = campaign_cooldown_evidence(fixture.root)[BUNDLE_ID]
                self.assertFalse(cooldown["verified"])
                self.assertEqual(cooldown["result"], "unknown")

                valid_entries = run_campaign_module._valid_supersession_entries(
                    fixture.root
                )
                selected = run_campaign_module._matching_supersession(
                    valid_entries,
                    BUNDLE_ID,
                    fixture.occurrences,
                    POLICY_SHA256,
                )
                self.assertEqual(
                    selected,
                    fixture.supersessions[c2_match]
                    if c2_match is not None
                    else None,
                )

                selected_manifests = self.membership_binding(fixture, supplied)
                if c3_session is None:
                    self.assertIsNone(selected_manifests)
                else:
                    self.assertIsNotNone(selected_manifests)
                    assert selected_manifests is not None
                    self.assertEqual(selected_manifests[0]["session_id"], c3_session)


if __name__ == "__main__":
    unittest.main()
