"""The floor binder reads executed members from a campaign log's member rows only.

Block-5 defect D5 (docs/analysis/b5/DEVIATION-LOG.md, DLE-4): the runner's
campaign log carries per-member rows (``scripts/run_campaign.py`` ``log_row``,
which writes no ``record_type``) and campaign-level records that each carry a
``record_type``. The in-runner whole-window evaluation
(``idle_admission_whole_window_verdict``) lists the campaign's bundles in
``bundle_ids``. The binder used to count that list as executed members too, so
every calibration bundle appeared twice and every floor cell whose log carries
the evaluation was left unbound ("does not bind every calibration bundle exactly
once"). Synthetic data only; the row shapes mirror the writers' key sets.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.analysis_engine import inputs


ROOT_ID = "evidence-synthetic-floor-v5"
EXACTLY_ONCE = "does not bind every calibration bundle exactly once"
ABSOLUTE = tuple(f"syn-floor-abs-r{index:02d}" for index in range(1, 6))
BLOCKS = tuple(
    tuple(f"syn-floor-b{block}-{label}" for label in ("A1", "B1", "B2", "A2"))
    for block in range(1, 3)
)
REFUSED = ("syn-floor-refused-r01", "syn-floor-refused-r02")
TIMESTAMP = "2000-01-01T00:00:00Z"


def _attestation_row(index: int) -> dict:
    return {
        "schema_version": "joulewise.campaign_provenance_attestation.v1",
        "record_type": "campaign_provenance_attestation",
        "timestamp": TIMESTAMP,
        "campaign_provenance_manifest": f"campaign_manifests/session-{index}.json",
        "campaign_provenance_manifest_sha256": "0" * 64,
        "campaign_provenance_schema_version": "joulewise.campaign_provenance.v2",
        "campaign_provenance_session_id": f"session-{index}",
    }


def _member_row(run_id: str, run_index: int, *, status: str = "ok") -> dict:
    """``log_row`` plus the invoked member's extra fields; no ``record_type``."""

    row = {
        "timestamp": TIMESTAMP,
        "config": f"configs/{run_id}.json",
        "run_id": run_id,
        "status": status,
        "exit_code": 0 if status == "ok" else 3,
        "duration_s": 1.5,
        "run_index": run_index,
        "executed_order": {"index": run_index, "config": f"{run_id}.json", "run_id": run_id},
        "model_load_boundary": run_index == 1,
        "members": [{"bundle_id": run_id, "status": status}],
        "preceding_campaign_cooldown": None,
        "campaign_provenance_manifest": "campaign_manifests/session-1.json",
        "child_stderr": f"logs/{run_id}.stderr",
    }
    if status == "failed":
        row["child_refusal"] = "refused: idle admission"
    return row


def _verdict_row() -> dict:
    return {
        "schema_version": "joulewise.campaign_verdict.v1",
        "timestamp": TIMESTAMP,
        "record_type": "campaign_verdict",
        "status": "verdict",
        "collection": "usable",
        "counts": {"ok": 1},
        "provisional": False,
        "strict_validation": "passed",
        "analysis_manifest": None,
        "campaign_provenance": None,
        "idle_admission_core": None,
    }


def _evaluation_row(bundle_ids: list[str]) -> dict:
    """The in-runner whole-window evaluation (run_campaign.py whole_row)."""

    return {
        "schema_version": "joulewise.idle_admission_whole_window.v1",
        "timestamp": TIMESTAMP,
        "record_type": "idle_admission_whole_window_verdict",
        "status": "passed",
        "claim_licensing": True,
        "runs_dir": "runs",
        "evaluation_scope": {"runs_root": "runs", "started_at": TIMESTAMP, "completed_at": TIMESTAMP},
        "evaluation_basis": {"sha256": "1" * 64, "member_occurrences": []},
        "campaign_policy": {},
        "bundle_ids": list(bundle_ids),
        "waived_bundles": [],
        "occurrence_supersessions": [],
        "excluded_bundles": [],
        "member_failures": [],
        "source_campaign_manifests": [],
        "idle_admission_core": {},
        "row_provenance": {},
        "window_membership": {},
    }


def gamma_shaped_log() -> list[dict]:
    """Attestations, refused and executed member rows, verdicts, then the evaluation."""

    rows = [_attestation_row(index) for index in range(1, 4)]
    run_index = 0
    for refused in REFUSED[:1]:
        run_index += 1
        rows.append(_member_row(refused, run_index, status="failed"))
    executed = [*ABSOLUTE, *(member for block in BLOCKS for member in block)]
    for bundle_id in executed:
        run_index += 1
        rows.append(_member_row(bundle_id, run_index))
        rows.append(_attestation_row(run_index + 10))
    for refused in REFUSED[1:]:
        run_index += 1
        rows.append(_member_row(refused, run_index, status="failed"))
    rows.extend(_verdict_row() for _ in range(3))
    rows.append(_evaluation_row(executed))
    return rows


