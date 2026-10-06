"""HAZARD_PACK flag path through the fiducial writer (gate-prune core lane VPF).

DESIGN.md (core prune) rows A6-R2/R3, A7, A8 and A15.  On a HAZARD window (the
runs root carries the hazard lineage locator) the writer records these
representation checks as ``joulewise.flag.v1`` records in
``<custody>/flags/core-fiducial.jsonl`` and keeps collecting; on the legacy
path (no locator) the same state still refuses exactly as before.  Each test
also pins a keeper that still refuses on HAZARD.

Every run is the real writer CLI in a private synthetic repository (the
calibration witness sandbox), driven by the fixture sampler and fake MLX.
This module imports no flag code so it also runs against the base commit,
where each HAZARD assertion fails.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
import unittest

from joulewise.calibration_exits import RefusalCode
from tests import test_calibration_exits as exits
from tests.calibration_exits_fixtures.custody_hang import BlockedArtifact, CustodyFixture

# Module attributes, never names bound here: a TestCase class imported into
# this namespace would be collected and run (the whole witness corpus).
REPO_ROOT = exits.REPO_ROOT

HAZARD_LOCATOR_SCHEMA = "joulewise.hazard_window_lineage_locator.v1"
LOCATOR_BASENAME = ".joulewise-launch-lineage.json"
WINDOW_PLAN_ID = "hazard-window-plan"
WINDOW_ATTEMPT = 2
_TIME_SCALE = "0.001"
_SAMPLER_ACK_TIMEOUT_S = 30.0


def tearDownModule() -> None:
    exits.assert_no_owned_fake_sampler_survivors()


class HazardWriterRig:
    """One witness sandbox; ``hazard()`` turns a session's runs root into a HAZARD root."""

    def __init__(self, witness: "exits.PublicGovernedExitWitnessTests") -> None:
        self.w = witness
        self.repo = witness.repo

    def real_writer_state(self, session_id: str) -> dict:
        return self.w._state_real_writer(session_id)

    def runs_root(self, state: dict) -> Path:
        return Path(state["output_root"]).parent

    def custody(self, state: dict) -> Path:
        return self.repo / f"custody-{state['session_id']}"

    def hazard(self, state: dict) -> Path:
        custody = self.custody(state)
        custody.mkdir(parents=True, exist_ok=True)
        (custody / "night_plan.json").write_text(json.dumps({
            "plan_id": WINDOW_PLAN_ID,
            "hazard_window": {"attempt": WINDOW_ATTEMPT},
        }) + "\n", encoding="utf-8")
        runs_root = self.runs_root(state)
        runs_root.mkdir(parents=True, exist_ok=True)
        locator = runs_root / LOCATOR_BASENAME
        locator.write_text(json.dumps({
            "schema_version": HAZARD_LOCATOR_SCHEMA,
            "launch_lineage": {"window_context": {"custody_root": str(custody)}},
        }) + "\n", encoding="utf-8")
        return locator

    def legacy(self, state: dict) -> None:
        (self.runs_root(state) / LOCATOR_BASENAME).unlink(missing_ok=True)

    def writer_args(self, state: dict, *, slot: str = "pre", extra=()) -> list[str]:
        return [
            "--allow-live", "--power-policy", state["epoch"]["power_policy"],
            "--ledger", str(self.w.ledger), "--head-pin", str(self.w.pin),
            "--session-id", state["session_id"], "--slot", slot,
            "--attempt-id", f"{state['session_id']}-{slot}",
            "--output-root", str(state["output_root"]),
            "--sampler-binary", str(self.w.fake_sampler), "--sampler-direct-for-test",
            "--time-scale-for-test", _TIME_SCALE,
            "--battery-probe-fixture-for-test",
            str(REPO_ROOT / "tests/fixtures/battery_float/float.ioreg"),
            "--identity-epoch-json-for-test", str(state["identity_path"]),
            "--sampler-ready-timeout-s", str(_SAMPLER_ACK_TIMEOUT_S),
            "--rollover-timeout-s", "1.0",
            *extra,
        ]

    def writer_env(self, state: dict, **overrides: str) -> dict[str, str]:
        return {
            **exits._fresh_cli_env(),
            "JW_FAKE_SAMPLER_MODE": "normal",
            "JW_FAKE_HW_MODEL": state["epoch"]["hardware_model"],
            "JW_FAKE_OS_BUILD": state["epoch"]["os_build"],
            "JW_FAKE_SAMPLER_ELAPSED_NS": "200000",
            "JW_FAKE_TIME_SCALE": _TIME_SCALE,
            "JW_FAKE_TIME_ORIGIN": repr(time.time()),
            **overrides,
        }

    def run_writer(self, state: dict, *, slot: str = "pre", extra=(), **env: str):
        return self.w._run_script(
            self.w.writer_script, *self.writer_args(state, slot=slot, extra=extra),
            env=self.writer_env(state, **env),
        )

    def flags(self, state: dict) -> list[dict]:
        path = self.custody(state) / "flags" / "core-fiducial.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def flags_of_kind(self, state: dict, kind: str) -> list[dict]:
        return [flag for flag in self.flags(state)
                if isinstance(flag.get("observed"), dict) and flag["observed"].get("kind") == kind]


