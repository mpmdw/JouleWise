# R1 smoke launcher `ProcessType=Interactive` (RUN_STATE 274): cold executing review

- **Verdict: ADMIT.** No fixes required. Nothing found that should block tonight's re-smoke.
- **Target:** `fix/2026-11-11-r1-smoke-274` @ `9570bce3b`, parent `e6d8a62c6`. 16 lines: `scripts/launch_align_r0.py` (+5), `tests/align/test_r1_smoke_launcher.py` (+11).
- **Reviewer:** Fable 5.2, cold (did not write the change; Opus built it). Run on the Air, 2026-11-11 20:25 to 20:45 PST, in detached worktrees under `/Volumes/JW-EXT/jw-wt/rev-smoke274-*`. No MBP access, no host-changing command, no outcome data read.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | r1-smoke plist carries `ProcessType` = `Interactive` | PASS. Rendered plist has `<key>ProcessType</key><string>Interactive</string>` (plistlib puts the key and value on separate lines; the parsed value is the exact string the night installer requires, `night_agent_install.py:589, 675, 1081`). The night and night-probe templates at this commit hash to the two digests the prereg pins (`e62a461b…`, `1570b745…`). |
| 2 | R0 kind byte-identical to `e6d8a62c6` | PASS. Rendered both kinds from both commits with the same fixed inputs: R0 `runner.json` and plist are byte-identical. The existing test `test_r0_runner_json_and_plist_bytes_unchanged_and_r1_has_exit_timeout` (baseline `2d54da7e9`) also passes. |
| 3 | No other key changes | PASS. r1-smoke `runner.json` is byte-identical; the only plist key that differs is `ProcessType` (absent to `Interactive`). `ExitTimeOut` 400, `ProgramArguments`, `EnvironmentVariables`, `WorkingDirectory`, log paths unchanged. |
| 4 | New test fails at parent, passes at head, kills a mutant | PASS. See the mutant table. |
| 5 | Four modules at head | PASS. See the test table. |
| 6 | Binding | Covered by the existing basis; no new ruling needed. See below. |
| 7 | Other differences from the night's launch | None that should block. See findings. |

## Mutants

Run in `rev-smoke274-mut` against `test_r1_smoke_plist_runs_interactive_like_the_night_templates`; the worktree was restored after each.

| Mutant | Result |
|---|---|
| M0: launcher from `e6d8a62c6`, test from head | killed (test fails at the parent) |
| M1: value `Background` | killed |
| M2: value `Standard` | killed |
| M3: value `interactive` (lower case) | killed |
| M4: key `ProcesType` | killed |
| M5: night template changed to `Background` | killed (the template half of the test) |
| M6: assignment hoisted out of the r1-smoke branch, so R0 gets it too | killed by the R0 byte-identity test (the new test alone passes, as expected) |

## Tests at `9570bce3b`

One module at a time, `nice -n 10 python3.13 -B`, `TMPDIR` on the SSD, internal disk 27 to 28 GB free before each.

| Module | Result |
|---|---|
| `tests.align.test_r1_smoke_launcher` | 37 tests, OK (24 s) |
| `tests.hazards.test_refusal_allowlist` | 24 tests, OK, 1 skipped (143 s). The skip is "the block-5 design branch is not in this clone"; it names none of the launcher, the runner or `r1_runtime.py`. No failures, so no accepted-failure question arises. |
| `tests.align.test_r1_followup` | 12 tests, OK (46 s) |
| `tests.align.test_v4_registration` | 24 tests, OK (127 s). Condition 13 stays green; `launch_align_r0.py` is not a condition-13 path. |

## Binding (check 6)

My view: the change is covered and needs no new ruling.

- The prereg pins the operating condition as "captures launched by a launchd agent with `ProcessType=Interactive`" (`preregistration_d079_epoch_25g83_rev1.md:608`). The change moves the smoke into that condition; the failed run was the one outside it.
- RL-84 P-1: the predecessor is there "so that step-D starts from the state a W1 member starts from". W1 members are captured under the Interactive night job, so a predecessor captured under the default type was not run as W1 runs it.
- `launch_align_r0.py` is in `_NAMED_ARTIFACTS` and strict, but `registration_receipt.json` is still `PENDING_LEAD_REGISTRATION` with all 329 artifact digests unset. Nothing signed is rebound; the cost of an executed-bytes change before signing is a delta review before the smoke, and this is it.
- Suggested, not required: RUN_STATE 275 cites these three in one line, and says that the item-273 run's partial Part A output was taken outside the registered launch condition and is not used.

## Findings

None is blocking.

1. **Defect 2 of item 274 is not addressed on this branch (medium, not blocking).** `_prove_group_absent` (`run_night.py:511-531`) still ends on a 0.01 s census, below pgrep's ~13.8 ms cost. Reading the code, that floor is reached only when the 5 s window has been used up, which needs a group that is not provably empty for 5 s. That fits the failed run: the timed-out `sudo powermetrics` is root-owned, cannot be signalled by the user, and had about 230 s of frames left. On a clean Part A the first census gets a 1 s timeout and should answer. So this should not recur if the capture finishes, but any part that fails with a stranded root child will again report rc 2 instead of a clean part refusal. I could not check this against the MBP receipts; it is an inference from the code and item 274.
2. **Capture margin (low).** At the R1 night's ~127 ms a frame the 3,000-frame capture takes ~380 s against the 460 s timeout, about 80 s spare. The timeout would be hit at ~153 ms a frame, just above the prereg's 150 ms cadence stop. Adequate; no change asked.
3. **Environment differs from the night's, unchanged by this commit (low).** The smoke job sets `LC_ALL=C` and a PATH with `/opt/homebrew/bin`; the night job sets only PATH (courier directory plus system paths). Both ran through every setup step of the item-273 run without error. Same domain (`gui/<uid>`), same working directory (the repo). Neither sets nice, `LowPriorityIO`, `Nice` or umask.
4. **Smoke-only desk steps, unchanged (informational).** The launch wrapper SIGSTOPs `corespotlightd` and `spotlightknowledged` and the helper runs `pmset displaysleepnow` with a 300 s dwell; `run_night.py` does neither. These came with the R0 desk design and passed in the item-273 run. They are a state difference from a W1 member, for the research lead to weigh if it matters; they are not a failure risk for the re-smoke.
5. **The smoke adds two process layers (informational).** launchd starts bash, then the helper, then the runner; the night starts `run_night.py` directly. The Interactive type has to be inherited through them. RUN_STATE item 47 (b6 loop: zsh guard, probe, `sudo powermetrics`, 131 ms after the template went Interactive) is evidence that it is. The re-smoke's first capture cadence will confirm it; check `launchctl print` shows `spawn type = interactive` if the cadence is still slow.
6. **The R0 kind still runs under the default type (informational).** By design here, to keep R0 bytes identical. Any later R0 check that takes a `powermetrics -i 100` capture would meet the same slow cadence.
