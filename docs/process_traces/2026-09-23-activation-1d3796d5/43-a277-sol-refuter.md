```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Two fail-open successor paths found; 18 mutants killed, with nine full mutant runs unfinished at the timebox.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "descendant",
    "head_start": "408b96c301f0d0bf7b0852513343ca4f198f77e3",
    "head_end": "408b96c301f0d0bf7b0852513343ca4f198f77e3",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 2,
      "should_fix": 3,
      "nit": 0
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "An absolute path to real launchctl is classified as rehearsal, so publication skips the successor claim."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "summary": "A colon in a valid predecessor plan ID makes the missing-custody guard lose its identity and admit further candidates."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "summary": "A readable but malformed receipt with no condition rows licenses watchdog release and a successor."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "summary": "Claim creation fsyncs file contents but does not sync the new directory entry before publication."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "summary": "Focused regressions miss independent claim-digest and claim-creation collision failures."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_zero_capture_facts tests.test_arm_retry tests.test_evidence_night tests.test_magistrate_watchdog > /tmp/a277-refuter-baseline.log 2>&1",
      "cwd": "/tmp/a277-refuter-head",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 310 tests in 1253.672s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 310 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a277_refuter_full_pending.py > /tmp/a277-full-pending-summary.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["publish_no_reread KILLED", "Nine other full mutant runs interrupted at timebox"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "all pending mutants reported"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a277_refuter_race.py",
      "cwd": "/tmp/a277-refuter-head",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["10/10 trials: exactly one claimant won"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "exactly_one.*true"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check 313efcca..408b96c3",
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
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Nine mutants passed focused tests, but their four-module runs were interrupted to honor the 50-minute timebox; they are not claimed as full-suite survivors.",
      "needs": "Replay the nine named mutants in temporary copies if full mutation survival is required."
    }
  ]
}
```

## Findings

**F1 — Blocker: real launchctl can take the rehearsal branch.** [Check](/Users/edr/code/wt-1d3796d5-ref-a277/joulewise/evidence_night.py:1209) and [publish_install](/Users/edr/code/wt-1d3796d5-ref-a277/joulewise/evidence_night.py:1574) equate “real” with the literal string `launchctl`; [claim creation](/Users/edr/code/wt-1d3796d5-ref-a277/joulewise/evidence_night.py:1655) is skipped otherwise. `/bin/launchctl` resolves to the real executable and is accepted by the installer, yet an executed fixture check recorded `fake_launchctl=true`, `rehearsal_ready=true`, and a passing successor row. Two different `publish_install` contenders then both reached the mocked installer probe with **no claim created**. No real launchctl command was run.

**F2 — Blocker: release-key parsing loses a valid identity.** [The `split(":", 2)` guard](/Users/edr/code/wt-1d3796d5-ref-a277/joulewise/evidence_night.py:830) assumes neither the plan ID nor custody path contains a colon; [plan parsing](/Users/edr/code/wt-1d3796d5-ref-a277/joulewise/night_gate.py:424) imposes no such restriction. In a full `evidence_night.check` fixture, `pre:decessor` was recognized before its custody was removed. With the release key still recorded, removal changed the successor row to **pass with no predecessor**. The ordinary `predecessor` control failed with “released predecessor custody is missing.” Two distinct later candidates also passed the isolated production successor row with zero claims.

**F3 — Should fix: malformed receipt accepted.** [The terminal predicate](/Users/edr/code/wt-1d3796d5-ref-a277/joulewise/arm_retry.py:221) accepts an empty `conditions` list, although the [receipt validator](/Users/edr/code/wt-1d3796d5-ref-a277/joulewise/night_gate.py:1932) requires C1–C5. Replacing the fixture receipt’s rows with `[]` produced `watchdog_release=true`, `successor=pass`, and `rehearsal_ready=true`. This pre-existing release permissiveness now grants the new successor route.

**F4 — Should fix: claim directory durability is unestablished.** [Claim creation](/Users/edr/code/wt-1d3796d5-ref-a277/joulewise/evidence_night.py:901) fsyncs the temporary regular file, links it at the final name, and proceeds toward publication without syncing the claims directory. An instrumented run recorded `fsync_targets=["regular_file"]`. The link is atomic against competing processes, but the record’s persistence across power loss is not established before the plan is published. A power-loss outcome was not simulated.

**F5 — Should fix: claim regressions are insufficiently discriminating.** The focused [claim tests](/Users/edr/code/wt-1d3796d5-ref-a277/tests/test_evidence_night.py:2664) passed when final creation was changed to a plain write, and the focused [license tests](/Users/edr/code/wt-1d3796d5-ref-a277/tests/test_arm_retry.py:480) passed when the existing-claim digest comparison was removed. With plain writes, a forced two-candidate race let both reach the installer probe in 3/3 trials. Removing the existing-claim identity check likewise let both through in 3/3 staggered trials. On HEAD, the second candidate was refused. These mutants’ **full-suite survival remains unverified**.

## Mutants

Each mutant changed one temporary copy. `KILLED` names the failing test from the four-module fail-fast run. `SURVIVED focused` means its named focused test passed; the full run was interrupted.

