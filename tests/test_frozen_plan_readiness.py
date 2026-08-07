from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_frozen_plan_readiness.py"
SPEC = importlib.util.spec_from_file_location("validate_frozen_plan_readiness", VALIDATOR)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR_MODULE
SPEC.loader.exec_module(VALIDATOR_MODULE)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def ledger_row_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


class FrozenPlanFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.repo = root / "repo"
        self.plan_dir = self.repo / "plans" / "window-alpha"
        self.evidence_root = root / "runs_d117_alpha"
        self.bound_root = root / "runs_d117_alpha_bound"
        self.config = self.plan_dir / "configs" / "member-one.json"
        self.stage_manifest = self.plan_dir / "stages" / "stage-one.json"
        self.plan_path = self.plan_dir / "frozen-plan.json"
        self.sidecar = self.plan_dir / "frozen-plan.sha256"
        self.readiness_path = self.plan_dir / "readiness-record.json"
        self.acceptance = self.repo / "configs" / "calibration" / "acceptance.json"
        self.pin = self.repo / "configs" / "calibration" / "head.json"
        self.ledger = self.repo / "runs" / "ledger.jsonl"
        self.waivers = self.repo / "waivers.json"
        self.epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        self._build()

    def _write(self, path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def _git(self, *args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _build(self) -> None:
        self.repo.mkdir()
        self.evidence_root.mkdir()
        self.bound_root.mkdir()
        self._git("init", "-q")
        self._git("config", "user.email", "fixture@example.invalid")
        self._git("config", "user.name", "Fixture")
        self._write(self.config, json_bytes({"run_id": "member-one"}))
        self.write_stage()
        self.write_plan()
        self._write(
            self.acceptance,
            json_bytes(
                {
                    "schema_version": "joulewise.calibration_acceptance_bound.v2",
                    "acceptance_id": "synthetic-issued",
                    "artifact_role": "issued",
                    "identity_epoch": self.epoch,
                }
            ),
        )
        self._write(
            self.pin,
            json_bytes(
                {
                    "sequence": 0,
                    "head_digest": "0" * 64,
                    "ledger_schema": "joulewise.calibration_observation_ledger.v1",
                }
            ),
        )
        self._write(self.ledger, b"")
        self._write(self.waivers, b"[]\n")
        self.write_readiness()
        self.commit_pin()

    def write_stage(self, *, expected: int = 1, members: list[dict] | None = None) -> None:
        if members is None:
            members = [
                {
                    "member_id": "member-one",
                    "config_path": "configs/member-one.json",
                    "config_sha256": sha256(self.config.read_bytes()),
                }
            ]
        self._write(
            self.stage_manifest,
            json_bytes(
                {
                    "schema_version": "joulewise.stage_manifest.v1",
                    "manifest_id": "stage-one-v1",
                    "plan_id": "plan-d117-alpha-v1",
                    "expected_member_count": expected,
                    "members": members,
                }
            ),
        )

    def write_plan(self, *, stage_expected: int = 1) -> None:
        plan = {
            "schema_version": "joulewise.frozen_window_plan.v1",
            "plan_id": "plan-d117-alpha-v1",
            "freeze_status": "frozen_before_measurement",
            "evidence_root_id": "evidence-d117-alpha-v1",
            "expected_fresh_physical_path": str(self.evidence_root),
            "expected_fresh_bound_physical_path": str(self.bound_root),
            "stage_manifests": [
                {
                    "stage_manifest_id": "stage-one-v1",
                    "stage_manifest_path": "stages/stage-one.json",
                    "stage_manifest_sha256": sha256(self.stage_manifest.read_bytes()),
                    "expected_member_count": stage_expected,
                    "predecessor": None,
                    "successor": None,
                }
            ],
        }
        self._write(self.plan_path, json_bytes(plan))
        self._write(
            self.sidecar,
            f"{sha256(self.plan_path.read_bytes())}  frozen-plan.json\n".encode(),
        )

    def readiness(self) -> dict:
        return json.loads(self.readiness_path.read_text(encoding="utf-8"))

    def write_readiness(self, overrides: dict | None = None) -> None:
        record = {
            "schema_version": "joulewise.frozen_plan_readiness.v1",
            "review_status": "reviewed",
            "plan_id": "plan-d117-alpha-v1",
            "plan_path": "frozen-plan.json",
            "plan_sha256": sha256(self.plan_path.read_bytes()),
            "sidecar_path": "frozen-plan.sha256",
            "sidecar_sha256": sha256(self.sidecar.read_bytes()),
            "physical_ledger_path": "runs/ledger.jsonl",
            "committed_ledger_head_pin_path": "configs/calibration/head.json",
            "acceptance_artifact_path": "configs/calibration/acceptance.json",
            "acceptance_artifact_sha256": sha256(self.acceptance.read_bytes()),
            "acceptance_artifact_role": "issued",
            "identity_epoch": self.epoch,
            "waiver_set_path": "waivers.json",
            "launch_commands": [
                {
                    "name": "science",
                    "argv": [
                        "python3",
                        str(self.repo / "scripts" / "run_campaign.py"),
                        "--runs-dir",
                        str(self.evidence_root),
                        "--plan-dir",
                        str(self.plan_dir),
                    ],
                }
            ],
            "bracket_session_identifiers": {
                "session_id": "bracket-session-alpha",
                "pre_attempt_id": "bracket-session-alpha-pre",
                "post_attempt_id": "bracket-session-alpha-post",
            },
        }
        if overrides:
            record.update(overrides)
        self._write(self.readiness_path, json_bytes(record))

    def commit_pin(self) -> None:
        self._git("add", "configs/calibration/head.json")
        self._git("commit", "-q", "-m", "pin head")

    def validate(self) -> dict:
        return VALIDATOR_MODULE.validate(self.plan_dir, self.evidence_root, self.repo)

    def check(self, receipt: dict, check_id: str) -> dict:
        return next(row for row in receipt["checks"] if row["check"] == check_id)

    def cli(self, *extra: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--plan-dir",
                str(self.plan_dir),
                "--evidence-root",
                str(self.evidence_root),
                "--repo",
                str(self.repo),
                *extra,
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )


class FrozenPlanReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.fixture = FrozenPlanFixture(Path(self.tempdir.name))

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def assert_refuses(self, check_id: str, reason: str) -> dict:
        receipt = self.fixture.validate()
        self.assertEqual(receipt["result"], "REFUSE")
        check = self.fixture.check(receipt, check_id)
        self.assertEqual(check["result"], "REFUSE")
        self.assertIn(reason, check["reasons"])
        return receipt

    def test_every_check_passes_for_complete_synthetic_fixture(self) -> None:
        receipt = self.fixture.validate()
        self.assertEqual(receipt["result"], "PASS")
        self.assertEqual(receipt["refusal_reasons"], [])
        self.assertEqual(
            {row["check"] for row in receipt["checks"]},
            {
                "plan_integrity",
                "stage_manifests",
                "fresh_physical_roots",
                "ledger_head",
                "acceptance_artifact",
                "waiver_set",
                "launch_command_paths",
                "campaign_lock",
                "bracket_session_identifiers",
            },
        )
        self.assertTrue(all(row["result"] == "PASS" for row in receipt["checks"]))

    def test_plan_integrity_refuses_tampered_plan_bytes(self) -> None:
        self.fixture.plan_path.write_bytes(self.fixture.plan_path.read_bytes() + b" ")
        self.assert_refuses("plan_integrity", "plan_sha256_mismatch")

    def test_stage_manifest_refuses_wrong_expected_member_count(self) -> None:
        self.fixture.write_plan(stage_expected=2)
        self.fixture.write_readiness()
        self.assert_refuses("stage_manifests", "stage_member_count_mismatch")

    def test_stage_manifest_refuses_missing_member_config(self) -> None:
        self.fixture.config.unlink()
        self.assert_refuses("stage_manifests", "stage_member_config_missing")

    def test_stage_manifest_refuses_wrong_chain_links(self) -> None:
        plan = json.loads(self.fixture.plan_path.read_text())
        plan["stage_manifests"][0]["successor"] = "undeclared-stage"
        self.fixture.plan_path.write_bytes(json_bytes(plan))
        self.fixture.sidecar.write_bytes(
            f"{sha256(self.fixture.plan_path.read_bytes())}  frozen-plan.json\n".encode()
        )
        self.fixture.write_readiness()
        self.assert_refuses("stage_manifests", "stage_manifest_chain_mismatch")

    def test_fresh_roots_refuse_reuse(self) -> None:
        (self.fixture.evidence_root / "prior-member").mkdir()
        self.assert_refuses("fresh_physical_roots", "physical_root_not_empty")

    def test_fresh_roots_refuse_argument_not_bound_by_plan(self) -> None:
        other = self.fixture.root / "other-empty-root"
        other.mkdir()
        receipt = VALIDATOR_MODULE.validate(
            self.fixture.plan_dir, other, self.fixture.repo
        )
        check = self.fixture.check(receipt, "fresh_physical_roots")
        self.assertIn("evidence_root_argument_mismatch", check["reasons"])

    def test_ledger_refuses_physical_head_different_from_committed_pin(self) -> None:
        self.fixture.ledger.write_bytes(
            ledger_row_bytes({"sequence": 1, "receipt_digest": "a" * 64})
        )
        self.assert_refuses("ledger_head", "ledger_physical_head_pin_mismatch")

    def test_ledger_refuses_missing_physical_file(self) -> None:
        self.fixture.ledger.unlink()
        self.assert_refuses("ledger_head", "physical_ledger_missing")

    def test_ledger_refuses_worktree_pin_not_equal_to_head(self) -> None:
        self.fixture.pin.write_bytes(
            json_bytes(
                {
                    "sequence": 1,
                    "head_digest": "a" * 64,
                    "ledger_schema": "joulewise.calibration_observation_ledger.v1",
                }
            )
        )
        self.assert_refuses("ledger_head", "ledger_head_pin_not_committed")

    def test_acceptance_refuses_nonissued_role(self) -> None:
        value = json.loads(self.fixture.acceptance.read_text())
        value["artifact_role"] = "schema_fixture_unissued"
        self.fixture.acceptance.write_bytes(json_bytes(value))
        self.fixture.write_readiness()
        self.assert_refuses("acceptance_artifact", "acceptance_artifact_not_issued")

    def test_acceptance_refuses_identity_epoch_mismatch(self) -> None:
        value = json.loads(self.fixture.acceptance.read_text())
        value["identity_epoch"]["os_build"] = "25F85"
        self.fixture.acceptance.write_bytes(json_bytes(value))
        self.fixture.write_readiness()
        self.assert_refuses(
            "acceptance_artifact", "acceptance_identity_epoch_mismatch"
        )

    def test_waiver_set_refuses_any_entry(self) -> None:
        self.fixture.waivers.write_bytes(json_bytes([{"reason": "never"}]))
        self.assert_refuses("waiver_set", "waiver_set_not_empty")

    def test_launch_command_refuses_relative_runs_dir(self) -> None:
        record = self.fixture.readiness()
        record["launch_commands"][0]["argv"][3] = "relative/runs"
        self.fixture.readiness_path.write_bytes(json_bytes(record))
        self.assert_refuses(
            "launch_command_paths", "launch_command_path_not_absolute"
        )

    def test_launch_command_refuses_missing_runs_dir(self) -> None:
        record = self.fixture.readiness()
        record["launch_commands"][0]["argv"] = ["python3", "/tmp/launch.py"]
        self.fixture.readiness_path.write_bytes(json_bytes(record))
        self.assert_refuses(
            "launch_command_paths", "launch_command_runs_dir_missing"
        )

    def test_launch_command_refuses_waiver_or_environment_override(self) -> None:
        for forbidden in ("--waivers", "--environment-override=accepted.json"):
            with self.subTest(forbidden=forbidden):
                record = self.fixture.readiness()
                record["launch_commands"][0]["argv"].append(forbidden)
                if forbidden == "--waivers":
                    record["launch_commands"][0]["argv"].append(
                        str(self.fixture.waivers)
                    )
                self.fixture.readiness_path.write_bytes(json_bytes(record))
                self.assert_refuses(
                    "launch_command_paths", "launch_command_forbidden_override"
                )
                self.fixture.write_readiness()

    def test_campaign_lock_refuses(self) -> None:
        (self.fixture.evidence_root / "campaign.lock").write_text("held\n")
        self.assert_refuses("campaign_lock", "campaign_lock_present")

    def test_bracket_identifiers_refuse_duplicates(self) -> None:
        record = self.fixture.readiness()
        record["bracket_session_identifiers"]["post_attempt_id"] = record[
            "bracket_session_identifiers"
        ]["pre_attempt_id"]
        self.fixture.readiness_path.write_bytes(json_bytes(record))
        self.assert_refuses(
            "bracket_session_identifiers", "bracket_session_identifiers_invalid"
        )

    def test_bracket_identifiers_refuse_already_claimed_value(self) -> None:
        self.fixture.ledger.write_bytes(
            ledger_row_bytes(
                {
                    "sequence": 1,
                    "receipt_digest": "a" * 64,
                    "session_id": "bracket-session-alpha",
                }
            )
        )
        self.fixture.pin.write_bytes(
            json_bytes(
                {
                    "sequence": 1,
                    "head_digest": "a" * 64,
                    "ledger_schema": "joulewise.calibration_observation_ledger.v1",
                }
            )
        )
        self.fixture.commit_pin()
        self.assert_refuses(
            "bracket_session_identifiers", "bracket_session_identifier_claimed"
        )

    def test_malformed_record_fails_closed_for_every_check(self) -> None:
        self.fixture.readiness_path.write_text("not-json\n", encoding="utf-8")
        receipt = self.fixture.validate()
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertTrue(all(row["result"] == "REFUSE" for row in receipt["checks"]))

    def test_cli_pass_is_exit_zero_and_json(self) -> None:
        completed = self.fixture.cli()
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        receipt = json.loads(completed.stdout)
        self.assertEqual(receipt["result"], "PASS")

    def test_cli_refusal_is_exit_two_and_json(self) -> None:
        self.fixture.waivers.write_bytes(json_bytes([{"reason": "never"}]))
        completed = self.fixture.cli()
        self.assertEqual(completed.returncode, 2, completed.stderr.decode())
        receipt = json.loads(completed.stdout)
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertIn("waiver_set_not_empty", receipt["refusal_reasons"])

    def test_cli_usage_error_is_exit_two_and_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        receipt = json.loads(completed.stdout)
        self.assertEqual(receipt["refusal_reasons"], ["invalid_arguments"])

    def test_runbook_d117_addendum_preserves_settle_and_zero_retry_order(self) -> None:
        runbook = (REPO_ROOT / "docs" / "phase_2" / "window_runbook.md").read_text(
            encoding="utf-8"
        )
        start = runbook.index("### D-117 addendum — two-slot session capability")
        end = runbook.index("## 5B. Pre-flight calibration screen", start)
        addendum = runbook[start:end]
        normalized = " ".join(addendum.split())
        for required in (
            "existing 180-second settle",
            "calibration retry count is zero",
            "D-102 successor-trigger probe",
            "before the bound corpus, references, or any science stage",
            "Never interrupt or kill a running whole-window verdict",
        ):
            self.assertIn(required, normalized)
        self.assertLess(addendum.index("two-slot"), addendum.index("reserved `pre` slot"))
        self.assertLess(
            addendum.index("reserved `pre` slot"),
            addendum.index("D-102 successor-trigger probe"),
        )


if __name__ == "__main__":
    unittest.main()
