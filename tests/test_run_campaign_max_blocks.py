"""Desk-only controller boundary tests; synthetic bundles are not live evidence."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import shutil
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
               waived_at=None, authentication=None, verdict=None,
               policy=TEST_CAMPAIGN_POLICY, analysis=None, persist_provenance=False,
               prospective=None):
        args = campaign.parse_args([str(self.configs), "--runs-dir", str(self.runs),
            "--campaign-policy", str(policy), *extra])
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
                strict_valid=info.run_id not in (invalid_at, waived_at),
                waiver=(campaign.Waiver("run_id", info.run_id, "desk waiver", "test",
                    "2026-10-04T00:00:00Z", "strict_invalid")
                    if info.run_id == waived_at else None))]

        with ExitStack() as stack:
            for name, value in (
                ("authenticate_campaign_writer_preflight", authentication),
                ("publish_campaign", None), ("remove_campaign", None),
                ("new_campaign_provenance", (provenance_path, provenance)),
                ("campaign_environment_preflight", {"admitted": True}),
                ("campaign_cooldown_before_member", {"result": "recovered"}),
                ("utc_timestamp", "2026-10-04T00:00:00Z"),
            ):
                stack.enter_context(patch.object(campaign, name, return_value=value))
            if not persist_provenance:
                stack.enter_context(patch.object(campaign, "write_campaign_provenance"))
            if verdict is not None:
                stack.enter_context(patch.object(campaign, "collection_verdict_for",
                    return_value=(verdict, ["desk stage-verdict refusal"])))
            if analysis is not None:
                stack.enter_context(patch.object(campaign, "load_analysis_manifest", return_value=analysis))
            if prospective is not None:
                stack.enter_context(patch.object(campaign, "resolve_prospective_analysis_manifest_v3",
                    return_value=prospective))
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

    def snapshot(self, rc):
        def normalized(path):
            return path.read_text().replace(str(self.root), "<ROOT>").replace(str(ROOT), "<REPO>")
        return {"rc": rc, "log": normalized(self.runs / "campaign_log.jsonl"),
            "artifacts": {str(path.relative_to(self.runs)): normalized(path)
                for path in sorted(self.runs.rglob("*")) if path.is_file()
                and path.name != "campaign_log.jsonl"}}

    def test_unflagged_authenticated_purposes_match_main_golden_log_rc_and_artifacts(self):
        # Generated with main's 8fa002f7 script through this same desk harness.
        golden = json.loads((ROOT / "tests/fixtures/campaign_max_blocks_authenticated_main.json").read_text())
        for purpose in ("CAMPAIGN_TRANSACTION", "T0_REHEARSAL"):
            for permitted in (1, 3, 5):
                with self.subTest(purpose=purpose, permitted=permitted):
                    self.runs = self.root / "runs"
                    self.invoked = []
                    auth = self.authentication(permitted, purpose=purpose)
                    self.assertIsNotNone(auth)
                    rc = self.invoke(authentication=auth, persist_provenance=True)
                    self.assertEqual(self.snapshot(rc), golden["snapshot"])
                    self.assertEqual(self.invoked, [row["run_id"] for row in self.entries])
                    self.assertNotIn("block_limit", self.rows()[-1]["preflight"])
                    shutil.rmtree(self.runs)

    def test_failure_at_each_position_is_never_the_limit_stop(self):
        for position in (1, 2, 3, 4):
            with self.subTest(position=position):
                self.runs = self.root / f"failure-{position}"
                self.invoked = []
                self.assertEqual(self.invoke(["--max-blocks", "1"], fail_at=position), 1)
                self.assertEqual(len(self.invoked), position)
                self.assertFalse(any(row.get("record_type") == "campaign_stop" for row in self.rows()))

    def test_wider_failure_budget_with_block_limit_refuses_before_dispatch(self):
        # D-078: a bounded occurrence is never topped up past a failed member.
        with self.assertRaisesRegex(ValueError, "--max-failures must be 1"):
            self.invoke(["--max-blocks", "1", "--max-failures", "9"])
        self.assertEqual(self.invoked, [])

    def test_exit_zero_with_invalid_member_is_not_a_complete_block(self):
        self.assertEqual(self.invoke(["--max-blocks", "1"], invalid_at="block1-member4"), 1)
        self.assertFalse(any(row.get("record_type") == "campaign_stop" for row in self.rows()))

    def test_waived_member_never_qualifies_as_a_complete_block(self):
        self.assertEqual(self.invoke(["--max-blocks", "1"], waived_at="block1-member4"), 1)
        self.assertEqual(len(self.invoked), 4)
        self.assertEqual(self.rows()[-2]["status"], "waived")
        self.assertEqual(self.rows()[-2]["members"][0]["collection_classification"], "waived")
        self.assertFalse(any(row.get("record_type") == "campaign_stop" for row in self.rows()))

    def test_limit_reached_with_failed_stage_verdict_has_no_stop_row_or_rc3(self):
        for verdict in ("blocked", "invalid"):
            with self.subTest(verdict=verdict):
                self.runs = self.root / verdict
                self.invoked = []
                self.assertEqual(self.invoke(["--max-blocks", "1"], verdict=verdict), 1)
                self.assertEqual(len(self.invoked), 4)
                self.assertEqual(self.rows()[-1]["collection"]["verdict"], verdict)
                self.assertFalse(any(row.get("record_type") == "campaign_stop" for row in self.rows()))

    def test_limit_reached_with_claim_barrier_has_no_stop_row_or_rc3(self):
        analysis = campaign.AnalysisManifestState(self.configs / "analysis_manifest.json",
            {}, "desk-claim", "0" * 64)
        policy = ROOT / "configs/campaign_policies/quiet_mac_p2_production.json"
        self.assertEqual(self.invoke(["--max-blocks", "1"], policy=policy, analysis=analysis), 1)
        self.assertEqual(len(self.invoked), 4)
        verdict = self.rows()[-1]
        self.assertEqual(verdict["collection"]["verdict"], "usable")
        self.assertEqual(verdict["claim_readiness"]["verdict"], "not_ready_for_analysis")
        self.assertIn("cpu_admission_core_failed", verdict["claim_readiness"]["reasons"])
        self.assertFalse(any(row.get("record_type") == "campaign_stop" for row in self.rows()))

    def test_production_policy_with_v5_prospective_manifest_fragment_can_stop(self):
        # Unit coverage only: reuse the real v5 producer's analysis semantics,
        # with desk pin/domain inputs. No pack validation or runner rehearsal.
        from tests.test_d117_contrast_v5_pack import D117ContrastV5PackTests

        fixture = D117ContrastV5PackTests()
        fixture.setUp()
        fixture.configure(fixture.write_prefill_pin(self.root))
        producer = fixture.generator
        families = [{"condition_family_id": producer.family_id(arm, model),
            "canonical_domain_sha256": "0" * 64}
            for arm in ("decode", producer.PREFILL_ARM) for model in ("A", "B")]
        manifest = producer.build_analysis_manifest("0" * 64, {"manifest_id": "desk-root"},
            "0" * 64, [], [], families, "0" * 64, "0" * 64)
        fragment = {key: manifest[key] for key in ("schema_version", "manifest_id", "design", "contrasts")}
        path = self.root / "v5-analysis-fragment.json"
        path.write_text(json.dumps(fragment) + "\n")
        prospective = campaign.ProspectiveManifestIdentity(path, fragment["manifest_id"],
            hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(fragment["schema_version"], "joulewise.analysis_manifest.v3.prospective")
        self.assertEqual(fragment["design"]["sampling_plan"]["planned_n_blocks"], 10)
        policy = ROOT / "configs/campaign_policies/quiet_mac_p2_production.json"
        self.assertEqual(self.invoke(["--max-blocks", "1"], authentication=self.authentication(),
            policy=policy, prospective=prospective), campaign.MAX_BLOCKS_REACHED_RC)
        self.assertEqual(len(self.invoked), 4)
        verdict = self.rows()[-2]
        self.assertEqual(verdict["analysis_manifest"], prospective.to_log())
        self.assertEqual(verdict["preflight"]["campaign_policy"]["policy_id"], "quiet-mac-p2-production")
        self.assertEqual(verdict["claim_readiness"]["verdict"], "not_assessed")

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

    def authentication(self, permitted=1, *, purpose="G2B_SHAKEDOWN"):
        def artifact(name, value):
            path = self.root / name
            value = {**value, "desk_note": "authenticated"}
            raw = (json.dumps(value) + "\n").encode()
            path.write_bytes(raw)
            return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
        authorization = artifact("authorization.json", {"permitted_blocks": permitted,
            "purpose": purpose})
        go = artifact("go.json", {"authorization": authorization})
        consumption = artifact("consumption.json", {"go_receipt": go})
        return {"authentication": {"consumption_path": consumption["path"],
                                   "consumption_sha256": consumption["sha256"]}}

    def test_g2b_requires_explicit_matching_limit_before_dispatch(self):
        auth = self.authentication()
        with self.assertRaisesRegex(ValueError, "G2B_SHAKEDOWN authorization requires --max-blocks"):
            self.invoke(authentication=auth)
        for value in ("2", "9"):
            with self.assertRaisesRegex(ValueError, "permitted_blocks"):
                self.invoke(["--max-blocks", value], authentication=auth)
        with self.assertRaisesRegex(ValueError, "permitted_blocks"):
            self.invoke(["--max-blocks", "1"], authentication=self.authentication(3))
        auth = self.authentication()
        self.assertEqual(self.invoked, [])
        self.assertEqual(self.invoke(["--max-blocks", "1"], authentication=auth), campaign.MAX_BLOCKS_REACHED_RC)
        self.assertEqual(len(self.invoked), 4)
        self.assertEqual(self.rows()[-1]["block_limit"]["source"], "authorization")

    def test_other_authenticated_purposes_refuse_explicit_limit_before_dispatch(self):
        for purpose in ("CAMPAIGN_TRANSACTION", "T0_REHEARSAL"):
            with self.subTest(purpose=purpose):
                with self.assertRaisesRegex(ValueError, "requires G2B_SHAKEDOWN authorization"):
                    self.invoke(["--max-blocks", "1"], authentication=self.authentication(purpose=purpose))
                self.assertEqual(self.invoked, [])
                self.assertFalse((self.runs / "campaign.lock").exists())

    def test_g2b_missing_flag_refuses_even_without_contrast_role(self):
        for role in ("comparative_abba_member", "neg8_reference_corpus_member"):
            with self.subTest(role=role):
                for row in self.entries:
                    row["role"] = role
                self.write_order()
                with self.assertRaisesRegex(ValueError, "G2B_SHAKEDOWN authorization requires --max-blocks"):
                    self.invoke(authentication=self.authentication())
                self.assertEqual(self.invoked, [])

    def test_hash_mismatch_at_each_authenticated_hop_refuses(self):
        for name in ("consumption.json", "go.json", "authorization.json"):
            with self.subTest(name=name):
                auth = self.authentication()
                path = self.root / name
                value = json.loads(path.read_bytes())
                # Preserve every required field and nested hash reference.
                # A digest-bypass mutant must reach dispatch, not a KeyError.
                if name == "authorization.json":
                    value["permitted_blocks"] = 2
                else:
                    value["desk_note"] = "changed after authentication"
                path.write_text(json.dumps(value) + "\n")
                limit = "2" if name == "authorization.json" else "1"
                with self.assertRaisesRegex(campaign.LaunchLineageError, "hash mismatch"):
                    self.invoke(["--max-blocks", limit], authentication=auth)
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
        self.assertEqual(self.invoke(authentication=self.authentication(purpose="CAMPAIGN_TRANSACTION")), 0)
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
