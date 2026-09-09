```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Confirmed the fixture timeout/cure boundary and in-memory mutation sensitivity; full campaign replay is blocked by checkout mismatch and read-only temporary storage.",
  "workspace": {
    "base_requested": "21e31107",
    "base_mode": "informational",
    "head_start": "0656bb98bcc8103383b0b65085f5b1e448b5627b",
    "head_end": "0656bb98bcc8103383b0b65085f5b1e448b5627b",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-09-rehearsal-harvest/70-item1-cold-start-deadline-derivation.md"
  ],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 0,
      "nit": 0
    },
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= FAKE_POWERMETRICS_SLEEP_SCALE=3.5 python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_member_survives_fixture_sleep_slack",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-ref-308-delta']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= FAKE_POWERMETRICS_SLEEP_SCALE=1 python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_member_survives_fixture_sleep_slack",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-ref-308-delta']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff 21e31107..112e86e4 --stat -- joulewise scripts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "rg -n 'FAKE_POWERMETRICS_SLEEP_SCALE|--no-sleep' joulewise scripts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": []
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --quiet 0656bb98..112e86e4 -- joulewise scripts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "Actual checkout is 0656bb98, not the stated 112e86e4. Target fixture and identity-test sources were loaded from Git objects for memory-only probes. Production directories match the target.",
      "needs": "Lead supplies a correctly pinned checkout for final campaign verification."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: campaign tests require temporary bundles and executable files. Named commands fail during import because no writable temporary directory exists. Full scenario outcomes and campaign-regression mutation were not obtained.",
      "needs": "Lead performs the blocked checks at 112e86e4 in a writable test environment, or explicitly accepts the narrower execution evidence."
    }
  ]
}
```

## Findings

No code defect established. This is **partial verification**, not a clean execution sign-off.

**1. Counterfactual pair — confirmed at the fixture/adapter boundary; four-scenario replay blocked.**

Loaded the fixture from `112e86e4` into memory, patched its argv/environment, and streamed its output through a pipe. The parent used a real `subprocess.run(..., timeout=17.5)`. A replacement `_run_bounded_capture` passed its bytes or actual exception to production `measure_post_run_idle`.

Observed:

| Scale | Fixture mode | Boundary outcome |
|---|---|---|
| 3.5 | Sleeping | Real `TimeoutExpired`, deadline 17.5; `post_idle_unavailable` |
| 3.5 | `--no-sleep` | Bounded drift; 100 post samples |
| 1 | Sleeping | Also timed out at 17.5 on this machine |
| 1 | `--no-sleep` | Bounded drift; 100 post samples |

Selected exact output lines:

```text
TIMEOUT_FORMULA 17.5 15.0
scale=3.5 no_sleep=False always_sleep=False {"idle_drift": {"reason": "post_idle_unavailable", "status": "unknown"}}
scale=1 no_sleep=False always_sleep=False {"idle_drift": {"reason": "post_idle_unavailable", "status": "unknown"}}
```

The initial probe expected paced scale 1 to succeed; that expectation failed with `AssertionError`, exit 1. The subsequent scale-1 unpaced probe passed. Both successful unpaced captures returned `post_sample_count: 100` and `idle_drift_bound_w: 0.9637533` for the probe’s fixed baseline.

This did **not** execute `_produced_retry_member`, its command-wrapper bypass, bundle custody, or strict validation.

I also invoked the four named tests together at both scales, using the requested environment:

```text
tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_cpu_admission_reads_final_attempt_telemetry
tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_environment_refusal_does_not_hide_valid_retry_telemetry
tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_missing_final_attempt_telemetry_fails_closed
tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound
```

Both invocations, and the new regression individually at both scales, stopped during import:

```text
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-ref-308-delta']
```

All four commands exited 1 before test execution. These are environment failures, not reproduced scenario assertion failures.

**2. Production untouched — confirmed.**

The requested production diff has no entries. Additionally, `joulewise` and `scripts` are identical between the actual checkout and target commit, making local production-source inspection applicable.

`_capture_timeout_s` remains:

```python
nominal_s = count * (self._interval_ms(config) / 1000.0)
return max(15.0, nominal_s * 1.5 + 10.0)
```

Execution returned `17.5` for 100 samples and `15.0` for three samples at 20 Hz. Production grep returned no matches for either fixture knob; exit 1 is the expected no-match result.

**3. Synthetic timestamps — drift equivalence confirmed; blanket artifact equivalence would be incorrect.**

Executed the target’s `test_unpaced_sentinel_preserves_drift_with_synthetic_timestamps` with memory-backed output and temporary-directory substitution:

```text
Ran 1 test in 3.075s

OK
```

