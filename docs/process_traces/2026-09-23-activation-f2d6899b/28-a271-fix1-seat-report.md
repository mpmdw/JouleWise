```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the amended A271 arm-check behavior and regressions; the required pilot-protocol amendment is outside WRITE_SCOPE.",
  "workspace": {
    "base_requested": "f81e34ec",
    "base_mode": "exact",
    "head_start": "f81e34ec079bfda56c0b0132fe98135355006193",
    "head_end": "f81e34ec079bfda56c0b0132fe98135355006193",
    "upstream_end": "f81e34ec079bfda56c0b0132fe98135355006193",
    "branch": "feat/2026-09-23-a271-corecaptured"
  },
  "pathspec": [
    "joulewise/evidence_night.py",
    "tests/test_evidence_night.py",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "unowned_dirty": [
    "joulewise/night_gate.py",
    "joulewise/evidence_night.py",
    "joulewise/corecaptured_loop.py",
    "tests/test_corecaptured_loop.py",
    "tests/test_night_gate.py",
    "tests/test_evidence_night.py",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_evidence_night.py tests/test_docs_freshness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["245 passed, 648 subtests passed in 822.92s (0:13:42)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "245 passed, 648 subtests passed"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/a271-fix1-mutants.educ0c/run_mutants.py",
      "cwd": "/tmp/a271-fix1-mutants.educ0c",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FAILED tests/test_night_gate.py::NightGateTests::test_corecaptured_t0_threshold_is_three_spawns",
          "FAILED tests/test_evidence_night.py::LifecycleTests::test_corecaptured_arm_threshold_is_three_spawns",
          "FAILED tests/test_evidence_night.py::LifecycleTests::test_corecaptured_one_new_spawn_after_toggle_refuses"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FAILED.*test_corecaptured_one_new_spawn_after_toggle_refuses"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_evidence_night.py::LifecycleTests::test_corecaptured_arm_persistence_restarts_once_and_refuses",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["1 passed in 3.28s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 passed"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
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
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": ["Interrupted during test_arm_readiness_evidence_t0.py; no suite summary."]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Cold ruling 16 Q2 requires a pilot_protocol_v3.json threshold field and ruling ID; that path is outside WRITE_SCOPE and was not edited.",
      "needs": "Lead-issued scope expansion or lead edit."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide unittest discovery was interrupted after about 20 minutes; the requested four-module gate passed.",
      "needs": "Lead runs the canonical suite at the final candidate."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No live machine commands were run. The cold final pass and next arm notice remain lead-owned.",
      "needs": "Lead final pass and notice."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json"],
    "reason": "Cold ruling 16 Q2 requires recording the t0 machine-state threshold in the pilot protocol.",
    "blocked_work": "Add the threshold field and append ruling 16 to the protocol's ruling string.",
    "minimal_change": "Add t0_corecaptured_spawns_max: 2 and append cold gate 16 A271 Q2 (2026-09-23) to ruling."
  }
}
```

## Change

The inherited seven-file diff was kept uncommitted. This resumed turn changed three allowed files.

