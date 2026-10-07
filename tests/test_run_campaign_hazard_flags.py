"""HAZARD_PACK flag path through scripts/run_campaign.py (gate-prune core lane RC).

Each test runs a real collection stage in process (``run_campaign.main``) whose
members are dispatched to a small fake CLI subprocess.  The runs root carries a
HAZARD lineage locator (``joulewise.hazard_window_lineage_locator.v1``), which
is all the HAZARD predicate reads; its custody root holds the window plan, so
every flag lands in ``<custody>/flags/core-run_campaign.jsonl`` bound to the
window plan id.  Where a row needs an authenticated launch lineage (A4, A12),
the authentication is the real one from ``tests.test_window_lineage.build_window``.

Every relaxation is checked three ways: the HAZARD scenario collects and flags;
its keeper still refuses; the same scenario on a plain (legacy) runs root still
refuses exactly as before and writes no flag.  Mock telemetry throughout: these
test collection and records, not idle-power physics.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise import measurement_liveness, window_lineage
from joulewise.flags.schema import validate_flag
from joulewise.measurement_liveness import Identity
import scripts.run_campaign as run_campaign

ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
TEST_POLICY = ROOT / "tests" / "fixtures" / "campaign_policy_test.json"
GENERATOR = ROOT / "scripts" / "generate_matrix.py"
START = "Tue Sep 8 01:02:03 2026"
PLAN_ID = "plan-hazard-rc-window"
FLAG_FILE = "core-run_campaign.jsonl"
PREFLIGHT_ENV = "JOULEWISE_CAMPAIGN_PREFLIGHT_JSON"


def _observe(pid: int) -> Identity:
    # This process is LIVE with a fixed start time (so the lock and registry
    # carry a parseable identity); every other pid is observed for real.
    if pid == os.getpid():
        return Identity("LIVE", START)
    return measurement_liveness.observe_identity(pid)


def setUpModule() -> None:
    temporary = tempfile.TemporaryDirectory()
    unittest.addModuleCleanup(temporary.cleanup)
    env = patch.dict(os.environ, {
        "JOULEWISE_CUSTODY_PARENT": str(Path(temporary.name) / "custody-parent"),
        "JOULEWISE_ADDITIONAL_CUSTODY_PARENTS": "[]",
    })
    env.start()
    unittest.addModuleCleanup(env.stop)
    identity = patch.object(run_campaign, "observe_identity", side_effect=_observe)
    identity.start()
    unittest.addModuleCleanup(identity.stop)


FAKE_CLI = textwrap.dedent(
    """
    import json, os, sys
    from pathlib import Path

    ROOT = Path({root!r})
    sys.path.insert(0, str(ROOT))
    from joulewise import reduce as reduce_module
    from joulewise.bundle import RunBundleWriter, sanitize_id_component
    from joulewise.clock import FakeClock
    from joulewise.interfaces import PowerSample, RuntimeEvent
    from joulewise.provenance import output_policy, prompt_provenance
    from joulewise.schemas import BenchmarkConfig

    config_path = Path(sys.argv[2])
    runs_dir = Path(sys.argv[sys.argv.index("--runs-dir") + 1])
    data = json.loads(config_path.read_text())
    run_id = sanitize_id_component(data["run_id"])
    with (runs_dir.parent / (runs_dir.name + ".order.log")).open("a") as handle:
        handle.write(run_id + "\\n")
    (runs_dir.parent / (runs_dir.name + "." + run_id + ".preflight.json")).write_text(
        os.environ.get({preflight_env!r}, "null"))
    if "nometa" in run_id:
        (runs_dir / run_id).mkdir(parents=True)
        raise SystemExit(9)
    if "badutf8" in run_id:
        (runs_dir / run_id).mkdir(parents=True)
        (runs_dir / run_id / "metadata.json").write_bytes(bytes([0xFF, 0xFE, 0x7B]))
        raise SystemExit(9)
    if "foreignlineage" in run_id:
        (runs_dir / run_id).mkdir(parents=True)
        (runs_dir / run_id / "metadata.json").write_text(json.dumps({{"extra": {{
            "launch_lineage": {{"schema_version": "foreign"}},
            "launch_lineage_locator_sha256": "0" * 64}}}}))
        raise SystemExit(0)
    if "nobundle" in run_id:
        raise SystemExit(0)

    config = BenchmarkConfig.from_mapping(data)
    backend = config.hardware_target.telemetry_backend.value
    writer = RunBundleWriter.create(runs_dir, config, FakeClock(start=3.0))

    def event(t, kind, phase, metadata=None):
        writer.append_event(RuntimeEvent(timestamp_s=t, event_type=kind, phase=phase,
                                         message=kind + " " + phase, metadata=metadata or {{}}))

    event(0.0, "stage_started", "measured_run")
    event(0.0, "sampling_started", "measured_run")
    event(0.0, "phase_start", "tokenize")
    event(0.05, "phase_end", "tokenize", {{"prompt_tokens": 3}})
    event(0.05, "phase_start", "prefill", {{"prompt_tokens": 3}})
    event(0.5, "phase_end", "prefill")
    event(0.5, "phase_start", "decode")
    event(0.6, "token", "decode")
    event(0.7, "token", "decode")
    event(0.8, "phase_end", "decode")
    event(1.0, "sampling_stopped", "measured_run")
    event(1.0, "stage_completed", "measured_run")
    writer.write_power_trace([PowerSample(timestamp_s=t / 4, power_w=7.5, source=backend, rail="mock")
                              for t in range(5)])
    writer.write_metadata({{
        "device": {{"telemetry": backend, "rail_manifest": ["mock"]}},
        "adapters": {{"telemetry": {{"name": backend}}}},
        "clock_anchor_bound_s": 0.0,
        "idle_drift_bound_w": 0.0,
        "idle_baseline": {{"power_w_mean": 5.0, "power_w_stddev": 0.0, "duration_s": 1.0,
                          "sample_count": 2, "telemetry_backend": backend,
                          "idle_window_suspect": False}},
        "workload_observed": {{"token_count": 5, "output_token_count": 2}},
        "workload_provenance": {{
            "prompt": prompt_provenance([1, 2, 3], text="test"),
            "generator": {{"name": "fake_cli", "version": "test"}},
            "tokenizer": {{"backend": "mock", "identifier": "fake", "revision": "test",
                          "class": "FakeTokenizer", "vocab_size": None}},
            "model": {{"source": config.model.source, "revision": config.model.revision}},
            "output_policy": output_policy("fixed_budget_exact", requested_tokens=2,
                                           emitted_tokens=2,
                                           stop_condition="requested_tokens_emitted"),
        }},
    }})
    writer.write_summary(reduce_module.reduce_bundle(writer.path))
    writer.finalize()
    """
).lstrip()


class _StubTelemetry:
    """Idle sub-windows on a FakeClock: each capture sleeps its window and
    returns the next power from ``powers`` (the last repeats)."""

    def __init__(self, clock, powers, thermal: str | None = "nominal") -> None:
        self._clock = clock
        self._powers = list(powers)
        self._thermal = thermal
        self.captures = 0

    def measure_idle(self, config, context=None):
        from joulewise.schemas import IdleBaseline, TelemetryBackend

        seconds = config.sampling.idle_seconds
        self._clock.sleep(seconds)
        power = self._powers[min(self.captures, len(self._powers) - 1)]
        self.captures += 1
        return IdleBaseline(power_w_mean=power, power_w_stddev=0.0, duration_s=seconds,
                            sample_count=5, telemetry_backend=TelemetryBackend.POWERMETRICS,
                            idle_window_suspect=False)

    def thermal_state(self, config):
        return SimpleNamespace(thermal_pressure=self._thermal)


class _Stage(unittest.TestCase):
    """A fresh runs root (HAZARD or plain) plus a config directory per test."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.cli = self.base / "fake_cli.py"
        self.cli.write_text(FAKE_CLI.format(root=str(ROOT), preflight_env=PREFLIGHT_ENV))

    # fixtures -----------------------------------------------------------------

    def hazard_root(self, name: str = "runs_claim") -> Path:
        runs = self.base / name
        runs.mkdir()
        self.custody = self.base / "custody"
        self.custody.mkdir(exist_ok=True)
        (runs / window_lineage.LOCATOR_BASENAME).write_text(json.dumps({
            "schema_version": window_lineage.HAZARD_LOCATOR_SCHEMA,
            "launch_lineage": {"window_context": {"custody_root": str(self.custody)}},
        }) + "\n")
        (self.custody / "night_plan.json").write_text(json.dumps({
            "plan_id": PLAN_ID, "hazard_window": {"attempt": 1}}) + "\n")
        return runs

    def plain_root(self, name: str = "runs_plain") -> Path:
        runs = self.base / name
        runs.mkdir()
        self.custody = self.base / "custody"
        self.custody.mkdir(exist_ok=True)
        return runs

    def configs(self, *run_ids: str, name: str = "configs") -> Path:
        directory = self.base / name
        directory.mkdir()
        for index, run_id in enumerate(run_ids, start=1):
            payload = json.loads(BASE_CONFIG.read_text())
            payload["run_id"] = run_id
            payload["workload_profile"]["repetitions"] = 1
            (directory / f"{index:02d}-{run_id}.json").write_text(json.dumps(payload) + "\n")
        return directory

    def idle_policy(self, **cooldown) -> Path:
        payload = json.loads(TEST_POLICY.read_text())
        payload["idle_admission"]["enabled"] = True
        payload["cooldown"].update(cooldown)
        path = self.base / "policy-idle.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return path

    # running ------------------------------------------------------------------

    def run_stage(self, configs: Path, runs: Path, *extra: str,
                  policy: Path = TEST_POLICY) -> SimpleNamespace:
        argv = [str(configs), "--runs-dir", str(runs), "--campaign-policy", str(policy),
                "--cli-cmd", shlex.join([sys.executable, str(self.cli)]),
                "--max-failures", "10", *extra]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = run_campaign.main(argv)
        return SimpleNamespace(code=code, out=out.getvalue(), err=err.getvalue())

    def invoked(self, runs: Path) -> list[str]:
        path = runs.parent / (runs.name + ".order.log")
        return path.read_text().split() if path.exists() else []

    def flags(self) -> list[dict]:
        path = self.custody / "flags" / FLAG_FILE
        if not path.exists():
            return []
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        for row in rows:
            self.assertEqual(validate_flag(row), [], row)
            self.assertEqual(row["blinding"], "STRUCTURE")
            self.assertEqual(row["source"]["collector"], "core.core-run_campaign")
        return rows

    def kinds(self) -> list[str]:
        return [row["observed"].get("kind") for row in self.flags()
                if row["code"] == "campaign.runner_record_flagged"]

    def log_rows(self, runs: Path) -> list[dict]:
        path = runs / "campaign_log.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

    def verdicts(self, runs: Path) -> list[dict]:
        return [row for row in self.log_rows(runs) if row.get("record_type") == "campaign_verdict"]

    def provenance_members(self, runs: Path) -> list[dict]:
        manifests = sorted((runs / "campaign_manifests").glob("*.json"))
        return [member for path in manifests for member in json.loads(path.read_text())["members"]]


