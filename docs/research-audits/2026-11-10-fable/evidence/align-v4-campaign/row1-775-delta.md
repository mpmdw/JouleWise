## Row-1 delta review of PR #775 (b4b6aeb19): ADMIT WITH FIXES

Report time: Sat Nov 14 05:28 PST 2026 (`date`).

Note: the harness blocked writing REPORT.md ("subagents return findings as text"), so the full report is below. The logs it cites are in /Volumes/JW-EXT/scratch/review-pr775-delta/:
- item3*.out and item5*.out: test logs
- mut/results-*.json and mut/base-results-*.json: mutant tables
- mut/mutants.py and mut/base_mutants.py: the mutants
- e2e/ and e2e2/: the end-to-end fixtures
- kits/: the kit copy

All three throwaway worktrees (rv775d, rv775d-mut, rv775d-base) are removed. Blinding held: no slot, transcript, energy, power, meter or powermetrics file opened, nothing under ~/night-*, no SSH.

### Verdict
The split is correct. I ran the pilot's exact bytes and flags end to end against fake host binaries, and every guard worked.

The problem is test coverage. `scripts/launch_cadence_span.py` copies the fence, claim, bootstrap and bootout body of `launch_align_r0.launch`. Before the split, the cadence path ran through that shared function, so it inherited the base launcher's LaunchAgent and fence suites. The copy has no tests of its own:
- 25 of 43 mutants survive the cadence suite.
- Of 13 matching mutants run on the base launcher, the base suites kill 10.

Today the copy is faithful: my diff shows only `base.` prefixes, the kind and the plan print. All fixes are test-only, so no frozen path changes and no kit re-pin is needed. They do not block the pilot.

### Findings, ranked
1. **MEDIUM: the copied fence and claim code has no test of its own.** These mutants survive:
   - F1: the active-fence refusal is dropped.
   - F2: the fence check never matches.
   - F3: the magistrate's own PID is accepted as the claimer.
   - F4: the claim is never awaited.
   - F5: the wrong owner PID is written.
   - F6: the fence deadline is set 1 h late.
   - F7: the fence is written outside the lock.
   - F9: the fence is cleared even when bootout is indeterminate.
   - F10: the MAX_DESK_SECONDS check is removed.
   - F11: the live-magistrate check is removed.
   - F12: the new-output check is removed.

   On the base launcher, test_magistrate_desk_fence and test_r1_smoke_launcher kill F1, F3, F4, F5 and F10. Fix: port the base suites' LaunchAgent fixture to launch_cadence_span.py. That fixture is a fake launchctl that spawns the plist, plus fake pgrep and kill, and it runs the real wrapper. My e2e run shows it works against this module unchanged.
2. **MEDIUM: wrapper argv positions, the `run` verb and outer-run cleanup are untested.** These mutants survive:
   - W2: pgrep becomes /usr/bin/false, so the Spotlight pause is silently skipped.
   - W3: pgrep and kill are swapped.
   - W4: the wrong self-bootout target.
   - W9: PATH dropped.
   - A5: `run` is routed to the base launcher, whose r0 branch would do display prep and then `Popen(dict)`.
   - R2: a stuck runner is not terminated.
   - R3: no TERM grace for the runner's Automatic restore.
   - R4: no signal traps.

   The base suites kill W2, R2, R3 and R4 on the base copy. Fix: the same wrapper test, plus an assert on `main(["run", ...])` routing and a test with a child that ignores TERM.
3. **LOW: the launcher's own blackout refusal is untested.** B1 (`--batch-window` ignored), B3 (no window at all) and B7 (t0 not taken from the clock) survive, because the tests only launch at 13:20. The behavior is correct when executed:
   - 21:30 with `--batch-window 02:00-02:35`: rc 2, "worst-case span ... meets a batch blackout (02:00-02:35)", no custody directory created.
   - 20:45: proceeds.
   - 10:00 with no flag: rc 2 on the default 11:45-13:15 window.
   - The runner's `plan` also refuses at t0 21:30 (rc 1).

   Fix: one test at a 21:30 t0.