| Brief and ruling item | Initial diff audit → final state |
|---|---|
| F1; Q2 action 1, slow log read at both call sites | **DONE → DONE.** The clock precedes each read and the count includes timestamps through completion: [night_gate.py:1509](/Users/edr/code/wt-f2d6899b-a271/joulewise/night_gate.py:1509), [evidence_night.py:860](/Users/edr/code/wt-f2d6899b-a271/joulewise/evidence_night.py:860). Tests: `test_corecaptured_t0_window_anchors_before_slow_log_read`, `test_corecaptured_arm_window_anchors_before_slow_log_read`. |
| F2; Q2 action 2, bounded commands and radio restoration | **MISSING 30 s log bound → DONE.** The log read is now 30 s; off/on are 30 s each; restart is 60 s: [evidence_night.py:862](/Users/edr/code/wt-f2d6899b-a271/joulewise/evidence_night.py:862). Timeout tests cover off, wait, on, and command bounds. The production t0 runner already has a 30 s timeout at [run_night.py:64](/Users/edr/code/wt-f2d6899b-a271/scripts/run_night.py:64) and [run_night.py:343](/Users/edr/code/wt-f2d6899b-a271/scripts/run_night.py:343). |
| F3; Q2 action 4, parser blanks | **DONE → DONE.** [corecaptured_loop.py:38](/Users/edr/code/wt-f2d6899b-a271/joulewise/corecaptured_loop.py:38) ignores whitespace-only lines; a nonblank malformed line and empty output still error. Test: `test_blank_lines_anywhere_are_ignored_but_empty_output_is_not`. |
| F4; Q2 action 4, exactly-two boundaries | **DONE → DONE.** Tests: `test_corecaptured_t0_threshold_is_three_spawns`, `test_corecaptured_arm_threshold_is_three_spawns`. All three requested boundary mutants failed in scratch copies: `> 2` → `>= 2`, `<= 2` → `< 2`, and post-toggle `>= 1` → `>= 2`. |
| B1; Q3 conditions 1 and 3 | **MISSING → DONE.** [evidence_night.py:1091](/Users/edr/code/wt-f2d6899b-a271/joulewise/evidence_night.py:1091) licenses actuation only after item 0 and every earlier row pass. Otherwise [evidence_night.py:875](/Users/edr/code/wt-f2d6899b-a271/joulewise/evidence_night.py:875) records `remediation: "not_licensed"` and fails above two. `test_loaded_night_agent_makes_corecaptured_read_only` and `test_failed_census_makes_corecaptured_read_only` each record five spawns and only a log command. `test_failed_census_read_only_count_of_two_passes_without_actuation` covers the lower boundary. The all-pass clean and persistent cases assert one off, one on, and restart only on persistence. |
| S4; Q2 action 3, one new spawn after toggle | **DONE → DONE.** [evidence_night.py:917](/Users/edr/code/wt-f2d6899b-a271/joulewise/evidence_night.py:917); test: `test_corecaptured_one_new_spawn_after_toggle_refuses`. |
| S5, restored assertion | **DONE → DONE.** `test_check_passes_and_writes_only_check_json` again asserts no `launchctl` call at [test_evidence_night.py:892](/Users/edr/code/wt-f2d6899b-a271/tests/test_evidence_night.py:892). |
| S1 and N1/N2, handback text | **DONE → DONE.** [NIGHT_HANDBACK.md:84](/Users/edr/code/wt-f2d6899b-a271/docs/process/NIGHT_HANDBACK.md:84) includes the corecaptured refusal. [NIGHT_HANDBACK.md:265](/Users/edr/code/wt-f2d6899b-a271/docs/process/NIGHT_HANDBACK.md:265) names the log read, exact line, restart route, 0.5-core observation, arm/t0 read failures, 80–95 s cadence, and 1–3 s t0 read cost. |
| S3, busy-core re-sample | **DONE as documented deviation.** The existing `machine_quiet` 30 s observer runs immediately after the corecaptured row at [evidence_night.py:1097](/Users/edr/code/wt-f2d6899b-a271/joulewise/evidence_night.py:1097); no separate observer was added. |
| Q2 protocol record; Q3 condition 2 contract; next notice; Q3 condition 4 final pass | **MISSING.** The protocol and contract are outside WRITE_SCOPE. The next arm notice and cold final pass belong to the lead. Proposed text follows. |

On a scratch extraction of `f81e34ec` with the new tests overlaid, the slow-read test failed `2 != 3`; the blank-line and loaded-night tests also failed. On the completed diff, the requested suite passed. The repository-wide discovery was started but interrupted without a summary; it is a verification gap.

## Verification notes

The three scratch mutants each exited 1 on the named boundary test. The final worktree contains only the original seven dirty paths, and `git diff --check` is clean. No commit was made.

## Residual risk

**Proposed replacement for `docs/contracts/evidence_night_entry.md:175`:**

> `check` makes at most three machine moves, each at most once per invocation and each only after item 0 and every earlier row passed: (1) the fast-forward-only pull of the canonical checkout (item 1, D-183); (2) one Wi-Fi power off/on cycle (`networksetup -setairportpower en0 off`, 8 s, `on`) when more than two `corecaptured` spawns were counted in the last ten minutes; (3) one `sudo -n /usr/local/sbin/joulewise-restart-fseventsd` when new spawns persist 180 s after that cycle. Every move and its exit code is recorded in `check.json`.

**Proposed check-row inventory addition after item 6:** For a `quiet_predicate_evidence` chain, the `corecaptured` row reads `/usr/bin/log show --last 10m`, records the spawn count, and fails if the read cannot be measured. When item 0 or an earlier row failed, it records `remediation: "not_licensed"` and fails above two spawns without actuation. Otherwise, above two spawns it performs at most one Wi-Fi off/on cycle, waits 180 s, re-reads the log, and attempts the single allowlisted fseventsd restart if at least one new spawn appears. `check.json` records the counts, remediation, and available command exit codes.

**Proposed other stale-text updates:**

- `joulewise/arm_retry.py:31` comment: `# Explicit assignments are intentional: new codes and new machine-state causes under an existing code require review.` Extend the `night_refused_not_quiet` description to include more than two `corecaptured` spawns at t0 and persistent spawning after the arm check’s licensed toggle.
- `configs/campaigns/quiet_predicate_evidence_01/README.md:60`: Add: “The arm check reads the last ten minutes of launchd `corecaptured` spawn reports; with prior checks clear, more than two licenses one Wi-Fi toggle and a 180 s recheck. The t0 check is detection only and refuses with `night_refused_not_quiet` above two spawns.”
- `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json`: Add `"t0_corecaptured_spawns_max": 2` and append `cold gate 16 A271 Q2 (2026-09-23)` to `ruling`. This is the blocking scope request in the envelope.

The next arm notice must name the new refusal in plain words. Q2’s latent under-13-minute arm-to-t0 risk remains recorded; no timing change was made.