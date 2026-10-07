"""HAZARD_PACK flag path through the controller (gate-prune core lane CTL).

DESIGN.md (core-prune) section 3.1 rows A1, A5, A11, A14, A17 and A18, plus
PLAN2 section 2.3 errata s2-01 (the controller part) and s2-02.

Each relaxed refusal is tested three ways:

- on a HAZARD root it now collects a bundle and writes its flag;
- the same scenario with ``hazard=None`` (the legacy path) still refuses;
- the keeper next to it (a physics or number-integrity check) still refuses
  on the HAZARD root.

A1, A5 and A14 run on a real HAZARD window (``tests.test_window_lineage``:
real lineage, git, ledger and a real Revision-5 pre-slot capture).  A11, A17,
A18 and s2-02 exercise the member lifecycle; there the HAZARD dispatch
(``joulewise.flags.core.hazard_flag_context``) is patched to return a context
whose custody root is a temporary directory, because the lifecycle stages do
not depend on how the context was obtained.  These tests check collection
only; the reducer's claim barrier is unchanged and is not under test here.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import PropertyMock, patch

from joulewise import adapters, arm_readiness, battery_float, controller
from joulewise import calibration_ledger as ledger
from joulewise.clock import FakeClock
from joulewise.environment import evaluate_environment_policy
from joulewise.flags import core as flags_core
from joulewise.interfaces import AdapterResult, FailureReason
from joulewise.sampler_teardown import SamplerTeardown
from joulewise.schemas import BenchmarkConfig, CampaignPolicy, RunStatus
from tests.test_controller import (
    AdmissionIdleRegistry,
    DeterministicClock,
    RetryAdmissionPowermetricsRegistry,
    _produce_admission_powermetrics_bundle,
    campaign_policy_fixture,
    make_config,
)
from tests.test_window_lineage import EVIDENCE, ROOT, _MockWorkloadRegistry, build_window

WRITER = "core-controller"


def read_flags(custody: Path) -> list[dict[str, Any]]:
    path = custody / flags_core.FLAGS_DIRNAME / f"{WRITER}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_bytes().splitlines() if line.strip()]


def codes(custody: Path) -> list[str]:
    return [flag["code"] for flag in read_flags(custody)]


def observed(flag: dict[str, Any]) -> Any:
    value = flag["observed"]
    return value.get("value", value) if isinstance(value, dict) and value.get("scope_unresolved") else value


# ---------------------------------------------------------------------------
# A real HAZARD window (A1, A5, A14)


class _WindowRegistry(_MockWorkloadRegistry):
    """Mock workload; the telemetry reports the given device metadata."""

    def __init__(self, device_metadata: dict[str, Any] | None = None) -> None:
        self._device_metadata = device_metadata

    def resolve_telemetry(self, config, clock):
        telemetry, failure = super().resolve_telemetry(config, clock)
        if self._device_metadata is not None:
            value = self._device_metadata
            telemetry.device_metadata = lambda config, context=None: json.loads(json.dumps(value))
        return telemetry, failure


AC_PREFLIGHT = {"snapshot": {
    "power_source": "AC Power", "power": {"external_connected": True}, "low_power_mode": False}}


def run_window_member(w, *, preflight: dict[str, Any] | None = None,
                      registry: Any = None, power_policy: str = "ac_high_power"):
    """``tests.test_window_lineage.run_member`` with the policy inputs exposed."""

    config = BenchmarkConfig.from_mapping(json.loads(w.member_path.read_bytes()))
    policy = CampaignPolicy.from_mapping(json.loads(
        (ROOT / "configs/campaign_policies/quiet_mac_exploratory.json").read_bytes()))
    policy = replace(policy, idle_admission=replace(policy.idle_admission, enabled=False))
    with patch.object(sys, "argv", ["joulewise", "run", str(w.member_path)]), \
            patch.dict(os.environ, {}, clear=True):
        return controller.run_benchmark(
            config, w.claim, FakeClock(start=1700000000),
            registry=registry or _WindowRegistry(), environment_snapshot=None,
            campaign_policy=policy,
            campaign_environment_preflight=json.loads(json.dumps(preflight or AC_PREFLIGHT)),
            instrument_calibration_dir=w.capture, instrument_power_policy=power_policy)


def load_attachment(w, *, hazard: Any, power_policy: str = "ac_high_power",
                    runtime_power_policy: str | None = "ac_high_power",
                    runtime_powermetrics_sha256: str | None = None):
    """The attachment alone, with the HAZARD context passed explicitly."""

    config = BenchmarkConfig.from_mapping(json.loads(w.member_path.read_bytes()))
    digest = (runtime_powermetrics_sha256 if runtime_powermetrics_sha256 is not None
              else EVIDENCE["bindings"]["powermetrics_sha256"])
    with patch.object(sys, "argv", ["joulewise", "run", str(w.member_path)]), \
            patch.dict(os.environ, {}, clear=True):
        return controller._load_instrument_calibration_attachment(
            w.capture, power_policy=power_policy,
            runtime_powermetrics_sha256=digest,
            runtime_power_policy=runtime_power_policy, runs_root=w.claim, config=config,
            **hazard_keyword(hazard))


def hazard_keyword(hazard: Any) -> dict[str, Any]:
    """Pass ``hazard`` only when set, so legacy twins also run on the base commit."""

    return {} if hazard is None else {"hazard": hazard}


def evidence_missing_verdict(*_args, **_kwargs) -> battery_float.PairVerdict:
    return battery_float.PairVerdict(
        kind="calibration", status="battery_float_evidence_missing",
        reasons=("pre evidence missing: gauge update stale",),
        pre_raw_sha256=None, post_raw_sha256=None, pre_update_age_s=None,
        post_update_age_s=None, delta_q_mah=None)


class HazardWindowAttachmentTests(unittest.TestCase):
    """A1, A5, A14 on a real HAZARD window, one window per test."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.w = build_window(Path(tmp.name))
        self.custody = self.w.custody
        self.hazard = flags_core.hazard_flag_context(self.w.claim, writer=WRITER)
        self.assertIsNotNone(self.hazard, "the fixture root must carry the HAZARD locator")

    def rerun(self):
        """Run the member again: remove its bundle, keep the flag file."""

        for child in self.w.claim.iterdir():
            if child.is_dir() and child.name == "hazard-member":
                import shutil

                shutil.rmtree(child)
        return run_window_member(self.w)

    # A1 ------------------------------------------------------------------

    def test_a1_battery_verdict_not_pass_collects_and_flags_once(self) -> None:
        with patch.object(battery_float, "authenticate_capture", side_effect=evidence_missing_verdict):
            bundle, summary = run_window_member(self.w)
            self.assertTrue((bundle / "metadata.json").exists())
            self.rerun()
        flags = [flag for flag in read_flags(self.custody)
                 if flag["code"] == "calibration.capture_battery_pair_unverified"]
        self.assertEqual(len(flags), 1, "a window fact emitted by every member is one line")
        self.assertEqual(flags[0]["scope"]["level"], "window")
        value = observed(flags[0])
        self.assertEqual(value["slot"], "pre")
        self.assertEqual(value["status"], "battery_float_evidence_missing")
        # The raw pair is still carried into the bundle.
        for phase in ("pre", "post"):
            self.assertEqual(
                (bundle / "instrument_calibration/raw" / f"battery_float.{phase}.ioreg").read_bytes(),
                (self.w.capture / "raw" / f"battery_float.{phase}.ioreg").read_bytes())

    def test_a1_legacy_path_still_refuses_the_same_verdict(self) -> None:
        with patch.object(battery_float, "authenticate_capture", side_effect=evidence_missing_verdict):
            with self.assertRaisesRegex(ValueError, "G2-b pre slot battery battery_float_evidence_missing"):
                load_attachment(self.w, hazard=None)

    def test_a1_keeper_changed_battery_raw_bytes_still_refuse(self) -> None:
        raw = self.w.capture / "raw/battery_float.post.ioreg"
        raw.write_bytes(raw.read_bytes() + b" ")
        with patch.object(battery_float, "authenticate_capture", side_effect=evidence_missing_verdict):
            # The verdict is relaxed on HAZARD; the raw-pair carry still refuses.
            with self.assertRaisesRegex(ValueError, "G2-b pre slot battery"):
                run_window_member(self.w)
        self.assertFalse((self.w.claim / "hazard-member").exists())

    # A5 ------------------------------------------------------------------

    def test_a5_member_attachment_runs_no_git(self) -> None:
        git_calls: list[tuple] = []

        def no_git(*args, **_kwargs):
            git_calls.append(args)
            raise arm_readiness.ArmReadinessError("readiness_pack_unreadable", "git refused by the test")

        def no_committed_pin(*args, **_kwargs):
            git_calls.append(("git show HEAD:<pin>",) + args)
            return None

        with patch.object(arm_readiness, "_run_git", side_effect=no_git), \
                patch.object(ledger, "_committed_pin_bytes", side_effect=no_committed_pin):
            bundle, summary = run_window_member(self.w)
        self.assertEqual(git_calls, [])
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        self.assertEqual(metadata["instrument_calibration"]["g2b_pre_slot"]["slot"], "pre")

    def _relocated_pack_context(self):
        """The window's authenticated context, its pack copied outside configs/campaigns."""

        import shutil

        moved = self.w.repo / "packs" / self.w.pack.name
        shutil.copytree(self.w.pack, moved)
        real = arm_readiness.authenticate_campaign_launch_lineage

        def relocated(*args, **kwargs):
            context = dict(real(*args, **kwargs))
            context["pack_root"] = str(moved)
            return context

        return moved, relocated

    def test_census_pack_outside_configs_campaigns_collects_and_flags(self) -> None:
        # Refusal census 2026-10-06: at ba0e0c72e this raised
        # "G2-b attachment pack root is not <repo>/configs/campaigns/<pack>"
        # and every member of the window refused before its bundle.
        moved, relocated = self._relocated_pack_context()
        with patch.object(arm_readiness, "authenticate_campaign_launch_lineage", side_effect=relocated):
            attachment = load_attachment(self.w, hazard=self.hazard)
        self.assertIsNotNone(attachment)
        flags = [flag for flag in read_flags(self.custody) if flag["code"] == "records.pin_ledger"]
        self.assertEqual(len(flags), 1, flags)
        self.assertEqual(flags[0]["scope"]["level"], "window")
        value = observed(flags[0])
        self.assertEqual(value["kind"], "pack_root_layout")
        self.assertEqual(value["pack_root"], str(moved))
        self.assertEqual(Path(value["repository"]).resolve(), self.w.repo.resolve())

    def test_census_relocated_pack_outside_any_worktree_refuses(self) -> None:
        # Sol 6.1 review F10: with no repository the ledger cannot be found, so
        # the session binding cannot be checked; that stays a refusal.
        import shutil

        outside = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR") or None))
        self.addCleanup(shutil.rmtree, outside, True)
        moved = outside / self.w.pack.name
        shutil.copytree(self.w.pack, moved)
        real = arm_readiness.authenticate_campaign_launch_lineage

        def relocated(*args, **kwargs):
            context = dict(real(*args, **kwargs))
            context["pack_root"] = str(moved)
            return context

        with patch.object(arm_readiness, "authenticate_campaign_launch_lineage", side_effect=relocated):
            with self.assertRaises(arm_readiness.ArmReadinessError):
                load_attachment(self.w, hazard=self.hazard)

    def test_census_relocated_pack_keeper_session_binding_still_refuses(self) -> None:
        _moved, relocated = self._relocated_pack_context()
        real = ledger.calibration_session_status

        def unfinalized(*args, **kwargs):
            status = json.loads(json.dumps(real(*args, **kwargs), default=str))
            status["slots"]["pre"]["finalized"] = False
            return status

        with patch.object(arm_readiness, "authenticate_campaign_launch_lineage", side_effect=relocated), \
                patch.object(ledger, "calibration_session_status", side_effect=unfinalized):
            with self.assertRaisesRegex(ValueError, "requires its session's finalized pre slot"):
                load_attachment(self.w, hazard=self.hazard)

    def test_a5_legacy_path_still_runs_git(self) -> None:
        with patch.object(arm_readiness, "_run_git",
                          side_effect=arm_readiness.ArmReadinessError("readiness_pack_unreadable", "refused")):
            with self.assertRaises(arm_readiness.ArmReadinessError):
                load_attachment(self.w, hazard=None)

    def test_a5_ledger_shape_not_governed_extension_collects_and_flags(self) -> None:
        with patch.object(ledger.CalibrationLedgerSnapshot, "is_governed_open_bracket_extension",
                          new_callable=PropertyMock, return_value=False):
            bundle, summary = run_window_member(self.w)
        self.assertTrue((bundle / "metadata.json").exists())
        flags = [flag for flag in read_flags(self.custody) if flag["code"] == "records.pin_ledger"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["scope"]["level"], "window")
        self.assertIn("refusal_reasons", observed(flags[0]))

    def test_a5_legacy_path_still_refuses_ledger_shape(self) -> None:
        with patch.object(ledger.CalibrationLedgerSnapshot, "is_governed_open_bracket_extension",
                          new_callable=PropertyMock, return_value=False):
            with self.assertRaisesRegex(ValueError, "does not match the authenticated finalized pre slot"):
                load_attachment(self.w, hazard=None)

    def test_a5_keeper_unfinalized_pre_slot_still_refuses(self) -> None:
        real = ledger.calibration_session_status

        def unfinalized(*args, **kwargs):
            status = json.loads(json.dumps(real(*args, **kwargs), default=str))
            status["slots"]["pre"]["finalized"] = False
            return status

        with patch.object(ledger, "calibration_session_status", side_effect=unfinalized):
            with self.assertRaisesRegex(ValueError, "requires its session's finalized pre slot"):
                run_window_member(self.w)
        self.assertFalse((self.w.claim / "hazard-member").exists())

    def test_a5_keeper_session_window_mismatch_still_refuses(self) -> None:
        real = ledger.load_calibration_ledger_snapshot

        def foreign_window(*args, **kwargs):
            snapshot = real(*args, **kwargs)
            sessions = tuple(replace(session, window_id="another-window")
                             for session in snapshot.bracket_sessions)
            return replace(snapshot, bracket_sessions=sessions)

        with patch.object(ledger, "load_calibration_ledger_snapshot", side_effect=foreign_window):
            with self.assertRaisesRegex(ValueError, "does not match the authenticated finalized pre slot"):
                run_window_member(self.w)

    def test_a5_keeper_receipt_t1_binding_mismatch_still_refuses(self) -> None:
        real = ledger.load_calibration_ledger_snapshot

        def foreign_t1(*args, **kwargs):
            snapshot = real(*args, **kwargs)
            sessions = []
            for session in snapshot.bracket_sessions:
                pre = session.finalized_slots.get("pre")
                if pre is not None:
                    pre = replace(pre, t1_bindings={**pre.t1_bindings, "power_policy": "foreign"})
                    session = replace(session, finalized_slots={**session.finalized_slots, "pre": pre})
                sessions.append(session)
            return replace(snapshot, bracket_sessions=tuple(sessions))

        with patch.object(ledger, "load_calibration_ledger_snapshot", side_effect=foreign_t1):
            with self.assertRaisesRegex(ValueError, "does not match the authenticated finalized pre slot"):
                run_window_member(self.w)
        self.assertFalse((self.w.claim / "hazard-member").exists())

    def test_a5_uncommitted_pin_refuses_on_legacy_and_is_not_read_on_hazard(self) -> None:
        with patch.object(ledger, "_committed_pin_bytes", return_value=b"another pin\n"):
            with self.assertRaises(ValueError):
                load_attachment(self.w, hazard=None)
            attachment = load_attachment(self.w, hazard=self.hazard)
        self.assertEqual(attachment.metadata["g2b_pre_slot"]["slot"], "pre")

    # A14 -----------------------------------------------------------------

    def test_a14_runtime_power_policy_unverified_collects_and_flags(self) -> None:
        preflight = {"snapshot": {"power_source": "Battery Power",
                                  "power": {"external_connected": True}, "low_power_mode": False}}
        bundle, summary = run_window_member(self.w, preflight=preflight)
        self.assertTrue((bundle / "metadata.json").exists())
        flags = [flag for flag in read_flags(self.custody)
                 if flag["code"] == "calibration.power_policy_unverified"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["scope"]["level"], "window")
        self.assertEqual(observed(flags[0])["runtime_observation"], None)
        self.assertEqual(observed(flags[0])["recorded_label"], "ac_high_power")
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        self.assertIsNone(metadata["instrument_calibration"]["binding_observations"]["power_policy"])

    def test_a14_cli_label_mismatch_collects_and_flags(self) -> None:
        bundle, _summary = run_window_member(self.w, power_policy="battery_any")
        self.assertTrue((bundle / "metadata.json").exists())
        flags = [flag for flag in read_flags(self.custody)
                 if flag["code"] == "calibration.power_policy_unverified"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(observed(flags[0])["cli_label"], "battery_any")

    def test_a14_legacy_path_still_refuses_labels(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not match a runtime-observed power policy"):
            load_attachment(self.w, hazard=None, runtime_power_policy=None)
        with self.assertRaisesRegex(ValueError, "evidence/power-policy binding is invalid"):
            load_attachment(self.w, hazard=None, power_policy="battery_any")

    def test_a14_unobserved_binary_digest_collects_with_member_flag(self) -> None:
        registry = _WindowRegistry({"rail_manifest": ["mock"], "powermetrics": {}})
        bundle, _summary = run_window_member(self.w, registry=registry)
        self.assertTrue((bundle / "metadata.json").exists())
        flags = [flag for flag in read_flags(self.custody)
                 if flag["code"] == "instrument.binary_identity_unmeasured"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["scope"]["level"], "member")
        self.assertEqual(flags[0]["scope"]["run_id"], bundle.name)
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        self.assertIsNone(
            metadata["instrument_calibration"]["binding_observations"]["powermetrics_sha256"])

    def test_a14_legacy_path_still_refuses_unobserved_digest(self) -> None:
        config = BenchmarkConfig.from_mapping(json.loads(self.w.member_path.read_bytes()))
        with patch.object(flags_core, "hazard_flag_context", return_value=None), \
                patch.object(sys, "argv", ["joulewise", "run", str(self.w.member_path)]), \
                patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                controller.run_benchmark(
                    config, self.w.claim, FakeClock(start=1700000000),
                    registry=_WindowRegistry({"rail_manifest": ["mock"], "powermetrics": {}}),
                    environment_snapshot=None, campaign_environment_preflight=AC_PREFLIGHT,
                    instrument_calibration_dir=self.w.capture,
                    instrument_power_policy="ac_high_power")
        self.assertFalse((self.w.claim / "hazard-member").exists())

    def test_a14_keeper_different_binary_digest_still_refuses(self) -> None:
        registry = _WindowRegistry({"rail_manifest": ["mock"],
                                    "powermetrics": {"executable_sha256": "0" * 64}})
        with self.assertRaisesRegex(ValueError, "powermetrics binding does not match"):
            run_window_member(self.w, registry=registry)
        self.assertFalse((self.w.claim / "hazard-member").exists())
        self.assertNotIn("instrument.binary_identity_unmeasured", codes(self.custody))


class AttachmentKeeperUnitTests(unittest.TestCase):
    """A14 keepers that a real capture cannot exercise: evidence status and bound."""

    def write_capture(self, root: Path, evidence: dict[str, Any]) -> Path:
        import hashlib

        root.mkdir(parents=True)
        raw = json.dumps(evidence).encode()
        (root / "instrument_evidence.json").write_bytes(raw)
        (root / "manifest.json").write_text(json.dumps({
            "schema_version": "joulewise.instrument_validation_manifest.v1",
            "artifacts": {"instrument_evidence.json": hashlib.sha256(raw).hexdigest()}}))
        return root

    def test_a14_keepers_evidence_status_and_bound_still_refuse_on_hazard(self) -> None:
        hazard = flags_core.HazardFlagContext(
            writer=WRITER, custody_root=None, plan_id=None, attempt=None, scope_resolved=False)
        bindings = {"power_policy": "battery_any", "powermetrics_sha256": "a" * 64}
        with tempfile.TemporaryDirectory() as tmp:
            for name, evidence in (
                ("invalid", {"status": "invalid", "bindings": bindings, "b_fiducial_s": 0.01}),
                ("bound", {"status": "valid", "bindings": bindings, "b_fiducial_s": float("nan")}),
                ("bindings", {"status": "valid", "bindings": None, "b_fiducial_s": 0.01}),
            ):
                directory = self.write_capture(Path(tmp) / name, evidence)
                with self.assertRaisesRegex(ValueError, "evidence/power-policy binding is invalid"), \
                        redirect_stderr_to_null():
                    controller._load_instrument_calibration_attachment(
                        directory, power_policy="ac_high_power",
                        runtime_powermetrics_sha256="a" * 64, runtime_power_policy="ac_high_power",
                        **hazard_keyword(hazard))


class redirect_stderr_to_null:
    """Silence the unwritten-flag marker of a context with no custody root."""

    def __enter__(self):
        import contextlib

        self._stack = contextlib.ExitStack()
        sink = self._stack.enter_context(open(os.devnull, "w"))
        self._stack.enter_context(contextlib.redirect_stderr(sink))
        return self

    def __exit__(self, *exc):
        self._stack.close()
        return False


# ---------------------------------------------------------------------------
# Member lifecycle (A11, A17, A18, s2-01, s2-02)


class _LifecycleBase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.custody = Path(tmp.name) / "custody"
        self.custody.mkdir()
        self.context = flags_core.HazardFlagContext(
            writer=WRITER, custody_root=self.custody, plan_id=None, attempt=None,
            scope_resolved=False)

    def hazard(self):
        return patch.object(flags_core, "hazard_flag_context", return_value=self.context)

    def member_flags(self, code: str) -> list[dict[str, Any]]:
        return [flag for flag in read_flags(self.custody) if flag["code"] == code]


def _guard(**fields: Any) -> dict[str, Any]:
    value = {
        "display_power_state": "all_asleep",
        "screensaver_engaged": False,
        "screensaver_module": "Ventura",
        "screensaver_delay_s": 1200,
        "hid_idle_s": 5.0,
        "power": {"adapter_watts": 140.0, "adapter_description": "synthetic adapter"},
        "errors": {},
    }
    value.update(fields)
    return value


class EnvironmentGuardTests(_LifecycleBase):
    """A11 and the controller half of PLAN2 s2-01."""

    def run_awake(self, run_id: str):
        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        snapshot = {**snapshot, "display_power_state": "any_awake"}
        return controller.run_benchmark(
            make_config(run_id), self.runs_root, FakeClock(start=1_700_000_000.0),
            registry=AdmissionIdleRegistry([False]), environment_snapshot=snapshot,
            campaign_policy=policy, campaign_policy_binding=binding,
            campaign_environment_preflight=preflight)

    def run_live_guard(self, run_id: str, guards: list[dict[str, Any]], *,
                       preflight_snapshot: dict[str, Any] | None = None,
                       registry: Any = None):
        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        if preflight_snapshot is not None:
            preflight = {**preflight, "snapshot": preflight_snapshot,
                         "evaluation": evaluate_environment_policy(
                             preflight_snapshot, policy.environment_guard),
                         "admitted": False}
        calls = iter(range(10_000))

        def observe(**_kwargs):
            # The listed observations in order; the last one repeats (the
            # post-run observation reads the same probe).
            index = min(next(calls), len(guards) - 1)
            return json.loads(json.dumps(guards[index]))

        with patch("joulewise.controller.collect_environment_guard_observation",
                   side_effect=observe):
            return controller.run_benchmark(
                make_config(run_id), self.runs_root, DeterministicClock(),
                registry=registry or AdmissionIdleRegistry([False]), environment_snapshot=snapshot,
                campaign_policy=policy, campaign_policy_binding=binding,
                campaign_environment_preflight=preflight)

    def test_a11_awake_display_collects_with_quiet_state_flag(self) -> None:
        with self.hazard():
            bundle, summary = self.run_awake("hazard-a11-awake")
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertTrue((bundle / "power_trace.csv").exists())
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        admission = metadata["environment_admission"]
        self.assertEqual(admission["decision"], "admitted")
        self.assertIs(admission["critical_environment_passed"], False)
        flags = self.member_flags("env.member_quiet_state_violated")
        self.assertEqual(len(flags), 1, "one flag per code per member")
        self.assertEqual(flags[0]["scope"]["run_id"], bundle.name)
        self.assertEqual(flags[0]["scope"]["level"], "member")
        phases = {row.get("phase") for row in observed(flags[0])["findings"]}
        self.assertEqual(phases, {"per_run_evaluation", "before_attempt_1", "after_attempt_1"})
        self.assertEqual(self.member_flags("env.member_guard_flagged"), [])

    def test_a11_failed_power_and_thermal_findings_are_guard_flags(self) -> None:
        # Measured by the battery and thermal hazard journals: DISCLOSE here.
        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        snapshot = {**snapshot, "thermal_pressure": "serious", "power_source": "Battery Power"}
        with self.hazard():
            bundle, summary = controller.run_benchmark(
                make_config("hazard-a11-proxies"), self.runs_root, FakeClock(start=1_700_000_000.0),
                registry=AdmissionIdleRegistry([False]), environment_snapshot=snapshot,
                campaign_policy=policy, campaign_policy_binding=binding,
                campaign_environment_preflight=preflight)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertEqual(self.member_flags("env.member_quiet_state_violated"), [])
        flags = self.member_flags("env.member_guard_flagged")
        self.assertEqual(len(flags), 1)
        found = {row["code"] for row in observed(flags[0])["findings"]}
        self.assertEqual(found, {"thermal_not_nominal", "power_source_not_ac"})

    def test_a11_legacy_awake_display_still_aborts(self) -> None:
        bundle, summary = self.run_awake("legacy-a11-awake")
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.UNKNOWN_ERROR)
        self.assertEqual(read_flags(self.custody), [])

    def test_a11_unknown_display_collects_with_guard_flag(self) -> None:
        unknown = _guard(display_power_state=None)
        with self.hazard():
            bundle, summary = self.run_live_guard("hazard-a11-unknown", [unknown, unknown])
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertEqual(self.member_flags("env.member_quiet_state_violated"), [])
        flags = self.member_flags("env.member_guard_flagged")
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["scope"]["run_id"], bundle.name)
        admission = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]
        self.assertEqual(admission["decision"], "admitted")
        self.assertIs(admission["critical_environment_passed"], True)

    def run_raising_guard(self, run_id: str, raise_on: set[int]):
        """The fixture's real-valued guard observations, except that the listed calls raise."""

        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        calls = iter(range(10_000))
        seen: list[int] = []

        def observe(**_kwargs):
            index = next(calls)
            seen.append(index)
            if index in raise_on or (-1 in raise_on):
                raise OSError(5, "Input/output error", "system_profiler")
            return _guard()

        with patch("joulewise.controller.collect_environment_guard_observation", side_effect=observe):
            result = controller.run_benchmark(
                make_config(run_id), self.runs_root, DeterministicClock(),
                registry=AdmissionIdleRegistry([False]), environment_snapshot=snapshot,
                campaign_policy=policy, campaign_policy_binding=binding,
                campaign_environment_preflight=preflight)
        return result, seen

    def test_triage_c_a_guard_collector_exception_is_a_flag_not_a_failed_member(self) -> None:
        # Refusal-census triage (c), 2026-10-07: the collector raising inside
        # one guard observation failed the member (the probe re-raised it on
        # the controller thread).  Now that observation is unmeasured: one
        # env.member_guard_flagged finding names it, the other observations'
        # physics readings still apply, and the member is collected.
        with self.hazard():
            (bundle, summary), seen = self.run_raising_guard("hazard-triage-c-one", {1})
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertGreaterEqual(len(seen), 3)
        self.assertEqual(self.member_flags("env.member_quiet_state_violated"), [])
        flags = self.member_flags("env.member_guard_flagged")
        self.assertEqual(len(flags), 1)
        raised = [row for row in observed(flags[0])["findings"] if row.get("status") == "collector_raised"]
        self.assertEqual(len(raised), 1, observed(flags[0]))
        self.assertIn("OSError", raised[0]["error"])
        admission = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]
        self.assertEqual(admission["decision"], "admitted")
        self.assertIs(admission["critical_environment_passed"], True)

    def test_triage_c_every_guard_observation_raising_still_collects_unmeasured(self) -> None:
        # No physics reading at all: every guard observation (admission and
        # post-run) is unmeasured.  The member is collected with the guard
        # flag, whose findings name the post-run observation too.  Audit-fix
        # batch 1 (item 6, 2026-10-07): the post-run observation is unmeasured,
        # not failed, evidence.  Before: post_run_environment_refusals gave
        # environment_admission_failed, which the whole-window verdict turned
        # into member.whole_window_member_failure (EXCLUDE_MEMBER).
        from joulewise.environment_admission import post_run_environment_refusals
        with self.hazard():
            (bundle, summary), _seen = self.run_raising_guard("hazard-triage-c-all", {-1})
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        flags = self.member_flags("env.member_guard_flagged")
        self.assertEqual(len(flags), 1)
        raised = [row for row in observed(flags[0])["findings"] if row.get("status") == "collector_raised"]
        self.assertIn("post_run", [row.get("phase") for row in raised])
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        post_run = metadata["environment"]["post_run_observation"]
        self.assertIn("OSError", post_run["collector_error"])
        self.assertEqual(post_run_environment_refusals(metadata), ())

    def test_item6_only_the_post_run_collector_raising_is_disclosed_not_failed(self) -> None:
        from joulewise.environment_admission import post_run_environment_refusals
        with self.hazard():
            (_bundle, clean), seen = self.run_raising_guard("hazard-item6-count", set())
        self.assertEqual(clean.status, RunStatus.SUCCEEDED, clean.failure_message)
        self.assertEqual(self.member_flags("env.member_guard_flagged"), [])
        last = len(seen) - 1  # the post-run observation is the run's last guard call
        with self.hazard():
            (bundle, summary), _seen = self.run_raising_guard("hazard-item6-post", {last})
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        (flag,) = self.member_flags("env.member_guard_flagged")
        self.assertEqual(flag["scope"]["run_id"], bundle.name)
        self.assertEqual({row.get("phase") for row in observed(flag)["findings"]}, {"post_run"})
        self.assertEqual(self.member_flags("env.member_quiet_state_violated"), [])
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        self.assertEqual(post_run_environment_refusals(metadata), ())
        # A measured reading in a post-run observation still refuses, collector error or not.
        awake = {**metadata["environment"]["post_run_observation"], "display_power_state": "any_awake"}
        self.assertEqual(post_run_environment_refusals({"environment": {"post_run_observation": awake}}),
                         ("environment_admission_failed",))
        # A legacy-shaped unknown reading (no collector error) still refuses as before.
        unknown = {key: value for key, value in awake.items() if key != "collector_error"}
        unknown["display_power_state"] = None
        self.assertEqual(post_run_environment_refusals({"environment": {"post_run_observation": unknown}}),
                         ("environment_admission_failed",))

    def test_triage_c_legacy_guard_collector_exception_still_fails(self) -> None:
        (_bundle, summary), _seen = self.run_raising_guard("legacy-triage-c", {1})
        self.assertEqual(summary.status, RunStatus.FAILED)

    def test_a11_legacy_unknown_display_still_aborts(self) -> None:
        unknown = _guard(display_power_state=None)
        bundle, summary = self.run_live_guard("legacy-a11-unknown", [unknown, unknown])
        self.assertEqual(summary.status, RunStatus.FAILED)

    def test_a11_keeper_busy_idle_admission_still_aborts(self) -> None:
        with self.hazard():
            _bundle, summary = self.run_live_guard(
                "hazard-a11-busy", [_guard()] * 4,
                registry=AdmissionIdleRegistry([False, False], cpu_busy_sequence=[0.9, 0.9]))
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertIn("idle environment admission failed after one retry", summary.failure_message)

    def test_s2_01_stage_preflight_does_not_decide_the_member(self) -> None:
        policy, _binding, _preflight, snapshot = campaign_policy_fixture(exploratory=False)
        awake_stage = {**snapshot, "display_power_state": "any_awake"}
        with self.hazard():
            bundle, summary = self.run_live_guard(
                "hazard-s201", [_guard(), _guard()], preflight_snapshot=awake_stage)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        admission = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]
        self.assertIs(admission["critical_environment_passed"], True)
        self.assertIs(admission["reference_provenance_present"], True)
        eligibility = controller._experiment_cooldown_reference_eligibility(bundle, summary)
        self.assertTrue(eligibility["eligible"], eligibility)

    def test_s2_01_stage_preflight_without_evaluation_does_not_decide_the_member(self) -> None:
        # The shape of a stage preflight whose probe raised (A10): no evaluation.
        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        preflight = {**preflight, "evaluation": None, "admitted": False,
                     "error": "injected preflight probe failure"}
        with self.hazard(), patch("joulewise.controller.collect_environment_guard_observation",
                                  side_effect=lambda **_kwargs: _guard()):
            bundle, summary = controller.run_benchmark(
                make_config("hazard-s201-noeval"), self.runs_root, DeterministicClock(),
                registry=AdmissionIdleRegistry([False]), environment_snapshot=snapshot,
                campaign_policy=policy, campaign_policy_binding=binding,
                campaign_environment_preflight=preflight)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        admission = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]
        self.assertIs(admission["critical_environment_passed"], True)
        self.assertIs(admission["reference_provenance_present"], True)
        eligibility = controller._experiment_cooldown_reference_eligibility(bundle, summary)
        self.assertTrue(eligibility["eligible"], eligibility)

    def test_a11_second_attempt_guard_failure_collects_with_flag(self) -> None:
        awake = _guard(display_power_state="any_awake")
        with self.hazard():
            bundle, summary = self.run_live_guard(
                "hazard-a11-attempt2", [_guard(), _guard(), awake, _guard()],
                registry=AdmissionIdleRegistry([False, False], cpu_busy_sequence=[0.9, 0.1]))
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        admission = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]
        self.assertEqual([row["admitted"] for row in admission["attempts"]], [False, True])
        self.assertIs(admission["critical_environment_passed"], False)
        flags = self.member_flags("env.member_quiet_state_violated")
        self.assertEqual(len(flags), 1)
        self.assertEqual([row["phase"] for row in observed(flags[0])["findings"]], ["before_attempt_2"])

    def test_a11_legacy_second_attempt_guard_failure_still_aborts(self) -> None:
        awake = _guard(display_power_state="any_awake")
        _bundle, summary = self.run_live_guard(
            "legacy-a11-attempt2", [_guard(), _guard(), awake, _guard()],
            registry=AdmissionIdleRegistry([False, False], cpu_busy_sequence=[0.9, 0.1]))
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertIn("display became or remained awake", summary.failure_message)

    def test_s2_01_legacy_stage_preflight_still_decides_the_member(self) -> None:
        policy, _binding, _preflight, snapshot = campaign_policy_fixture(exploratory=False)
        awake_stage = {**snapshot, "display_power_state": "any_awake"}
        bundle, summary = self.run_live_guard(
            "legacy-s201", [_guard(), _guard()], preflight_snapshot=awake_stage)
        admission = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]
        self.assertIs(admission["critical_environment_passed"], False)

    def test_s2_01_cooldown_reference_eligibility_follows_the_members_own_quiet_state(self) -> None:
        unknown = _guard(display_power_state=None)
        awake = _guard(display_power_state="any_awake")
        with self.hazard():
            guard_only = self.run_live_guard("hazard-ref-unknown", [unknown, unknown])
            violated = self.run_live_guard("hazard-ref-awake", [_guard(), awake])
        # An unknown guard state alone (one DISCLOSE flag) does not exclude the
        # member as the next member's cooldown reference.
        eligibility = controller._experiment_cooldown_reference_eligibility(*guard_only)
        self.assertTrue(eligibility["eligible"], eligibility)
        # A measured quiet-state violation does.
        eligibility = controller._experiment_cooldown_reference_eligibility(*violated)
        self.assertFalse(eligibility["eligible"])
        self.assertIn("critical_environment_not_passed", eligibility["reasons"])


