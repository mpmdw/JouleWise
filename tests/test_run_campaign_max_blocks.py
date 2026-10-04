"""Desk-only controller boundary tests; synthetic bundles are not live evidence."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tests.test_run_campaign import ROOT, TEST_CAMPAIGN_POLICY, run_campaign_module as campaign, write_config


class CampaignMaxBlocksTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.configs = self.root / "configs"
        self.configs.mkdir()
        self.runs = self.root / "runs"
        self.entries = []
        for block in (1, 2, 3):
            for position, model in enumerate(("A", "B", "B", "A"), 1):
                run_id = f"block{block}-member{position}"
                name = f"{run_id}.json"
                write_config(self.configs, name, run_id)
                self.entries.append({"index": len(self.entries) + 1, "config": name,
                    "run_id": run_id, "model_tag": model,
                    "role": "comparative_contrast_member", "block_index": block,
                    "position_in_block": position})
        self.write_order()
        self.invoked = []

    def write_order(self):
        (self.configs / campaign.ORDER_MANIFEST_NAME).write_text(
            json.dumps({"executed_order": self.entries}) + "\n")

    def invoke(self, extra=(), *, fail_at=None, invalid_at=None, interrupt_at=None,
               authentication=None):
        args = campaign.parse_args([str(self.configs), "--runs-dir", str(self.runs),
            "--campaign-policy", str(TEST_CAMPAIGN_POLICY), *extra])
        provenance_path = self.runs / "campaign_manifests" / "fixed.json"
        provenance = {"session_id": "fixed", "first_physical_run_id": None,
                      "members": [], "cooldown_gates": [], "environment_preflight": None}

        def child(command, **_kwargs):
            config = json.loads(Path(command[command.index("run") + 1]).read_bytes())
            run_id = config["run_id"]
            self.invoked.append(run_id)
            bundle = self.runs / run_id
            bundle.mkdir()
            if len(self.invoked) == interrupt_at:
                raise KeyboardInterrupt
            status = "failed" if len(self.invoked) == fail_at else "succeeded"
            (bundle / "summary_metrics.json").write_text(json.dumps({"status": status}))
            return subprocess.CompletedProcess(command, 1 if status == "failed" else 0)

        def evaluate(info, runs, _waivers, _cooldowns):
            bundle = runs / info.run_id
            summary = bundle / "summary_metrics.json"
            status = json.loads(summary.read_bytes())["status"] if summary.exists() else None
            return [campaign.MemberEvaluation(bundle_id=info.run_id, bundle_path=bundle,
                config_name=info.path.name, status=status,
                strict_valid=info.run_id != invalid_at)]

        with ExitStack() as stack:
            for name, value in (
                ("authenticate_campaign_writer_preflight", authentication),
                ("publish_campaign", None), ("remove_campaign", None),
                ("new_campaign_provenance", (provenance_path, provenance)),
                ("write_campaign_provenance", None),
                ("campaign_environment_preflight", {"admitted": True}),
                ("campaign_cooldown_before_member", {"result": "recovered"}),
                ("utc_timestamp", "2026-10-04T00:00:00Z"),
            ):
                stack.enter_context(patch.object(campaign, name, return_value=value))
            stack.enter_context(patch.object(campaign.time, "monotonic", return_value=1.0))
            stack.enter_context(patch.object(campaign, "run_authenticated_campaign_child", side_effect=child))
            stack.enter_context(patch.object(campaign, "evaluate_members", side_effect=evaluate))
            stack.enter_context(redirect_stdout(io.StringIO()))
            return campaign.run_campaign(args)

    def rows(self):
        return [json.loads(line) for line in (self.runs / "campaign_log.jsonl").read_text().splitlines()]

    def test_stops_after_exactly_n_complete_blocks(self):
        for limit in (1, 2, 3):
            with self.subTest(limit=limit):
                self.runs = self.root / f"runs-{limit}"
                self.invoked = []
                self.assertEqual(self.invoke(["--max-blocks", str(limit)]), campaign.MAX_BLOCKS_REACHED_RC)
                expected = [row["run_id"] for row in self.entries[:4 * limit]]
                self.assertEqual(self.invoked, expected)
                self.assertEqual(sorted(path.name for path in self.runs.iterdir() if path.is_dir()), expected)
                self.assertTrue(all((self.runs / name / "summary_metrics.json").is_file() for name in expected))
                self.assertFalse((self.runs / "campaign.lock").exists())
                terminal = self.rows()[-1]
                self.assertEqual(terminal["record_type"], "campaign_stop")
                self.assertEqual(terminal["stop_reason"], "max_blocks_reached")
                self.assertEqual(terminal["exit_code"], campaign.MAX_BLOCKS_REACHED_RC)
                self.assertEqual(terminal["completed_blocks"], limit)
                self.assertEqual(terminal["last_block_index"], limit)
                self.assertEqual(terminal["last_block_members"], expected[-4:])
                self.assertEqual(terminal["schema_version"], "joulewise.campaign_stop.v1")

    def test_absent_option_matches_legacy_wire_bytes_and_rc(self):
        self.assertEqual(self.invoke(), 0)
        self.assertEqual(self.invoked, [row["run_id"] for row in self.entries])
        wire = (self.runs / "campaign_log.jsonl").read_text().replace(str(self.root), "<ROOT>").replace(str(ROOT), "<REPO>")
        golden = ROOT / "tests/fixtures/campaign_max_blocks_legacy.jsonl"
        self.assertEqual(wire, golden.read_text())

    def test_failure_at_each_position_is_never_the_limit_stop(self):
        for position in (1, 2, 3, 4):
            with self.subTest(position=position):
                self.runs = self.root / f"failure-{position}"
                self.invoked = []
                self.assertEqual(self.invoke(["--max-blocks", "1", "--max-failures", "9"], fail_at=position), 1)
                self.assertEqual(len(self.invoked), position)
                self.assertFalse(any(row.get("record_type") == "campaign_stop" for row in self.rows()))

    def test_exit_zero_with_invalid_member_is_not_a_complete_block(self):
        self.assertEqual(self.invoke(["--max-blocks", "1"], invalid_at="block1-member4"), 1)
        self.assertFalse(any(row.get("record_type") == "campaign_stop" for row in self.rows()))

    def test_interrupt_cannot_report_a_complete_block(self):
        with self.assertRaises(KeyboardInterrupt):
            self.invoke(["--max-blocks", "1"], interrupt_at=4)
        self.assertFalse((self.runs / "block1-member4/summary_metrics.json").exists())
        self.assertFalse((self.runs / "campaign.lock").exists())
        self.assertFalse(any(row.get("record_type") == "campaign_stop" for row in self.rows()))

    def test_existing_complete_block_counts_without_another_dispatch(self):
        self.assertEqual(self.invoke(["--max-blocks", "1"]), campaign.MAX_BLOCKS_REACHED_RC)
        self.invoked = []
        self.assertEqual(self.invoke(["--max-blocks", "1"]), campaign.MAX_BLOCKS_REACHED_RC)
        self.assertEqual(self.invoked, [])

    def test_count_is_independent_of_split_stage_block_numbering(self):
        for row in self.entries:
            row["block_index"] += 5
        self.write_order()
        self.assertEqual(self.invoke(["--max-blocks", "2"]), campaign.MAX_BLOCKS_REACHED_RC)
        self.assertEqual(len(self.invoked), 8)
        self.assertEqual(self.rows()[-1]["completed_blocks"], 2)
        self.assertEqual(self.rows()[-1]["last_block_index"], 7)

    def test_missing_order_or_malformed_block_refuses_before_dispatch(self):
        original = copy.deepcopy(self.entries)
        for mutation in ("missing", "position", "model", "repeated", "partial", "repetitions"):
            with self.subTest(mutation=mutation):
                self.entries = copy.deepcopy(original)
                self.write_order()
                if mutation == "missing":
                    (self.configs / campaign.ORDER_MANIFEST_NAME).unlink()
                elif mutation == "position":
                    self.entries[3]["position_in_block"] = 3
                elif mutation == "model":
                    self.entries[3]["model_tag"] = "B"
                elif mutation == "repeated":
                    for row in self.entries[4:8]:
                        row["block_index"] = 1
                elif mutation == "partial":
                    self.entries.pop()
                    (self.configs / "block3-member4.json").unlink()
                else:
                    write_config(self.configs, "block1-member1.json", "block1-member1", repetitions=2)
                if mutation != "missing":
                    self.write_order()
                with self.assertRaises(ValueError):
                    self.invoke(["--max-blocks", "1"])
                self.assertEqual(self.invoked, [])
                self.assertFalse((self.runs / "campaign.lock").exists())
                write_config(self.configs, "block3-member4.json", "block3-member4")
                write_config(self.configs, "block1-member1.json", "block1-member1")

    def test_nonpositive_limit_refuses(self):
        for value in ("0", "-1"):
            with self.assertRaisesRegex(ValueError, "--max-blocks"):
                self.invoke(["--max-blocks", value])

    def authentication(self, permitted=1):
        def artifact(name, value):
            path = self.root / name
            raw = (json.dumps(value) + "\n").encode()
            path.write_bytes(raw)
            return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
        authorization = artifact("authorization.json", {"permitted_blocks": permitted,
            "purpose": "G2B_SHAKEDOWN"})
        go = artifact("go.json", {"authorization": authorization})
        consumption = artifact("consumption.json", {"go_receipt": go})
        return {"authentication": {"consumption_path": consumption["path"],
                                   "consumption_sha256": consumption["sha256"]}}

    def test_authenticated_limit_applies_without_cli_and_cannot_be_overridden(self):
        auth = self.authentication()
        for value in ("2", "9"):
            with self.assertRaisesRegex(ValueError, "permitted_blocks"):
                self.invoke(["--max-blocks", value], authentication=auth)
        self.assertEqual(self.invoked, [])
        self.assertEqual(self.invoke(authentication=auth), campaign.MAX_BLOCKS_REACHED_RC)
        self.assertEqual(len(self.invoked), 4)
        self.assertEqual(self.rows()[-1]["block_limit"]["source"], "authorization")

    def test_hash_mismatch_at_each_authenticated_hop_refuses(self):
        for name in ("consumption.json", "go.json", "authorization.json"):
            with self.subTest(name=name):
                auth = self.authentication()
                (self.root / name).write_text('{"permitted_blocks": 99}\n')
                with self.assertRaises(campaign.LaunchLineageError):
                    self.invoke(authentication=auth)
                self.assertEqual(self.invoked, [])

    def test_limit_comes_from_replayed_pack_night_authorization(self):
        from tests.test_arm_readiness import LaunchConsumptionV2Tests

        fixture = LaunchConsumptionV2Tests("test_v2_claim_is_fsynced_and_replays_from_consumption")
        fixture.setUp()
        try:
            fixture._settle()
            runs = Path(fixture.arm["arm_context"]["claim_runs_root"])
            authenticated = fixture._authenticate_campaign(runs)
            binding = campaign._authenticated_campaign_block_limit(authenticated)
            self.assertEqual(binding["max_blocks"], 1)
            self.assertEqual(binding["purpose"], "G2B_SHAKEDOWN")
            authorization = Path(binding["authorization"]["path"])
            value = json.loads(authorization.read_bytes())
            self.assertEqual(value["permitted_blocks"], binding["max_blocks"])
            value["permitted_blocks"] = 2
            authorization.write_text(json.dumps(value) + "\n")
            with self.assertRaises(campaign.LaunchLineageError):
                campaign._authenticated_campaign_block_limit(authenticated)
        finally:
            fixture.doCleanups()

    def test_authorization_does_not_limit_reference_corpus(self):
        for row in self.entries:
            row.update(role="neg8_reference_corpus_member", position_in_block=1)
        self.write_order()
        self.assertEqual(self.invoke(authentication=self.authentication()), 0)
        self.assertEqual(len(self.invoked), 12)

    def test_real_mock_cli_finishes_four_strict_valid_bundles_and_no_fifth(self):
        # Exercise the real CLI/controller/validator, with only process identity
        # substituted as in test_run_campaign's subprocess fixture. No hardware.
        from joulewise.cli import validate_bundle

        probe = self.root / "identity-probe"
        probe.write_text("#!/bin/sh\nprintf 'Tue Sep 8 01:02:03 2026 S\\n'\n")
        probe.chmod(0o755)
        result = subprocess.run([sys.executable, str(ROOT / "scripts/run_campaign.py"),
            str(self.configs), "--runs-dir", str(self.runs), "--campaign-policy",
            str(TEST_CAMPAIGN_POLICY), "--max-blocks", "1"], cwd=ROOT,
            env={**os.environ, "JOULEWISE_IDENTITY_PROBE": str(probe),
                "JOULEWISE_CUSTODY_PARENT": str(self.root / "registry-custody"),
                "JOULEWISE_ADDITIONAL_CUSTODY_PARENTS": "[]"},
            text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, campaign.MAX_BLOCKS_REACHED_RC, result.stdout + result.stderr)
        for row in self.entries[:4]:
            bundle = self.runs / row["run_id"]
            self.assertEqual(validate_bundle(bundle, strict=True), [])
            self.assertEqual(json.loads((bundle / "summary_metrics.json").read_bytes())["status"], "succeeded")
        self.assertTrue(all(not (self.runs / row["run_id"]).exists() for row in self.entries[4:]))
        self.assertEqual(self.rows()[-1]["stop_reason"], "max_blocks_reached")
        self.assertFalse((self.runs / "campaign.lock").exists())


if __name__ == "__main__":
    unittest.main()
