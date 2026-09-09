WRITE_SCOPE: ["RUN_STATE.md","TASK_QUEUE.md","docs/process/state_kernel.json","tests/test_gen_state.py","docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md","docs/process_traces/2026-09-08-handoff-redo/64-bookkeeping-t38b-astra.md"]

# Bookkeeping seat — T38b closing delta for the 2026-09-08 handoff-redo session (gpt-6-astra, medium; dictated fills — verify EVERY fact against git/PR list/trace files; flag what you cannot verify)

HEAD = main c9e2981c. Since the T38 checkpoint (eacadff7) the following landed on main, all no-ff merges (verify with
`git log --merges --oneline eacadff7..HEAD` and `gh pr view N --json state,mergeCommit` if GitHub is reachable;
otherwise from the merge commit messages):
- f3a5001c + f3a1b344: tests/test_gen_state.py EXPECTED_IDS and count pin follow the T38 kernel (the T38 merge had
  broken the fidelity test; the first fix was committed past a piped test gate — record that as a process note:
  gate on the process rc, never on a pipeline, memory rule re-learned).
- 481df11c: T0-ACID-CLOCK-03 prune — the ±2 h clock-family regression in tests/test_launch_window.py removed after
  the rule-11 same-signature escalation (flaky on Linux CI and under load, always readiness_clock_preflight_refused).
- 23012b52: PR #295 (headless magistrate's trace 21/21a-21g, NIGHT_HANDBACK for rehearsal-20260909, its own
  durable-state section).
- d477e138: PR #298 G2A-CHAIN-ROUTING-01 (chain/preflight/driver take measurement root/head/interpreter from the v2
  plan; conflict in docs/process/NIGHT_HANDBACK.md resolved by keeping both PR #295's installer note and the
  routing handoff paragraph).
- a9a70516: T0-ACID-CLOCK-03 deterministic regression (consult trace 59: the old test froze one anchor while ARM
  sampled live clocks; the 5 ms live-delta / 1 ms skew checks at joulewise/arm_readiness.py ~6512-6515 failed with
  elapsed time; replacement injects fixed readers, asserts authored evidence, stops before ARM; 4/4 runs + under
  load OK; counterfactuals rejected; trace 61-63).
- c9e2981c: PR #299 ICLOUD-BACKUP-PROBE-01 (bounded backup-root discovery + JOULEWISE_BACKUP_ROOTS in the three
  paper producers; XS/AS pins re-recorded with lineage; golden replay byte-identical; trace 40-49, 53-55, 58, 99c).

Do:
A. TASK_QUEUE.md: mark DONE with merge SHAs: G2A-CHAIN-ROUTING-01 (d477e138), ICLOUD-BACKUP-PROBE-01 (c9e2981c);
   add T0-ACID-CLOCK-03 as DONE (481df11c prune + a9a70516 replacement) with the one-line root cause; keep the
   follow-up rows (G2A-PREFLIGHT-ARGV-ASSERT-01, WINDOW-STATUS-GUARD-CENSUS-01, ICLOUD-CUSTODY-LOCATOR-01,
   WATCHDOG-NITS-01, G2A-FIRST-WINDOW-01, D169-STAGE3-01) as they are.
B. docs/process/state_kernel.json: retire the G2A-CHAIN-ROUTING-01 and ICLOUD-BACKUP-PROBE-01 rows the same way
   the T38 seat retired WATCHDOG-INSTALL-01 (look at that diff: `git show eacadff7 -- docs/process/state_kernel.json`
   and `git show eacadff7 -- TASK_QUEUE.md`), and update any dependency that named them; then
   `python3 scripts/gen_state.py` and `python3 scripts/gen_state.py --check` rc 0.
C. tests/test_gen_state.py: update EXPECTED_IDS (remove the two retired IDs) and the count pin (151 → 149) with a
   dated comment; `python3 -m unittest tests.test_gen_state` rc 0 is part of acceptance — run it to a log and
   gate on the process rc, not a pipeline.
D. RUN_STATE.md: one short T38b addendum paragraph under T38 (2026-09-08 ~07:15 PDT): the merges above; all four
   session lanes landed; the interactive magistrate stands down after this delta; the headless magistrate
   (activation 784a764e) arms rehearsal-20260909 in its 01:56-02:15 PDT 9 Sep window after Ed's no-NO; next lane
   = G2A-FIRST-WINDOW-01 per trace 27 after rehearsal acceptance; D169-STAGE3-01 needs a ruling first.
E. 00-DURABLE-STATE.md: APPEND a short dated section "2026-09-08 ~07:15 PDT — handoff-redo session closing" with the
   merge list and the stand-down statement (the twin 71607 and daemon/spare 71666/71682/71687 retirement result is
   recorded by the magistrate in a follow-up commit; say "pending at this write"). Append only; touch nothing above.
F. Write docs/process_traces/2026-09-08-handoff-redo/64-bookkeeping-t38b-astra.md with every verification you ran
   and any fact you could not verify.
Acceptance: gen_state --check rc 0; tests.test_gen_state rc 0; tests.test_docs_freshness rc 0 (each to a log,
rc captured from the process). Never the repository-wide suite; no `git commit`; header < 8192 bytes; genre
implementation verdict keys.