def _refusal(test: unittest.TestCase, completed) -> dict:
    test.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
    lines = [line for line in completed.stderr.splitlines() if line.startswith("{")]
    return json.loads(lines[-1])


class _SandboxCase(unittest.TestCase):
    def setUp(self) -> None:
        witness = exits.PublicGovernedExitWitnessTests(methodName="runTest")
        witness.setUp()
        self.addCleanup(witness.doCleanups)
        self.addCleanup(witness.tearDown)
        self.rig = HazardWriterRig(witness)

    def assert_window_flag(self, flag: dict, code: str) -> None:
        self.assertEqual(flag["schema_version"], "joulewise.flag.v1")
        self.assertEqual(flag["code"], code)
        self.assertEqual(flag["scope"]["level"], "window")
        self.assertEqual(flag["scope"]["plan_id"], WINDOW_PLAN_ID)
        self.assertEqual(flag["scope"]["attempt"], WINDOW_ATTEMPT)
        self.assertEqual(flag["source"]["collector"], "core.core-fiducial")
        self.assertEqual(flag["blinding"], "STRUCTURE")


class CommittedPinTests(_SandboxCase):
    """A6-R2: the committed-pin (``git show``) comparison is a flag on HAZARD."""

    def test_uncommitted_pin_refuses_legacy_and_flags_hazard(self) -> None:
        state = self.rig.real_writer_state("session-pin")
        # Same pin value, different bytes: git HEAD no longer equals the file.
        pin = json.loads(self.rig.w.pin.read_text(encoding="utf-8"))
        self.rig.w.pin.write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")

        # Legacy: the snapshot carries calibration_ledger_head_uncommitted, so
        # the slot is not a governed extension of the committed pin.
        legacy = self.rig.run_writer(state)
        refusal = _refusal(self, legacy)
        self.assertEqual(refusal["code"], RefusalCode.RESERVED_SLOT_MISMATCH.value)
        self.assertEqual(self.rig.flags(state), [])

        self.rig.hazard(state)
        completed = self.rig.run_writer(state)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")
        flags = self.rig.flags_of_kind(state, "historical_custody_unverified")
        self.assertEqual(len(flags), 1, self.rig.flags(state))
        self.assert_window_flag(flags[0], "calibration.writer_record_flagged")
        self.assertEqual(flags[0]["observed"], {
            "kind": "historical_custody_unverified", "slot": "pre", "writer": "fiducial"})

    def test_reserved_identity_mismatch_still_refuses_on_hazard(self) -> None:
        # Keeper (R1 stays in the writer): the reserved vectors differ from the
        # writer's own reads, i.e. the identity changed mid-window.
        state = self.rig.real_writer_state("session-r1-keeper")
        identity = dict(state["epoch"], hardware_model="Mac99,1")
        state["identity_path"].write_text(json.dumps(identity) + "\n", encoding="utf-8")
        self.rig.hazard(state)
        refusal = _refusal(self, self.rig.run_writer(state))
        self.assertIn(refusal["code"], {RefusalCode.RESERVED_SLOT_MISMATCH.value,
                                        RefusalCode.FROZEN_PROTOCOL_INVALID.value})
        self.assertFalse(Path(state["custody_locator"]).exists())


