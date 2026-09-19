# Record 62a — lead triage of the post-merge cross-unit review 62 (main `6032b9e9`, four merges), 2026-09-19 14:0x PDT

Verdict received: no merged change is unsound; Q1 (fixture vs semantic check) and Q2 (manifest consumers) clean.

| # | Severity | Disposition |
|---|---|---|
| F2 | should_fix | Every hosted CI runner is ubuntu; after PR #363 the load worker's join ladder / SIGTERM escalation path and the real `collect` path have no automated coverage anywhere (4 of 46 tests skip on Linux). ACCEPT as queue data: fold into kernel 249 (CI-SHARD-RUNNER-FILE-BASED-01) as a second deliverable — a macOS CI job or a Linux-neutral fake-probe collect smoke — and state the coverage loss in the kernel row. The bench replays on the M3 (records 21/34/42/60) are the current coverage. |
| F3 | should_fix | Kernel row 232 / TASK_QUEUE A232 say the harness is unmerged; row 244 still asks the byte-pin question. ALREADY CURED on the bookkeeping branch (commit `571e0d52`: 232 note, 244 retired, 248/249 registered) — the review ran on main, which the bookkeeping branch reaches with the next records-only merge / close-out push. |
| N1 | nit | The darwin guard on the moved ladder test also swallows the platform-independent "Process.start() must close both Pipe ends" (N3) block. ACCEPT: move that block back into the cross-platform fake-clock test — added to brief 63 (Stage A fix round 1 touches that module). |
| N2 | nit | Neither new module (`test_generator_head_pin_relation`, and the harness module) is in `scripts/test_timings.json`, so the quick tier's weight map treats them as unmeasured. Queue data with 249 (a timings refresh). |
| N3 | nit | Row 244 named `d117_contrast_v5` as a byte-pin holder; it never had one (the judge corrected this in ruling 10 of packet 09). Row is retired; the retirement note in the kernel already carries the correction. |

Row 11's post-merge cross-unit review for PRs #360, #361, #362, #363 is thereby done in this activation, not deferred.
