# Seat: Mythos 5.2, #775 delta

Sat Nov 14 05:09:20 PST 2026 (`date`). Cold seat for the launcher delta `efbd0b020` → `b4b6aeb19`. I did not write the launcher, the kit or the item draft.

## Verdict

**ADMIT WITH FIXES** for issuing the counted pilot on `b4b6aeb19`.

The launcher split is sound: no guard of consequence was lost, the leg's bytes are unchanged, and W1 isolation holds. The item cannot be issued as drafted, though. Five findings must close first (F1–F5); F1 and F2 need a line from the research lead, and F3–F5 are draft edits.

## Answers

**1. Guards.** None lost that matters.

| Guard | New launcher | Status |
|---|---|---|
| Fence publish; refusal on a live fence | Same code, through the base's `fence_lock`, `read_fence`, `write_fence` | Kept |
| Refusal of a span that meets 02:00–02:35 | `cadence_plan` → `plan_span`, moved verbatim | Kept, when the flag is passed (F8) |
| Deadline ≥ worst case + 560 s | `cadence_minimum_seconds` | Kept |
| Wrapper, Spotlight pause, ExitTimeOut 400, Interactive | Same wrapper blob (`d451ec67`); same plist keys | Kept |
| Agent-free handoff, clear | Delegated to `launch_align_r0.main` | Kept |
| Night agent loaded; HEAD and frozen bytes; restore | Runner preflight and close, code unchanged | Kept |
| Kit sha | Never checked by either launcher; the receipt records it | Unchanged |

- Dropped: the `remaining <= dwell` pre-check and the `--soak-reference` refusal (the flag no longer exists). Both are harmless.
- Following the draft literally, the magistrate launches `cl-dev-01` L001–L003 and nothing else. A launch from 21:22:30 to 02:35 is refused by `plan_span`. See F4 and F5 for what the literal text does wrong.

**2. "No byte that runs inside a leg changed."** True of everything in RL-150 R5's class A list, but not literally (F6).
- 34 of the 37 frozen blobs are identical at both commits.
- The whole-tree change list for the range holds no other executed file: only `hazard_refusals.json` (read by tests only), docs, tests, kits and the ledger.

**3. W1 isolation.** Real.
- `launch_align_r0.py` at `b4b6aeb19` is the base blob (`d2e8cba0`, same as `fe907d0d3`).
- No file under `scripts/` or `joulewise/` outside the campaign names a campaign module.
- The watchdog imports only `FENCE_NAME`, `fence_lock` and `read_fence`, and treats the fence by pid and deadline, not by kind.
- Shared state is the desk fence, `r0-launches/<token>/`, the `com.joulewise.align-r0.*` label and the host power lock. That is the r1-smoke coupling, unchanged by the delta.

**4. Commands.** Every flag and path in the draft matches the CLI at `b4b6aeb19`: `validate-kit`, `plan`, `preflight`, `launch`, and the receipt keys the Check script reads. The plan numbers are right (1,251 / 6,903 / 16,650 / 17,210 s). The epoch bounds are 13:20 and 20:45 PST. The defects are in F3–F5 and F7.

**5. Countability.** F1, F2 and F3.

## Findings

### Must close before the item is issued

**F1. §2.8 line 2 cannot be filled as drafted.** Major; research lead.
- The draft expects "full suite green: CI on `589748f15`". The builder's own runs (`summary-base.txt`, `summary-head.txt`, the PR body) show eight modules red on base and head alike: `test_smoke_delta_sol1`, `_sol2`, `test_v4_executed_closure`, `test_v4_dynamic_closure`, `test_w1bm_sol1`, `_sol2`, `test_timing_receipts`, and three tests in `test_w1_prequal`.
- Their fix is PR #777 (`b27fec059`), which edits three frozen paths: `v4_registration.py`, `align_r1_rehearsal.py` and `run_align_r1_smoke.py`. A green tree therefore cannot stand for `b4b6aeb19`.
- One red is `test_meter_through_the_hazard_pack_driver_flags_the_member_it_lost` ("driver exit 3"). The campaign's meter feed uses that supervisor (`joulewise/b5/driver.py`, frozen).
- Fix: the research lead rules line 2 for this kit with the reds named and the meter one explained, or the pilot waits for #777 and a re-pin. I did not read CI.

