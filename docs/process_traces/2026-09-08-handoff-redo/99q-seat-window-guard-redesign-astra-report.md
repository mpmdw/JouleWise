```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented marker-based measurement census; 368 tests and 30 counterfactuals passed within the eight-path write scope.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "head_end": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "upstream_end": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "branch": "fix/2026-09-08-window-status-liveness"
  },
  "pathspec": [
    "scripts/window_status.sh",
    "scripts/run_night.py",
    "scripts/run_campaign.py",
    "joulewise/measurement_liveness.py",
    "tests/test_window_status_guard.py",
    "tests/test_measurement_liveness.py",
    "tests/test_run_night.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_measurement_liveness tests.test_window_status_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK\\s*$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night tests.test_run_campaign > /private/tmp/window-liveness-writers.log 2>&1",
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
      "kind": "test",
      "cmd": "python3 /private/tmp/window-liveness-counterfactuals.py > /private/tmp/window-liveness-counterfactuals.log 2>&1",
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
      "kind": "lint",
      "cmd": "bash -n scripts/window_status.sh && git diff --check",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Verification used temporary custody, fake identity probes, and mocked measurement launches; this is not live quiet-Mac validation.",
      "needs": "Lead owns final review, bookkeeping, and deployment to the measurement checkout."
    }
  ]
}
```

## Change

Replaced argv inspection with independent chain and campaign identity checks. Unknown observations refuse before status or Git mutation. Campaign registry cleanup checks ownership; existing campaign-lock serialization, explicit stale repair, chain once-only behavior, and freeze behavior remain intact.

The shared setting is `JOULEWISE_CUSTODY_PARENT`, defaulting to `~/night-custody`. Additional reader roots use the JSON-array setting `JOULEWISE_ADDITIONAL_CUSTODY_PARENTS`.

## Verification notes

Final results: **24 census/shell tests**, **344 night/campaign tests**, and **30/30 counterfactuals detected**. Every mutation was restored. Syntax, whitespace, and scope checks passed.

The broader discovery and launch/watchdog suites were intentionally excluded under the explicit ruling. No repository commit, push, deployment, or live capture occurred.

Replay evidence: [counterfactual harness](/private/tmp/window-liveness-counterfactuals.py), [counterfactual results](/private/tmp/window-liveness-counterfactuals.log), [writer-suite results](/private/tmp/window-liveness-writers.log).

## Clause map

Each listed counterfactual produced the intended assertion failure.

| Production site | Biting assertion | Executed counterfactual |
|---|---|---|
| `joulewise/measurement_liveness.py:187` | `tests/test_window_status_guard.py:79`: live chain preserves status and avoids Git | M01: ignore chain markers |
| `joulewise/measurement_liveness.py:151` | `tests/test_window_status_guard.py:85`: closed chain publishes | M02: hide exit markers |
| `joulewise/measurement_liveness.py:179` | `tests/test_window_status_guard.py:91`: reused PID warns and permits | M03: compare PID alone |
| `joulewise/measurement_liveness.py:172` | `tests/test_window_status_guard.py:96`: dead PID permits | M04: refuse dead chain owner |
| `joulewise/measurement_liveness.py:257` | `tests/test_window_status_guard.py:101`: legacy/malformed markers refuse | M05: downgrade uncertainty to warning |
| `joulewise/measurement_liveness.py:186` | `tests/test_window_status_guard.py:79`: sent marker cannot close chain | M06: short-circuit on sent |
| `joulewise/measurement_liveness.py:203` | `tests/test_window_status_guard.py:107`: sent marker cannot close campaign | M07: short-circuit on sent |
| `joulewise/measurement_liveness.py:240` | `tests/test_window_status_guard.py:107`: unrelated spaced runs root refuses | M08: omit registry discovery |
| `scripts/run_campaign.py:8251` | `tests/test_run_campaign.py:188`: ordinary child sees registration | M09: remove ordinary registration |
| `scripts/run_campaign.py:7282` | `tests/test_run_campaign.py:191`: AXI child sees registration | M10: remove AXI registration |
| `scripts/run_campaign.py:8028` | `tests/test_run_campaign.py:191`: AXI exception removes owned entry | M11: remove AXI cleanup |
| `joulewise/measurement_liveness.py:90` | `tests/test_measurement_liveness.py:110`: replacement entries survive | M12: unlink unconditionally |
| `joulewise/measurement_liveness.py:172` | `tests/test_measurement_liveness.py:101`: dead registry owner warns; entry remains | M13: treat stale entry as live |
| `scripts/run_campaign.py:3159` | `tests/test_run_campaign.py:197`: dry-run/maintenance publish nothing | M14: register every lock acquisition |
| `scripts/window_status.sh:44` | `tests/test_window_status_guard.py:117`: mentions do not affect output; `ps` stub remains untouched | M15: restore argv census |
| `joulewise/measurement_liveness.py:186` | `tests/test_window_status_guard.py:79`: live `unittest` path refuses | M16: restore word exemption |
| `scripts/window_status.sh:96` | `tests/test_window_status_guard.py:125`: freeze prevents Git publication | M17: remove freeze branch |
| `joulewise/measurement_liveness.py:257` | `tests/test_window_status_guard.py:133`: root errors preserve status/Git | M18: convert root errors to clear |
| `scripts/run_night.py:379` | `tests/test_run_night.py:383`: chain marker contains start token | M19: omit token value |
| `scripts/run_night.py:375` | `tests/test_run_night.py:383`: observer receives child PID | M20: observe driver PID |
| `joulewise/measurement_liveness.py:232` | `tests/test_measurement_liveness.py:157`: additional roots are discovered as JSON path data | M21: ignore additional roots |
| `joulewise/measurement_liveness.py:218` | `tests/test_measurement_liveness.py:168`: reconcile once; continued instability refuses | M22: omit reconciliation |
| `joulewise/measurement_liveness.py:68` | `tests/test_measurement_liveness.py:183`: zombie identity is DEAD | M23: treat zombie as live |
| `joulewise/measurement_liveness.py:159` | `tests/test_measurement_liveness.py:80`: malformed exit cannot close chain | M24: accept every exit record |
| `joulewise/measurement_liveness.py:210` | `tests/test_measurement_liveness.py:89`: registry entry governs without target lock | M25: require referenced lock |
| `joulewise/measurement_liveness.py:171` | `tests/test_window_status_guard.py:133`: probe uncertainty refuses | M26: clear UNKNOWN observations |
| `scripts/window_status.sh:96` | `tests/test_window_status_guard.py:125`: freeze still allows local status write | M27: exit before status write |
| `scripts/run_campaign.py:8946` | `tests/test_run_campaign.py:188`: ordinary exception removes owned entry | M28: remove ordinary cleanup |
| `scripts/run_campaign.py:3170` | `tests/test_run_campaign.py:188`: campaign lock records start identity | M29: null lock start token |
| `joulewise/measurement_liveness.py:128` | `tests/test_measurement_liveness.py:140`: failed publication removes partial entry | M30: leave partial registration |

## Residual risk

Hand-launched chains remain uncovered during settle periods and inter-campaign gaps. Direct collectors, custom launchers, and older uninstrumented checkouts may be uncovered. A dead campaign parent can leave surviving measurement children. Launches after census remain a snapshot race; `lstart` tokens have one-second precision.

Next step: lead reviews the diff and deploys to the actual measurement checkout with matching custody settings. Retain driver-managed chains, sequential publication/launch, and full agent exit during capture.