class IdleAdmissionEvidenceTests(_LifecycleBase):
    """A18: evidence-only idle-admission conditions."""

    def run_member(self, run_id: str, registry: Any, *, records: Any = "real"):
        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        patches = [patch("joulewise.controller.collect_environment_guard_observation",
                         side_effect=lambda **_kwargs: _guard())]
        if records != "real":
            patches.append(patch.object(controller, "_adapter_idle_admission_records",
                                        return_value=records))
        import contextlib

        with contextlib.ExitStack() as stack:
            for item in patches:
                stack.enter_context(item)
            return controller.run_benchmark(
                make_config(run_id), self.runs_root, DeterministicClock(),
                registry=registry, environment_snapshot=snapshot, campaign_policy=policy,
                campaign_policy_binding=binding, campaign_environment_preflight=preflight)

    def test_a18_missing_cpu_telemetry_admits_and_flags(self) -> None:
        with self.hazard():
            bundle, summary = self.run_member("hazard-a18-missing", AdmissionIdleRegistry([False]),
                                              records=[])
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        admission = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]
        self.assertEqual(admission["decision"], "admitted")
        self.assertEqual(len(admission["attempts"]), 1)
        final = admission["attempts"][-1]
        self.assertIs(final["admitted"], True)
        # Nothing passing is fabricated: the evaluator's own output says failed.
        self.assertIs(final["cpu_admission"]["admitted"], False)
        self.assertIs(admission["reference_provenance_present"], False)
        flags = self.member_flags("member.idle_admission_telemetry_missing")
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["scope"]["run_id"], bundle.name)
        self.assertEqual(observed(flags[0])["conditions"], ["cpu_baseline_telemetry_missing"])
        # Never a cooldown reference.
        eligibility = controller._experiment_cooldown_reference_eligibility(bundle, summary)
        self.assertFalse(eligibility["eligible"])
        self.assertIn("reference_provenance_incomplete", eligibility["reasons"])

    def test_a18_legacy_missing_cpu_telemetry_still_aborts(self) -> None:
        _bundle, summary = self.run_member("legacy-a18-missing", AdmissionIdleRegistry([False]),
                                           records=[])
        self.assertEqual(summary.status, RunStatus.FAILED)

    def test_a18_unknown_gpu_admission_admits_and_flags(self) -> None:
        with self.hazard():
            bundle, summary = self.run_member("hazard-a18-gpu", AdmissionIdleRegistry([None]))
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        final = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]["attempts"][-1]
        self.assertIsNone(final["gpu_admitted"])
        self.assertEqual(final["cpu_admission"]["conditions"], ["gpu_idle_admission_unknown"])
        flags = self.member_flags("member.idle_admission_telemetry_missing")
        self.assertEqual(len(flags), 1)

    def test_a18_legacy_unknown_gpu_admission_still_aborts(self) -> None:
        bundle, summary = self.run_member("legacy-a18-gpu", AdmissionIdleRegistry([None]))
        self.assertEqual(summary.status, RunStatus.FAILED)
        final = json.loads((bundle / "metadata.json").read_bytes())["environment_admission"]["attempts"][-1]
        self.assertIs(final["gpu_admitted"], False)

    def test_a18_keeper_busy_cpu_still_aborts_on_hazard(self) -> None:
        with self.hazard():
            _bundle, summary = self.run_member(
                "hazard-a18-busy", AdmissionIdleRegistry([False, False], cpu_busy_sequence=[0.9, 0.9]))
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(self.member_flags("member.idle_admission_telemetry_missing"), [])

    def test_a18_keeper_threshold_plus_missing_evidence_still_aborts(self) -> None:
        # GPU suspect (a threshold condition) alongside unknown CPU evidence.
        with self.hazard():
            _bundle, summary = self.run_member(
                "hazard-a18-mixed", AdmissionIdleRegistry([True, True]), records=[])
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(self.member_flags("member.idle_admission_telemetry_missing"), [])


