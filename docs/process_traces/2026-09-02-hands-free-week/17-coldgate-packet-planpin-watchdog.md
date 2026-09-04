# Cold-gate packet: the plan-pin landing and the built relaunch watchdog (2026-09-03)

Assembled by the magistrate. Objects: branch `feat/2026-09-03-night-plan-pin` at `90698150` (worktree `/Users/edr/code/JouleWise-wt-planpin`) and branch `feat/2026-09-03-magistrate-watchdog` at `b93f5ffb` (worktree `/Users/edr/code/JouleWise-wt-watchdog-build`), both read-only. Atomic questions only.

## 1. Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## 2. Convening triggers (charter §3)
- Item 2: the plan-pin landing reinterprets rulings R-6 and R-7, and the watchdog reinterprets R-9 (exhibit 11a); the proposed addenda are exhibit 17j.
- Item 3: installing a standing launchd job that starts Claude sessions, and the first stand-down that kills the magistrate's own session tree, are irreversible actions.
- Item 4: the fence predicate, stand-down timings and census rule are process rules (adopted provisionally in file 15 by the prior gate; now built).

## 3. Questions (REFUSE any you cannot decide from the exhibits and the code)
**Q1.** Plan pin: does the v2 plan (`measurement_root`, `measurement_head`) with the stale check on the measurement checkout satisfy the intent of R-6 and R-7 as written (quote the clauses), and is the installer's raw-plan validation now exactly the gate's acceptance? Execute: a v2 plan with a trailing newline in `measurement_head`, a relative `measurement_root`, a v1 plan, and a valid plan through both `NightPlan.from_mapping` and `scripts/install_night_agent.sh --render-only`; paste exit codes.
**Q2.** Watchdog build: does `scripts/magistrate_watchdog.py` at `63d12162` implement every row of the adopted rulings (exhibit 15, rows 1–11) as its clause map claims (exhibit 17f addendum, 17h)? Execute the execution refuter's probes (exhibit 17i §Charge results and the three mutation probes) and the fix-round regressions; paste results.
**Q3.** Install handoff (exhibit 15 row 10): the sequence "email install notice → install → at the first stand-down request, kill the magistrate's own session tree including the Terminal-hosted interactive twin and the `claude daemon` + spares it parents". Is any step irreversible without a recovery path, and does D-171 (exhibit 11b) authorize it as written?
**Q4.** Ordering: merge plan-pin → install watchdog → first stand-down → arm G2-a under a v2 plan pinned to the measurement checkout. Is this consistent with exhibit 14 Q6 (the pin change must precede the first real window's arming) and with the retired-v1 rule for the two existing custody roots?
**Q5.** The relaunch prompt `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`: name any way a relaunched session could violate R-9, D-127 or the lieutenant-forbidden list (arming a night, git operations in the canonical checkout while a plan is armed, ratifying a process rule).
**Q6.** Are the three proposed addenda in exhibit 17j installable as written? Give exact amended text if not.
**Q7.** Packet hygiene (charter §6): complete and neutral? Note: the watchdog contract-lens refutation is exhibit 17k.

## 4. What the seats must not do
Do not read RUN_STATE.md, council_log.md, run reports, CLAUDE.local.md, session memory, or scratchpads. Do not start any `claude` or `codex` session (`--help` reads only). Do not write under any checkout, `~/Library/LaunchAgents` or `~/night-custody`. Use a scratch directory of your own. Do not end mid-flight.

## 5. Exhibit manifest

```
9f0e6be1beec32b0eb525886181e3704bf3d57343ac046bf84c8ec4322228611  11a-exhibit-ruling-unattended-stage1.md
cae85fe18bc96d7fbbdda1b2ea170879ea2c9096523eaab6ebff7cb013de520a  11b-exhibit-D-171-verbatim.md
7a5ece363feb4c82458e5c8ce71c8ea2044a67ff4f57c83aa901b412d4316895  14-coldgate-fable-ruling-packet-11.md
eb919b87bf7639e73a719ceb93993a0fa5697dd4046a6e986c65d4d5aed86d9b  15-watchdog-gate-synthesis.md
13d249b4d0d67d96f96b84fffb5d7886fdba36f6f507dab281bfd84dd954cdb7  17a-planpin-01-landing.md
2a5493f1b40a930fb8875893b58593709cfcb0e7c4a850e65126f959a4f4925f  17b-planpin-05-refuter-execution.md
71d589a64af2d8314a95b813a41f9550ac1827353c9a906a7dd3d324b0e4e087  17c-planpin-06-fix-round-1.md
8abce2074bdc90d97ee4fad3d3c224a542babcd2077674392fa77d0dd6ee9313  17d-planpin-10-fix-round-2.md
4512a72c4c4d58dfefdd6e171f5fbff5e622604ef3682a2706d12411314dd886  17e-planpin-11-delta-round-1.md
2af2f21b67d3518206f7624b0336b155a803be2f1ea94993691bcd50b164a25c  17f-watchdog-01-landing.md
062a4c83125eb31ef3f06547dcd5f5e46cf79b4bc10cd841bb41d030d33e47e1  17g-watchdog-02-spawn-bench.md
9ec2fd7952ad3187be1749b65babc2e8e86ad7b2cb0297f3edba709f65e5e470  17h-watchdog-03-fix-round-1.md
d90a2b52a85f550405ed67969549783eeb5406cb484647c3a82126444fa42db1  17i-watchdog-04-refuter-execution.md
b42bdc0490471887dff227c4a30692322d1e0dafa5468eb48fbf81c82d37549f  17j-proposed-ruling-addenda.md
d3e8771765d0a9e3bc040164049c0b134b3854ba5525823ff99c747fa3fe3149  17k-watchdog-05-refuter-contract.md
```
