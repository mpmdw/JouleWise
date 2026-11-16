# PR #799 gate 6 repair — Sol round 7, 2026-11-16

Explicit user priority selects this AGENT repair ahead of the generated lane head. Mission M0: no active stop card; both target worktrees clean at intake. Source authority: RL-172(c)(g)(i), RL-173 at origin/audit/2026-11-10-fable (746e44a16), design 15.13–15.16 on the controller branch, and the prior round handoffs. No phase exit-checklist row exists for this repair.

Cold refusal: /Volumes/JW-EXT/scratch/sol-gate6-800-799/FINAL-MESSAGE.md; full report: /Volumes/JW-EXT/jw-wt/mythos-repo/docs/run_reports/2026-11-16-cold-review-pr799-pr800.md.

F4 reproduced: a successful verdict with its declared summary missing was published and read as final, and disappeared from signed replay history. Publication now requires and hashes the declared summary before signing. Reading refuses an absent or unreadable declared summary. Error verdicts declaring no summary remain valid. No draw policy changed.

Verification (artifacts: /Volumes/JW-EXT/scratch/sol-ctl-r7/):
- regression799-before.log: three expected failures, one valid error-verdict control passed.
- desk799-after.log: all 76 desk tests passed, including missing summary, read failure, signed history refusal, and error-verdict roundtrip.
- cadence799.log: 246 safe cadence tests passed. The 12 real-signalling launcher fixtures were excluded; the harness stubs PID observations and rejects nonzero signals and Popen signalling methods.
- checks799.log: 48 host-command, guard and docs checks passed. State projections and diff whitespace checked before commit.

The unrestricted canonical suite is left to off-host CI: local discovery includes process-signalling fixtures forbidden by the user. No hardware evidence is claimed. No scientific number or frozen capture path changes. No MBP contact, custody access, merge, external messages or delegated seats. PROJECT_STATUS is unchanged because advisor-visible scientific state did not change.

Next: commit/push #799, rebase #800 linearly, complete F1–F3/F5 controller regressions, verify code CI at both heads and update PR bodies from files. Fresh admission, native span and research-lead rulings remain separate gates. Rerun first-of-group, reference-hash binding, unknown L002 recovery, prior-span Q1/marker switch-over and non-counting desk clearance remain open, without a new ruling.
