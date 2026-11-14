# Fable cold review: `sm-window-state` (audit Q2, section 8.2 item 1 shadow step, section 8.3)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 03:45 PST. Reviewed head `d68a11919`
(`feat/2026-11-11-sm-window-state`, base `origin/main` `41c7a1444`). Builder: Sol xhigh.

**Verdict: ADMIT-WITH-FIXES.** F-1 blocks: the module returns UNKNOWN for every directory on a stock macOS temp
path, and its own test module fails outside the builder's sandbox. Round 2 goes back to Sol.

## What I did

- Read all of `joulewise/window_state.py` (626 lines) and the test list (32 tests).
- Checked scope: only the five allowed files changed; nothing existing imports the module.
- Ran `python3.13 -B -m unittest tests.test_window_state` on the Air.
  - With the default `TMPDIR` (`/var/folders/...`): **45 failures in 32 tests.**
  - With `TMPDIR` under `/private/tmp`: 32 tests, OK. The builder's sandbox set such a `TMPDIR`.
- Compared the reader's field vocabulary with the writer on the W1 line (`scripts/run_night.py:2277-2325`).
- Mutation-tested 22 points of the classifier, the state precedence and the reader: 20 killed, 2 survived.

## Findings

| # | Severity | Finding | Fix |
|---|---|---|---|
| F-1 | **Blocking** | `observe_night_dir` walks from `/` with `O_NOFOLLOW` on every component. On macOS `/var` and `/tmp` are symlinks, so any custody root under them reads as `DIRECTORY_UNREADABLE_OR_UNSAFE`. The Air watcher will check results out under a scratch path of exactly that kind. | Resolve the root once (`os.path.realpath`), then refuse symlinks at and below the root only. Tests must pass with the default `TMPDIR`, with one under `/var/folders` and one under `/tmp`. |
| F-2 | Medium | The W1 writer records `measurement_outcome` as `invalid`, `absent` or `unreadable` when the payload record is bad. The reader treats those words as unknown vocabulary and returns `UNKNOWN`. That is safe but loses the answer the record already has. | Treat the three words as known not-complete statuses: `CHAIN_FAILED`, reason `PAYLOAD_NOT_COMPLETE`. |
| F-3 | Medium | The W1 result carries its own `chain_outcome`. The reader validates the word and then ignores it. Shadow mode exists to compare. | New invariant `RECORDED_OUTCOME_DISAGREES` when the recorded word and the derived outcome differ (`COMPLETE` matches both measured outcomes). |
| F-4 | Medium | Chain exit 0, payload complete, slots file missing gives `MEASURED_WITH_FLAGS`. The slots file is the payload; without it nothing usable was produced (audit section 5, machine 14). | `CHAIN_FAILED`, reason `PAYLOAD_SLOTS_MISSING`. |
| F-5 | Medium | No dwell invariant for the two silent states the audit is about: a plan past `t0 + 900 s` with no night record and no `launch_abandoned.json`, and an open chain past the completion epoch. | Invariants `NO_NIGHT_RECORD_AFTER_T0` and `CHAIN_OPEN_PAST_COMPLETION`, each with a boundary test. |
| F-6 | Low | Two surviving mutants: removing the `chain.unkilled` guard in `_outcome`, and forcing `delivery_recorded = True` for a git-push receipt. | One test each. |
| F-7 | Low | `EXIT_WORDS` differs from the plan words of `joulewise/exit_contract.py` (PR #722): `usage` and `hold` are rejected as unknown, `aborted` is not a plan word. | Accept `complete, refused, failed, stopped, usage, hold, aborted`; only `complete` on code 0 can be measured. No import of the other module. |

## What is sound

- Both historical failures classify correctly: GO with chain exit 3 is `CHAIN_FAILED`; REFUSED with no chain
  marker is `REFUSED_PRE_CHAIN`.
- No path yields a measured outcome without `chain.started`, `chain.exited` and exit 0; a caller's contract
  cannot bless a nonzero code.
- `derive_window_state` is pure, and plist facts are tri-state: an unobserved plist never reads as uninstalled.
- Reports carry fixed codes and counts only. Fault strings and record text are not copied.

## Round 2 delta review (2026-11-11 04:25 PST)

Reviewed `9a2390b6b` (Sol's round 2 on the same branch).

**Verdict: ADMIT.**

| Finding | Disposition |
|---|---|
| F-1 | Fixed. The root's ancestors are resolved once; a symlink as the root itself, or anywhere below it, is still refused, and the root's identity is re-checked after opening. On the Air: 43 tests OK with the default temp directory (`/var/folders/...`) and with `/tmp`. The module also re-runs itself under three temp settings. |
| F-2 | Fixed. `invalid`, `absent` and `unreadable` are known not-complete payload statuses: `CHAIN_FAILED`. |
| F-3 | Fixed. `RECORDED_OUTCOME_DISAGREES` compares the record's own `chain_outcome` with the derived outcome. |
| F-4 | Fixed. A complete payload with no slots file is `CHAIN_FAILED`, `PAYLOAD_SLOTS_MISSING`. |
| F-5 | Fixed. `NO_NIGHT_RECORD_AFTER_T0` (strictly after t0 + 900 s) and `CHAIN_OPEN_PAST_COMPLETION`. |
| F-6 | Fixed. Both earlier survivors are now killed. |
| F-7 | Fixed. The contract words are `complete, refused, failed, stopped, usage, hold, aborted`. |

Ten mutants on the changed code, ten killed: the two earlier survivors; the recorded-outcome comparison
removed; the missing-slots rule removed; the 900 s allowance removed; the open-chain boundary made inclusive;
the root-is-a-directory check removed; `unreadable` dropped from the known statuses; unknown contract words
treated as complete; the nonzero-exit rule removed. Sol reports its own pass of 160 mutants with no survivor.

Not covered: Python 3.11 locally (CI runs it). Plist facts are always supplied by the caller; the module never
contacts a host.