class CleanupFailedRuntime:
    def __init__(self, delegate: Any) -> None:
        self._delegate = delegate
        self.name = delegate.name

    def __getattr__(self, name: str) -> Any:
        return getattr(self._delegate, name)

    def cleanup(self, config, context=None) -> AdapterResult:
        return AdapterResult(ok=False, failure_reason=FailureReason.CLEANUP_FAILED,
                             message="worker pid 4242 survived cleanup")


class CleanupFailedRegistry:
    def resolve_runtime(self, config, clock):
        runtime, failure = adapters.resolve_runtime(config, clock)
        return CleanupFailedRuntime(runtime), failure

    def resolve_telemetry(self, config, clock):
        return adapters.resolve_telemetry(config, clock)

    def resolve_transport(self, config):
        return adapters.resolve_transport(config)


class TeardownTests(_LifecycleBase):
    """A17 and PLAN2 s2-02."""

    def run_contaminated(self, run_id: str):
        escaped = {"pid": 999999, "argv": ["injected", "escaped", "sampler"]}
        signals: list[tuple[str, Any, bool]] = []
        real_killpg, real_kill = os.killpg, os.kill

        def record_killpg(pgid, sig):
            signals.append(("killpg", sig, report_exists()))
            return real_killpg(pgid, sig)

        def record_kill(pid, sig):
            signals.append(("kill", sig, report_exists()))
            return real_kill(pid, sig)

        teardowns: list[SamplerTeardown] = []
        real_init = SamplerTeardown.__init__

        def tracking_init(instance, *args, **kwargs):
            real_init(instance, *args, **kwargs)
            teardowns.append(instance)

        def report_exists() -> bool:
            return any(item.report is not None for item in teardowns)

        with patch.object(SamplerTeardown, "_wide_argv_census", return_value=[escaped]), \
                patch.object(SamplerTeardown, "__init__", tracking_init), \
                patch("os.killpg", side_effect=record_killpg), \
                patch("os.kill", side_effect=record_kill):
            bundle, summary = _produce_admission_powermetrics_bundle(
                self.runs_root, run_id, RetryAdmissionPowermetricsRegistry())
        return bundle, summary, signals

    def test_a17_contaminated_census_reduces_normally_and_flags(self) -> None:
        with self.hazard():
            bundle, summary, signals = self.run_contaminated("hazard-a17-sampler")
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertTrue((bundle / "power_trace.csv").exists())
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        teardown = metadata["uncertainty_evidence"]["process_group_teardown"]
        self.assertEqual(teardown["status"], "contaminated")
        flags = self.member_flags("teardown.survivors")
        self.assertEqual(len(flags), 1)
        value = observed(flags[0])
        self.assertEqual(value["kind"], "sampler")
        self.assertEqual(value["status"], "contaminated")
        self.assertEqual(value["escaped_candidates"], 1)
        self.assertEqual(value["pids"], [{"pid": 999999, "argv": ["injected", "escaped", "sampler"]}])
        self.assertEqual(flags[0]["scope"]["run_id"], bundle.name)
        self.assertEqual([row for row in signals if row[2]], [],
                         "no signal is sent after the teardown report exists")
        # One true stop marker.
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        self.assertEqual(sum(event["event_type"] == "sampling_stopped" for event in events), 1)

    def test_a17_legacy_contaminated_census_still_fails(self) -> None:
        _bundle, summary, _signals = self.run_contaminated("legacy-a17-sampler")
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertIn("teardown census reported contamination", summary.failure_message)

    def test_a17_runtime_cleanup_failed_is_recorded_not_fatal(self) -> None:
        with self.hazard():
            bundle, summary = controller.run_benchmark(
                make_config("hazard-a17-runtime"), self.runs_root, FakeClock(start=1_700_000_000.0),
                registry=CleanupFailedRegistry())
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        flags = self.member_flags("teardown.survivors")
        self.assertEqual(len(flags), 1)
        self.assertEqual(observed(flags[0])["kind"], "runtime")
        self.assertEqual(observed(flags[0])["status"], "cleanup_failed")
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        cleanup = [event for event in events
                   if event["event_type"] == "stage_completed" and event["phase"] == "cleanup"]
        self.assertEqual(cleanup[-1]["metadata"]["cleanup_ok"], False)
        self.assertEqual(cleanup[-1]["metadata"]["failure_reason"], "cleanup_failed")

    def test_a17_legacy_runtime_cleanup_failed_still_fails(self) -> None:
        _bundle, summary = controller.run_benchmark(
            make_config("legacy-a17-runtime"), self.runs_root, FakeClock(start=1_700_000_000.0),
            registry=CleanupFailedRegistry())
        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.CLEANUP_FAILED)

    def run_stop_raises(self, run_id: str):
        class StopRaisesTelemetry:
            def __init__(self, inner):
                self._inner = inner
                self.name = inner.name
                self.calls = 0

            def __getattr__(self, name):
                return getattr(self._inner, name)

            def stop_sampling(self, config, context=None):
                self.calls += 1
                if self.calls == 1:
                    self._inner.stop_sampling(config, context)
                    raise RuntimeError("injected stop failure after a completed run")
                return []

        class Registry:
            def resolve_runtime(self, config, clock):
                return adapters.resolve_runtime(config, clock)

            def resolve_telemetry(self, config, clock):
                telemetry, failure = adapters.resolve_telemetry(config, clock)
                return StopRaisesTelemetry(telemetry), failure

            def resolve_transport(self, config):
                return adapters.resolve_transport(config)

        return controller.run_benchmark(
            make_config(run_id), self.runs_root, FakeClock(start=1_700_000_000.0),
            registry=Registry())

    def test_s2_02_stop_failure_keeps_runtime_result_and_true_stop_marker(self) -> None:
        with self.hazard():
            bundle, summary = self.run_stop_raises("hazard-s202")
        self.assertEqual(summary.status, RunStatus.FAILED)
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        stops = [event for event in events if event["event_type"] == "sampling_stopped"]
        self.assertEqual(len(stops), 1)
        self.assertEqual(stops[0]["message"],
                         "measured window stopped; telemetry tail retained outside window")
        self.assertTrue(any(event["event_type"] == "token" for event in events),
                        "the token timeline is kept")
        self.assertTrue(any((bundle / "outputs").iterdir()), "the outputs are kept")
        token_times = [event["timestamp_s"] for event in events if event["event_type"] == "token"]
        self.assertLessEqual(max(token_times), stops[0]["timestamp_s"])

    def test_s2_02_true_stop_marker_is_stamped_before_the_tail(self) -> None:
        stamps: list[tuple[float, float]] = []
        real = controller._Execution._append_sampling_stopped

        def capture(execution, stamp):
            stamps.append((stamp.epoch_s, execution._clock.now()))
            return real(execution, stamp)

        with self.hazard(), patch.object(controller._Execution, "_append_sampling_stopped", capture):
            bundle, _summary = controller.run_benchmark(
                make_config("hazard-s202-tail"), self.runs_root, FakeClock(start=1_700_000_000.0),
                post_window_sampling_dwell_s=3.0)
        self.assertEqual(len(stamps), 1)
        self.assertAlmostEqual(stamps[0][1] - stamps[0][0], 3.0)
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        stops = [event for event in events if event["event_type"] == "sampling_stopped"]
        self.assertEqual([event["timestamp_s"] for event in stops], [stamps[0][0]])

    def test_s2_02_legacy_stop_failure_loses_the_runtime_result(self) -> None:
        bundle, summary = self.run_stop_raises("legacy-s202")
        self.assertEqual(summary.status, RunStatus.FAILED)
        events = [json.loads(line) for line in (bundle / "events.jsonl").read_text().splitlines()]
        self.assertFalse(any(event["event_type"] == "token" for event in events))
        stops = [event for event in events if event["event_type"] == "sampling_stopped"]
        self.assertEqual([event["message"] for event in stops],
                         ["telemetry sampling stopping (failure path)"])

    def test_s2_02_carried_survivor_is_measured_and_recorded_never_refused(self) -> None:
        survivor = subprocess.Popen(["/bin/sleep", "60"])
        self.addCleanup(survivor.wait)
        self.addCleanup(survivor.kill)
        flags_core.emit(self.context, "teardown.survivors", level="member", run_id="earlier-member",
                        observed={"kind": "sampler", "status": "contaminated",
                                  "group_survivors": 0, "escaped_candidates": 1,
                                  "pids": [{"pid": survivor.pid, "argv": ["/bin/sleep", "60"]}]})
        policy, binding, preflight, snapshot = campaign_policy_fixture(exploratory=False)
        with self.hazard(), patch("joulewise.controller.collect_environment_guard_observation",
                                  side_effect=lambda **_kwargs: _guard()):
            bundle, summary = controller.run_benchmark(
                make_config("hazard-s202-carried"), self.runs_root, DeterministicClock(),
                registry=AdmissionIdleRegistry([False]), environment_snapshot=snapshot,
                campaign_policy=policy, campaign_policy_binding=binding,
                campaign_environment_preflight=preflight)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        carried = [flag for flag in self.member_flags("teardown.survivors")
                   if observed(flag)["kind"] == "carried_over"]
        self.assertEqual(len(carried), 1)
        self.assertEqual(carried[0]["scope"]["run_id"], bundle.name)
        self.assertEqual([row["pid"] for row in observed(carried[0])["pids"]], [survivor.pid])


