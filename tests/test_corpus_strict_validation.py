"""Read-only strict-validation regression over the retained run corpus."""

from __future__ import annotations

import json
import subprocess
import unittest
import sys
import tempfile
from pathlib import Path
from unittest import mock

from joulewise.analysis_engine.inputs import _read_bundle
from joulewise.bundle_read import BundleReader
from joulewise.clock import FakeClock
from joulewise.cli import _STRICT_LEGACY_BUNDLE_IDENTITIES, validate_bundle
from joulewise.controller import run_benchmark
from joulewise.schemas import BenchmarkConfig


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = REPO_ROOT / "runs"


class RetainedCorpusStrictValidationTests(unittest.TestCase):
    def test_six_frozen_acceptance_gate_bundles_pass_strict_read_only(self) -> None:
        if not RUNS_ROOT.is_dir():
            message = (
                "ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require "
                "the retained runs/ corpus"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)
        bundles = sorted(
            path.parent for path in RUNS_ROOT.rglob("summary_metrics.json")
        )
        self.assertTrue(bundles, "runs/ exists but contains no run bundles")
        by_identity = {}
        for bundle in bundles:
            metadata = json.loads((bundle / "metadata.json").read_text())
            identity = (metadata.get("run_id"), metadata.get("config_sha256"))
            if identity in _STRICT_LEGACY_BUNDLE_IDENTITIES:
                by_identity[identity] = bundle
        self.assertEqual(set(by_identity), set(_STRICT_LEGACY_BUNDLE_IDENTITIES))
        self.assertEqual(len(by_identity), 6)
        failures = {}
        for bundle in by_identity.values():
            problems = validate_bundle(bundle, strict=True)
            if problems:
                failures[str(bundle.relative_to(REPO_ROOT))] = problems
        self.assertEqual(failures, {})

    def test_dirty_unknown_and_changed_provenance_are_hard_excluded_at_admission(self) -> None:
        clean = {
            "git_commit": "1" * 40,
            "tracked": "clean",
            "staged": "clean",
            "untracked": "clean",
            "diff_sha256": "2" * 64,
        }
        cases = {
            "dirty": {
                "start": {**clean, "tracked": "dirty", "diff_sha256": "3" * 64},
                "end": {**clean, "tracked": "dirty", "diff_sha256": "3" * 64},
                "changed_during_run": False,
                "reason_codes": ["start_tracked_dirty", "end_tracked_dirty"],
            },
            "unknown": {
                "start": {
                    "git_commit": "unknown",
                    "tracked": "unknown",
                    "staged": "unknown",
                    "untracked": "unknown",
                    "diff_sha256": "unknown",
                },
                "end": {
                    "git_commit": "unknown",
                    "tracked": "unknown",
                    "staged": "unknown",
                    "untracked": "unknown",
                    "diff_sha256": "unknown",
                },
                "changed_during_run": None,
                "reason_codes": [
                    "start_git_commit_unknown",
                    "start_tracked_unknown",
                    "start_staged_unknown",
                    "start_untracked_unknown",
                    "start_diff_identity_unknown",
                    "end_git_commit_unknown",
                    "end_tracked_unknown",
                    "end_staged_unknown",
                    "end_untracked_unknown",
                    "end_diff_identity_unknown",
                ],
            },
            "changed": {
                "start": clean,
                "end": {**clean, "git_commit": "4" * 40, "diff_sha256": "5" * 64},
                "changed_during_run": True,
                "reason_codes": ["source_changed_during_run"],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "runs"
            for label, case in cases.items():
                with self.subTest(label=label):
                    config_data = json.loads(
                        (REPO_ROOT / "configs/examples/mock_local.json").read_text()
                    )
                    config_data["run_id"] = f"source-{label}"
                    config = BenchmarkConfig.from_mapping(config_data)
                    with mock.patch(
                        "joulewise.bundle._capture_source_state",
                        return_value=dict(clean),
                    ):
                        bundle, _ = run_benchmark(config, runs, FakeClock())
                    metadata_path = bundle / "metadata.json"
                    metadata = json.loads(metadata_path.read_text())
                    metadata["source_provenance"].update(
                        {
                            **case,
                            "claim_eligible": False,
                        }
                    )
                    metadata_path.write_text(
                        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                    self.assertTrue(BundleReader(bundle).is_complete())
                    evidence = _read_bundle(
                        {"entry_id": label},
                        bundle,
                        runs,
                        config_data,
                        validate_bundle,
                    )
                    self.assertEqual(evidence.inclusion_status, "excluded")
                    self.assertIn("bundle_strict_invalid", evidence.base_reason_codes)
                    self.assertTrue(
                        any(
                            "claim-ineligible source provenance" in problem
                            for problem in evidence.strict_problems
                        )
                    )


class CorpusCompatibilityReceiptTests(unittest.TestCase):
    def test_schema_and_conflicting_suite_revocations_are_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            bundle = corpus / "conflicting-suite"
            (bundle / "outputs").mkdir(parents=True)
            (bundle / "summary_metrics.json").write_text(
                json.dumps(
                    {
                        "status": "failed",
                        "failure_reason": "unknown_error",
                        "failure_message": "compatibility fixture",
                        "measurement_quality": {
                            "token_counts_source": "runtime_observed"
                        },
                    }
                )
                + "\n"
            )
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "run_id": "conflicting-suite",
                        "suite": {"suite_id": "fixture"},
                        "workload_observed": {"output_token_count": 2},
                        "workload_provenance": {
                            "output_policy": {
                                "name": "fixed_budget_exact",
                                "requested_tokens": 2,
                                "emitted_tokens": 2,
                                "stop_condition": "suite_completed",
                            },
                            "sampler": {"kind": "greedy"},
                            "tokenizer": {"name": "fixture-tokenizer"},
                        },
                    }
                )
                + "\n"
            )
            events = [
                {
                    "timestamp_s": 0.0,
                    "event_type": "item_start",
                    "phase": "suite",
                    "message": "start",
                    "metadata": {
                        "item_id": "item-0",
                        "item_index": 0,
                        "output_policy": "fixed_budget_exact",
                        "planned_output_tokens": 2,
                    },
                },
                {
                    "timestamp_s": 1.0,
                    "event_type": "item_end",
                    "phase": "suite",
                    "message": "end",
                    "metadata": {
                        "item_id": "item-0",
                        "item_index": 0,
                        "status": "succeeded",
                        "emitted_tokens": 2,
                        "stop_reason": "requested_tokens_emitted",
                    },
                },
            ]
            (bundle / "events.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events)
            )
            (bundle / "outputs" / "suite_items.jsonl").write_text(
                json.dumps(
                    {
                        "item_id": "item-0",
                        "item_index": 0,
                        "status": "failed",
                        "emitted_tokens": 2,
                        "stop_reason": "truncated",
                        "tokens": [{"index": 0}, {"index": 1}],
                        "emitted_token_ids": [10, 11],
                    }
                )
                + "\n"
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "corpus_compat_receipt.py"),
                    str(corpus),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        receipt = json.loads(completed.stdout)
        self.assertEqual(
            set(receipt),
            {"schema_version", "corpus_root", "bundle_count", "bundles", "summary"},
        )
        self.assertEqual(
            receipt["schema_version"], "joulewise.corpus_compat_receipt.v1"
        )
        self.assertEqual(receipt["bundle_count"], 1)
        row = receipt["bundles"][0]
        self.assertEqual(set(row), {"bundle_id", "relative_path", "gates"})
        self.assertEqual(
            set(row["gates"]), {"strict_readable", "exact", "replay", "ratio"}
        )
        for gate in row["gates"].values():
            self.assertEqual(set(gate), {"eligible", "revocation_reasons"})
            self.assertFalse(gate["eligible"])
        self.assertEqual(
            row["gates"]["strict_readable"]["revocation_reasons"],
            ["strict_validation_failed"],
        )
        for gate_name in ("exact", "replay", "ratio"):
            self.assertIn(
                "suite_item_record_marker_conflict",
                row["gates"][gate_name]["revocation_reasons"],
            )
        self.assertIn(
            "output_policy_required",
            row["gates"]["ratio"]["revocation_reasons"],
        )


if __name__ == "__main__":
    unittest.main()