class HistoricalCustodyTests(unittest.TestCase):
    """A6-R2/R3: the historical custody pass and its budget are skipped on HAZARD.

    The fixture ledger holds three committed, finalized historical observations
    (``CustodyFixture``); a bracket session is opened on top of it.
    """

    def _session(self, fixture: CustodyFixture) -> tuple[HazardWriterRig, dict]:
        rig = HazardWriterRig(fixture.witness)
        state = rig.real_writer_state("session-history")
        return rig, state

    def test_deleted_historical_custody_refuses_legacy_and_flags_hazard(self) -> None:
        with CustodyFixture() as fixture:
            rig, state = self._session(fixture)
            (fixture.custodies[0] / "events.jsonl").unlink()

            # Legacy: the snapshot carries calibration_ledger_custody_invalid.
            refusal = _refusal(self, rig.run_writer(state))
            self.assertEqual(refusal["code"], RefusalCode.RESERVED_SLOT_MISMATCH.value)

            rig.hazard(state)
            completed = rig.run_writer(state)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "valid")
            flags = rig.flags_of_kind(state, "historical_custody_unverified")
            self.assertEqual(len(flags), 1, rig.flags(state))

    def test_slow_historical_custody_times_out_legacy_and_is_never_read_on_hazard(self) -> None:
        with CustodyFixture() as fixture:
            rig, state = self._session(fixture)
            with BlockedArtifact(fixture.custodies[0] / "events.jsonl") as fifo:
                refusal = _refusal(self, rig.run_writer(state, extra=("--custody-budget-s", "3")))
                self.assertEqual(refusal["code"], RefusalCode.LEDGER_CUSTODY_TIMEOUT.value)
                self.assertTrue(fifo.entered.is_set())
            with BlockedArtifact(fixture.custodies[0] / "events.jsonl") as fifo:
                rig.hazard(state)
                completed = rig.run_writer(state, extra=("--custody-budget-s", "3"))
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                # The historical pass never opened the blocked artifact.
                self.assertFalse(fifo.entered.is_set())

    def test_exhausted_custody_budget_still_refuses_on_hazard(self) -> None:
        # Keeper: the CustodyDeadline still exists and is still checked on
        # HAZARD (preparation ledger reads and this capture's own custody
        # verification at finalization); only the historical pass is gone.
        with CustodyFixture() as fixture:
            rig, state = self._session(fixture)
            rig.hazard(state)
            refusal = _refusal(self, rig.run_writer(state, extra=("--custody-budget-s", "0.05")))
            self.assertEqual(refusal["code"], RefusalCode.LEDGER_CUSTODY_TIMEOUT.value)


class DisplaySleepTests(_SandboxCase):
    """A7: a failed ``pmset displaysleepnow`` action is a flag on HAZARD."""

    def test_failed_display_action_flags_and_capture_finalizes(self) -> None:
        state = self.rig.real_writer_state("session-display")
        self.rig.hazard(state)
        completed = self.rig.run_writer(state, extra=(
            "--sleep-display-before-capture", "--display-arm-binary", "/usr/bin/false"))
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")
        flags = self.rig.flags_of_kind(state, "display_sleep_action_failed")
        self.assertEqual(len(flags), 1, self.rig.flags(state))
        self.assert_window_flag(flags[0], "calibration.writer_record_flagged")
        self.assertEqual(flags[0]["observed"]["slot"], "pre")
        self.assertEqual(flags[0]["observed"]["returncode"], 1)
        self.assertEqual(flags[0]["source"]["legacy_code"], RefusalCode.DISPLAY_ARM_FAILED.value)

    def test_negative_countdown_still_refuses_on_hazard(self) -> None:
        state = self.rig.real_writer_state("session-countdown")
        self.rig.hazard(state)
        refusal = _refusal(self, self.rig.run_writer(state, extra=("--arm-countdown-s", "-1")))
        self.assertEqual(refusal["code"], RefusalCode.DISPLAY_ARM_FAILED.value)
        self.assertEqual(self.rig.flags_of_kind(state, "display_sleep_action_failed"), [])