4. **LOW: kit validation at launch is untested.** K2 (runner.kind refusal dropped) and K3 (no `load_kit` validation) survive. The runner re-validates the kit and its frozen bytes at its own preflight, which test_runner_guards covers. Neither the old path nor the new one checks the kit's sha at launch; the pin comes from the magistrate's `shasum` line and the receipt asserts. So nothing was lost there.
5. **LOW: the ExitTimeOut assert is loose.** W5 (`+10` instead of `+40`) survives on both the new and base launchers. Fix: assert ExitTimeOut == 400.
6. **INFO: one census test will be red at the PR head.** At cf63121bc, `hazards.test_refusal_allowlist` fails exactly as it does on base fe907d0d3: the unlisted base site `launch_align_r0.launch` "parts c runs", which PR #777 lists. It passes at b4b6aeb19 and 589748f15, because 589748f15 still carried the line. The draft cites CI on 589748f15, which is consistent. Expect head CI to fail that test until #777 lands.
7. **INFO: stale text in the pilot draft.**
   - Line 14 says the in-tree kit at the measured commit is "pre-RL-150 text, sha `3b33c52d…feac`". At b4b6aeb19 the in-tree cl-dev-01.json is actually `75c99163…c3cb` (RL-150 text, pinned to efbd0b020). `3b33c52d…` is 79031dcd8's kit, and that sha ends `…55cd`, not `…feac`.
   - Line 40 has a truncated sentence: "(At `b4b6aeb19` the in-tree `CommittedKitTests` test the in-tree kit; )".
   - Neither affects any command.

### 1. launch_align_r0.py bytes and file classes
`git diff fe907d0d3 b4b6aeb19 -- scripts/launch_align_r0.py` is empty.

| file (efbd0b020..b4b6aeb19) | class | note |
|---|---|---|
| scripts/launch_cadence_span.py (new) | launch-side | Outer supervisor; runs no leg code |
| scripts/launch_align_r0.py | launch-side | Back to base bytes |
| scripts/cadence_legs_runner.py | runtime-in-span | Docstring only: the AST minus the module docstring equals efbd0b020's (executed) |
| kits cl-dev-01 and cl-dev-02 | kit data | RL-150 R7/R8 wording; still pinned to efbd0b020 at b4b6aeb19, re-pinned in 589748f15 |
| BLOCK-QUEUE.json, cadence_queue_design.md | docs/ledger | Not executed |
| configs/gates/hazard_refusals.json | test/census | The base-owned line; reverted in cf63121bc |
| tests/cadence/test_legs_runner.py, test_runner_guards.py | test/census | — |
| tests/host_command_sites.json | test/census | 7 entries: description strings and parser defaults |

- **Frozen paths.** Over the kit's 37 frozen paths, efbd0b020..b4b6aeb19 changes only the runner (docstring), launch_align_r0 and launch_cadence_span. b4b6aeb19..589748f15 and b4b6aeb19..cf63121bc change none of them, so the CI-equivalence claim holds.
- **Imports.** No non-campaign file under scripts/, joulewise/ or configs/ references campaign code.

### 2. Launch guards: mutants and an executed run

**New launcher.** 43 mutants against tests.cadence.* (5 modules), under a guard that blocked system launchctl, pmset and kill spawns and any signal to a non-descendant. The guard log was empty and the worktree was clean afterwards.

| guard | killed | survived |
|---|---|---|
| fence claim/refusal | F8 (failed launch leaves its fence) | F1–F7, F9–F12 |
| batch-window / deadline | B2 (argv passthrough), B4 (format), B5 (deadline fit), B6 (reserves) | B1, B3, B7 |
| kit | K1 (exists), K4 (`--legs` passthrough), K5 (`--legs` format) | K2, K3 |
| wrapper, Spotlight, ExitTimeOut, ProcessType | W1 (callbacks to the wrong module), W6 (ExitTimeOut 20), W7 (Background), W8 (label namespace) | W2, W3, W4, W5, W9 |
| agent-free | A1 (display sleep and dwell), A2 (any kind), A3 (kindless spec), A4 (no cleanup grace) | A5 |
| restore on clear | R1 (`clear` routing), R5 (`handoff` routing) | R2, R3, R4 |

Total: 18 killed, 25 survived.

**Same mutants on the base launcher** (fe907d0d3, test_r1_smoke_launcher + test_magistrate_desk_fence):
- Killed: F1, F3, F4, F5, F10, W2, R2, R3, R4.
- Survived: F9, F11, F12, W5.
- W3 was not run on the base: that fixture's fake `kill` can signal real PIDs.

