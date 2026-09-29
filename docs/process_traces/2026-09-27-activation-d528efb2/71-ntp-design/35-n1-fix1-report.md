```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the scoped N1 safety and attestation fixes; one policy-document pin remains red for the lead to update.",
  "workspace": {
    "base_requested": "e7371399",
    "base_mode": "descendant",
    "head_start": "0c2b1fbb1e1fe692cbeba89b405d1429ce1fecba",
    "head_end": "0c2b1fbb1e1fe692cbeba89b405d1429ce1fecba",
    "upstream_end": "0c2b1fbb1e1fe692cbeba89b405d1429ce1fecba",
    "branch": "feat/2026-09-28-ntp-n1"
  },
  "pathspec": [
    "joulewise/network_time_window.py",
    "tests/test_network_time_window.py",
    "scripts/run_night.py",
    "tests/test_run_night.py",
    "joulewise/night_gate.py",
    "tests/test_night_gate.py",
    "joulewise/arm_retry.py",
    "tests/test_arm_retry.py",
    "tests/test_launch_window.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_network_time_window -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 41 tests", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_run_night -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 255 tests in 125.558s", "OK (skipped=9)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_night_gate -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 104 tests", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_arm_retry -q",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 37 tests", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_launch_window -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 39 tests in 499.449s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The arm-retry document-pin test fails because the rendered policy now includes the required network-time refusal rows and lead-owned documents have not been updated.",
      "needs": "Lead updates the three named policy documents and reruns tests.test_arm_retry."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "N3 must populate OLD_IDLE_PLANS, but its ruled WRITE_SCOPE omits joulewise/network_time_window.py.",
      "needs": "Lead explicitly adds that path to N3's future scope."
    }
  ]
}
```

## Change

- **B1/F3, F4, F5:** Continuation lines, including the unindented braces in the preserved real log, now retain their parent timestamp. Query numbering skips orphaned raw files after an interrupted write. A non-object OFF receipt returns `network_time_unattested`. The regressions use the archived real bytes, an unindented marker followed by a clean query, an orphaned `h6-query-1.txt`, and `[]` as the OFF receipt.
- **F1/F2, S3:** Normal child exit requires a process-group absence probe before query or ON. Recovery rechecks a known group even when `chain.exited` exists; unknown or missing identity keeps the marker and blocks restoration. The dead man no longer turns an empty start marker into proof. Driver recovery refusals are recorded as `night_chain_alive` or the registered `night_refused_network_time_marker_invalid`. Tests exercise surviving descendants and an unknown PGID at the production driver and dead-man calls.
- **B2, S1, S2, S4, N1–N4:** The launch module injects network-time functions and tests pack refusal with the enforced set empty. Both original network-time reasons now have explanations in `COLD_GATE_CODES`, with the exact registry assertion restored; the marker reason is registered too. Added the ruled clock, build, boot, interval, exit-path, and ordering tests. `--h7` now uses all five paired readings for the estimator’s offset span and divides by its recorded `rate_fit_baseline_s`.

The OFF-guard and route-guard deletion runs each made its corresponding driver test fail **by assertion** (`failures=1, errors=0`); both tests pass on this implementation. Read-only inspection of the real W1-d04 `instrument_evidence.json` confirmed `clock_anchor.clock_stamps` contains all five readings and its computed span equals the stored `0.00148773193359375` s.

## Verification notes

The lead-owned documents need these exact rendered policy rows:

    | `night_refused_network_time_off_unproved` | Network time OFF or its exact command receipt was not proved. |
    | `night_refused_network_time_route_unenforced` | The capture route has no enforced network-time consumer. |
    | `night_refused_network_time_marker_invalid` | A pending network-time restore marker is malformed or unreadable. |

The single `tests.test_arm_retry` failure is its byte-equality check against [NIGHT_HANDBACK.md](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/docs/process/NIGHT_HANDBACK.md), with the same pending update needed in the runbook and pack GO contract. No document, Git, system setting, real system log, capture, or battery write/probe was performed.

## Residual risk

**N5 — future NEEDS_SCOPE:** N3’s scope must include `joulewise/network_time_window.py` so that seat can populate `OLD_IDLE_PLANS`. Lead-owned live bench checks remain outstanding.