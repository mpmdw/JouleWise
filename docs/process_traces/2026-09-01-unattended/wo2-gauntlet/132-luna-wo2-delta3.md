```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Focused cures and all requested mutants pass their guards, but the null-pgid dead-man branch has a launch race that violates R-7.",
  "workspace": {
    "base_requested": "f07c85d51b386c9c00fb41cb529c8f113c8fe28e",
    "base_mode": "exact",
    "head_start": "f07c85d51b386c9c00fb41cb529c8f113c8fe28e",
    "head_end": "f07c85d51b386c9c00fb41cb529c8f113c8fe28e",
    "upstream_end": "f07c85d51b386c9c00fb41cb529c8f113c8fe28e",
    "branch": "feat/2026-09-01-night-driver"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-ROUND",
    "findings": [
      {
        "id": "D1",
        "severity": "blocker",
        "title": "Null-pgid dead-man branch races real launch",
        "where": "scripts/run_night.py:349-420,1279-1314",
        "evidence": "O_EXCL creates chain.started empty before Popen; dead-man can read it before or during Popen, write chain.exited launch_failed, and start the courier while the real chain is alive. R-3/R-7 do not tolerate this."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-review-delta-round/worktree-tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 88 tests in 0.957s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 88 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "(cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-review-delta-round/baseline && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-review-delta-round/baseline-tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate)",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 88 tests in 0.987s", "FAILED (failures=5)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "for name in launch null sleep verdict excl term boundary inverse push deadline; do (cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-review-delta-round/mutant-$name && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-review-delta-round/mutant-$name-tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate); done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["launch rc=1", "null rc=1", "sleep rc=1", "verdict rc=1", "excl rc=1", "term rc=1", "boundary rc=1", "inverse rc=1", "push rc=1", "deadline rc=1"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "launch rc=1[\\s\\S]*deadline rc=1"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show --format= --unified=12 f07c85d5 -- scripts/run_night.py && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## feat/2026-09-01-night-driver...origin/feat/2026-09-01-night-driver"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## feat/2026-09-01-night-driver"
      }
    }
  ],
  "flags": [
    {
      "id": "D1",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Dead-man can misclassify an empty in-progress chain.started marker as a completed launch failure.",
      "needs": "Add launch/dead-man synchronization or an unambiguous launch-state protocol, then rerun this delta audit."
    }
  ]
}
```

## Findings

Verdict: FIX-ROUND.

Cure results:

| Item | Pre-fix execution | Post-fix |
|---|---|---|
| F3 Popen failure | `AssertionError: chain launch failure escaped instead of becoming a refusal: chain executable missing` | Passes refusal validation, null pid/pgid, `launch_failed`, courier, two pushes, rc 3 |
| F3 empty/null markers | `AssertionError: 3 != 0` for both tests | Pass; courier runs and `killpg` is not called |
| F1 equality | 224 already contained `>=`; named test passed. `>` and inverse `<=` mutants fail `AssertionError: 0 != 3` | Dynamic `_next_deadman_epoch` and `window_max_s - 1` twin pass |
| F4 wait | `AssertionError: 1 not less than or equal to 0.3` | Bounded formula and rechecks pass; `stop_epoch_s=None` behavior remains unchanged |

§2 checks: descriptor closure is exactly once through `finally` at `373-389`, including `_write_all` failure. Reporting order is result, durable publish, courier, courier record, durable publish (`1208`, `914-930`). Valid `pgid` plus existing `chain.exited` bypasses the liveness block and reaches courier without `killpg` (`1281`, `1338`).

The blocker is the timing race: `_claim_chain_start` creates an empty marker before `Popen`. Dead-man can observe that marker at `1281-1288`, write `chain.exited`, and launch the courier while `Popen` is still starting. If `Popen` then succeeds, the real chain is alive during courier execution; if it fails, both paths can race to create `chain.exited`.

| abort_reason | termination_proven | verdict / base rc |
|---|---:|---|
| `night_chain_launch_failed` | true | `REFUSED / 3` |
| `night_chain_launch_failed` | false | `REFUSED / 3` |
| other census abort | true | `ABORTED / 4` |
| other abort | false | `REFUSED / 3` |

An unsent courier overrides the process rc to 6.

Mutants: all died. Launch catch → `test_chain_spawn_failure_records_refusal_and_finishes_reporting`; null flag → both null/empty dead-man tests; unconditional sleep → `test_courier_wait_caps_sleep_at_the_dead_man_epoch`; dropped refusal clause → launch-failure test; removed result O_EXCL → `test_exclusive_record_writers_and_markers_are_fsynced`; termination always true → `test_unproven_chain_termination_records_unkilled_and_spawns_no_courier`; both equality mutants → boundary test; dropped second push → `test_courier_spawn_failure_records_outcome_and_second_publish`; deadline 600 → `test_courier_deadline_is_derived_from_the_measured_artifact`.

Commands used: the V1 suite, the V2 224 baseline copy, and the V3 mutant loop above. No real chain, courier, launchd, or push ran. Worktree status is clean.

## Residual risk

`_next_deadman_epoch` protects the normal run-path calculation for `t0 >= 07:00` by selecting the next civil day, but `dead_man()` itself has no explicit pre-`t0` guard. That adjacent behavior predates this delta and was not counted as the blocker.