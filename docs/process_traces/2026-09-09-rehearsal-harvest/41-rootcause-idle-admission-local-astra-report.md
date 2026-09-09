```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "blocked",
  "completion": "partial",
  "summary": "Traced the drift derivation and excluded relevant source drift; the actual failure cause remains unresolved because the enforced read-only sandbox prevents fixture execution.",
  "workspace": {
    "base_requested": "83ab38ed",
    "base_mode": "exact",
    "head_start": "83ab38edcacd67312171c0051cc31cc70a9be682",
    "head_end": "83ab38edcacd67312171c0051cc31cc70a9be682",
    "upstream_end": "83ab38edcacd67312171c0051cc31cc70a9be682",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "unresolved",
    "remediation": "none"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-idle-rc']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 71 tests"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff 58d9225b HEAD -- joulewise/controller.py joulewise/adapters/powermetrics.py joulewise/uncertainty_evidence.py joulewise/cli.py tests/test_controller.py tests/test_run_campaign.py tests/fixtures/fake_powermetrics_process.py",
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
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path\nfrom joulewise.adapters.powermetrics import parse_powermetrics_records as parse, decode_rich_telemetry as rich, idle_window_gpu_quality as quality, duration_weighted_mean_and_sample_variance as weighted\nfrom joulewise.uncertainty_evidence import derive_idle_drift_evidence as derive\nraw = Path(\"tests/fixtures/powermetrics_sample.plist\").read_bytes()\ndef inputs(anchor):\n    rows = parse(raw, timestamp_anchor_s=anchor)\n    powers = [r.combined_power_w for r in rows]\n    mean, _ = weighted(powers, [r.elapsed_ns / 1e9 for r in rows])\n    suspect = quality(rich(raw, timestamp_anchor_s=anchor))[\"idle_window_suspect\"]\n    return dict(pre_power_w=powers, post_power_w=powers, pre_power_w_mean=mean, pre_idle_window_suspect=suspect, post_idle_window_suspect=suspect)\nproduced = derive(**inputs(1788957994.0))\nreplayed = derive(**inputs(None))\nprint(\"producer_bound_w\", produced[2], \"strict_derived_bound_w\", replayed[2])\nprint(\"idle_drift_equal\", produced[0] == replayed[0])\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "producer_bound_w 1.0110630954235948 strict_derived_bound_w 1.0110630954235948",
          "idle_drift_equal True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "idle_drift_equal True"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The class and six controlled single-test invocations fail during import because tempfile.gettempdir() cannot create its probe under the enforced read-only sandbox. No fixture test executes, so no environment-dependent pass/fail flip was established.",
      "needs": "Lead: run the bounded diagnostic below with writable temporary storage and return its output, or provide the failing bundle. No repository edits are needed."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The evaluator arithmetic is deterministic for fixed inputs, but the reported failure cannot yet be classified as fixture-only. The failing bundle's stored drift evidence and producer exception were unavailable.",
      "needs": "Do not weaken strict equality or declare scientific neutrality before identifying the divergent input or producer failure."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Yesterday's replay record used scripts/shard_tests.py --workers 4, whereas today's supplied failures used an isolated unittest class. The evidence does not establish an overnight machine-state change independently of execution context.",
      "needs": ""
    }
  ]
}
```

## Causal chain

**The derivation is located; the trigger is not yet established.** Both supplied failure logs confirm the same four assertions and `FAILED (failures=4)`. Neither contains the stored drift values or an underlying producer exception.

1. [`scripts/run_campaign.py:2793`](/Users/edr/code/JouleWise-wt-idle-rc/scripts/run_campaign.py:2793) calls `validate_bundle(..., strict=True)` and makes validation problems determine `strict_valid`.

2. [`joulewise/cli.py:1361`](/Users/edr/code/JouleWise-wt-idle-rc/joulewise/cli.py:1361) reads:
   - `raw/powermetrics_idle.plist`;
   - `raw/powermetrics_idle_post.plist`;
   - `metadata.idle_baseline.power_w_mean`;
   - GPU contamination indicators decoded from those raw files;
   - recorded `uncertainty_evidence.idle_drift_guard`.

   It compares the resulting evidence dictionary and bound using exact equality.

3. [`derive_idle_drift_evidence`, line 1377](/Users/edr/code/JouleWise-wt-idle-rc/joulewise/uncertainty_evidence.py:1377) computes:

   ```
   run_bound_w = max(abs(power_w - recorded_pre_mean_w)
                     for every pre/post sample)
   effective_bound_w = run_bound_w                  # n_bundles == 0
   effective_bound_w = max(run_bound_w, guard_w)    # valid calibrated guard
   ```

   Insufficient samples, unknown/contaminated GPU evidence, or an invalid calibration guard instead produce unknown evidence and no bound.

4. The producer, [`measure_post_run_idle`, line 1018](/Users/edr/code/JouleWise-wt-idle-rc/joulewise/adapters/powermetrics.py:1018), calls that same derivation using its retained pre-idle records, current baseline, and captured post-idle records. Retry promotion copies the final admitted raw slice to the canonical pre-idle filename. Therefore, the validator’s fixed filename is **not by itself an attempt-selection defect**.

5. `_produced_retry_member` changes rich-telemetry CPU fields; it does not change these raw power samples or GPU fields.

The reported `drift_term_unknown` makes a producer fallback worth investigating. Both the adapter and controller can return `post_idle_unavailable` after an exception; retained capture bytes can subsequently survive through custody salvage. That could yield raw files from which validation derives a bound while stored evidence remains unknown. **This is a hypothesis, not a confirmed diagnosis.**

V3 provides a minimal, executed arithmetic probe using committed fixture bytes. Its side-by-side result was:

```text
producer_bound_w 1.0110630954235948 strict_derived_bound_w 1.0110630954235948
idle_drift_equal True
```

An additional in-memory invocation of the actual retry adapter’s `measure_post_run_idle`, with capture bytes supplied and no filesystem writes, returned the same bound. These probes do **not** reproduce the failing generated bundle.

| Counterfactual | Named test execution | Fixed-byte producer/derivation probe |
|---|---|---|
| Canonical corpus root; backup roots empty | Blocked before test starts | Equal; `1.0110630954235948 W` |
| `R7F_CORPUS_ROOT` unset | Same blocker | Same result |
| Corpus root points at this worktree | Same blocker | Same result |
| `TZ=UTC` | Same blocker | Same result |
| `LC_ALL=C` | Same blocker | Same result |
| `JOULEWISE_BACKUP_ROOTS` unset | Same blocker | Same result |
| CI | Passing shards, lead-established | Not executed here |
| Yesterday | Recorded passing **sharded** run | Relevant source bytes identical |

The worktree has no `runs*` directories; the canonical repository has numerous such directories. Neither the isolated drift calculation nor its raw-input selection searches those directories. The committed sampler fixture is also identical in both checkouts.

**Soundness:** the inspected calculation has no ambient corpus, locale, timezone, filesystem-order, or current-wall-clock input. Fixed-byte probes remained identical across the tested environment settings. However, the complete failure cannot responsibly be declared fixture-only. The bound is claim-bearing: [`reduce.py:467`](/Users/edr/code/JouleWise-wt-idle-rc/joulewise/reduce.py:467) computes `E_drift_bound_j = window.duration_s * idle_drift_bound_w`.

## Remediation

A minimal code cure is not justified until the missing divergent input or exception is captured. Keep the strict comparison intact.

The next exact step is this **single-test diagnostic**, run by the lead with writable temporary storage. It preserves the assertion and prints stored versus derived evidence, plus any bounded-capture exception:

```bash
PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 -c '
import json, traceback, unittest
from unittest.mock import patch
import tests.test_run_campaign as t
from joulewise.adapters import powermetrics as pm
from joulewise.uncertainty_evidence import derive_idle_drift_evidence

original_evaluate = t.run_campaign_module.evaluate_member
original_capture = pm.PowermetricsTelemetryAdapter._run_bounded_capture

def capture(self, *args, **kwargs):
    try:
        return original_capture(self, *args, **kwargs)
    except Exception:
        print("CAPTURE_EXCEPTION", kwargs.get("artifact_name"), flush=True)
        traceback.print_exc()
        raise

def evaluate(bundle, **kwargs):
    result = original_evaluate(bundle, **kwargs)
    metadata = result.metadata
    evidence = metadata["uncertainty_evidence"]
    print("STORED", json.dumps({
        "idle_drift": evidence.get("idle_drift"),
        "idle_drift_bound_w": metadata.get("idle_drift_bound_w"),
        "idle_baseline": metadata.get("idle_baseline"),
    }, sort_keys=True), flush=True)
    try:
        pre = (bundle / "raw" / pm.RAW_IDLE_NAME).read_bytes()
        post = (bundle / "raw" / pm.RAW_IDLE_POST_NAME).read_bytes()
        derived = derive_idle_drift_evidence(
            pre_power_w=[r.combined_power_w for r in pm.parse_powermetrics_records(pre)],
            post_power_w=[r.combined_power_w for r in pm.parse_powermetrics_records(post)],
            pre_power_w_mean=metadata["idle_baseline"]["power_w_mean"],
            pre_idle_window_suspect=pm.idle_window_gpu_quality(pm.decode_rich_telemetry(pre))["idle_window_suspect"],
            post_idle_window_suspect=pm.idle_window_gpu_quality(pm.decode_rich_telemetry(post))["idle_window_suspect"],
            calibration_guard=evidence["idle_drift_guard"],
        )
        print("DERIVED", json.dumps(derived, sort_keys=True), flush=True)
    except Exception:
        traceback.print_exc()
    print("PROBLEMS", result.validation_problems, flush=True)
    print((bundle / "logs" / "controller.log").read_text(), flush=True)
    return result

with patch.object(t.run_campaign_module, "evaluate_member", evaluate), patch.object(pm.PowermetricsTelemetryAdapter, "_run_bounded_capture", capture):
    unittest.main(module=t, defaultTest="IdleAdmissionCoreVerdictTests.test_environment_refusal_does_not_hide_valid_retry_telemetry", verbosity=2)
'
```

The defect-shaped regression should pin the **actual observed failure trigger** at the capture/input seam, exercise retry promotion and strict replay, and verify producer evidence against preserved raw bytes. Its precise failure injection depends on that diagnostic; inventing one now would risk testing a different defect.

## Disproved alternatives

- **Relevant code changed overnight:** byte comparisons found no differences across `58d9225b`, `5d13d0e6`, `5db38b58`, and this checkout for the producer, validator, derivation, campaign evaluator, helper tests, synthetic sampler, and plist fixture.
- **Timezone or locale directly changes this arithmetic:** controlled fixed-byte probes did not change either evidence or bound.
- **Canonical `runs/` contents directly feed the drift formula:** the inspected path reads explicit bundle-local files.
- **CPU-field replacement directly changes drift inputs:** those replacements do not alter the raw sentinel inputs.

Platform-wide behavior, transient capture failures, and differences between isolated and sharded execution remain untested.

## Residual risk

No files changed, no full suite ran, and no hardware measurements ran. The blocking restriction came from the session’s enforced read-only sandbox: Python could not create even its temporary-directory probe. The current evidence supports deterministic replay arithmetic, **not a confirmed root cause or a fixture-only soundness verdict**.