class CooldownUnknownTests(_Stage):
    """A2 and A19: an unknown cooldown result never blocks a HAZARD member."""

    MEMBERS = ("hz-cool-a", "hz-cool-b", "hz-cool-c")

    def _ineligible(self):
        return patch.object(run_campaign, "cooldown_reference_eligibility",
                            return_value={"eligible": False, "reasons": ["fixture_ineligible"]})

    def test_a2_unknown_reference_flags_and_invokes_every_member(self) -> None:
        # Mock telemetry: the self-referenced fallback cannot measure either,
        # so the cooldown stays unknown, is flagged, and never blocks.
        runs = self.hazard_root()
        with self._ineligible():
            result = self.run_stage(self.configs(*self.MEMBERS), runs, policy=self.idle_policy())
        self.assertEqual(self.invoked(runs), list(self.MEMBERS), result.err)
        executions = [member["execution"] for member in self.provenance_members(runs)]
        self.assertNotIn("blocked_before_invoke", executions)
        flags = [row for row in self.flags() if row["code"] == "cooldown.result_unknown"]
        self.assertEqual(sorted(row["scope"]["run_id"] for row in flags), ["hz-cool-b", "hz-cool-c"])
        for row in flags:
            self.assertEqual(row["scope"]["level"], "member")
            self.assertEqual(row["scope"]["plan_id"], PLAN_ID)
            self.assertEqual(row["observed"]["reason_class"], "unmeasured")
            self.assertEqual(row["observed"]["reason"],
                             "mock telemetry has no thermal recovery evidence")
            self.assertEqual(row["observed"]["fallback"],
                             {"from": "reference_unavailable",
                              "reference_selection": "hazard_self_referenced"})

    def test_a2_s2_05_fallback_cooldown_is_measured_and_verifies(self) -> None:
        # s2-05: with a working instrument the fallback cooldown is MEASURED
        # (self-referenced here: no eligible baseline, no anchor), carries a
        # hash-addressed raw trace, and verifies in the harvest's own join, so
        # member.cooldown_evidence_unverified does not fire.
        from joulewise.analysis_engine.inputs import campaign_cooldown_evidence
        from joulewise.clock import FakeClock

        runs = self.hazard_root()
        clock = FakeClock(start=100.0)
        telemetry = _StubTelemetry(clock, [5.0])
        # create=True: on a base without the helper the stage still runs, and
        # the test fails on the refusal itself (members 2 and 3 blocked).
        with self._ineligible(), patch.object(
                run_campaign, "_hazard_cooldown_telemetry", return_value=(telemetry, clock, None),
                create=True):
            result = self.run_stage(self.configs(*self.MEMBERS), runs,
                                    policy=self.idle_policy(cap_s=300.0))
        self.assertEqual(result.code, 0, result.err)
        self.assertEqual(self.invoked(runs), list(self.MEMBERS), result.err)
        self.assertEqual([row for row in self.flags() if row["code"] == "cooldown.result_unknown"], [])
        fallback = [row for row in self.flags()
                    if row["observed"].get("kind") == "cooldown_fallback_reference"]
        self.assertEqual(sorted(row["scope"]["run_id"] for row in fallback), ["hz-cool-b", "hz-cool-c"])
        for row in fallback:
            self.assertEqual(row["observed"]["reference_selection"], "hazard_self_referenced")
            self.assertEqual(row["observed"]["result"], "recovered")
        evidence = campaign_cooldown_evidence(runs, None)
        for member in self.MEMBERS[1:]:
            self.assertEqual(evidence[member]["result"], "recovered")
            self.assertIs(evidence[member]["verified"], True, evidence[member])
        cooldowns = [member["preceding_campaign_cooldown"]
                     for member in self.provenance_members(runs)
                     if (member.get("preceding_campaign_cooldown") or {}).get("result")
                     == "recovered"]
        self.assertEqual(len(cooldowns), 2)
        for note in cooldowns:
            self.assertEqual(note["reference_selection"], "hazard_self_referenced")
            self.assertEqual(note["fallback_from"]["result"], "unknown")
            # The thresholds are the stage policy file's, not a second copy.
            policy = json.loads(self.idle_policy(cap_s=300.0).read_text())["cooldown"]
            for key in ("sustained_window_s", "tolerance_fraction", "cap_s", "subwindow_s"):
                self.assertEqual(note["thresholds"][key], policy[key])

    def test_a2_legacy_root_still_blocks_and_writes_no_flag(self) -> None:
        runs = self.plain_root()
        with self._ineligible():
            result = self.run_stage(self.configs(*self.MEMBERS), runs, policy=self.idle_policy())
        self.assertEqual(result.code, 1)
        self.assertEqual(self.invoked(runs), ["hz-cool-a"])
        self.assertIn("cooldown v2 failed closed before invoke", result.err)
        executions = [member["execution"] for member in self.provenance_members(runs)]
        self.assertEqual(executions.count("blocked_before_invoke"), 2)
        self.assertFalse((self.custody / "flags").exists())

    def test_a19_unmeasured_cooldown_flags_and_invokes(self) -> None:
        runs = self.hazard_root()
        note = {"result": "unknown", "reason": "telemetry adapter unavailable",
                "failure_reason": "ADAPTER_UNAVAILABLE"}
        with patch.object(run_campaign, "campaign_cooldown_before_member", return_value=note):
            result = self.run_stage(self.configs(*self.MEMBERS[:2]), runs, policy=self.idle_policy())
        self.assertEqual(self.invoked(runs), list(self.MEMBERS[:2]), result.err)
        flags = [row for row in self.flags() if row["code"] == "cooldown.result_unknown"]
        self.assertEqual([row["scope"]["run_id"] for row in flags], ["hz-cool-b"])
        self.assertEqual(flags[0]["observed"]["reason_class"], "unmeasured")
        self.assertEqual(flags[0]["observed"]["failure_reason"], "ADAPTER_UNAVAILABLE")

    def test_a2_hazard_anchor_is_not_filtered_by_manifest_id(self) -> None:
        # A GAMMA stage (analysis manifest id X) in a HAZARD root whose catalog
        # holds an eligible anchor recorded with analysis_manifest_id None.
        anchor = {"source_kind": "neg8_reference_start", "baseline": {"power_w_mean": 5.0}}
        record = SimpleNamespace(value={"analysis_manifest_id": None, "cooldown_anchor": anchor},
                                 path=Path("anchor.json"))
        real = run_campaign.prior_campaign_cooldown_anchor
        found: list = []

        def anchor_lookup(runs_dir, manifest_id, policy_sha256, log_path=None):
            with patch.object(run_campaign, "load_authenticated_campaign_catalog",
                              return_value=[record]), \
                    patch.object(run_campaign, "_cooldown_anchor_eligibility",
                                 return_value={"eligible": True}):
                value = real(runs_dir, manifest_id, policy_sha256, log_path)
            found.append((manifest_id, value))
            return value

        configs = self.base / "gamma"
        configs.mkdir()
        base = self.base / "gamma-base.json"
        base.write_text(BASE_CONFIG.read_text())
        generated = subprocess.run(
            [sys.executable, str(GENERATOR), "--base", str(base), "--model-tag", "mock",
             "--out-dir", str(configs)], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(generated.returncode, 0, generated.stderr)
        manifest_id = json.loads((configs / "analysis_manifest.json").read_text())["manifest_id"]
        for runs, expected in ((self.hazard_root(), anchor), (self.plain_root(), None)):
            found.clear()
            with self.subTest(hazard=expected is not None), \
                    patch.object(run_campaign, "prior_campaign_cooldown_anchor",
                                 side_effect=anchor_lookup):
                self.run_stage(configs, runs, "--dry-run")
                self.assertEqual(len(found), 1)
                self.assertEqual(found[0][0], None if expected is not None else manifest_id)
                self.assertEqual(found[0][1], expected)


REFERENCE_UNAVAILABLE = ("preceding baseline is ineligible and no eligible frozen clean "
                         "cooldown anchor is available")


def _baseline(power: float) -> dict:
    return {"power_w_mean": power, "power_w_stddev": 0.0, "duration_s": 30.0, "sample_count": 30,
            "telemetry_backend": "powermetrics", "idle_window_suspect": False}


def _evaluation(bundle_id: str, *, power: float = 4.0, decision: str = "admitted",
                attempt_admitted: bool = True, guard: dict | None = None,
                finding_status: str = "pass"):
    admission = {
        "decision": decision,
        "critical_environment_passed": True,
        "reference_provenance_present": True,
        "attempts": [{"attempt": 1, "admitted": attempt_admitted}],
        "per_run_environment_evaluation": {
            "eligible": finding_status == "pass", "snapshot_sha256": "c" * 64,
            "findings": [{"code": "display_not_all_asleep", "field": "display_power_state",
                          "status": finding_status}]},
        "guard_observations": [guard or {"phase": "before_attempt_1",
                                         "display_power_state": "all_asleep",
                                         "screensaver_engaged": False}],
    }
    return run_campaign.MemberEvaluation(
        bundle_id=bundle_id, bundle_path=Path("/nonexistent") / bundle_id, config_name="c.json",
        status="ok", strict_valid=True, summary={"idle_baseline": _baseline(power)},
        metadata={"environment_admission": admission, "campaign_policy": {"sha256": "d" * 64}})


class ReferenceEligibilityTests(_Stage):
    """s2-01: a cooldown reference is judged by the member's own quiet-state readings."""

    def test_flagged_decision_with_a_quiet_admitted_attempt_is_eligible_on_hazard(self) -> None:
        context = run_campaign._hazard_flag_context(self.hazard_root())
        evaluation = _evaluation("ref-flagged", decision="flagged")
        self.assertTrue(run_campaign.cooldown_reference_eligibility(
            evaluation, hazard=context)["eligible"])
        legacy = run_campaign.cooldown_reference_eligibility(evaluation)
        self.assertFalse(legacy["eligible"])
        self.assertEqual(legacy["reasons"], ["idle_admission_not_passed"])

    def test_keepers_flagged_decisions_that_are_not_quiet_stay_ineligible(self) -> None:
        context = run_campaign._hazard_flag_context(self.hazard_root())
        awake = {"phase": "after_attempt_1", "display_power_state": "any_awake",
                 "screensaver_engaged": False}
        cases = {
            "own_attempt_failed": _evaluation("r1", decision="flagged", attempt_admitted=False),
            "display_awake": _evaluation("r2", decision="flagged", guard=awake),
            "own_finding_failed": _evaluation("r3", decision="flagged", finding_status="fail"),
        }
        for name, evaluation in cases.items():
            with self.subTest(name):
                result = run_campaign.cooldown_reference_eligibility(evaluation, hazard=context)
                self.assertFalse(result["eligible"])
                self.assertIn("idle_admission_not_passed", result["reasons"])

    def test_admitted_member_that_broke_the_quiet_state_is_ineligible_on_hazard(self) -> None:
        # A HAZARD member is not aborted by its guard any more (lane CTL A11),
        # so a definitive violation must keep its baseline from being a reference.
        context = run_campaign._hazard_flag_context(self.hazard_root())
        evaluation = _evaluation("ref-awake", guard={"phase": "after_attempt_1",
                                                     "display_power_state": "any_awake",
                                                     "screensaver_engaged": False})
        result = run_campaign.cooldown_reference_eligibility(evaluation, hazard=context)
        self.assertFalse(result["eligible"])
        self.assertEqual(result["reasons"], ["quiet_state_violated"])
        self.assertTrue(run_campaign.cooldown_reference_eligibility(evaluation)["eligible"])
        unknown = _evaluation("ref-unknown", guard={"phase": "after_attempt_1",
                                                    "display_power_state": None,
                                                    "screensaver_engaged": None})
        self.assertTrue(run_campaign.cooldown_reference_eligibility(
            unknown, hazard=context)["eligible"])


class MeasuredCooldownTests(_Stage):
    """s2-05: a reference-unavailable cooldown becomes a measured one, from the policy file."""

    def setUp(self) -> None:
        super().setUp()
        self.runs = self.hazard_root()
        self.hazard = run_campaign._hazard_flag_context(self.runs)
        self.provenance = self.runs / "campaign_manifests" / "campaign-test.json"
        self.config = self.configs("hz-next") / "01-hz-next.json"
        self.info = run_campaign.ConfigInfo(path=self.config, run_id="hz-next",
                                            raw_run_id="hz-next", repetitions=1)

    def binding(self, **cooldown):
        payload = json.loads(TEST_POLICY.read_text())
        payload["idle_admission"]["enabled"] = True
        payload["cooldown"].update({"subwindow_s": 5.0, "sustained_window_s": 5.0,
                                    "coverage_fraction": 0.8, "tolerance_fraction": 0.1,
                                    "cap_s": 300.0, "require_thermal_nominal": True,
                                    **cooldown})
        path = self.base / f"policy-{len(list(self.base.glob('policy-*')))}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return run_campaign.load_campaign_policy(str(path))

    def measure(self, telemetry, clock, binding, *, note=None, evaluations=(), hazard="ctx"):
        from joulewise.cooldown import cooldown_disposition_from_raw

        unknown = note or {"result": "unknown", "reason": REFERENCE_UNAVAILABLE,
                           "session_id": "campaign-test", "after_bundle_id": "hz-prev",
                           "following_run_id": "hz-next", "recorded_at": "2026-10-06T00:00:00Z"}
        with patch.object(run_campaign, "_hazard_cooldown_telemetry",
                          return_value=(telemetry, clock, None)):
            result = run_campaign._hazard_measured_cooldown(
                self.hazard if hazard == "ctx" else hazard, dict(unknown),
                following_info=self.info, runs_dir=self.runs,
                log_path=self.runs / "campaign_log.jsonl", session_evaluations=list(evaluations),
                provenance_path=self.provenance, session_id="campaign-test",
                policy_binding=binding)
        if result.get("raw_artifact"):
            raw = self.provenance.parent / result["raw_artifact"]["path"]
            rows = [json.loads(line) for line in raw.read_text().splitlines()]
            self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),
                             result["raw_artifact"]["sha256"])
            self.assertEqual(cooldown_disposition_from_raw(rows), result["result"])
        return result

    def test_self_referenced_waits_out_a_decaying_tail(self) -> None:
        from joulewise.clock import FakeClock

        clock = FakeClock()
        # Six 5 s captures still hot (one 30 s window), then idle at 5.0 W.
        telemetry = _StubTelemetry(clock, [9.0] * 6 + [5.0])
        note = self.measure(telemetry, clock, self.binding())
        self.assertEqual(note["result"], "recovered")
        self.assertEqual(note["reference_selection"], "hazard_self_referenced")
        # Release needs two adjacent steady 30 s windows after the tail.
        self.assertEqual(telemetry.captures, 18)
        self.assertEqual(note["waited_s"], 90.0)
        self.assertEqual(note["reference_power_w"], 5.0)
        self.assertEqual(note["self_reference"]["window_s"], 30.0)
        self.assertEqual(note["fallback_from"], {"result": "unknown", "reason": REFERENCE_UNAVAILABLE})
        kinds = [row["observed"] for row in self.flags()]
        self.assertEqual(kinds, [{"kind": "cooldown_fallback_reference",
                                  "reference_selection": "hazard_self_referenced",
                                  "result": "recovered", "fallback_from": "reference_unavailable"}])

    def test_keepers_falling_rising_or_hot_power_is_never_released(self) -> None:
        # Sol review F1: a still-falling tail and a rising level are not steady,
        # also under the council's tolerance 1.0; a hot machine is not cool.
        from joulewise.clock import FakeClock

        for name, powers, thermal, cooldown in (
            ("still_falling", [10.0 * 0.95 ** k for k in range(80)], "nominal", {}),
            ("rising", [5.0 * 1.05 ** k for k in range(80)], "nominal", {}),
            ("council_falling", [10.0 * 0.8 ** k for k in range(80)], "nominal",
             {"sustained_window_s": 5.0, "tolerance_fraction": 1.0}),
            ("council_rising", [5.0 * 1.2 ** k for k in range(80)], "nominal",
             {"sustained_window_s": 5.0, "tolerance_fraction": 1.0}),
            ("thermal_not_nominal", [5.0], "serious", {}),
        ):
            with self.subTest(name):
                self.provenance = self.runs / "campaign_manifests" / f"campaign-{name}.json"
                clock = FakeClock()
                note = self.measure(_StubTelemetry(clock, powers, thermal), clock,
                                    self.binding(**cooldown))
                self.assertEqual(note["result"], "cap_hit")
                self.assertGreaterEqual(note["waited_s"], 300.0)

    def test_thresholds_come_from_the_policy_file(self) -> None:
        # The council's block-5 values (sustained 5 s, tolerance 1.0) are read
        # and recorded; the self-referenced test never runs looser than the
        # cooldown-v2 defaults (30 s windows, 10 %), since it has no idle anchor.
        from joulewise.clock import FakeClock

        clock = FakeClock()
        telemetry = _StubTelemetry(clock, [5.0])
        note = self.measure(telemetry, clock, self.binding(sustained_window_s=5.0,
                                                           tolerance_fraction=1.0, cap_s=240.0))
        self.assertEqual(note["result"], "recovered")
        self.assertEqual(telemetry.captures, 12)
        self.assertEqual(note["thresholds"]["tolerance_fraction"], 1.0)
        self.assertEqual(note["thresholds"]["sustained_window_s"], 5.0)
        self.assertEqual(note["thresholds"]["cap_s"], 240.0)
        self.assertEqual(note["self_reference"]["window_s"], 30.0)
        self.assertEqual(note["self_reference"]["stability_fraction"], 0.1)
        # A policy stricter than the floor is used as written.
        self.provenance = self.runs / "campaign_manifests" / "campaign-strict.json"
        clock = FakeClock()
        strict = self.measure(_StubTelemetry(clock, [5.0]), clock,
                              self.binding(sustained_window_s=60.0, tolerance_fraction=0.05))
        self.assertEqual(strict["self_reference"], {
            "window_s": 60.0, "stability_fraction": 0.05,
            "rule": "max(policy.sustained_window_s, 30 s); min(policy.tolerance_fraction, 0.10); "
                    "two-sided"})

    def test_last_eligible_session_baseline_is_the_first_fallback(self) -> None:
        from joulewise.clock import FakeClock

        clock = FakeClock()
        evaluations = [_evaluation("hz-early", power=4.0),
                       _evaluation("hz-prev", power=9.0, decision="abort")]
        note = self.measure(_StubTelemetry(clock, [4.2]), clock, self.binding(),
                            evaluations=evaluations)
        self.assertEqual(note["result"], "recovered")
        self.assertEqual(note["reference_selection"], "hazard_last_eligible_baseline")
        self.assertEqual(note["fallback_reference_source"], {"bundle_id": "hz-early"})
        self.assertEqual(note["reference_power_w"], 4.0)

    def test_window_opening_anchor_from_another_runs_root_is_the_second_fallback(self) -> None:
        from joulewise.clock import FakeClock

        bound = self.base / "runs_bound"
        bound.mkdir()
        plan = json.loads((self.custody / "night_plan.json").read_text())
        plan["hazard_window"]["runs_roots"] = {"claim": str(self.runs), "bound": str(bound)}
        (self.custody / "night_plan.json").write_text(json.dumps(plan) + "\n")
        anchor = {"source_kind": "neg8_reference_start", "bundle_id": "neg8-start-1",
                  "baseline": _baseline(3.5)}
        seen: list = []

        def lookup(root, manifest_id, policy_sha256, log_path=None):
            seen.append((Path(root).name, manifest_id))
            return anchor if Path(root) == bound.resolve() else None

        clock = FakeClock()
        with patch.object(run_campaign, "prior_campaign_cooldown_anchor", side_effect=lookup):
            note = self.measure(_StubTelemetry(clock, [3.6]), clock, self.binding())
        self.assertEqual(seen, [("runs_claim", None), ("runs_bound", None)])
        self.assertEqual(note["result"], "recovered")
        self.assertEqual(note["reference_selection"], "hazard_window_opening_anchor")
        self.assertEqual(note["reference_power_w"], 3.5)

    def test_unmeasured_and_legacy_notes_pass_through_unchanged(self) -> None:
        from joulewise.clock import FakeClock

        clock = FakeClock()
        telemetry = _StubTelemetry(clock, [5.0])
        unmeasured = {"result": "unknown", "reason": "telemetry adapter unavailable"}
        self.assertEqual(self.measure(telemetry, clock, self.binding(), note=unmeasured), unmeasured)
        legacy = {"result": "unknown", "reason": REFERENCE_UNAVAILABLE}
        self.assertEqual(self.measure(telemetry, clock, self.binding(), note=legacy, hazard=None),
                         legacy)
        self.assertEqual(telemetry.captures, 0)
        self.assertEqual(self.flags(), [])