class HeldStopEvidenceTests(unittest.TestCase):
    """s2-02: a retried stop never replaces the first recorded stop evidence."""

    @staticmethod
    def execution(hazard: Any, telemetry: Any) -> Any:
        from joulewise.clock import ClockStamp

        execution = object.__new__(controller._Execution)
        execution._hazard = hazard
        execution._clock = FakeClock(start=1_700_000_000.0)
        execution._controller_log = []
        execution._sampling_stop_claimed = False
        execution._sampling_started_stamp = ClockStamp(1.0, 1.0, 1.0, 0.001, 0.001)
        execution._post_window_sampling_dwell_s = 0.0
        execution._config = execution._context = None
        execution._samples = ["held"]
        execution._uncertainty_evidence = {"clock_anchor": {"identity": "held"}}
        execution._telemetry = telemetry
        return execution

    @staticmethod
    def telemetry(samples: list[Any]) -> Any:
        from joulewise.interfaces import TelemetryStopResult

        class Telemetry:
            name = "mock"

            def stop_sampling_with_evidence(self, *args, **kwargs):
                return TelemetryStopResult(list(samples), {})

        return Telemetry()

    def stop_again(self, hazard: Any, samples: list[Any]) -> Any:
        from joulewise.clock import ClockStamp

        execution = self.execution(hazard, self.telemetry(samples))
        execution._stop_sampling_once(ClockStamp(2.0, 2.0, 2.0, 0.001, 0.001))
        return execution

    def test_hazard_keeps_held_samples_and_anchor_whatever_the_retry_returns(self) -> None:
        hazard = flags_core.HazardFlagContext(
            writer=WRITER, custody_root=None, plan_id=None, attempt=None, scope_resolved=False)
        for retry in ([], ["retry"]):
            execution = self.stop_again(hazard, retry)
            self.assertEqual(execution._samples, ["held"])
            self.assertEqual(execution._uncertainty_evidence, {"clock_anchor": {"identity": "held"}})

    def test_hazard_keeps_held_samples_or_anchor_independently(self) -> None:
        from joulewise.clock import ClockStamp
        from types import SimpleNamespace

        hazard = flags_core.HazardFlagContext(
            writer=WRITER, custody_root=None, plan_id=None, attempt=None, scope_resolved=False)
        anchor_only = self.execution(hazard, self.telemetry(["retry"]))
        anchor_only._samples = []
        anchor_only._stop_sampling_once(ClockStamp(2.0, 2.0, 2.0, 0.001, 0.001))
        self.assertEqual(anchor_only._samples, [])
        self.assertEqual(anchor_only._uncertainty_evidence, {"clock_anchor": {"identity": "held"}})
        samples_only = self.execution(hazard, self.telemetry(["retry"]))
        samples_only._uncertainty_evidence = {}
        samples_only._stop_sampling_once(ClockStamp(2.0, 2.0, 2.0, 0.001, 0.001))
        self.assertEqual(samples_only._samples, ["held"])
        unbounded = self.execution(
            hazard, SimpleNamespace(name="mock", stop_sampling=lambda *_args: ["retry"]))
        unbounded._stop_sampling_once(ClockStamp(2.0, 2.0, 2.0, 0.001, 0.001))
        self.assertEqual(unbounded._samples, ["held"])

    def test_legacy_retry_still_replaces_the_stop_evidence(self) -> None:
        execution = self.stop_again(None, ["retry"])
        self.assertEqual(execution._samples, ["retry"])
        self.assertEqual(execution._uncertainty_evidence, {})


