# PR #800 gate 6 repair — Sol round 7, 2026-11-16

Explicit user direction selects this AGENT repair ahead of the ordinary queue. Mission M0: no active stop card; both target worktrees were clean at 585bfa8cd / f65960678. Read the refusal and full cold report, RL-172(c)(g)(i) and RL-173 from origin/audit/2026-11-10-fable (746e44a16), design 15.13–15.16, prior handoffs, orchestration and relevant implementations. No phase exit-checklist row exists. The kernel latest-report pointer and generated restart view now name this report.

## Dispositions

Design 15.17 and the PR tables own the full disposition map. F1–F3/F5 are fixed in this branch; F4 is inherited from #799 at 419e184c0. Failed prior command/restore/feed-stop evidence now produces a bad terminal status. A controller-state standing lease survives watchdog cleanup and PID changes; deliberate releases and launch intents record handoffs. An unknown census retains an owned fence while known handoffs remain released. Queue kit locators are contained before staging writes. No policy ruling, frozen runner, watchdog, scientific constant or real custody file changed.

## Reproduction and verification

Artifacts live in /Volumes/JW-EXT/scratch/sol-ctl-r7/.
- regression800-before.log: seven expected assertion failures across F1/F2/F3/F5 cases (including both path sentinels). The clean-prior and known-handoff controls passed before repair.
- regression800-after-final.log: all eight new controller tests pass.
- regression799-before.log / desk799-after.log: three expected desk failures before repair, 76 desk tests pass afterward.
- The first broad 421-test run caught three integration failures: an incomplete old clean-prior fixture and two foreign-fence interlock cases. The fixture now carries actual clean terminal/restore/feed proof; a foreign fence still uses the existing wait/restore lane. Focused deadline and foreign-run controls pass after correction. Logs are preserved, not relabelled green.

Final stack verification artifacts:
- arm-stub-final.log: six isolated arm-child tests passed.
- checks800-final.log: 48 host-command/guard/docs checks passed.
- bookkeeping800.log: 75 state/docs tests passed.
- synthetic-final.log: all 15 named scenarios passed with the actual exported frozen runners; no missing-pin fallback.
- cadence800-final.log: the complete safe cadence selection on the rebased stack; its terminal result and code-CI outcome are carried into the verified PR body and final handoff. This report does not replace those exact logs with a historical pass.

 The local safe harness stubs PID observations and rejects nonzero signals plus Popen signalling. Twelve launcher-fixture tests that start/terminate real processes stay excluded. Six isolated arm-child tests use a PID stub inside the child, fake launchctl and a harmless sleep that exits naturally. The unrestricted canonical suite is left to off-host CI because local signalling is forbidden by the user. No hardware validation is claimed.

## Stack and authority

Rebased all eleven #800 commits linearly on #799 419e184c0. Only two documentation header conflicts occurred; both branches' notes were preserved. rebase-range-diff.txt shows unchanged implementation patches. Force push uses an explicit lease at the reviewed remote head f65960678. New commits end with the requested Sol coauthor trailer. PR bodies are files under the scratch directory, edited with gh pr edit --body-file and re-read exactly.

No MBP contact, real custody access, process signalling, merge or delegated seats. PROJECT_STATUS is unchanged because scientific/advisor-visible state did not change. Checks protect operational admission; no new scientific number was produced. The report adds no new gate or process rule.

## Open research-lead questions and next step

Do not decide: disposed-ancestor first-of-group semantics (count executed ancestor vs resolve rerun chains; prior recommendation preserved); whether a disposition can release unknown L002 evidence; N12 reference-hash binding; Q1 records for hand-armed v1.1 spans and typed-marker switch-over; non-counting desk-disagreement clearance. External offload descendant/custody assertions and future campaign-scope authenticated history stay with their named owners.

Next exact step: the lead obtains the outstanding rulings and fresh cold admission at the pushed heads, then satisfies the remaining owner gate-ledger rows and watched native span before installation. No installation or merge is authorized here.