class ChildMetadataAbsentTests(_Stage):
    """A4 and A12, under the real HAZARD launch authentication."""

    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_window_lineage import build_window

        temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporary.cleanup)
        cls.window = build_window(Path(temporary.name))
        cls.authentication = run_campaign.authenticate_campaign_writer_preflight(
            [cls.window.member_path], cls.window.claim)

    def _authenticated(self, authentication=None):
        return patch.object(run_campaign, "authenticate_campaign_writer_preflight",
                            return_value=authentication or self.authentication)

    def test_a4_member_without_metadata_fails_alone_and_is_flagged(self) -> None:
        runs = self.hazard_root()
        with self._authenticated():
            result = self.run_stage(self.configs("hz-nometa-1", "hz-nobundle-2"), runs)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(self.invoked(runs), ["hz-nometa-1", "hz-nobundle-2"])
        flags = [row for row in self.flags() if row["observed"].get("kind") == "child_metadata_absent"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["scope"]["level"], "member")
        self.assertEqual(flags[0]["scope"]["run_id"], "hz-nometa-1")
        self.assertEqual(flags[0]["observed"]["returncode"], 9)
        statuses = {row.get("run_id"): row.get("status") for row in self.log_rows(runs)}
        self.assertEqual(statuses["hz-nometa-1"], "failed")

    def test_a4_undecodable_metadata_fails_alone_and_is_flagged(self) -> None:
        # Bytes a crashed child left half-written (not UTF-8) are the same
        # absent-metadata fact: that member fails, the next one still runs.
        runs = self.hazard_root()
        with self._authenticated():
            result = self.run_stage(self.configs("hz-badutf8-1", "hz-nobundle-2"), runs)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(self.invoked(runs), ["hz-badutf8-1", "hz-nobundle-2"])
        self.assertEqual([row["scope"]["run_id"] for row in self.flags()
                          if row["observed"].get("kind") == "child_metadata_absent"],
                         ["hz-badutf8-1"])
        statuses = {row.get("run_id"): row.get("status") for row in self.log_rows(runs)}
        self.assertEqual(statuses["hz-badutf8-1"], "failed")

    def test_a4_keeper_foreign_child_lineage_still_ends_the_stage(self) -> None:
        runs = self.hazard_root()
        with self._authenticated():
            result = self.run_stage(self.configs("hz-foreignlineage-1", "hz-nobundle-2"), runs)
        self.assertEqual(result.code, 2)
        self.assertIn("launch_lineage_conflict", result.err)
        self.assertEqual(self.invoked(runs), ["hz-foreignlineage-1"])

    def test_a4_legacy_root_still_ends_the_stage_on_absent_metadata(self) -> None:
        runs = self.plain_root()
        with self._authenticated():
            result = self.run_stage(self.configs("hz-nometa-1", "hz-nobundle-2"), runs)
        self.assertEqual(result.code, 2)
        self.assertIn("child bundle lacks readable launch metadata", result.err)
        self.assertEqual(self.invoked(runs), ["hz-nometa-1"])
        self.assertEqual(self.flags(), [])

    def _broken_chain(self) -> dict:
        authentication = copy.deepcopy(self.authentication)
        authentication["authentication"]["consumption_path"] = str(self.base / "consumption-gone.json")
        return authentication

    def test_a12_hazard_stage_does_not_reread_the_block_limit_chain(self) -> None:
        runs = self.hazard_root()
        with self._authenticated(self._broken_chain()):
            result = self.run_stage(self.configs("hz-nobundle-1"), runs)
        self.assertNotIn("launch_binding_mismatch", result.err)
        self.assertEqual(self.invoked(runs), ["hz-nobundle-1"])

    def test_a12_block_limit_returns_none_and_keeps_the_max_blocks_refusal(self) -> None:
        context = run_campaign._hazard_flag_context(self.hazard_root())
        self.assertIsNotNone(context)
        self.assertIsNone(run_campaign.campaign_block_limit(
            None, self._broken_chain(), [], [], hazard=context))
        with self.assertRaises(run_campaign.LaunchLineageError):  # legacy reader unchanged
            run_campaign.campaign_block_limit(None, self._broken_chain(), [], [])
        with self.assertRaisesRegex(ValueError, "requires G2B_SHAKEDOWN authorization"):
            run_campaign.campaign_block_limit(2, self.authentication, [], [], hazard=context)

    def test_a12_legacy_root_still_refuses_the_broken_chain(self) -> None:
        runs = self.plain_root()
        with self._authenticated(self._broken_chain()):
            result = self.run_stage(self.configs("hz-nobundle-1"), runs)
        self.assertEqual(result.code, 2)
        self.assertIn("launch_binding_mismatch", result.err)
        self.assertEqual(self.invoked(runs), [])


