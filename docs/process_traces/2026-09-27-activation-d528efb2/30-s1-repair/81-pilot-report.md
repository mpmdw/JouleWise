```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Parity prototype and two pilots completed; the T5 pilot remains excluded under parity.",
  "workspace": {
    "base_requested": "601a06c5",
    "base_mode": "exact",
    "head_start": "601a06c5c2712fa2ea1d8aada078c05ccd12b38e",
    "head_end": "601a06c5c2712fa2ea1d8aada078c05ccd12b38e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "tests/bfgs_fixtures.py",
    "tests/test_floor_extraction.py",
    "tests/test_analysis_integration.py",
    "tests/test_mint_floor_artifact.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_bfgs_fixtures",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 15 tests in 10.925s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_mint_floor_artifact.AuthenticationTests.test_authenticated_replay_does_not_import_prefill_refusal",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.006s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -c 'import tests.bfgs_fixtures as f, tests.test_mint_floor_artifact as t, unittest; t.write_passing_pair=f.write_charging_pair; unittest.main(module=None, argv=[\"unittest\",\"tests.test_mint_floor_artifact.AuthenticationTests.test_authenticated_replay_does_not_import_prefill_refusal\"])'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["WindowBatteryRefusal: window battery refusal: member: battery_float_confounded (pre IsCharging is not No, pre InstantAmperage exceeds 200 mA)", "FAILED (errors=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "battery_float_confounded"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -c 'import tests.bfgs_fixtures as f, unittest; f.PARITY_TEST_IDS=frozenset((\"tests.test_floor_extraction.SpecMembershipBindingTests.test_full_coverage_has_no_membership_refusal\",)); unittest.main(module=None, argv=[\"unittest\",\"tests.test_floor_extraction.SpecMembershipBindingTests.test_full_coverage_has_no_membership_refusal\"])'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.036s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -c 'import tests.bfgs_fixtures as f, tests.test_floor_extraction as t, unittest; f.PARITY_TEST_IDS=frozenset((\"tests.test_floor_extraction.SpecMembershipBindingTests.test_full_coverage_has_no_membership_refusal\",)); t.write_passing_pair=f.write_charging_pair; unittest.main(module=None, argv=[\"unittest\",\"tests.test_floor_extraction.SpecMembershipBindingTests.test_full_coverage_has_no_membership_refusal\"])'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": ["WindowBatteryRefusal: window battery refusal: plan-r01: battery_float_confounded (pre IsCharging is not No, pre InstantAmperage exceeds 200 mA); plan-r02: battery_float_confounded (pre IsCharging is not No, pre InstantAmperage exceeds 200 mA); plan-r03: battery_float_confounded (pre IsCharging is not No, pre InstantAmperage exceeds 200 mA)", "FAILED (errors=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "battery_float_confounded"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -c 'import tests.bfgs_fixtures as f, unittest; f.PARITY_TEST_IDS=frozenset((\"tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_unpinned_model_is_included_by_loader\",)); unittest.main(module=None, argv=[\"unittest\", \"tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_unpinned_model_is_included_by_loader\"])'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: 'excluded' != 'included'", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "T5 remains excluded under parity, triggering R3-3 stop condition 6. Its exact base reasons are adapter_continuity_failed, cpu_admission_core_failed, environment_admission_failed, environment_admission_missing, whole_window_verdict_conflict, and whole_window_verdict_provenance_invalid.",
      "needs": "Lead applies the ruling's cold-gate return for the failed pilot and decides the bounded builder replay task."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "PARITY_TEST_IDS remains empty because the ruling assigns that list to the lead. Floor GREEN and T5 runs used temporary in-process grants; their source tests are not independently green until granted.",
      "needs": "Lead adds the approved pilot test IDs to PARITY_TEST_IDS."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "A T5 charging-pair plant cannot demonstrate GREEN-to-RED while the unplanted test is already RED.",
      "needs": "Repeat the T5 plant after its unplanted test becomes green."
    }
  ]
}
```

## Change

The helper prototype patches only `CustodyTelemetryIdentity.production_predicate_exempt` and guards use by test ID. The two completed pilots retain byte-identical assertions.

