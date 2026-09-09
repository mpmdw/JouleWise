```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Round 3 matches the consult replacement behavior; the Mac-calibrated cadence assumption is closed statically, with execution blocked by unavailable writable temporary storage.",
  "workspace": {
    "base_requested": "bdbc9e75",
    "base_mode": "exact",
    "head_start": "016ac5f0d37f57a3e71fe9a3a99775c3cbc46d84",
    "head_end": "016ac5f0d37f57a3e71fe9a3a99775c3cbc46d84",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff bdbc9e75..016ac5f0 -- tests/test_run_campaign.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "         self.assertEqual(drift[\"post_sample_count\"], 100, drift)",
          "-        self.assertEqual(stages_checked, [True])",
          " ",
          "     def test_real_powermetrics_capture_timeout_is_unchanged(self) -> None:",
          "         from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PowermetricsTelemetryAdapter"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_member_survives_fixture_sleep_slack tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_real_powermetrics_capture_timeout_is_unchanged",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-ref-308-delta']"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --exit-code bdbc9e75..016ac5f0 -- tests/test_idle_admission.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"]
      },
      "expected": {"exit_code": 0, "tail_regex": "using /tmp instead"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check bdbc9e75..016ac5f0 -- tests/test_run_campaign.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"]
      },
      "expected": {"exit_code": 0, "tail_regex": "using /tmp instead"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Static review completed. Targeted unittest execution failed during import because no temporary directory was writable; no platform replay or executed sleeping-fixture counterfactual is claimed.",
      "needs": "Lead replays the affected tests and sleeping-fixture counterfactual in writable Linux and Mac environments."
    }
  ]
}
```

## Findings

None.

1. **Consult equivalence — satisfied.** The replacement at `tests/test_run_campaign.py:9610` has an identical AST to consult 87’s §Minimal replacement. Only its explanatory comment differs: it adds the stress-floor provenance and sparse-window explanation. This has no behavioral effect.

2. **Probe removal and helper preservation — satisfied.** No `_stage_idle_drift_sentinel`, `checked_sentinel`, `stages_checked`, `_window_gap_stats`, or `TracePoint` reference remains in the replaced method. The controller patch and diagnostic filesystem scan are gone. An in-memory comparison confirmed that all file bytes outside this method are unchanged, including the shared helper’s round-2 derived-count handling.

3. **Assertion portability — satisfied under consult 87’s stated prerequisites.** These are all three assertions in the replaced method:

   | Assertion | Linux, inherited 1× | Mac, 3.4× slack | Inherited 7× |
   |---|---|---|---|
   | Line 9633: `strict_valid is True` | Expected; effective fixture scale is 3.5 | Expected after successful capture | Expected if earlier deadlines complete |
   | Line 9639: drift status equals `"bounded"` | Expected; bounded fixture does not sleep | Expected; sentinel avoids per-record oversleep | Expected; sentinel still does not sleep |
   | Line 9644: post sample count equals `100` | Expected; stress floor activates five-second cap | Expected; stressed baseline activates cap | Expected if admission completes; cap remains five seconds |

   Thirty admission intervals at effective scale 3.5 span approximately 5.25 seconds, so the capped post duration is five seconds and its count is `ceil(5 / .05) = 100`. At scale 7, the baseline also reaches that cap. No assertion requires an internal measured-window sample gap.

   Mac scheduling slack is separate from the inherited fixture multiplier. These conclusions do not promise success when additional host delays exhaust unchanged admission deadlines.

4. **Defect discrimination — retained.** The helper at `tests/test_run_campaign.py:9550` appends `--no-sleep` only for bounded captures. Removing that append restores one sleep before every emitted record, including record zero (`tests/fixtures/fake_powermetrics_process.py:77–83`). For 100 records, requested sleeping totals **17.5 seconds at 3.5×**, plus processing overhead; at 7× it totals **35 seconds**.

   `_capture_timeout_s` retains the **17.5-second** deadline, passed to actual `subprocess.run`. The resulting `TimeoutExpired` propagates into `measure_post_run_idle`, whose exception handler returns drift status `"unknown"` with reason `"post_idle_unavailable"`. That contradicts the bounded assertion at **line 9639**; any earlier strict-validation failure also fails the test.

   `test_real_capture_timeout_leaves_post_idle_unavailable` at `tests/test_idle_admission.py:546` is untouched. The timeout-formula test at `tests/test_run_campaign.py:9646` is byte-unchanged.

5. **Same-signature statement — CLOSED for this delta.** The Mac-calibrated non-null cadence assumption is removed. Its replacement acceptance assertion is `drift["status"] == "bounded"` at **line 9639**. The 100-record assertion at line 9644 is supported by the retained stress floor, rather than unstressed host timing.

Static command tails were:

```text
REPLACEMENT_AST_IDENTICAL=PASS
OUTSIDE_REPLACED_METHOD_BYTE_IDENTICAL=PASS
REMOVED_PROBES_ABSENT=PASS
```

The focused unittest command exited **1 during import**, with `FileNotFoundError: ... No usable temporary directory found`. No test body executed. Workspace remained clean at `016ac5f0`.

## Residual risk

Platform passes and the sleeping-fixture counterfactual remain unexecuted here. At inherited 7×, admission requires approximately 10.85 seconds of requested sleeping against a 15-second deadline; additional scheduling delays can exhaust that margin.

The removed cadence/clock-anchor immutability checks and wrapper-completion count are no longer coverage supplied by this regression. The lead’s next step is writable Linux/Mac replay and explicit confirmation that restoring sleeping bounded capture fails through `post_idle_unavailable`.