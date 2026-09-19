# Exhibit D — delta re-audit round 1 (activation 507514d5, record 04, Astra high) finding D5-T1 and the lead's bench-fix account (record 04a)

## Record 04 findings block (verbatim)
```json
  "status": "findings",
  "completion": "complete",
  "summary": "Original findings are fixed within the authorized 0.1-core scope; all three mutations are killed. One new should-fix: the load regression can fail under valid scheduler delays.",
  "workspace": {
    "base_requested": "d066d271",
    "base_mode": "descendant",
    "head_start": "05e90616bad6e22a220d5520170d0a3fb7dc0c4e",
    "head_end": "05e90616bad6e22a220d5520170d0a3fb7dc0c4e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
-
    "findings": [
      {
        "id": "D5-T1",
        "severity": "should_fix",
        "title": "Real-load regression confuses scheduler starvation with incorrect core budgeting",
        "call_site": "tests/test_sample_quiet_predicate_evidence.py:622",
        "counterfactual_input": "Correct duty_periods(.1, 3, .5, burn, clock), with each sleep waking 1.05 seconds late.",
        "observed": "The deterministic scheduling fixture produces 0.03333333333333437 cores, below the test's 0.06-core minimum, despite correct configuration and intentional no-catch-up behavior.",
        "recommendation": "Keep deterministic budget and CLI-to-worker assertions; distinguish scheduler shortfall from implementation failure in the real scheduling check."
      }
    ]
  },
  "verification": [
```

## Record 04a (verbatim)

# Delta re-audit round 1 outcome, bench fix for D5-T1, and close-out (lead, 2026-09-18 22:36–22:40 PDT)

Record 04 (Astra high, read-only, detached worktree at `05e90616`): blocker 0, should_fix 1, nit 0; D1 all nine original findings FIXED, none REGRESSED; D2 no assertion weakened or removed; D3 row keys, shared types and values unchanged under `joulewise.quiet_predicate_evidence.v1`; D4 unknown census stays null, never clean, and `summarize` keeps clean/unknown apart on a two-row fixture; D4b census exit-code semantics match production (`quiet_admission.py:188,268`, `run_night.py:394,2023,2298,2515`); D6 same-signature: none found. Its flags: G1 (the supplied mutation modules carry the `d066d271` source; the auditor applied the original substitutions in memory — the bench counts in 03a differ for that reason), G2 (0.2-core case absent under the cap, as ruled in 03a).

D5-T1 (should_fix): `test_real_load_tracks_point_one_core_and_guards_worker_budget` asserted the achieved fraction within ±0.04 of 0.1 over a real 3 s window, so a scheduler that wakes each sleep ~1 s late (counterfactual: 0.033 cores with correct code) would fail it on a loaded host. Bench fix `498ad1d0` (smaller than a seat contract; rule 9): over-burning above 0.14 cores is always a failure; when the summed `wake_late_s` is within the 0.12 s tolerance budget the two-sided check stands; when starvation is observed the deficit must be explained by the late wakes alone (`fraction ≥ 0.1 − 0.04 − 0.1·late/duration`), with the observed numbers in the assertion message. Budgeting correctness itself stays with the deterministic fake-clock test and the pre-launch config guard that kills the cores mutation.

Executed evidence: module run twice → `OK` (41 tests, ≈5 s each); `mutations.py cores` → `MUTATION cores run 41 failures 4 errors 4`. Pushed as `498ad1d0` on `feat/2026-09-18-quiet-predicate-evidence-harness`.

Still owed before the PR (successor): a fresh delta re-audit covering `498ad1d0` (one changed test) — this activation did not re-audit its own bench fix; the twelve-row ledger (full sharded replay, hosted CI on the branch head, terminal review); the 0.2-core deferral decision; then the evidence memo work of lane 232 stage A on an unarmed, census-clean machine.

Children stopped: all three Astra seats exited before this record (statuses OK); no `sample_quiet_predicate_evidence` or `codex exec` process alive at close-out. Worktrees removed: wt-ref-contract-507514d5, wt-ref-exec-507514d5, wt-ref-delta-507514d5. Kept: wt-harness-232 (branch at `498ad1d0`, clean) and wt-mag-507514d5 (this branch).