**Executed end to end** (fake launchctl that spawns the plist, fake pmset, pgrep and kill, fake runner; real kit c76344c5, `--legs L001,L002,L003 --batch-window 02:00-02:35`):
1. `launch` returned rc 0 with "exit the magistrate session now". The fence was claimed by the wrapper's bash PID, not the magistrate's. The plan printed worst 16650, expected 6903, windows ["02:00-02:35"].
2. The plist had wrapper `run_align_r0_launchagent.sh`, helper `launch_cadence_span.py`, ExitTimeOut 400, ProcessType Interactive, label `com.joulewise.align-r0.<token>`.
3. The wrapper did handoff via base, then preflight. The only pmset call was `-g batt`, so no display sleep: agent-free.
4. The Spotlight census ran pgrep for both daemons. With a fake match it sent `-STOP` and then `-CONT 900000001`, and removed its record.
5. The runner got the correct `run` argv, including `--legs`, `--batch-window` and the fence deadline.
6. On clear the fence was removed, then the wrapper booted out its own label.
7. With a live foreign fence in place, launch refused (rc 2, "an active desk fence already exists"), made no launchctl call, and left the foreign fence intact.

### 3. W1 closures
- W1IsolationTests: 2 OK.
- test_v4_executed_closure: residue `['joulewise/align/apple/rl145_prints.py', 'scripts/align_r1_part_c.py']`.
- test_v4_dynamic_closure: residue `['joulewise/align/apple/rl145_prints.py']`.
- Base fe907d0d3 gives identical failures and residue. No campaign file is in either closure, and no PR commit touches those two files.

### 4. Kit validation
- **sha.** `git show 589748f15:…/cl-dev-01.json` has sha256 c76344c50aebc271cef5711ecb4f9b05482e8b5593a57afa16e973dfe1dc66d7. It is identical at cf63121bc.
- **validate-kit.** `validate-kit KIT --repo <b4b6aeb19> --batch-window 02:00-02:35` gives rc 0, ok true, frozen_commit b4b6aeb19…, frozen_paths_verified true, legs 12.
- **Frozen hashes.** I compared all 37 path hashes independently against `git show b4b6aeb19:<path>`: 0 mismatches.
- **Plan.** At 13:20 and at 20:45: budget 1251 s per leg, expected 6903 s, worst case 16650 s, blackout_clear true, all matching the draft.
- **Times.** The draft's epochs map to 13:20 and 20:45 PST. A 20:45 launch has its worst-case end at 01:22:30 and its fence end at 01:46:50. MAX_DESK_SECONDS is 43200, well above 18110.

### 5. Unit tests at b4b6aeb19 (all OK)

| module | tests |
|---|---|
| cadence.test_kit | 18 |
| cadence.test_legs_runner | 42 |
| cadence.test_queue | 12 |
| cadence.test_runner_guards | 8 |
| cadence.test_stops_desk | 14 |
| test_r1_smoke_launcher | 58 |
| test_rl145_part_c | 22 |
| test_host_command_sites | 2 |
| test_git_fixture_maintenance | 5 |
| hazards.test_refusal_allowlist | 24 (1 skip) |

### 6. Draft commands against the real argparse
- **Launch flags.** All 12 flags in the draft's launch line exist (launch_cadence_span.py lines 194–209) and mean what the draft says: `--repo --python-bin --kit --legs --batch-window --output --disk-path --custody-root --magistrate-pid --deadline --exit-wait-seconds --start-wait-seconds`.
- **Other commands.** These also exist: `cadence_queue.py validate-kit KIT --repo --batch-window`, `cadence_legs_runner.py plan --kit --legs --batch-window`, and `launch_align_r0.py preflight --disk-path`.
- **Refusal claims.** The draft's list of what launch refuses is true. Launch additionally refuses a span that would cross the blackout.
- **Check script.** I ran the draft's first Check heredoc against a mock span of the same kit and roster. Every assert passed and it printed RECEIPT OK, so all the receipt keys, step names and desk-bundle files it reads exist.
- **Not run.** The R1-print heredoc needs production paths and was not executed.

### Housekeeping
The base-mutant runs left one orphaned fixture fake runner (PID 48693, a fake align_r0_checks.py under my scratch tmp). I verified its command line was in my tmp directory and stopped it with TERM by PID.
