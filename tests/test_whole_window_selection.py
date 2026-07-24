"""Defect-shaped whole-window selection-consumption regressions."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.whole_window import (
    validated_attempt_selection,
    whole_window_refusal_reasons,
)
from joulewise.analysis_engine.registry import (
    normalized_json_bytes,
    render_dispatch_receipt,
    sha256_bytes,
)
from tests.test_axi_analysis_manifest import AXI_VALID_BUNDLE, evidence_for


class WholeWindowSelectionTests(unittest.TestCase):
    def _real_fixture(self, root: Path):
        _registry, manifest, _raw, _configs, _roster = evidence_for("draft")
        entry = manifest["entries"][0]
        evidence = root / "axi_attempt_evidence" / manifest["manifest_id"]
        receipts_dir = evidence / "dispatch_receipts"
        receipts_dir.mkdir(parents=True)

        def receipt(attempt: int, run_id: str | None, *, failed: bool) -> dict:
            return {
                "schema_version": "joulewise.dispatch_receipt.v1",
                "manifest_id": manifest["manifest_id"],
                "entry_id": entry["entry_id"],
                "pair_id": entry["pair_id"],
                "arm": entry["arm"],
                "attempt_ordinal": attempt,
                "dispatch_started": True,
                "transport_status": "failed" if failed else "ok",
                "process_exit_code": 1 if failed else 0,
                "admitted_request_count": 0 if failed else 1,
                "finalized_run_id": run_id,
            }

        def row(receipt_value: dict, *, failed: bool) -> dict:
            raw = render_dispatch_receipt(receipt_value)
            digest = sha256_bytes(raw)
            (receipts_dir / f"{digest}.json").write_bytes(raw)
            return {
                "schema_version": "joulewise.attempt_ledger.v1",
                "manifest_id": manifest["manifest_id"],
                "entry_id": entry["entry_id"],
                "pair_id": entry["pair_id"],
                "arm": entry["arm"],
                "attempt_ordinal": receipt_value["attempt_ordinal"],
                "run_id": receipt_value["finalized_run_id"],
                "dispatch_receipt_sha256": digest,
                "technical_invalid_reason_code": (
                    "dispatch_failed_before_bundle_creation" if failed else None
                ),
                "reason_evidence_sha256": digest if failed else None,
                "eligible_for_analysis": not failed,
            }

        failed_row = row(receipt(0, None, failed=True), failed=True)
        eligible_row = row(receipt(1, "run-first", failed=False), failed=False)
        bundle = (
            root
            / "axi_attempt_bundles"
            / manifest["manifest_id"]
            / entry["entry_id"]
            / "a1"
            / "run-first"
        )
        shutil.copytree(AXI_VALID_BUNDLE, bundle)
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        metadata["run_id"] = "run-first"
        (bundle / "metadata.json").write_bytes(normalized_json_bytes(metadata))
        manifest_path = evidence / "analysis_manifest.json"
        manifest_path.write_bytes(normalized_json_bytes(manifest))
        ledger_path = evidence / "attempt_ledger.jsonl"

        def write_rows(rows: list[dict]) -> bytes:
            raw = "".join(
                json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
                for value in rows
            ).encode()
            ledger_path.write_bytes(raw)
            return raw

        ledger_raw = write_rows([failed_row, eligible_row])
        selection = {
            "attempt_ledger_path": ledger_path.relative_to(root).as_posix(),
            "attempt_ledger_sha256": hashlib.sha256(ledger_raw).hexdigest(),
            "analysis_manifest_path": manifest_path.relative_to(root).as_posix(),
            "analysis_manifest_sha256": hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest(),
            "selected_bundles": [
                {
                    "bundle_id": f"{entry['entry_id']}__a1__run-first",
                    "path": bundle.relative_to(root).as_posix(),
                    "entry_id": entry["entry_id"],
                    "attempt_ordinal": 1,
                    "run_id": "run-first",
                }
            ],
            "quarantined_attempts": [
                {
                    "entry_id": entry["entry_id"],
                    "attempt_ordinal": 0,
                    "run_id": None,
                    "properly_quarantined": True,
                    "recovery_continuity_verified": True,
                }
            ],
        }
        return selection, failed_row, eligible_row, write_rows, row, receipt

    def _fixture(self, root: Path, *, quarantined_run: str | None = None):
        evidence = root / "axi_attempt_evidence" / "m"
        evidence.mkdir(parents=True)
        row = {
            "entry_id": "e",
            "attempt_ordinal": 0,
            "run_id": "run",
            "eligible_for_analysis": True,
        }
        ledger_raw = (json.dumps(row) + "\n").encode()
        manifest_raw = json.dumps({"manifest_id": "m"}).encode()
        (evidence / "attempt_ledger.jsonl").write_bytes(ledger_raw)
        (evidence / "analysis_manifest.json").write_bytes(manifest_raw)
        selection = {
            "attempt_ledger_path": "axi_attempt_evidence/m/attempt_ledger.jsonl",
            "attempt_ledger_sha256": hashlib.sha256(ledger_raw).hexdigest(),
            "analysis_manifest_path": "axi_attempt_evidence/m/analysis_manifest.json",
            "analysis_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "selected_bundles": [
                {
                    "bundle_id": "e__a0__run",
                    "path": "axi_attempt_bundles/m/e/a0/run",
                    "entry_id": "e",
                    "attempt_ordinal": 0,
                    "run_id": "run",
                }
            ],
            "quarantined_attempts": (
                []
                if quarantined_run is None
                else [
                    {
                        "entry_id": "e",
                        "attempt_ordinal": 0,
                        "run_id": quarantined_run,
                        "properly_quarantined": True,
                        "recovery_continuity_verified": True,
                    }
                ]
            ),
        }
        return selection, row

    def test_authoritative_selection_descriptor_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection, row = self._fixture(Path(tmp))
            with patch(
                "joulewise.whole_window.validate_attempt_ledger",
                return_value={"e": row},
            ):
                self.assertEqual(
                    validated_attempt_selection(selection, Path(tmp)),
                    {"e__a0__run"},
                )

    def test_selected_and_quarantined_membership_must_be_disjoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection, row = self._fixture(Path(tmp), quarantined_run="run")
            with patch(
                "joulewise.whole_window.validate_attempt_ledger",
                return_value={"e": row},
            ):
                self.assertIsNone(validated_attempt_selection(selection, Path(tmp)))

    def test_every_rejected_attempt_must_be_listed_as_quarantined(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, row = self._fixture(root)
            row["eligible_for_analysis"] = False
            ledger = root / selection["attempt_ledger_path"]
            ledger_raw = (json.dumps(row) + "\n").encode()
            ledger.write_bytes(ledger_raw)
            selection["attempt_ledger_sha256"] = hashlib.sha256(
                ledger_raw
            ).hexdigest()
            selection["selected_bundles"] = []
            with patch(
                "joulewise.whole_window.validate_attempt_ledger",
                return_value={"e": None},
            ):
                self.assertIsNone(validated_attempt_selection(selection, root))

    def test_selected_descriptor_must_match_authoritative_first_eligible_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection, row = self._fixture(Path(tmp))
            later = {**row, "attempt_ordinal": 1, "run_id": "later"}
            with patch(
                "joulewise.whole_window.validate_attempt_ledger",
                return_value={"e": later},
            ):
                self.assertIsNone(validated_attempt_selection(selection, Path(tmp)))

    def test_real_validator_rejects_truncated_duplicate_and_reordered_ledgers(self) -> None:
        mutations = {
            "truncated": lambda failed, eligible: [failed],
            "duplicate": lambda failed, eligible: [failed, failed, eligible],
            "reordered": lambda failed, eligible: [eligible, failed],
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                selection, failed, eligible, write_rows, _row, _receipt = (
                    self._real_fixture(root)
                )
                ledger_raw = write_rows(mutate(failed, eligible))
                selection["attempt_ledger_sha256"] = hashlib.sha256(
                    ledger_raw
                ).hexdigest()
                self.assertIsNone(validated_attempt_selection(selection, root))

    def test_real_validator_accepts_complete_first_eligible_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, *_rest = self._real_fixture(root)
            self.assertEqual(
                validated_attempt_selection(selection, root),
                {"draft-off-000__a1__run-first"},
            )

    def test_real_validator_rejects_selection_of_later_eligible_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, failed, eligible, write_rows, make_row, make_receipt = (
                self._real_fixture(root)
            )
            later = make_row(
                make_receipt(2, "run-later", failed=False), failed=False
            )
            first_bundle = root / selection["selected_bundles"][0]["path"]
            later_bundle = first_bundle.parents[1] / "a2" / "run-later"
            shutil.copytree(first_bundle, later_bundle)
            metadata = json.loads((later_bundle / "metadata.json").read_bytes())
            metadata["run_id"] = "run-later"
            (later_bundle / "metadata.json").write_bytes(
                normalized_json_bytes(metadata)
            )
            ledger_raw = write_rows([failed, eligible, later])
            selection["attempt_ledger_sha256"] = hashlib.sha256(
                ledger_raw
            ).hexdigest()
            selection["selected_bundles"][0].update(
                bundle_id="draft-off-000__a2__run-later",
                path=later_bundle.relative_to(root).as_posix(),
                attempt_ordinal=2,
                run_id="run-later",
            )
            self.assertIsNone(validated_attempt_selection(selection, root))

    def test_frozen_neg8_derivation_keeps_committed_direct_resolution(self) -> None:
        # Delta-review P1 regression: selection-custody path resolution is a
        # CURRENT-strict improvement. A frozen row whose NEG-8 references are
        # reachable only through selection custody must keep the committed
        # runs_root/<bundle_id> resolution — the references stay unreadable
        # (None), the derived decision stays 'failed', and a stored 'passed'
        # stays in conflict. current=True may resolve them; current=False
        # must not.
        import tempfile
        from joulewise.whole_window import _derived_neg8_decision

        policy = {
            "require_bracket": True,
            "max_abs_delta_j": 0.05,
            "max_rel_delta": 0.25,
        }
        summary = {
            "gross_energy_j": 5.0,
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": {"point_j": 5.0, "lower_j": 4.9, "upper_j": 5.1}
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for position, bundle_id in (("start", "neg8-s"), ("end", "neg8-e")):
                hidden = root / "axi_attempt_bundles" / "a1" / bundle_id
                hidden.mkdir(parents=True)
                (hidden / "summary_metrics.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )
            manifest = {
                "attempt_ledger_selection": {
                    "selected_bundles": [
                        {
                            "bundle_id": bundle_id,
                            "path": f"axi_attempt_bundles/a1/{bundle_id}",
                        }
                        for bundle_id in ("neg8-s", "neg8-e")
                    ]
                },
                "members": [
                    {
                        "execution": "invoked",
                        "bundle_ids": ["neg8-s"],
                        "role": "neg8_daily_reference_start",
                        "sentinel_position": "start",
                    },
                    {
                        "execution": "invoked",
                        "bundle_ids": ["neg8-e"],
                        "role": "neg8_daily_reference_end",
                        "sentinel_position": "end",
                    },
                ],
            }
            frozen_decision, frozen_problem = _derived_neg8_decision(
                [manifest], root, policy, current=False
            )
        self.assertIsNone(frozen_problem)
        self.assertEqual(frozen_decision, "failed")

    def test_partial_and_full_basis_verdicts_coexist_without_latest_wins(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            partial = {
                "record_type": "idle_admission_whole_window_verdict",
                "bundle_ids": ["A"],
                "evaluation_basis": {
                    "sha256": "partial-basis",
                    "member_occurrences": [{"bundle_id": "A"}],
                },
            }
            full = {
                "record_type": "idle_admission_whole_window_verdict",
                "bundle_ids": ["A", "B"],
                "evaluation_basis": {
                    "sha256": "full-basis",
                    "member_occurrences": [
                        {"bundle_id": "A"},
                        {"bundle_id": "B"},
                    ],
                },
            }
            (root / "campaign_log.jsonl").write_text(
                json.dumps(partial) + "\n" + json.dumps(full) + "\n"
            )
            with patch(
                "joulewise.whole_window._validate_row",
                return_value=(True, ()),
            ) as validate:
                self.assertEqual(
                    whole_window_refusal_reasons(root, {"A", "B"}), ()
                )
            self.assertEqual(validate.call_count, 1)
            self.assertEqual(validate.call_args.args[0], full)

    def test_explicit_claim_basis_selects_only_its_matching_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [
                {
                    "record_type": "idle_admission_whole_window_verdict",
                    "bundle_ids": ["A", "B"],
                    "evaluation_basis": {
                        "sha256": basis,
                        "member_occurrences": [
                            {"bundle_id": "A"},
                            {"bundle_id": "B"},
                        ],
                    },
                }
                for basis in ("older-basis", "claim-basis")
            ]
            (root / "campaign_log.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows)
            )
            with patch(
                "joulewise.whole_window._validate_row",
                return_value=(True, ()),
            ) as validate:
                self.assertEqual(
                    whole_window_refusal_reasons(
                        root,
                        {"A", "B"},
                        evaluation_basis_sha256="claim-basis",
                    ),
                    (),
                )
            self.assertEqual(validate.call_count, 1)
            self.assertEqual(
                validate.call_args.args[0]["evaluation_basis"]["sha256"],
                "claim-basis",
            )


if __name__ == "__main__":
    unittest.main()