| Mutant | Result | Killing test |
|---|---|---|
| Drop chain-start fact | KILLED | `test_calibration_shared_ledger_does_not_change_clean_facts` |
| Drop reservation count | KILLED | `test_nested_marker_and_symlinked_directory_are_present` |
| Drop capture-entry count | KILLED | `test_index_and_capture_entries` |
| Drop envelope index/count | KILLED | `test_index_and_capture_entries` |
| Count symlink as absent | KILLED | `test_index_and_capture_entries` |
| Drop scan-complete comparison | KILLED | `test_each_disk_fact_and_claim_refuses` |
| Drop terminal-refusal comparison | KILLED | `test_door_disjointness_and_same_candidate_retry` |
| Drop composed `facts.clean` comparison | KILLED | `test_each_disk_fact_and_claim_refuses` |
| Drop `courier.sent` license comparison | KILLED | `test_bare_c5_needs_composed_disk_facts_and_delivery` |
| Drop 60 s spacing comparison | KILLED | `test_bare_c5_needs_composed_disk_facts_and_delivery` |
| Drop predecessor-is-successor comparison | KILLED | `test_each_disk_fact_and_claim_refuses` |
| Drop existing-claim ID comparison | KILLED | `test_a277_existing_claim_and_removed_root_still_bound_count` |
| Drop completion-boundary comparison | KILLED | `test_a277_calibration_capture_entry_blocks` |
| Drop release-observed comparison | KILLED | `test_a277_calibration_capture_entry_blocks` |
| Drop predecessor-count comparison | KILLED | `test_a277_multiple_released_predecessors_refused` |
| Drop missing-custody guard | KILLED | `test_a277_missing_custody_root_refused_while_release_is_recorded` |
| Create claim during rehearsal | KILLED | `test_a277_rehearsal_publication_does_not_create_successor_claim` |
| Skip publish-time successor reread | KILLED | `test_a277_publish_rereads_facts_before_claim` |
| Force scanner courier fact true | SURVIVED focused | — |
| Drop delivery plan-ID comparison | SURVIVED focused | — |
| Drop existing-claim digest comparison | SURVIVED focused | — |
| Create final claim with plain write | SURVIVED focused | — |
| Accept another candidate at claim creation | SURVIVED focused | — |
| Drop delivery message-ID comparison | SURVIVED focused | — |
| Drop candidate/predecessor ID comparison | SURVIVED focused | — |
| Drop candidate/predecessor SHA comparison | SURVIVED focused | — |
| Drop active claim check after root removal | SURVIVED focused | — |

The first 18 have completed four-module killing runs. The other nine have focused passing runs and **no completed full-suite verdict**.

## Race probe

| Code path | Trials | Result |
|---|---:|---|
| HEAD, simultaneous claim links | 10 | Exactly one candidate won every time. |
| HEAD, second creator enters after first claim exists | 3 | First retained the claim; second was refused every time. |
| Plain-write counterfactual | 3 | Both candidates reached the installer probe every time. |
| Removed existing-claim comparison counterfactual | 3 | Both candidates reached the installer probe every time. |
| HEAD with `/bin/launchctl` classified as rehearsal | 1 | Both reached the mocked probe; no claim existed. |

## Watchdog parity

`Release` means `_delivered_zero_capture_refusal` returned true. The three added shapes are marked †.

| Fixture | `313efcca` | HEAD |
|---|---|---|
| Clean calibration | Release | Release |
| Clean evidence | Release | Release |
| Nested custody reservation | Refuse | Refuse |
| Runs-root reservation | Refuse | Refuse |
| Calibration capture | Refuse | Refuse |
| Evidence capture | Refuse | Refuse |
| Broken capture symlink | Refuse | Refuse |
| Nonempty envelope index | Refuse | Refuse |
| Empty envelope index | Release | Release |
| `chain.started` | Refuse | Refuse |
| Missing chain | Refuse | Refuse |
| Ambiguous payload | Refuse | Refuse |
| Unrelated custody symlink | Release | Refuse |
| Torn unrelated ledger line | Release | Release |
| Chain-path symlink † | Release | Refuse |
| Receipt symlink † | Release | Refuse |
| Stray regular custody file † | Release | Release |

Every divergence is stricter symlink handling. No other release-predicate drift appeared in these 17 shapes.

## Delta same-signature statement

| Round-1 class | Same class found? | Evidence |
|---|---|---|
| Fact matched to wrong identity | **Yes** | F2: colon-delimited release key loses the predecessor identity. |
| Release-predicate drift | **No** | Only the recorded symlink tightening appeared in parity. |
| Non-atomic durable state | **Yes** | F4: the final claim directory entry is not synced. |
| Rehearsal side effect | **Yes, inverse direction** | F1: a real binary path takes the rehearsal branch and omits the claim. |

## Residual risk

Real launchctl operation and power-loss recovery were excluded by the hard fence. Nine mutants have focused outcomes only because their long four-module replays were stopped at the timebox. The repository worktree remains clean.