class StaleLockTests(_Stage):
    """A9 and V3: a stale campaign.lock is reclaimed and flagged; a live one refuses."""

    def _reaped_pid(self) -> int:
        child = subprocess.Popen([sys.executable, "-c", "pass"])
        child.wait()
        return child.pid

    def _lock(self, runs: Path, pid: int, start: str | None) -> str:
        text = (f"pid={pid} nonce={'ab' * 32} created_at=2026-10-05T00:00:00Z "
                f"start_time={json.dumps(start)}\n")
        (runs / "campaign.lock").write_text(text)
        return text

    def test_a9_lock_of_a_reaped_process_is_cleared_and_flagged(self) -> None:
        runs = self.hazard_root()
        stale = self._lock(runs, self._reaped_pid(), "Mon Oct 5 00:00:00 2026")
        result = self.run_stage(self.configs("hz-lock-1"), runs)
        self.assertEqual(result.code, 0, result.err)
        self.assertEqual(self.invoked(runs), ["hz-lock-1"])
        self.assertFalse((runs / "campaign.lock").exists())  # released normally
        flags = [row for row in self.flags() if row["observed"].get("kind") == "stale_lock_cleared"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["observed"]["lock"], stale.strip())
        self.assertEqual(flags[0]["observed"]["identity_state"], "DEAD")
        self.assertEqual(flags[0]["scope"]["level"], "window")

    def test_a9_pid_reuse_is_stale(self) -> None:
        runs = self.hazard_root()
        self._lock(runs, os.getpid(), "Sun Jan 4 00:00:00 2026")
        result = self.run_stage(self.configs("hz-lock-1"), runs)
        self.assertEqual(result.code, 0, result.err)
        self.assertEqual(self.kinds(), ["stale_lock_cleared"])

    def test_a9_keepers_live_unknown_and_unparseable_locks_refuse(self) -> None:
        unknown = patch.object(measurement_liveness, "observe_identity",
                               return_value=Identity("UNKNOWN"))
        cases = (
            ("live", lambda runs: self._lock(runs, os.getpid(), START), None),
            ("live_without_start", lambda runs: self._lock(runs, os.getpid(), None), None),
            ("unparseable", lambda runs: (runs / "campaign.lock").write_text("garbage\n"), None),
            ("unknown", lambda runs: self._lock(runs, 4242, "Mon Oct 5 00:00:00 2026"), unknown),
        )
        for name, make, context in cases:
            with self.subTest(name), (context or ExitStack()):
                runs = self.hazard_root(f"runs_{name}")
                make(runs)
                before = (runs / "campaign.lock").read_bytes()
                result = self.run_stage(self.configs("hz-lock-1", name=f"configs_{name}"), runs)
                self.assertEqual(result.code, 2)
                self.assertIn("another campaign appears to be running", result.err)
                self.assertEqual(self.invoked(runs), [])
                self.assertEqual((runs / "campaign.lock").read_bytes(), before)
        self.assertEqual(self.kinds(), [])

    def test_a9_legacy_root_still_refuses_a_stale_lock(self) -> None:
        runs = self.plain_root()
        self._lock(runs, self._reaped_pid(), "Mon Oct 5 00:00:00 2026")
        result = self.run_stage(self.configs("hz-lock-1"), runs)
        self.assertEqual(result.code, 2)
        self.assertIn("another campaign appears to be running", result.err)
        self.assertTrue((runs / "campaign.lock").exists())
        self.assertEqual(self.flags(), [])

    def test_a9_two_reclaimers_leave_exactly_one_lock(self) -> None:
        runs = self.hazard_root()
        self._lock(runs, self._reaped_pid(), "Mon Oct 5 00:00:00 2026")
        context = run_campaign._hazard_flag_context(runs)
        first_inside, release_first = threading.Event(), threading.Event()
        calls: list[str] = []

        def seam(_lock_path: Path) -> None:
            calls.append(threading.current_thread().name)
            if len(calls) == 1:
                first_inside.set()
                self.assertTrue(release_first.wait(10))

        outcome: dict[str, object] = {}

        def acquire(name: str) -> None:
            try:
                outcome[name] = run_campaign.acquire_campaign_lock(runs, hazard=context)
            except BaseException as exc:  # noqa: BLE001 - recorded for the assertion
                outcome[name] = exc

        with patch.object(run_campaign, "_HAZARD_LOCK_RECLAIM_SEAM", seam):
            first = threading.Thread(target=acquire, args=("first",), name="first")
            first.start()
            self.assertTrue(first_inside.wait(10))
            second = threading.Thread(target=acquire, args=("second",), name="second")
            second.start()
            time.sleep(0.3)
            self.assertTrue(second.is_alive(), "the second reclaimer did not wait on the flock")
            self.assertEqual(calls, ["first"])
            release_first.set()
            first.join(10)
            second.join(10)
        token = outcome["first"]
        self.assertIsInstance(token, run_campaign.CampaignLockToken)
        self.addCleanup(run_campaign.release_campaign_lock, token)
        self.assertIsInstance(outcome["second"], run_campaign.CampaignLockOwnershipError)
        self.assertEqual(sorted(path.name for path in runs.iterdir() if "lock" in path.name),
                         ["campaign.lock"])
        self.assertIn(f"pid={os.getpid()} ", (runs / "campaign.lock").read_text())
        self.assertEqual(self.kinds(), ["stale_lock_cleared"])

    def test_a9_keeper_a_lock_replaced_after_it_was_read_is_never_unlinked(self) -> None:
        # The reclaimer read a stale lock, but the path now names another
        # inode (another writer's lock): it refuses and leaves that lock alone.
        runs = self.hazard_root()
        self._lock(runs, self._reaped_pid(), "Mon Oct 5 00:00:00 2026")
        context = run_campaign._hazard_flag_context(runs)
        replacement = f"pid={os.getpid()} nonce={'cd' * 32} created_at=x start_time={json.dumps(START)}\n"

        def seam(lock_path: Path) -> None:
            lock_path.unlink()
            lock_path.write_text(replacement)

        with patch.object(run_campaign, "_HAZARD_LOCK_RECLAIM_SEAM", seam), \
                self.assertRaises(run_campaign.CampaignLockOwnershipError):
            run_campaign.acquire_campaign_lock(runs, hazard=context)
        self.assertEqual((runs / "campaign.lock").read_text(), replacement)
        self.assertEqual(self.kinds(), [])

    def test_f4a_unknown_identity_publishes_and_flags_and_the_stage_runs(self) -> None:
        """Opus triple audit F4a. Before: 'campaign start identity unavailable', exit 2, no member ran."""
        runs = self.hazard_root()
        unknown = lambda pid: Identity("UNKNOWN")  # noqa: E731
        with patch.object(run_campaign, "observe_identity", side_effect=unknown), \
                patch.object(measurement_liveness, "observe_identity", side_effect=unknown):
            result = self.run_stage(self.configs("hz-lock-1"), runs)
        self.assertEqual(result.code, 0, result.err)
        self.assertEqual(self.invoked(runs), ["hz-lock-1"])
        self.assertIn("registry_start_time_unavailable", self.kinds())
        self.assertFalse((runs / "campaign.lock").exists())

    def _torn(self, runs: Path, *, age_s: float = 120.0) -> Path:
        lock = runs / "campaign.lock"
        lock.write_bytes(b"")
        old = time.time() - age_s
        os.utime(lock, (old, old))
        return lock

    @unittest.skipUnless(Path(getattr(run_campaign, "LSOF_ARGV", ("/usr/sbin/lsof",))[0]).is_file(), "lsof is not installed")
    def test_f4b_an_old_unheld_torn_lock_is_reclaimed_and_flagged(self) -> None:
        """Opus triple audit F4b. Before: an empty lock refused this stage and every later one."""
        runs = self.hazard_root()
        self._torn(runs)
        result = self.run_stage(self.configs("hz-lock-1"), runs)
        self.assertEqual(result.code, 0, result.err)
        self.assertEqual(self.invoked(runs), ["hz-lock-1"])
        (flag,) = [row for row in self.flags() if row["observed"].get("kind") == "torn_lock_cleared"]
        self.assertEqual(flag["observed"]["torn_lock"]["open_holders"], 0)
        self.assertGreaterEqual(flag["observed"]["torn_lock"]["age_s"], 100)

    @unittest.skipUnless(Path(getattr(run_campaign, "LSOF_ARGV", ("/usr/sbin/lsof",))[0]).is_file(), "lsof is not installed")
    def test_f4b_keepers_young_held_or_registered_torn_locks_refuse(self) -> None:
        held_handles: list = []

        def held(runs: Path) -> None:
            held_handles.append(self._torn(runs).open("rb"))  # a live process holds the inode open

        def registered(runs: Path) -> None:
            self._torn(runs)
            measurement_liveness.publish_campaign(runs, "nonce", start_time=START)

        cases = (("young", lambda runs: self._torn(runs, age_s=1.0)), ("held", held), ("registered", registered))
        try:
            for name, make in cases:
                with self.subTest(name):
                    runs = self.hazard_root(f"runs_torn_{name}")
                    make(runs)
                    result = self.run_stage(self.configs("hz-lock-1", name=f"configs_torn_{name}"), runs)
                    self.assertEqual(result.code, 2, result.err)
                    self.assertIn("another campaign appears to be running", result.err)
                    self.assertEqual(self.invoked(runs), [])
                    self.assertTrue((runs / "campaign.lock").exists())
        finally:
            for handle in held_handles:
                handle.close()
            registry = measurement_liveness.custody_parent() / "active-campaigns"
            for entry in registry.iterdir() if registry.is_dir() else []:
                entry.unlink()
        self.assertNotIn("torn_lock_cleared", self.kinds())

    def _verdict(self, runs: Path) -> SimpleNamespace:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = run_campaign.main(["--whole-window-verdict", "--runs-dir", str(runs),
                                      "--campaign-policy", str(TEST_POLICY)])
        return SimpleNamespace(code=code, err=err.getvalue())

    def test_v3_whole_window_verdict_reclaims_a_stale_lock(self) -> None:
        runs = self.hazard_root()
        self._lock(runs, self._reaped_pid(), "Mon Oct 5 00:00:00 2026")
        result = self._verdict(runs)
        self.assertNotEqual(result.code, 2, result.err)
        self.assertTrue(self.log_rows(runs), "no verdict row was written")
        flags = [row for row in self.flags() if row["observed"].get("kind") == "stale_lock_cleared"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["source"]["stage"], "harvest")

    def test_v3_legacy_root_still_refuses(self) -> None:
        runs = self.plain_root()
        self._lock(runs, self._reaped_pid(), "Mon Oct 5 00:00:00 2026")
        result = self._verdict(runs)
        self.assertEqual(result.code, 2)
        self.assertEqual(self.log_rows(runs), [])


