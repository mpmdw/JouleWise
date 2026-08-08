"""Cross-layer D-117 refusal inventory and public-exit witnesses."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest

from joulewise.calibration_exits import (
    REFUSAL_BY_CODE,
    REFUSAL_INVENTORY,
    RefusalCode,
    TerminalResult,
)
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    LEDGER_SCHEMA,
    append_bracket_session_receipt,
    canonical_json_bytes,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RECOVERY_SCRIPT = REPO_ROOT / "scripts" / "recover_calibration_ledger.py"


def _fresh_cli_env() -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


class RefusalInventoryTests(unittest.TestCase):
    def test_generated_contract_projection_and_runbook_anchors_are_fresh(self) -> None:
        contract = (
            REPO_ROOT / "docs" / "contracts" / "calibration_ledger_append.md"
        ).read_text(encoding="utf-8")
        begin = "<!-- BEGIN GENERATED: calibration-refusal-registry -->\n"
        end = "\n<!-- END GENERATED: calibration-refusal-registry -->"
        actual = contract.split(begin, 1)[1].split(end, 1)[0]
        rows = [
            "| Code | Component | Phase | Exit ID | Terminal result | Night loss | Witness |",
            "|---|---|---|---|---|---:|---|",
            *[
                "| `{}` | {} | {} | `{}` | `{}` | `{}` | `{}` |".format(
                    record.code.value,
                    record.component,
                    record.phase,
                    record.exit_id,
                    record.terminal_result.value,
                    str(record.night_loss).lower(),
                    record.witness_id,
                )
                for record in REFUSAL_INVENTORY
            ],
        ]
        self.assertEqual(actual, "\n".join(rows))
        runbook = (REPO_ROOT / "docs" / "phase_2" / "window_runbook.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("D-117 §5 amendment", runbook)
        self.assertIn("D-117 §6 amendment", runbook)
        self.assertIn("D-117 §10 amendment", runbook)
        section_13 = runbook.split("## 13.", 1)[1] if "## 13." in runbook else ""
        self.assertNotIn("D-117 §", section_13)
        for record in REFUSAL_INVENTORY:
            self.assertEqual(
                record.runbook_anchor,
                "d-117-10-calibration-ledger-refusals-and-governed-exits",
            )

    def test_enum_inventory_and_executed_witness_ids_are_exact_sets(self) -> None:
        enum_codes = set(RefusalCode)
        inventory_codes = {record.code for record in REFUSAL_INVENTORY}
        discovered_witness_codes = {
            RefusalCode(record.witness_id.removeprefix("witness."))
            for record in REFUSAL_INVENTORY
        }
        self.assertEqual(enum_codes, inventory_codes)
        self.assertEqual(enum_codes, set(REFUSAL_BY_CODE))
        self.assertEqual(enum_codes, discovered_witness_codes)
        self.assertEqual(len(REFUSAL_INVENTORY), len(enum_codes))

    def test_registry_policy_is_complete_and_prior_crash_never_generic_stops(self) -> None:
        terminal_values = {result.value for result in TerminalResult}
        for record in REFUSAL_INVENTORY:
            with self.subTest(code=record.code.value):
                self.assertTrue(record.component)
                self.assertTrue(record.phase)
                self.assertTrue(record.retry_class)
                self.assertTrue(record.exit_id)
                self.assertTrue(record.command)
                self.assertTrue(record.runbook_anchor)
                self.assertIn(record.terminal_result.value, terminal_values)
                if record.prior_crash_reachable:
                    self.assertNotEqual(record.exit_kind, "stop-preserved")

    def test_every_registered_code_is_executed_through_public_explain_cli(self) -> None:
        observed: set[RefusalCode] = set()
        for code in RefusalCode:
            result = subprocess.run(
                [sys.executable, str(RECOVERY_SCRIPT), "explain", code.value],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=_fresh_cli_env(),
                check=False,
            )
            with self.subTest(code=code.value):
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(
                    set(payload), {"code", "exit_id", "arm_blocked", "next_command"}
                )
                self.assertEqual(payload["code"], code.value)
                observed.add(RefusalCode(payload["code"]))
        self.assertEqual(observed, set(RefusalCode))

    def test_operational_ast_has_no_free_form_ledger_refusals_or_substring_policy(self) -> None:
        paths = (
            REPO_ROOT / "joulewise" / "calibration_ledger.py",
            REPO_ROOT / "scripts" / "validate_powermetrics_fiducial.py",
            REPO_ROOT / "scripts" / "recover_calibration_ledger.py",
            REPO_ROOT / "scripts" / "reserve_calibration_window_bracket.py",
        )
        operational_functions = {
            "_open_ledger_lock",
            "_repair_locked",
            "inspect_calibration_ledger",
            "repair_calibration_ledger",
            "abandon_calibration_ledger_tail",
            "_locked_append",
            "_authenticated_head_pin",
            "validate_bracket_session_reservation_inputs",
            "append_bracket_session_receipt",
            "claim_bracket_session_slot",
            "finalize_bracket_session_slot",
            "abort_bracket_session",
            "terminal_head_pin_for_session",
            "calibration_session_status",
            "calibration_readiness",
            "advance_calibration_head_pin",
            "resume_finalize_bracket_session",
            "abort_calibration_session",
            "append_pending_receipt",
            "finalize_attempt_receipt",
            "_head_pin_for_valid_receipt",
            "head_pin_for_receipt",
        }
        violations: list[str] = []
        for path in paths:
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("exclusive writer " + "claim", source)
            self.assertNotIn("operation key " + "conflicts", source)
            self.assertNotIn("marker in " + "str(exc)", source)
            self.assertNotIn('print("refusing:', source)
            tree = ast.parse(source)
            parents: dict[ast.AST, ast.AST] = {}
            for parent in ast.walk(tree):
                for child in ast.iter_child_nodes(parent):
                    parents[child] = parent
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                if not isinstance(function, ast.Name) or function.id != "CalibrationLedgerError":
                    continue
                owner = node
                while owner in parents and not isinstance(
                    owner, (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    owner = parents[owner]
                if (
                    path.name == "calibration_ledger.py"
                    and isinstance(owner, ast.FunctionDef)
                    and owner.name not in operational_functions
                ):
                    continue
                if node.args and isinstance(node.args[0], (ast.Constant, ast.JoinedStr)):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
        self.assertEqual(violations, [])


class PublicGovernedExitWitnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name).resolve() / "repo"
        shutil.copytree(REPO_ROOT / "joulewise", self.repo / "joulewise")
        (self.repo / "scripts").mkdir()
        for name in (
            "recover_calibration_ledger.py",
            "validate_powermetrics_fiducial.py",
        ):
            shutil.copy2(REPO_ROOT / "scripts" / name, self.repo / "scripts" / name)
        self.pin = self.repo / "configs" / "calibration" / "calibration_ledger_head.json"
        self.pin.parent.mkdir(parents=True)
        self.pin.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": GENESIS_DIGEST,
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.ledger = self.repo / "runs" / "ledger.jsonl"
        self.ledger.parent.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@joulewise.invalid"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "JouleWise tests"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.repo, check=True)
        self.script = self.repo / "scripts" / "recover_calibration_ledger.py"
        self.epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        from joulewise.calibration_ledger import T1_FIELDS

        self.t1 = {field: f"value-{field}" for field in T1_FIELDS}
        self.t1.update(self.epoch)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.script),
                "--ledger",
                str(self.ledger),
                "--head-pin",
                str(self.pin),
                *args,
            ],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_cli_env(),
            check=False,
        )

    def _open_session(self, session_id: str = "session-witness") -> Path:
        plan = self.repo / "plans" / f"{session_id}.json"
        plan.parent.mkdir()
        plan.write_text(
            json.dumps({"plan_id": f"plan-{session_id}", "session_id": session_id})
            + "\n",
            encoding="utf-8",
        )
        plan_sha = hashlib.sha256(plan.read_bytes()).hexdigest()
        runs_root = self.repo / "runs" / session_id
        append_bracket_session_receipt(
            self.ledger,
            session_id=session_id,
            window_id=f"window-{session_id}",
            plan_id=f"plan-{session_id}",
            plan_sha256=plan_sha,
            evidence_root_id=f"evidence-{session_id}",
            runs_root=runs_root,
            slots={
                slot: {
                    "attempt_id": f"{session_id}-{slot}",
                    "custody_locator": str(
                        runs_root / "instrument_validation" / f"{session_id}-{slot}"
                    ),
                    "identity_epoch": self.epoch,
                    "t1_bindings": self.t1,
                }
                for slot in ("pre", "post")
            },
            head_pin_path=self.pin,
            require_committed_pin=False,
            repo_root=self.repo,
        )
        return plan

    def _complete_custody(self, session_id: str, slot: str) -> Path:
        root = (
            self.repo
            / "runs"
            / session_id
            / "instrument_validation"
            / f"{session_id}-{slot}"
        )
        (root / "raw").mkdir(parents=True)
        payloads = {
            "raw/powermetrics.plist": b"synthetic raw\n",
            "events.jsonl": b'{"event_type":"synthetic"}\n',
            "power_trace.csv": b"timestamp_s,power_w\n1,2\n",
        }
        for relative, raw in payloads.items():
            (root / relative).write_bytes(raw)
        evidence = {
            "validation_id": f"{session_id}-{slot}",
            "status": "valid",
            "b_fiducial_s": 0.025,
            "capture_wall_time_s": 99.0,
            "bindings": self.t1,
            "artifact_sha256": {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in payloads.items()
            },
        }
        evidence_raw = json.dumps(evidence, sort_keys=True).encode() + b"\n"
        (root / "instrument_evidence.json").write_bytes(evidence_raw)
        manifest_artifacts = {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in GOVERNED_ARTIFACTS
            if name != "manifest.json"
        }
        (root / "manifest.json").write_text(
            json.dumps(
                {
                    "validation_id": f"{session_id}-{slot}",
                    "artifacts": manifest_artifacts,
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return root

    def test_tail_refusal_then_public_abandon_exit_completes_operation(self) -> None:
        self.ledger.write_bytes(b'{"orphan":true}\n')
        refused = self._run("repair")
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(
            json.loads(refused.stdout)["code"], RefusalCode.TAIL_REQUIRES_ABANDON.value
        )
        exited = self._run(
            "abandon-tail",
            "--operator-identity",
            "test-operator",
            "--attestation-reason",
            "witness exact orphaned tail",
        )
        self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
        payload = json.loads(exited.stdout)
        self.assertEqual(payload["inspection"]["state"], "clean")
        self.assertEqual(
            payload["terminal_result"],
            REFUSAL_BY_CODE[RefusalCode.TAIL_REQUIRES_ABANDON].terminal_result.value,
        )

    def test_complete_custody_public_resume_reaches_operation_completed(self) -> None:
        plan = self._open_session("session-resume")
        self._complete_custody("session-resume", "pre")
        status = self._run(
            "session-status", "--session-id", "session-resume", "--plan", str(plan)
        )
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertEqual(json.loads(status.stdout)["slots"]["pre"]["custody_state"], "complete")
        refused = self._run(
            "readiness",
            "--phase",
            "pre-slot",
            "--session-id",
            "session-resume",
            "--slot",
            "pre",
            "--attempt-id",
            "session-resume-pre",
            "--plan",
            str(plan),
        )
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(
            json.loads(refused.stdout)["code"],
            RefusalCode.CUSTODY_COMPLETE_USE_RESUME.value,
        )
        resumed = self._run(
            "resume-finalize",
            "--session-id",
            "session-resume",
            "--slot",
            "pre",
            "--plan",
            str(plan),
        )
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)["terminal_result"], "operation_completed")

    def test_partial_custody_public_abort_reaches_declared_session_abort(self) -> None:
        plan = self._open_session("session-partial")
        partial = (
            self.repo
            / "runs"
            / "session-partial"
            / "instrument_validation"
            / "session-partial-pre"
        )
        (partial / "raw").mkdir(parents=True)
        (partial / "raw" / "powermetrics.plist").write_bytes(b"partial")
        refused = self._run(
            "readiness",
            "--phase",
            "pre-slot",
            "--session-id",
            "session-partial",
            "--slot",
            "pre",
            "--attempt-id",
            "session-partial-pre",
            "--plan",
            str(plan),
        )
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(
            json.loads(refused.stdout)["code"], RefusalCode.CUSTODY_PARTIAL.value
        )
        exited = self._run(
            "abort-session",
            "--session-id",
            "session-partial",
            "--plan",
            str(plan),
            "--reason",
            "partial-custody-witness",
        )
        self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
        self.assertEqual(
            json.loads(exited.stdout)["terminal_result"],
            REFUSAL_BY_CODE[RefusalCode.CUSTODY_PARTIAL].terminal_result.value,
        )

    def test_live_holder_refuses_resume_then_sigkill_allows_fresh_resume(self) -> None:
        plan = self._open_session("session-live")
        self._complete_custody("session-live", "pre")
        holder_code = (
            "import sys,time; from pathlib import Path; "
            "from joulewise.calibration_ledger import CalibrationWriterLease, claim_bracket_session_slot; "
            f"lease=CalibrationWriterLease(Path({str(self.ledger)!r})); lease.acquire(); "
            f"claim_bracket_session_slot(Path({str(self.ledger)!r}), session_id='session-live', slot='pre', attempt_id='session-live-pre'); "
            "print('LEASED', flush=True); time.sleep(60)"
        )
        holder = subprocess.Popen(
            [sys.executable, "-c", holder_code],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_cli_env(),
        )
        try:
            self.assertEqual(holder.stdout.readline().strip(), "LEASED")
            refused = self._run(
                "resume-finalize",
                "--session-id",
                "session-live",
                "--slot",
                "pre",
                "--plan",
                str(plan),
            )
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(
                json.loads(refused.stdout)["code"],
                RefusalCode.LIVE_WRITER_CONTENTION.value,
            )
            os.kill(holder.pid, signal.SIGKILL)
            holder.communicate(timeout=10)
            exited = self._run(
                "resume-finalize",
                "--session-id",
                "session-live",
                "--slot",
                "pre",
                "--plan",
                str(plan),
            )
            self.assertEqual(exited.returncode, 0, exited.stdout + exited.stderr)
            payload = json.loads(exited.stdout)
            self.assertEqual(
                payload["terminal_result"],
                REFUSAL_BY_CODE[
                    RefusalCode.LIVE_WRITER_CONTENTION
                ].terminal_result.value,
            )
        finally:
            if holder.poll() is None:
                holder.kill()
                holder.communicate(timeout=10)
            else:
                if holder.stdout is not None:
                    holder.stdout.close()
                if holder.stderr is not None:
                    holder.stderr.close()


if __name__ == "__main__":
    unittest.main()