class BindingStringTests(_SandboxCase):
    """A8: a binding string missing from the sampler header is filled and flagged."""

    def test_missing_hardware_model_is_filled_from_the_writer_read(self) -> None:
        state = self.rig.real_writer_state("session-binding")
        self.rig.hazard(state)
        completed = self.rig.run_writer(state, JW_FAKE_HW_MODEL="")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        evidence = json.loads(
            (Path(state["custody_locator"]) / "instrument_evidence.json").read_text())
        self.assertEqual(evidence["status"], "valid")
        self.assertEqual(evidence["bindings"]["hardware_model"], state["epoch"]["hardware_model"])
        flags = self.rig.flags_of_kind(state, "binding_read_substituted")
        self.assertEqual(len(flags), 1, self.rig.flags(state))
        self.assertEqual(flags[0]["observed"]["fields"], ["hardware_model"])

    def test_present_but_different_header_value_is_never_replaced(self) -> None:
        # Keeper: a measured identity that differs from the reservation is a
        # real identity change; it still fails the capture.
        state = self.rig.real_writer_state("session-binding-keeper")
        self.rig.hazard(state)
        completed = self.rig.run_writer(state, JW_FAKE_HW_MODEL="Mac99,1")
        self.assertNotEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(self.rig.flags_of_kind(state, "binding_read_substituted"), [])


class ExecutedCodeTests(_SandboxCase):
    """A15: executed estimator code that differs from the acceptance's is a flag."""

    def test_stale_estimator_code_refuses_legacy_and_flags_hazard(self) -> None:
        state = self.rig.real_writer_state("session-stale-code")
        reduce_path = self.rig.repo / "joulewise" / "reduce.py"
        reduce_path.write_text(reduce_path.read_text() + "\n# executed differs from sealed\n")

        refusal = _refusal(self, self.rig.run_writer(state))
        self.assertEqual(refusal["code"], RefusalCode.FROZEN_PROTOCOL_INVALID.value)
        self.assertEqual(refusal["context"]["reason"], "acceptance_artifact_stale")

        self.rig.hazard(state)
        completed = self.rig.run_writer(state)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        flags = [flag for flag in self.rig.flags(state)
                 if flag["code"] == "code.executed_differs_from_sealed"]
        self.assertEqual(len(flags), 1, self.rig.flags(state))
        self.assert_window_flag(flags[0], "code.executed_differs_from_sealed")
        observed = flags[0]["observed"]
        self.assertEqual(observed["component"], "fiducial_estimator_and_protocol")
        self.assertNotEqual(observed["recorded"]["estimator_code_sha256"]["joulewise/reduce.py"],
                            observed["executed"]["estimator_code_sha256"]["joulewise/reduce.py"])
        evidence = json.loads(
            (Path(state["custody_locator"]) / "instrument_evidence.json").read_text())
        self.assertEqual(evidence["acceptance_preflight"]["stale_code"]["executed"],
                         observed["executed"])

    def test_epoch_mismatch_still_refuses_with_stale_code_allowed(self) -> None:
        # Keeper: only the digest comparison relaxes; the epoch check stays.
        state = self.rig.real_writer_state("session-stale-epoch")
        reduce_path = self.rig.repo / "joulewise" / "reduce.py"
        reduce_path.write_text(reduce_path.read_text() + "\n# executed differs from sealed\n")
        identity = dict(state["epoch"], os_build="99Z999")
        state["identity_path"].write_text(json.dumps(identity) + "\n", encoding="utf-8")
        self.rig.hazard(state)
        refusal = _refusal(self, self.rig.run_writer(state))
        self.assertEqual(refusal["code"], RefusalCode.FROZEN_PROTOCOL_INVALID.value)
        self.assertEqual(refusal["context"]["reason"], "acceptance_artifact_epoch_mismatch")


if __name__ == "__main__":
    unittest.main()