class CarriedSurvivorUnitTests(unittest.TestCase):
    """s2-02 carried survivors: identity and ordering."""

    def test_reused_pid_naming_another_command_is_not_carried(self) -> None:
        from types import SimpleNamespace

        with tempfile.TemporaryDirectory() as tmp:
            hazard = flags_core.HazardFlagContext(
                writer=WRITER, custody_root=Path(tmp), plan_id=None, attempt=None,
                scope_resolved=False)
            flags_core.emit(hazard, "teardown.survivors", level="member", run_id="earlier",
                            observed={"pids": [{"pid": 55555, "argv": ["/bin/sleep", "60"]}]})
            execution = object.__new__(controller._Execution)
            execution._hazard = hazard
            execution._writer = SimpleNamespace(run_id="current")
            with patch.object(controller, "_measure_survivor_processes",
                              return_value={55555: {"command": "/bin/other", "cpu_percent": 6.0}}):
                execution._measure_carried_sampler_survivors()
            self.assertEqual(len(read_flags(Path(tmp))), 1, "a reused pid is not this survivor")

    def test_survivor_probe_runs_before_the_settle(self) -> None:
        order: list[str] = []
        real_settle = controller._Execution._settle_before_idle
        real_probe = controller._Execution._check_carried_sampler_survivors

        def settle(execution):
            order.append("settle")
            return real_settle(execution)

        def probe(execution):
            order.append("probe")
            return real_probe(execution)

        with tempfile.TemporaryDirectory() as tmp:
            context = flags_core.HazardFlagContext(
                writer=WRITER, custody_root=Path(tmp), plan_id=None, attempt=None,
                scope_resolved=False)
            with patch.object(flags_core, "hazard_flag_context", return_value=context), \
                    patch.object(controller._Execution, "_settle_before_idle", settle), \
                    patch.object(controller._Execution, "_check_carried_sampler_survivors", probe):
                controller.run_benchmark(make_config("hazard-probe-order"), Path(tmp) / "runs",
                                         FakeClock(start=1_700_000_000.0))
        self.assertEqual(order[:2], ["probe", "settle"])


class DispatchTests(unittest.TestCase):
    def test_plain_runs_root_is_the_legacy_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(flags_core.hazard_flag_context(Path(tmp), writer=WRITER))
            bundle, summary = controller.run_benchmark(
                make_config("legacy-dispatch"), Path(tmp) / "runs", FakeClock(start=1_700_000_000.0))
            self.assertEqual(summary.status, RunStatus.SUCCEEDED)
            self.assertFalse((Path(tmp) / "runs" / flags_core.FLAGS_DIRNAME).exists())


if __name__ == "__main__":
    unittest.main()
