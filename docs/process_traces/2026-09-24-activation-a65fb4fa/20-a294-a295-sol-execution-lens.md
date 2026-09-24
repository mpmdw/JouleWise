```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three should-fix findings; base/head refusal details match, both mutation controls work, and one named-suite failure reproduces at base.",
  "workspace": {
    "base_requested": "bd80d169",
    "base_mode": "exact",
    "head_start": "5ef72338b225281b951f4e3ccd8ca7a1675f21fb",
    "head_end": "5ef72338b225281b951f4e3ccd8ca7a1675f21fb",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "joulewise/night_gate.py",
        "line": 1275,
        "summary": "A clean receipt omits the new status probe from C5 evidence."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "joulewise/night_gate.py",
        "line": 1270,
        "summary": "The status command can invoke a configured fsmonitor hook despite --no-optional-locks."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "scripts/run_night.py",
        "line": 357,
        "summary": "A timed-out probe with partial output loses its result from refusal evidence."
      }
    ],
    "e1": "81 common fixture scenarios in base/head archives matched: 95 refusal events, 12 codes, and 60 distinct details. The only changed gate control flow is the new post-HEAD status check.",
    "e2": "HEAD mismatch skips status. A clean receipt differs only by C5 measurement_checkout_porcelain=[]; its C5 evidence array is unchanged. Later refusals gain the status ProbeResult in refusal.evidence. Consumer inspection found no key-shape break in watchdog, run_night, arm_retry, courier, or notice paths.",
    "e3": "Scratch Git checks stayed clean with .venv, runs, bytecode, egg-info, and .git/index.lock present; an untracked shadow module appeared in porcelain. Custody, staging, installer receipt, courier lock, and chain logs are outside the measurement clone or ignored; the chain starts after the gate. The production probe has a 30-second timeout. A configured fsmonitor hook remains an executable side effect.",
    "e4": "Deleting the refusal was killed by dirty tracked, untracked shadow, and real-Git tests; inverting stdout was killed by those and the clean-pass test; dropping the exit check was killed by the exit-128 test. The A295 test passed at a committed scratch head and failed after the window guard was removed and committed there.",
    "e5": "T6 uses /usr/bin/git without a skip, so a Linux image lacking that path fails it. A295 skips without /bin/zsh; this repository's Ubuntu CI installs /bin/zsh before unit tests. Linux CI was inspected, not run."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate tests.test_run_night tests.test_night_kinds tests.test_evidence_night tests.test_arm_retry tests.test_magistrate_watchdog tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 660 tests in 548.736s", "FAILED (failures=1, skipped=9)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: external watchdog (8 s): bind supervisor blocked in journal_block", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go",
      "cwd": "/tmp/jw-a294-review-b8d7e0ro/base",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: external watchdog (8 s): bind supervisor blocked in journal_block", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "python3 /tmp/jw_a294_mutate.py",
      "cwd": "/tmp",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["MUTANT drop_exit_check", "test_measurement_checkout_status_exit_128_is_probe_error 1 ERROR:"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "test_measurement_checkout_status_exit_128_is_probe_error 1"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_kinds.NightKindTests.test_committed_window_mutant_refused_by_real_prepare",
      "cwd": "/tmp/jw-a294-review-b8d7e0ro/head",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 18.511s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_kinds.NightKindTests.test_committed_window_mutant_refused_by_real_prepare",
      "cwd": "/tmp/jw-a294-review-b8d7e0ro/head",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: Refused not raised", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "Refused not raised"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The eight-second journal-block watchdog test fails at both base and head in isolation; the named suite has no other failure.",
      "needs": "Lead to assess the existing watchdog test separately."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The referenced 2026-09-24 03/04 brief directory is absent at this head; the supplied task text and available 29/43 authority notes were used.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — SHOULD-FIX:** [night_gate.py:1275](/Users/edr/code/wt-a65fb4fa-a294rev/joulewise/night_gate.py:1275) appends the result to an internal list but adds no C5 probe citation. Executed base/head clean receipts have identical C5 evidence arrays; only `measurement_checkout_porcelain=[]` is new. Later refusals do carry the result in `refusal.evidence`. Add a C5 citation and assert it in the clean-pass test.

- **F2 — SHOULD-FIX:** [night_gate.py:1270](/Users/edr/code/wt-a65fb4fa-a294rev/joulewise/night_gate.py:1270) relies on `--no-optional-locks` for a read-only status probe. In a scratch clone, that command invoked a configured `core.fsmonitor` hook; adding `-c core.fsmonitor=false` prevented the invocation. The hook can write or delay the t0 check, although the runner bounds it to 30 seconds. Git documents both the [optional-locks limit](https://git-scm.com/docs/git) and [fsmonitor hook behavior](https://git-scm.com/docs/git-config).

- **F3 — SHOULD-FIX:** [run_night.py:357](/Users/edr/code/wt-a65fb4fa-a294rev/scripts/run_night.py:357) retains bytes from `TimeoutExpired.stdout` even with `text=True`. An executed partial-output timeout returned exit 124 with bytes; the gate classified it as `night_probe_error` but recorded **zero** probe results in refusal evidence. Decode timeout output before constructing `ProbeResult`.

## Residual risk

Linux CI was inspected rather than executed. A295 skips when `/bin/zsh` is absent, while the configured Ubuntu unit job installs it; T6 has no skip for `/usr/bin/git`. The requested brief files were unavailable at the pinned head. The working tree remained clean and unchanged.