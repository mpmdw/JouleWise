WRITE_SCOPE: ["docs/process/state_kernel.json","TASK_QUEUE.md","RUN_STATE.md","tests/test_gen_state.py"]
SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Bookkeeping seat, part 2 — kernel fold rulings (gpt-6-astra, medium, genre implementation)

Continue the uncommitted work in this worktree (branch bookkeeping/2026-09-09-kernel-fold; your part-1 report is
/Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/20-seat-kernel-fold-astra-report.md;
the part-1 brief is 18-… beside it). Do not revert part 1. Lead rulings on your two early returns:

RULING F1 (dependency semantics): satisfy the rehearsal event dependency (target POST-WATCHDOG-REHEARSAL-20260909 → state satisfied,
evidence = 21i path + label "rehearsal-20260909 fired and harvested with a finding") AND add a NEW pending hard start dependency on
/tasks/NIGHT-REHEARSAL-01: kind task, target NIGHT-GATE-STUB-CHAIN-01, required "gate cure merged before any further stub or real
night (receipt refused night_probe_error on rehearsal-20260909)", scope start, strength hard, state pending, evidence null. The row
stays BLOCKED on that dependency. The second-stub-night question stays explicitly unresolved in the status_note (needs_ruling; cold gate
or Ed) — do not add a dependency for it.
RULING F2 (scope): tests/test_gen_state.py is now in scope for exactly one change — add NIGHT-GATE-STUB-CHAIN-01 to EXPECTED_IDS in
the position the file's ordering convention requires. Nothing else in that file.
F3: the cure evidence directory is outside this branch by design (it lands with the cure PR #309); keep the kernel evidence pointer to the
branch/commit form you used and add "PR #309" to the NIGHT-GATE-STUB-CHAIN-01 row's evidence label.
F4: T38d time stays "~04:20 PDT" as dictated (the lead's clock), 21i's ~03:40 is the harvest time; state both in T38d if you wish.

Acceptance: `python3 -m unittest tests.test_gen_state tests.test_docs_freshness` to a log with rc (named modules only);
`python3 scripts/gen_state.py --check`; `git diff --check`; no commit. Header < 8192 bytes; genre implementation; body = what changed
for F1/F2/F3/F4 + test tails with rc.