| Pilot | Repair | GREEN → charging-pair RED | Class rule |
|---|---|---|---|
| T2 `test_full_coverage_has_no_membership_refusal` | Main’s summary fixture, physical bound config and agreeing telemetry labels, passing pair, parity | GREEN with temporary ID grant → `battery_float_confounded` | Held, conditional on the lead’s ID grant |
| Bind + pair `test_authenticated_replay_does_not_import_prefill_refusal` | Schema-valid physical config before the existing rebind and pair | GREEN → `battery_float_confounded` | Held |
| T5 `test_real_controller_unpinned_model_is_included_by_loader` | Builder corpus plus parity | Still RED: `excluded` | Did not hold |

Exact final diff:

```diff
diff --git a/tests/bfgs_fixtures.py b/tests/bfgs_fixtures.py
index 71255204..a3885619 100644
--- a/tests/bfgs_fixtures.py
+++ b/tests/bfgs_fixtures.py
@@ -2,6 +2,7 @@
 
 from __future__ import annotations
 
+import contextlib
 import hashlib
 import json
 from pathlib import Path
@@ -10,7 +11,38 @@ import subprocess
 from typing import Any, Callable, Mapping
 from unittest.mock import patch
 
-from joulewise import battery_float
+from joulewise import battery_float, whole_window
+
+
+# Closed list: the only places where exemption parity changes behaviour.
+PARITY_SWITCHED_OFF = (
+    ("joulewise/analysis_engine/inputs.py", "anchor_fallback_member_unusable"),
+    ("joulewise/floor_extraction.py", "_cpu_admission_bundle_reasons"),
+    ("scripts/run_campaign.py", "_current_member_environment_refusals"),
+    ("scripts/run_campaign.py", "_member_readiness_reasons"),
+)
+
+# Closed list of test IDs granted parity.  Written by the lead from the
+# triage record; a seat never adds to it.
+PARITY_TEST_IDS: frozenset[str] = frozenset({
+})
+
+
+@contextlib.contextmanager
+def exemption_parity(test_id: str):
+    """For one named test, treat every bundle as exempt, as main treated it.
+
+    The battery gate, the bundle's config binding, the mock barrier and
+    strict validation are untouched: none of them reads the exemption.
+    """
+    if test_id not in PARITY_TEST_IDS:
+        raise AssertionError(f"exemption parity not granted to {test_id}")
+    with patch.object(
+        whole_window.CustodyTelemetryIdentity,
+        "production_predicate_exempt",
+        property(lambda self: True),
+    ):
+        yield
 
 
 FIXTURES = Path(__file__).parent / "fixtures" / "battery_float"
diff --git a/tests/test_analysis_integration.py b/tests/test_analysis_integration.py
index 72b0ada5..7203487e 100644
--- a/tests/test_analysis_integration.py
+++ b/tests/test_analysis_integration.py
@@ -118,7 +118,7 @@ from tests.test_run_campaign import (
     run_campaign_module,
 )
 from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
-from tests.bfgs_fixtures import produce_strict_bundle
+from tests.bfgs_fixtures import exemption_parity, produce_strict_bundle
 
 
 ROOT = Path(__file__).resolve().parents[1]
@@ -2020,7 +2020,7 @@ class AnalysisIntegrationTests(unittest.TestCase):
         manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
         target = manifest["entries"][0]
 
-        with mock.patch(
+        with exemption_parity(self.id()), mock.patch(
             "joulewise.analysis_engine.inputs.custody_telemetry_identity",
             return_value=PRODUCTION_TELEMETRY_IDENTITY,
         ):
diff --git a/tests/test_floor_extraction.py b/tests/test_floor_extraction.py
index 3cdeb24f..98472b06 100644
--- a/tests/test_floor_extraction.py
+++ b/tests/test_floor_extraction.py
@@ -115,6 +115,7 @@ from joulewise.whole_window import (
 )
 from joulewise.reduce import _integrate
 from tests.test_arm_readiness import LaunchConsumptionV2Tests
+from tests.bfgs_fixtures import exemption_parity, rebind_config, write_passing_pair
 
 # Whole-window verdict re-derivation anchors NEG-8 tolerances to a
 # repo-REGISTERED campaign policy (the only trust anchor outside bundle
@@ -6399,12 +6400,27 @@ class SpecMembershipBindingTests(_PermissiveStrictValidatorMixin, unittest.TestC
         )
 
     def test_full_coverage_has_no_membership_refusal(self) -> None:
-        with tempfile.TemporaryDirectory() as tmp:
+        with exemption_parity(self.id()), tempfile.TemporaryDirectory() as tmp:
             runs_root = Path(tmp)
             all_ids = [f"plan-r{index:02d}" for index in range(1, 4)]
             install_synthetic_recovered_manifest(runs_root, all_ids)
+            config_template = json.loads(
+                (Path(__file__).parent / "fixtures" / "d078_r01" / "config.json").read_text()
+            )
             for bundle_id in all_ids:
-                write_bundle(runs_root, bundle_id, make_summary(40.0, anchor_bound=0.0))
+                summary = make_summary(40.0, anchor_bound=0.0)
+                summary["measurement_quality"]["telemetry_source"] = "powermetrics"
+                write_bundle(runs_root, bundle_id, summary)
+                bundle = runs_root / bundle_id
+                config = copy.deepcopy(config_template)
+                config["run_id"] = bundle_id
+                (bundle / "config.json").write_text(json.dumps(config) + "\n")
+                metadata = json.loads((bundle / "metadata.json").read_text())
+                metadata["run_id"] = bundle_id
+                metadata["adapters"] = {"telemetry": {"name": "powermetrics"}}
+                (bundle / "metadata.json").write_text(json.dumps(metadata) + "\n")
+                rebind_config(bundle)
+                write_passing_pair(bundle)
             spec = {
                 "schema_version": EXTRACTION_SPEC_SCHEMA_VERSION,
                 "cells": [
diff --git a/tests/test_mint_floor_artifact.py b/tests/test_mint_floor_artifact.py
index ce192988..74acfc33 100644
--- a/tests/test_mint_floor_artifact.py
+++ b/tests/test_mint_floor_artifact.py
@@ -79,11 +79,18 @@ def stack_identity() -> dict:
     }
 
 
-def _install_support_bundle(root: Path, bundle_id: str) -> None:
+def _install_support_bundle(
+    root: Path, bundle_id: str, *, valid_config: bool = False,
+) -> None:
     """Authenticate spec members outside the target report cell."""
     bundle = root / bundle_id
     bundle.mkdir(parents=True)
-    config = {"run_id": bundle_id, "hardware_target": {"telemetry_backend": "powermetrics"}}
+    if valid_config:
+        config = load_json(REPO_ROOT / "configs" / "examples" / "mock_local.json")
+        config["run_id"] = bundle_id
+        config["hardware_target"]["telemetry_backend"] = "powermetrics"
+    else:
+        config = {"run_id": bundle_id, "hardware_target": {"telemetry_backend": "powermetrics"}}
     (bundle / "config.json").write_text(json.dumps(config), encoding="utf-8")
     (bundle / "metadata.json").write_text(json.dumps({"run_id": bundle_id}), encoding="utf-8")
     (bundle / "summary_metrics.json").write_text(
@@ -1045,7 +1052,7 @@ class AuthenticationTests(unittest.TestCase):
         temporary = tempfile.TemporaryDirectory()
         self.addCleanup(temporary.cleanup)
         runs_root = Path(temporary.name)
-        _install_support_bundle(runs_root, "member")
+        _install_support_bundle(runs_root, "member", valid_config=True)
         class LocalRefusalSession:
             ready = True
             refusal_reasons: tuple[str, ...] = ()
```

## Verification notes

The T5 run’s exact `base_reason_codes` were `adapter_continuity_failed`, `cpu_admission_core_failed`, `environment_admission_failed`, `environment_admission_missing`, `whole_window_verdict_conflict`, and `whole_window_verdict_provenance_invalid`. A separate strict-valid bundle from the same builder recorded `cadence_ratio_below_threshold`, `clock_anchor_unresolved`, and `clock_bound_unrecorded` in its own `window_evidence_precheck`, alongside environment admission reasons. Parity cannot clear reasons already recorded in produced evidence. No replay keyword or admission evidence was added.

The canonical suite was not run: this was the bounded scratch pilot, and its T5 stop condition fired. No commit or Git write was made.

## Residual risk

The lead must grant the approved parity IDs and adjudicate the failed T5 pilot under R3-3 stop condition 6. The ruled replay keyword is indicated by the builder summary, but this pilot also exposed adapter, CPU, and whole-window refusals; the keyword alone has not been shown to make this test green.