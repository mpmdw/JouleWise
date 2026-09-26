```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Applied R-F1's nine-call allowlist, proved the three C10 guards detect mutations, and completed focused verification.",
  "workspace": {
    "base_requested": "aa90f349",
    "base_mode": "exact",
    "head_start": "aa90f34913f9c966cdf98989b088dd1c1270dee6",
    "head_end": "aa90f34913f9c966cdf98989b088dd1c1270dee6",
    "upstream_end": "aa90f34913f9c966cdf98989b088dd1c1270dee6",
    "branch": "feat/2026-09-26-bfgs-s0-helper-fence"
  },
  "pathspec": ["tests/test_battery_float_consumers.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["...............", "----------------------------------------------------------------------", "Ran 116 tests in 91.361s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["......", "----------------------------------------------------------------------", "Ran 181 tests in 344.164s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["", "----------------------------------------------------------------------", "Ran 156 tests in 168.329s", "", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".......................................................................................................................sss....................................................ssssss", "----------------------------------------------------------------------", "Ran 237 tests in 93.553s", "", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=9\\)"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_epoch_continuation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".................................", "----------------------------------------------------------------------", "Ran 68 tests in 58.658s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["....", "----------------------------------------------------------------------", "Ran 27 tests in 203.550s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "V3's sole failure is the previously reported sandbox live-probe case: live[\"os_build\"] is None.",
      "needs": "Lead reruns the live probe outside this sandbox."
    }
  ]
}
```

## Change

[R-F1’s guard](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float_consumers.py) now permits exactly nine pre-existing `dataclasses.replace` calls, keyed by path, enclosing qualname, and `ast.unparse(call)`. Its tests show that a new call is flagged, an allowlisted call passes, and a stale entry fails the inventory check. All nine keys were confirmed at base `64e39bb9`. Every entry has the required reason: `predates PairVerdict (64e39bb9); cannot receive a PairVerdict`.

The nine entries and first-argument type evidence are:

| Path · enclosing qualname | `ast.unparse(call)` | First argument’s type or origin |
|---|---|---|
| `joulewise/arm_readiness_evidence_t0.py` · `_derive_power` | `_replace(battery, stdout=battery.stdout_bytes)` | `battery` comes from `_fresh_probe(...) -> _ProbeResult`. |
| `joulewise/night_gate.py` · `_check_machine.battery_runner` | `replace(battery_result, stdout=battery_result.stdout_bytes)` | `battery_result` comes from `_run(...) -> ProbeResult`. |
| `joulewise/night_gate.py` · `evaluate_static` | `replace(_finish(plan, probes, rows, None), verdict='PENDING')` | `_finish(...) -> Receipt`. |
| `joulewise/night_gate.py` · `evaluate_dynamic_hard` | `replace(_finish(plan, probes, rows, None, authored_monotonic_ns=rows['C4'].measured['clock_monotonic_ns']), verdict='PENDING')` | `_finish(...) -> Receipt`. |
| `scripts/run_night.py` · `bind_until_quiet` | `replace(refusal, detail=refusal.detail + '; ' + json.dumps(dict(samples_total=lines, last_busy_cores=metrics.get('busy_cores'), top_consumers=summary['top_consumers_at_decision'], quiet_samples_sha256=digest, quiet_samples_lines=lines), sort_keys=True))` | `refusal` is assigned `night_gate.Refusal(...)` by the bind loop. |
| `scripts/run_night.py` · `bind_until_quiet` | `replace(current, schema=night_gate.QUIET_RECEIPT_SCHEMA, admission=summary, verdict='REFUSED' if refusal else 'REHEARSAL_ONLY' if plan.receipt_class == 'REHEARSAL_STUB' else 'GO', refusal=refusal, authored_monotonic_ns=max(0, int(monotonic() * 1000000000.0)))` | `current` starts as `night_gate.Receipt(...)`; later assignments retain or decode a `Receipt`. |
| `scripts/run_night.py` · `run_night` | `replace(probes, run=first_census)` | `probes` comes from `make_probes() -> Probes`. |
| `scripts/validate_powermetrics_fiducial.py` · `_label_active_capture_detection` | `replace(detection, anchor_method=method, derivation_role='prospective')` | The caller supplies `detect_pulses(...) -> FiducialDetection`. |
| `scripts/validate_powermetrics_fiducial.py` · `rederive_artifact` | `replace(fresh, b_fiducial_s=max(float(stored_bound), float(fresh.b_fiducial_s)))` | `fresh` comes from `rederive_detection_from_artifacts(...) -> FiducialDetection`. |

The prior round’s C1–C7, C9–C11 and amendments 20–25 and 27 remain as mapped in report 43. This continuation changes C8’s guard only. C10 is a **baseline-green guard (C10)** under R-F2.

## Verification notes

The three C10 mutation runs each used a temporary in-scope edit to `evidence_night.py`; its original bytes were restored after each run.

- **No `skipped` state:** Replaced the ordinary `battery_brackets` inspection with a `skipped` row. Command: `python3 -m unittest tests.test_evidence_night.LifecycleTests.test_battery_brackets_has_no_skipped_state_or_exemption`. The guard went red with `Refused: pre-arm checks failed: battery_brackets`; `Ran 1 test in 0.523s`, `FAILED (errors=1)`.
- **No exemption:** Added `"battery_brackets"` to the skipped-state exemption tuple. Same command. The source assertion went red; `Ran 1 test in 0.774s`, `FAILED (failures=1)`.
- **Unreadable kind:** Replaced that branch’s failed `battery_brackets` inspection with a `skipped` row. Command: `python3 -m unittest tests.test_evidence_night.LifecycleTests.test_an_unreadable_payload_kind_fails_the_arm_check_closed`. The guard observed `'skipped' != 'fail'`; `Ran 1 test in 0.523s`, `FAILED (failures=1)`.

`git diff --check` passed. Only the scoped test file is modified. No commit, push, or full-suite run was made.

## Residual risk

V3 needs the lead’s live-probe rerun outside this sandbox; its only failure was `live["os_build"]` being `None`.