class _Evidence:
    def __init__(self, root: Path, campaign_rows: list[dict]):
        self.root = root
        executed = [*ABSOLUTE, *(member for block in BLOCKS for member in block)]
        order = {"manifest_id": "syn-floor-order", "executed_order": [{"run_id": item} for item in executed]}
        order_raw = (json.dumps(order, sort_keys=True) + "\n").encode()
        log_raw = "".join(json.dumps(row, sort_keys=True) + "\n" for row in campaign_rows).encode()
        (root / "order_manifest.json").write_bytes(order_raw)
        (root / "campaign_log.jsonl").write_bytes(log_raw)
        pins = {
            "evidence_root_id": ROOT_ID,
            "order_manifest": {"manifest_id": "syn-floor-order", "sha256": hashlib.sha256(order_raw).hexdigest()},
            "campaign_log": {"sha256": hashlib.sha256(log_raw).hexdigest()},
        }
        self.artifact = {
            # Multi-producer provenance with no producer plan for the cell keeps
            # the order manifest at the evidence root; only the order checks run.
            "provenance": {"producer_calibration_plans": []},
            "cells": [{
                "cell_id": "syn-floor-cell",
                "absolute": {"bundle_observations": [{"bundle_id": item} for item in ABSOLUTE]},
                "comparative": {"blocks": [
                    {"members": [{"bundle_id": item} for item in block]} for block in BLOCKS
                ]},
                "provenance": {"absolute": dict(pins), "comparative": dict(pins)},
            }],
        }

    def problems(self) -> tuple[str, ...]:
        return inputs._campaign_order_binding_problems(
            self.artifact, self.root / "floor.json", {ROOT_ID: self.root}, {},
        )


class CampaignLogMemberParseTests(unittest.TestCase):
    def evidence(self, rows: list[dict]) -> _Evidence:
        temporary = tempfile.TemporaryDirectory(prefix="campaign-log-members-")
        self.addCleanup(temporary.cleanup)
        return _Evidence(Path(temporary.name), rows)

    def test_gamma_shaped_log_with_trailing_evaluation_binds(self):
        rows = gamma_shaped_log()
        self.assertEqual(sum(1 for row in rows if "bundle_ids" in row), 1)
        self.assertEqual(self.evidence(rows).problems(), ())

    def test_member_ids_skip_every_campaign_level_record(self):
        rows = gamma_shaped_log()
        members = inputs._order_member_ids(rows, campaign_log=True)
        self.assertEqual(
            members,
            [REFUSED[0], *ABSOLUTE, *(member for block in BLOCKS for member in block), REFUSED[1]],
        )
        # Campaign-level records naming a member are not executed members either.
        shakedown = {"timestamp": TIMESTAMP, "record_type": "shakedown_gate", "gate": "g",
                     "status": "failed", "bundle_id": ABSOLUTE[0], "code": "c", "detail": "d"}
        stop = {"record_type": "campaign_stop", "run_id": ABSOLUTE[1], "status": "stopped"}
        self.assertEqual(inputs._order_member_ids([*rows, shakedown, stop], campaign_log=True), members)

    def test_duplicate_executed_member_row_still_refuses(self):
        rows = gamma_shaped_log()
        duplicate = next(row for row in rows if row.get("run_id") == BLOCKS[0][1])
        rows.insert(len(rows) - 1, dict(duplicate))
        problems = self.evidence(rows).problems()
        self.assertTrue(problems)
        self.assertTrue(all(EXACTLY_ONCE in problem for problem in problems), problems)
        self.assertTrue(all(problem.startswith("component_evidence_root_disagreement:") for problem in problems))

    def test_failed_member_row_still_counts_as_an_executed_attempt(self):
        rows = gamma_shaped_log()
        index = next(i for i, row in enumerate(rows) if row.get("run_id") == ABSOLUTE[2])
        rows.insert(index, _member_row(ABSOLUTE[2], 0, status="failed"))
        problems = self.evidence(rows).problems()
        self.assertTrue(any("campaign_log " + EXACTLY_ONCE in problem for problem in problems), problems)

    def test_order_manifest_branch_is_unchanged(self):
        # The order manifest's executed_order has no campaign-level records; its
        # parse is untouched, so even a row carrying record_type still counts.
        order = {"executed_order": [{"run_id": "a"}, {"record_type": "x", "bundle_ids": ["b", "c"]}]}
        self.assertEqual(inputs._order_member_ids(order, campaign_log=False), ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