class StagePreflightTests(_Stage):
    """A10: a raised or rejected stage environment preflight collects and flags."""

    def _sha(self) -> str:
        return hashlib.sha256(TEST_POLICY.read_bytes()).hexdigest()

    def _rejected(self) -> dict:
        return {
            "schema_version": "joulewise.campaign_environment_preflight.v1",
            "policy_sha256": self._sha(), "captured_at": "2026-10-06T00:00:00Z",
            "snapshot": {"display": "awake"},
            "evaluation": {"eligible": False, "snapshot_sha256": "a" * 64, "findings_sha256": "b" * 64,
                           "findings": [{"field": "displays_asleep", "actual": False, "status": "fail"},
                                        {"field": "power_source", "actual": "AC", "status": "pass"}]},
            "override": None, "enforced": True, "admitted": False,
        }

    def test_a10_raised_preflight_collects_with_a_policy_bound_record(self) -> None:
        runs = self.hazard_root()
        with patch.object(run_campaign, "campaign_environment_preflight",
                          side_effect=RuntimeError("pmset probe timed out")):
            result = self.run_stage(self.configs("hz-env-1", "hz-env-2"), runs)
        self.assertEqual(self.invoked(runs), ["hz-env-1", "hz-env-2"], result.err)
        child = json.loads((runs.parent / f"{runs.name}.hz-env-1.preflight.json").read_text())
        self.assertEqual(child["policy_sha256"], self._sha())
        self.assertIs(child["admitted"], False)
        self.assertEqual(child["error"], "RuntimeError: pmset probe timed out")
        # s2-01: the raise branch keeps a snapshot, including the python_packages
        # that reduce.py reads mlx_version from, and that snapshot's own evaluation.
        self.assertEqual(set(child["snapshot"]["python_packages"]), {"mlx", "mlx-lm", "transformers"})
        self.assertIsInstance(child["evaluation"], dict)
        self.assertIn("findings", child["evaluation"])
        flags = [row for row in self.flags() if row["code"] == "env.stage_preflight_not_admitted"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["observed"]["status"], "error")
        self.assertEqual(flags[0]["observed"]["campaign"], "configs")

    def test_a10_rejected_preflight_collects_and_flags_failed_fields(self) -> None:
        runs = self.hazard_root()
        with patch.object(run_campaign, "campaign_environment_preflight",
                          return_value=self._rejected()):
            result = self.run_stage(self.configs("hz-env-1"), runs)
        self.assertEqual(self.invoked(runs), ["hz-env-1"], result.err)
        flags = [row for row in self.flags() if row["code"] == "env.stage_preflight_not_admitted"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["observed"]["status"], "rejected")
        self.assertEqual(flags[0]["observed"]["failed_findings"],
                         [{"field": "displays_asleep", "status": "fail"}])

    def test_a10_legacy_root_still_refuses_both(self) -> None:
        for name, kwargs, code in (
            ("raised", {"side_effect": RuntimeError("pmset probe timed out")}, 2),
            ("rejected", {"return_value": self._rejected()}, 1),
        ):
            with self.subTest(name):
                runs = self.plain_root(f"runs_{name}")
                with patch.object(run_campaign, "campaign_environment_preflight", **kwargs):
                    result = self.run_stage(self.configs("hz-env-1", name=f"c_{name}"), runs)
                self.assertEqual(result.code, code)
                self.assertEqual(self.invoked(runs), [])
        self.assertEqual(self.flags(), [])