A separate in-memory comparison reported:

```text
RAW_DIFFERING_FIELDS ['elapsed_ns', 'processor.cpu_energy', 'processor.gpu_energy', 'timestamp']
RECORD_COUNTS 100 100
```

The fixture also recomputes ANE energy, but its value did not differ in this sample. Parsed timestamp metadata and derived rich-telemetry timestamps/durations consequently differ too.

The relevant consumers are:

- `measure_post_run_idle`, `joulewise/adapters/powermetrics.py:1021`: parses timestamps, elapsed intervals and energy counters, but passes only power arrays, baseline mean and contamination flags into drift derivation.
- `idle_window_gpu_quality`, same file:1949: uses GPU idle ratios and frequencies, without duration weighting.
- `derive_idle_drift_evidence`, `joulewise/uncertainty_evidence.py:1377`: derives counts, envelope, guard and effective bound from those inputs.
- Strict replay, `joulewise/cli.py:1362–1417`: independently follows the same sentinel derivation.
- Reducer drift-bound lookup, `joulewise/reduce.py:490`: consumes the resulting `idle_drift_bound_w`.

Thus the changed timing/energy fields are **read by parsers**, but do not enter this sentinel drift calculation. Raw bytes and their authentication hashes are not invariant.

The seat’s cadence/clock assertions establish preservation **across the sentinel stage within one execution**. They do not establish identical measured streams across separately paced and unpaced campaign executions.

**4. D-078 causal constraint — bounded sentinels are outside this check.**

The enforcement is in:

- `derive_powermetrics_anchor_v2`, `joulewise/uncertainty_evidence.py:332`, particularly the causal lower bound at :433–438.
- `derive_powermetrics_anchor_v3`, particularly :1056–1068, where `k_pre_spawn` includes record 0’s elapsed interval. An impossible first-parse bracket returns unresolved evidence.
- Strict clock replay, `joulewise/cli.py:1247–1306`, which reads `RAW_SAMPLES_NAME`, the measured capture.

`measure_post_run_idle` does not invoke these anchor validators. Its synthetic dates therefore neither trip nor bypass a sentinel causal check: that check is not applied to these bounded sentinels.

Synthetic `native_start + interval` is not proof that real time elapsed before availability. If such records were used for measured clock evidence, a sufficiently tight real spawn/first-parse bracket could reject them. The helper preserves pacing for `count=None`, and the fixture rejects `--no-sleep` without `-n`.

**5. Mutation — fixture regression fails and restores; campaign mutation remains blocked.**

In the in-memory fixture source, replaced both `not args.no_sleep` pacing guards with `True`, forcing sleeping. The target’s sentinel identity regression then failed:

```text
Ran 1 test in 0.443s

FAILED (failures=1)
```

Restoring the original source passed:

```text
Ran 1 test in 2.522s

OK

IDENTITY original PASS / always-sleep mutation FAIL / restored PASS
```

The always-sleep mutation also restored a real 17.5-second timeout at scale 3.5 despite supplying `--no-sleep`:

```text
scale=3.5 no_sleep=True always_sleep=True {"idle_drift": {"reason": "post_idle_unavailable", "status": "unknown"}}
NO_SLEEP_SCALE1_PASS; ALWAYS_SLEEP_TIMEOUT_CONFIRMED; campaign regression NOT EXECUTED
```

That follow-up probe exited 0. The requested **campaign** regression mutation was not executed.

**6. Same-signature statement and seat-report limits.**

Confirmed the same **timeout-to-producer signature**: 100 × 50 ms sleeping fixture, actual `TimeoutExpired` at 17.5 seconds, then `post_idle_unavailable`.

I did not independently reproduce the complete historical signature: retained partial sentinel → strict re-derivation mismatch → four scenario failures.

The seat report’s documented assertions support drift equivalence and within-run cadence/clock preservation. They should not be expanded into claims of identical artifacts, sentinel D-078 validation, or across-run clock equality. Its historical acceptance results remain seat evidence, not independently repeated results from this session.

## Residual risk

Full strict-validation execution and the campaign-regression mutation remain unverified. No live hardware validation was attempted. No files were modified.

**NEEDS_RULING**

- **Question:** Should the lead complete the blocked campaign matrix at `112e86e4` in a writable test environment and resume this review with the tails?
- **Options considered:** Lead-side execution preserves the requested acceptance; accepting only these memory probes leaves the campaign gates unverified.
- **Recommendation:** Complete the lead-side execution, including removal of the helper’s `--no-sleep` and the always-sleep campaign mutation.
- **Blocked work:** Four-scenario counterfactual outcomes, passing campaign regression at both scales, and its failing mutation.