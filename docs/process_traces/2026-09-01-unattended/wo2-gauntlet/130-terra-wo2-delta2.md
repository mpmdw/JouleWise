```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-ROUND: two kill-check gaps, an equality mutant survives, and two unattended failure paths violate the courier/dead-man contract.",
  "workspace": {
    "base_requested": "8510e6dc",
    "base_mode": "exact",
    "head_start": "cdf588955cffa9c9d8a48ee95547d79dc0608d9c",
    "head_end": "cdf588955cffa9c9d8a48ee95547d79dc0608d9c",
    "upstream_end": "cdf588955cffa9c9d8a48ee95547d79dc0608d9c",
    "branch": "feat/2026-09-01-night-driver"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FIX-ROUND",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Dead-man equality mutation survives",
        "where": "scripts/run_night.py:985",
        "evidence": "Changing the inverse strict guard from >= to > leaves all 84 tests green."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Kill check does not prove all claimed regressions",
        "where": "tests/test_gen_g2_phase_d.py:59; tests/test_run_night.py:666,680",
        "evidence": "The full-reconstruction test passes on 8510e6dc; the latter two error only because common setup names are absent, while their asserted properties already hold in the old source."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "Chain-launch exception loses the night",
        "where": "scripts/run_night.py:385",
        "evidence": "An OSError from chain Popen occurs after the exclusive chain.started claim and before durable publication or courier; dead-man later treats the incomplete marker as a live chain and also suppresses courier."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "Courier wait can cross the dead-man epoch",
        "where": "scripts/run_night.py:576-584",
        "evidence": "At dead-man minus less than one second, the unconditional one-second sleep crosses the epoch; the live lock can then make dead-man refuse instead of sending."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/post-five/cache python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 84 tests in 0.932s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 84 tests in .*s.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/audit-nine/prefix && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/audit-nine/cache python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 84 tests in 0.056s", "FAILED (failures=2, errors=38)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/post-five/prefix && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/post-five/cache python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 84 tests in 1.084s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 84 tests in .*s.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F5",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Without the mandated TMPDIR, one installer-render assertion compares /var/... with zsh's canonical /private/var/... and fails; the prescribed-TMPDIR worktree run is green.",
      "needs": "Normalize the test expectation if ambient-TMPDIR portability is required."
    }
  ]
}
```

## Findings

- **F1 blocker:** the strict dead-man boundary lacks an equality regression.
- **F2 blocker:** the seat’s claimed pre-fix kill evidence is incomplete.
- **F3 blocker:** chain `Popen` failure can leave only a zero-byte `chain.started`, with neither courier nor durable result.
- **F4 should-fix:** bound the one-second courier polling sleep by remaining time to the dead-man epoch.

## Kill check

`P` = pass; `E/F` = setup error, with old-body disposition. The seat table names 23 tests; row 5 is its separately added B-A installer probe, yielding the requested 24.

| Test | Pre-fix | Post-fix |
|---|---|---|
| absolute script help | E/F: `_resolve_courier_bin` absent; body fails old import order | P |
| missing courier refusal | E/F; body fails | P |
| courier spawn + second push | E/F; body fails | P |
| installer render/path/logs | E/F; body fails | P |
| installer no courier | E/F; body fails | P |
| write-once rerun | E/F; body fails | P |
| driver refusal schema | E/F; body fails | P |
| unproven termination | E/F; body fails | P |
| dead-man reaps gone pgid | E/F; body fails | P |
| dead-man live pgid | E/F; body fails (`killpg` absent) | P |
| malformed plans | E/F; body fails | P |
| rehearsal census observe-only | E/F; body fails | P |
| derived courier deadline | E/F; body fails | P |
| four courier attempts/backoffs | E/F; body fails | P |
| overrun excludes backoffs | E/F; body fails | P |
| run-path handoff | E/F; body fails | P |
| full chain reconstruction | **P — direct body execution** | P |
| exit before durable publish | E/**P body** — old order already correct | P |
| live 30-second census | E/**P body** — old code already has it | P |
| clone/push argv twice | E/F; old clone has `--branch main` | P |
| installer active-chain guard | E/F; body fails | P |
| code-map prefix reject | E/F; body fails | P |
| local night date | E/F; old code uses UTC | P |
| exclusive writers/fsync | E/F; body fails | P |

## Cure match

| Item | Result |
|---|---|
| B-A | MATCH — `run_night.py:23-28,531-543,675-679`; installer `47-53`; plist `18-24`; prompt `7-9`. |
| B-B | MATCH — exclusive writer `114-123`, claim `343-351`, rerun `816-835`. |
| B-C | MATCH — exact validator `172-204`; driver writer validates at `218-221`. |
| B-D | MATCH — proven termination `314-340`; dead-man pgid reap `1220-1244`. |
| B-E | MATCH — guarded parsing/fallback `907-949`; courier reporting follows. |
| B-F | MATCH — rehearsal census is observe-only at `1033-1062,1118-1160`. |
| S-a | MATCH — 300-second derived constant `44-46`; artifact test passes. |
| S-b | **MISMATCH** — retry/lock parts match `624-730`, but wait sleep crosses dead-man (`576-584`). |
| S-c | MATCH in code/test (`test_gen_g2_phase_d.py:59-75`), but not a pre-fix kill. |
| S-d | MATCH — session `385-392`, exit before publish `438-440,1173`, interval `43`. |
| S-e | MATCH — active-chain exit 3 and rollback `119-145`. |
| S-f | MATCH — local date `467-469`, code guard `70-77`, durable-before-courier `1259`, fsync path. |

## Delta defects

| Check | Result |
|---|---|
| Exception skips courier + durable record | FOUND — `run_night.py:385`, chain `Popen` OSError/EMFILE. |
| Crash leaves permanent courier refusal | NOT FOUND — stale/dead-pid locks are unlinked at `624-636`; freshness is bounded. |
| Popen pipe can fill | NOT FOUND — chain uses file handles; courier inherits launchd streams. |
| Sleep crosses dead-man | FOUND — `run_night.py:583`, one-second poll sleep. |
| Unregistered refusal reason written | NOT FOUND — `_write_driver_refusal` validates every driver document. |

## Mutants

| Mutant | Result |
|---|---|
| O_EXCL removed from shared result writer | `test_exclusive_record_writers_and_markers_are_fsynced` fails. |
| Unproven termination returns true | `test_unproven_chain_termination_records_unkilled_and_spawns_no_courier` errors. |
| Strict `<` changed to `<=` | **SURVIVED**. |
| Second durable push removed | `test_courier_spawn_failure_records_outcome_and_second_publish` fails. |
| Deadline set to 600 | `test_courier_deadline_is_derived_from_the_measured_artifact` fails. |

## Commands

```sh
git archive 8510e6dc | tar -x -C "$A/audit-nine/prefix"
TMPDIR="$A/post-five/cache" python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate
(cd "$A/audit-nine/prefix" && TMPDIR="$A/audit-nine/cache" python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate)
for n in mut-a mut-b mut-c mut-d mut-e; do (cd "$A/$n/prefix" && TMPDIR="$A/$n/cache" python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate); done
```

## Residual risk

No real chain, courier, `launchctl`, or push was started. The workspace remains clean and unmodified.