class RecordWriteTests(_Stage):
    """A13, A16 and A20: a failed record write is a flag, never a lost stage."""

    def test_a13_unauthenticated_campaign_log_is_flagged_and_collects(self) -> None:
        runs = self.hazard_root()
        error = run_campaign.CampaignAnalysisIdentityError(
            "campaign log or its provenance attestations cannot be authenticated",
            path=runs / "campaign_log.jsonl")
        with patch.object(run_campaign, "_campaign_log_analysis_identity_problem",
                          return_value=error):
            result = self.run_stage(self.configs("hz-log-1"), runs)
        self.assertEqual(result.code, 0, result.err)
        self.assertEqual(self.invoked(runs), ["hz-log-1"])
        flags = [row for row in self.flags() if row["observed"].get("kind") == "campaign_log_unauthenticated"]
        self.assertEqual(len(flags), 1)
        self.assertIn("cannot be authenticated", flags[0]["observed"]["detail"])

    def test_a13_legacy_root_still_refuses(self) -> None:
        runs = self.plain_root()
        error = run_campaign.CampaignAnalysisIdentityError("conflict", path=runs / "campaign_log.jsonl")
        with patch.object(run_campaign, "_campaign_log_analysis_identity_problem",
                          return_value=error):
            result = self.run_stage(self.configs("hz-log-1"), runs)
        self.assertEqual(result.code, 1)
        self.assertEqual(self.invoked(runs), [])
        self.assertEqual(self.flags(), [])

    def _raise_once(self, target: str, exc: BaseException, *, on_call: int = 1):
        real = getattr(run_campaign, target)
        calls = {"n": 0}

        def wrapper(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == on_call:
                raise exc
            return real(*args, **kwargs)

        return patch.object(run_campaign, target, side_effect=wrapper)

    def test_a16_member_provenance_failure_is_flagged_and_the_stage_continues(self) -> None:
        runs = self.hazard_root()
        with self._raise_once("record_campaign_member_provenance", OSError("disk full")):
            result = self.run_stage(self.configs("hz-rec-1", "hz-rec-2"), runs)
        self.assertEqual(self.invoked(runs), ["hz-rec-1", "hz-rec-2"], result.err)
        self.assertEqual(result.code, 0, result.err)
        flags = [row for row in self.flags() if row["code"] == "campaign.runner_record_flagged"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["scope"]["run_id"], "hz-rec-1")
        self.assertEqual(flags[0]["observed"], {"kind": "provenance_unpersisted",
                                                "phase": "provenance_invoked_member",
                                                "error_type": "OSError"})
        self.assertEqual(len(self.verdicts(runs)), 1)

    def test_a16_first_provenance_write_failure_still_collects(self) -> None:
        runs = self.hazard_root()
        with self._raise_once("write_campaign_provenance", OSError("read-only")):
            result = self.run_stage(self.configs("hz-rec-1", "hz-rec-2"), runs)
        self.assertEqual(self.invoked(runs), ["hz-rec-1", "hz-rec-2"], result.err)
        flags = [row for row in self.flags() if row["code"] == "campaign.runner_record_flagged"]
        self.assertEqual([(row["scope"]["level"], row["observed"]["phase"]) for row in flags],
                         [("window", "new_campaign_provenance")])

    def test_a16_keeper_lock_ownership_failure_still_ends_the_stage(self) -> None:
        runs = self.hazard_root()
        lock_error = getattr(run_campaign, "CampaignLockOwnershipError", RuntimeError)
        real = run_campaign.append_log

        def append_log(log_path, row, **kwargs):
            if row.get("run_id") == "hz-rec-1":  # member 1's log row
                raise lock_error("campaign log append requires a held campaign.lock")
            return real(log_path, row, **kwargs)

        with patch.object(run_campaign, "append_log", side_effect=append_log):
            result = self.run_stage(self.configs("hz-rec-1", "hz-rec-2"), runs)
        self.assertEqual(result.code, 2)
        self.assertEqual(self.invoked(runs), ["hz-rec-1"])
        self.assertEqual(self.kinds(), [])

    def test_a16_legacy_root_still_ends_the_stage(self) -> None:
        runs = self.plain_root()
        with self._raise_once("record_campaign_member_provenance", OSError("disk full")):
            result = self.run_stage(self.configs("hz-rec-1", "hz-rec-2"), runs)
        self.assertEqual(result.code, 2)
        self.assertEqual(self.invoked(runs), ["hz-rec-1"])
        self.assertEqual(self.flags(), [])

    # PLAN2 S4 (lane P2-RC) closes A20 differently: the HAZARD stage never
    # evaluates the idle-admission core, so a raising core cannot degrade the
    # verdict; the stage writes one provisional minimal row instead.
    def test_a20_core_verdict_failure_writes_a_fallback_verdict(self) -> None:
        runs = self.hazard_root()
        with patch.object(run_campaign, "idle_admission_core_verdict",
                          side_effect=ValueError("core evaluation broke")) as core:
            result = self.run_stage(self.configs("hz-ver-1"), runs)
        self.assertEqual(result.code, 0, result.err)
        core.assert_not_called()
        verdicts = self.verdicts(runs)
        self.assertEqual(len(verdicts), 1)
        self.assertEqual(verdicts[0]["idle_admission_core"], {"status": "deferred_to_desk"})
        self.assertIs(verdicts[0]["provisional"], True)
        self.assertEqual(self.kinds(), [])

    def test_a20_verdict_append_failure_retries_minimal(self) -> None:
        # The minimal row failing to append is flagged; the stage still ends with rc 1.
        runs = self.hazard_root()
        with self._raise_once("_hazard_minimal_verdict_row", OSError("short write")):
            result = self.run_stage(self.configs("hz-ver-1"), runs)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(self.verdicts(runs), [])
        self.assertEqual(self.kinds(), ["stage_verdict_degraded"])

    def test_a20_legacy_root_still_loses_the_verdict(self) -> None:
        runs = self.plain_root()
        with patch.object(run_campaign, "idle_admission_core_verdict",
                          side_effect=ValueError("core evaluation broke")):
            result = self.run_stage(self.configs("hz-ver-1"), runs)
        self.assertEqual(result.code, 2)
        self.assertEqual(self.verdicts(runs), [])
        self.assertEqual(self.flags(), [])


class DispatchTests(unittest.TestCase):
    """The predicate: a plain root and an ARM-shaped locator are legacy."""

    def test_only_the_hazard_locator_schema_dispatches(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertIsNone(run_campaign._hazard_flag_context(root))
            (root / window_lineage.LOCATOR_BASENAME).write_text(
                json.dumps({"schema_version": "joulewise.launch_lineage_locator.v1"}))
            self.assertIsNone(run_campaign._hazard_flag_context(root))
            (root / window_lineage.LOCATOR_BASENAME).write_text(
                json.dumps({"schema_version": window_lineage.HAZARD_LOCATOR_SCHEMA}))
            context = run_campaign._hazard_flag_context(root)
            self.assertIsNotNone(context)
            self.assertEqual(context.writer, "core-run_campaign")

    def test_lock_ownership_error_is_a_runtime_error(self) -> None:
        self.assertTrue(issubclass(run_campaign.CampaignLockOwnershipError, RuntimeError))


if __name__ == "__main__":
    unittest.main()