**F2. RL-150's F1 cannot close on its own words.** Major; research lead's line.
- RL-150 §2 F1 accepted "All 36 path hashes are unchanged". This kit has 37 paths: two changed and one new.
- RL-149 §2.4 names the research lead for "any change to a frozen kit path". §2.8 ends the authorization until a new kit passes lines 1 and 2.
- This report is the cold check of the three files. R5 class B also needs a mock span and a `plan`; I could run neither.
- Fix: the arm record carries the mock and plan at `b4b6aeb19` with kit `c76344c5…66d7`, the row-1 re-review result, and one line from the research lead accepting class B.

**F3. The Check script has the magistrate open the meter streams.** Major; draft edit.
- The loop over `r["feeds"]` re-hashes every feed file. The meter feed's files are its journal, two logs and every `stream-*.jsonl` (`MeterFeed.files`).
- The kit's `energy_read_rule` (R8) lets only the runner hash a stream. The draft itself says "Do not open `hazards/`, any `stream-*.jsonl`".
- Fix: skip the `meter` feed in the re-hash and keep its `proven_stopped` assert.

**F4. The measurement_mode line cannot pass as written.** Major; lead.
- The line says "must end verify OK". NOTE 1 says it cannot while the magistrate runs. Read literally, nothing launches.
- Fix: put the adopted rule in the item text. This is RL-150's F5 line.

**F5. The gates are bare `test` lines, and the launch window has no code backstop.** Major; draft edit.
- These print nothing on failure: the time window, HEAD, clean tree, `test ! -e "$KIT"` (the next line then overwrites it), the kit sha, `$OUT`, and the High Power marker.
- With the flag, the launcher accepts any t0 from 02:35 to 21:22:30. A launch between about 11:12 and 13:15 waits out the frozen 11:45–13:15 soak window (`cadence_legs_runner.py:455`). That can be up to two hours the plan does not budget.
- Fix: add `|| { echo "STOP …"; exit 1; }` to each, and repeat the time test as the first line of the Run block.

### Minor

**F6. Reword the class B claim.** Three changed files load in processes alive from soak start to leg close:
- `launch_cadence_span.py run` is the new supervisor. Its wait loop is line for line the r1-smoke branch.
- `cadence_legs_runner.py` changed by one docstring line.
- `launch_align_r0.py` is imported by the driver and the soak child, and lost only campaign names.

Behaviour inside a leg is unchanged, so class B stands on my reading.

**F7. Draft text.**
- The in-tree kit at `b4b6aeb19` is the RL-150 text pinned at `efbd0b020` (ledger sha `75c99163…`). It is not "the pre-RL-150 text, sha `3b33c52d…feac`", and no hash here ends in `feac`.
- The parenthetical "(At `b4b6aeb19` the in-tree `CommittedKitTests` test the in-tree kit; )" is cut off. Those tests pass but check the old kit, not the armed one.
- The PR head is `cf63121bc`, not `589748f15`. The extra commit reverts `hazard_refusals.json` only; the kit blob is the same.
- Lines 1, 2, 3 and 7 still hold placeholders.

**F8. `--batch-window` and `--legs` are still optional in a campaign-only launcher.**
- Without the window flag the plan falls back to 11:45–13:15, and a span may cross 02:00–02:35 with exit 0.
- Without `--legs` the draft's deadline refuses the launch.
- Fix: make both required in v1.1, and have the item require `plan.batch_windows` in the launch output.

**F9. The R1 print.** It raises if a leg's result has no `bundle`. Also print the G0 row's own `reference` and `release`; they sit in the same journal row.

**F10. No `QUEUE.json` exists at the PR head.** Line 3 is open. NOTE 2 (launch artifacts under the watchdog root) is unchanged by the delta and is the lead's call.

## What I did and did not do

- **Read through git:** the four commits of the range, the new and base launchers, the wrapper, the runner, `legs.py`, `kit.py`, `cadence_queue.py`, `run_align_r1_smoke.py`, the watchdog's fence code, and the kits at `79031dcd8` and `589748f15`.
- **`git diff A B` was blocked in this seat.** I used per-commit `git show`, `git log --stat` over the range and `ls-tree` blob ids instead.
- **Searches** used the existing worktree `rv775d` at `b4b6aeb19`. I could not confirm it is clean. Launcher, runner and kit bytes came from `git show`.
- **Not recomputed:** any sha256 (hash tools and Python were refused). The 34 unchanged pins rest on blob identity plus my earlier check. The three changed pins and the kit sha rest on the arm's `validate-kit --repo` line.
- **Not run:** any test, mock or plan. I did not read CI; those statements come from the builder's account.
- **Blinding held.** No slot, transcript, energy, power, meter or powermetrics file was opened, and nothing under `~/night-*`. No SSH. Nothing was written.