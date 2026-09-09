WRITE_SCOPE: ["docs/process/state_kernel.json","TASK_QUEUE.md","RUN_STATE.md"]
SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Bookkeeping seat — kernel fold for the rehearsal harvest (gpt-6-astra, medium, genre implementation; dictated fills)

Branch bookkeeping/2026-09-09-kernel-fold (your worktree) at the PR #308 head. Facts are dictated below; verify EACH against the named
primary artifact in THIS worktree before writing it, and flag any discrepancy in your report instead of resolving it yourself.
Primary artifacts: docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md (21i),
21h-rehearsal-20260909-arm-record.md, 21b-rehearsal-20260909-bench/night-harvest/* (night-result.json, night-receipt.json,
night-courier.sent, uninstall-output.txt, removal-output.txt), docs/process/NIGHT_HANDBACK.md §Executed.

Edits (docs/process/state_kernel.json is the ONE home; TASK_QUEUE.md and RUN_STATE.md are regenerated/updated by the repository's
generator — find it in THIS worktree via tests/test_gen_state.py and the existing kernel "pointer" conventions; never hand-edit a
generated region):
1. /tasks/NIGHT-REHEARSAL-01: dependencies[0] (event POST-WATCHDOG-REHEARSAL-20260909) → state satisfied, evidence = 21i path.
   status_note → the executed facts: fired 2026-09-09 02:56 PDT from activation 784a764e's arm (21h); result REHEARSAL_ONLY, chain
   exit 0, results branch night-results/20260909 @ a84e0f7f, courier email id 1a08599a4ff4d005; receipt REFUSED night_probe_error
   (gate read chain.zsh for the stub class) = FINDING, cure lane NIGHT-GATE-STUB-CHAIN-01; agents uninstalled, stub checkout + plan
   root removed (21i); acceptance items 2 and 6 met (6 conditional on the cure landing), item 3 PARTIAL (send recorded, inbox
   unverified), items 1, 4, 5 OPEN — item 5 (agents installed the morning before, 07:00 dead-man observed standing down) CANNOT be
   met by this night, so the row stays BLOCKED/PARTIAL, not DONE; whether a second stub night is required after the cure is a
   cold-gate/Ed ruling (record as needs_ruling in the note, do not decide).
2. Register a new task NIGHT-GATE-STUB-CHAIN-01 (P1 Phase Gate, [AGENT], status IN PROGRESS): "Night gate skips the chain/sidecar read
   for REHEARSAL_STUB plans (driver substitutes the built-in stub); C5 records chain_sha256 null + chain_stub; driver logs refusal
   reason on the gate verdict line" — authority 21i §The finding; evidence: branch fix/2026-09-09-night-gate-stub-chain at bb7090e2
   (seat report docs/process_traces/2026-09-09-rehearsal-harvest/02-seat-night-gate-stub-chain-astra-report.md, fix round 17-…);
   acceptance: the defect-shaped tests in tests/test_night_gate.py and tests/test_run_night.py pass, PR merged. Mirror the shape of
   an existing recently-registered row (e.g. WINDOW-STATUS-GUARD-CENSUS-01 or CLONE-READINESS-01) exactly.
3. CLONE-READINESS-01 note: add that the rehearsal clone is cut only after NIGHT-GATE-STUB-CHAIN-01 merges (else a stub night repeats the
   signature). Do not change its status.
4. RUN_STATE.md: add a short T38d paragraph (2026-09-09 ~04:20 PDT, headless activation 628c2eed) above T38c mirroring the current
   checkpoint style: rehearsal fired + finding + cure branch + nothing armed + next = cure merge → PR #308 merge → CLONE-READINESS-01
   rehearsal clone → G2-a inputs; pointer to 21i. Update the "Current checkpoint" line accordingly. Keep every prior checkpoint verbatim.
Acceptance: `python3 -m unittest tests.test_gen_state tests.test_docs_freshness` to a log with rc (named modules only); the
generator's own check mode if it has one; `git diff --check`; no commit. Header < 8192 bytes; genre implementation; body = per-edit
what/where + every discrepancy flagged + test tails with rc.
