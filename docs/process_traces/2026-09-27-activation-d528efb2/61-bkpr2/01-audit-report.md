AUDIT: FAIL

Bookkeeping PR audit (gate-ledger row 1, light tier), range `e3baaf2d..5789cad3` on branch `docs/2026-09-27-d528efb2`. The auditor is a fresh, non-author Opus 5.5 instance working read-only in `/Users/edr/code/JouleWise-wt-bkaudit-opus0928` (detached at `5789cad3`). There are no blockers. The FAIL comes from six should-fix findings, following the precedent of record item 25, where one should-fix gave FAIL. Every should-fix is a text edit on the records branch. No code is involved.

## Findings

**F1 (should_fix): the d528efb2 block in RUN_STATE is stale in its top half.**
- **Location:** `RUN_STATE.md:45-69`.
- **Why it matters:** the PAUSED block says it wins where the two disagree. But for D-138 it sends the successor to "the block below" for options (a)/(b)/(c), and that block is stale.
- **What is stale:**
  - **:45 and :48, the candidate.** The block names candidate `325d9f77` and issued bytes `80c23036…351b`. Executed:

    ```
    git show <c>:configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json | shasum -a 256
    ```

    This gives 325d9f77→80c23036, 8458f797→d6de84b8 and b953f4b0→d7076c78. `git ls-remote origin feat/2026-09-27-d138-25g83-issuance` gives `b953f4b0`. So the current candidate is `b953f4b0`, with digest `d7076c78…` (items 95 and 97).
  - **:53, the design addendum.** The block says the cold addendum "has been convened". It ISSUED (item 68). HOLD-BY-CONSTRUCTION-01 (item 82) and its A1 (item 97) followed.
  - **:58, the pedagogy pass.** The block says "to be applied after the addendum". The 37 items were applied (items 73 and 79), and a second pass followed (item 81).
  - **:60, the network-time lane.** The block says "being registered". It was registered in item 66.
  - **:64, S1.** The block says "its cold judge has been convened" and "a possible gate defect". S1-REPAIR-ROUTE-01 ISSUED (item 70) and its A1 ISSUED (item 112). The gate defect was ruled real and fixed as `601a06c5` (items 70 and 71).
  - **:69, option (b).** Option (b) lists "contract refuter 3, the whole suite on b953f4b0" as gates still to run. Both have returned: DISSENT with B1 (item 104), and 6 failures plus 9 errors (item 106). The correction email (item 105) raised the cost of (b), and the block does not mention it.
- **Fix:** refresh the summary half, or reduce it to a pointer into the record.

**F2 (should_fix): the science line overstates "no effect".**
- **Location:** `RUN_STATE.md:60`.
- **The text:** "caused 4 exclusions, but moved no member."
- **What the ruling says:** A2 §6 (`40-sci-a2-network-time/21-ruling.md:198`) says it "moved the clock of two members by 40 µs and 12 µs". A2's own "changes no member" (line 6) means membership.
- **Fix:** say "changed no member (two members' clocks moved 40 µs and 12 µs, inside allowance; C is 8.9 µs smaller)".

**F3 (should_fix): two new kernel lanes were registered before later rulings and not refreshed.** Both were registered at item 66 (`fbf0007d`, 23:48). The rulings in items 68 and 100 came after.
- **(a) NETWORK-TIME-OFF-ENFORCE-01** (`docs/process/state_kernel.json:5546`, TASK_QUEUE A332):
  - The acceptance states A3's witness rule ("coverage witness predating the first 180 s lead").
  - NTP-ENFORCE-DESIGN-01 §5 (`71-ntp-design/21-coldgate-fable-ruling.md:306-310`) amended that rule. The query now starts at OFF − 3,600 s, and the witness must be older than OFF.
  - The authority cites neither NTP-ENFORCE-DESIGN-01 nor its A1.
  - The status is `queued`, but N1 is implemented (`feat/2026-09-28-ntp-n1` at `36e8ba6e`) and is waiting on cold gate A2. The kernel uses `active` for 7 other lanes.
- **(b) OLD-EPOCH-EXPLICIT-R7-ROUTE-01** (`state_kernel.json:6180`, A335):
  - The lane says "after the D-138 default move" and cites design ruling §10 item 2.
  - D138-A1 §6 (`11-d138-design/31-addendum-ruling.md:257-263`) kept R7 as the default (R-1). It restated the condition for the later default-moving transaction, including an explicit R7 route with a test, required before that merge.
  - The lane's authority and timing should cite A1 §6 item 3.

**F4 (should_fix): the kernel disagrees with the record on two older lanes.**
- **(a) CALIB-ISSUE-25G83-D138-01** (`state_kernel.json:1518`; `TASK_QUEUE.md:946` and `:1233`):
  - It is still READY [AGENT] / `queued`, and its note is unchanged.
  - The record says the transaction "STOPS FOR GOOD" under HOLD-BY-CONSTRUCTION-01 §6.2 and waits for Ed's a/b/c (items 101, 102 and 105).
  - A successor selecting work from TASK_QUEUE could pick it up.
- **(b) S1-REGRESSION-01** (`state_kernel.json:8525`, A333):
  - The note says "its ruling file is not yet present in this tree".
  - That is false at this head. S1-REGRESSION-01-A1, A2 and A3, S1-REPAIR-ROUTE-01 and its A1 are all present, and the lane is in round 3.

**F5 (should_fix): evidence cited by the record is gitignored and will not reach main.**
- **The rule:** `.gitignore:45` is `docs/process_traces/**/*.log`.
- **Links that therefore resolve to nothing on the branch:**
  - `00-activation-record.md:94` → `30-s1-repair/22-r2-H2-plants.log`
  - `:132` → `50-d138-issuance-seat/mutation/lead-sim-freeze-plant.log`
  - `:219` → `50-d138-issuance-seat/fix2/red_record_lead.log`
  - (`:52` also, but it predates this range.)
- **Where the files are:** they exist only in the untracked tree of `JouleWise-wt-bk-77b1bee2`. `git status --ignored` lists 41 such files, including:
  - the per-test HR/DT/P6 red and green logs behind item 75's "RED_RECORD=PASS";
  - the P-1..P-3 pilot logs behind item 120;
  - the `replay/independent/*.log` files;
  - the `71-ntp-design/38-probes/*.log` files.
- **Fix:** `git add -f`, or rename the files to `.txt`.

**F6 (should_fix): item 128 gives a wrong reason for holding P6.**
- **Location:** `00-activation-record.md:457`.
- **The text:** "the second pass's 25 items (item 81) change the sealed issuance text, whose digest the transaction pins".
- **What the pass targets:** `refuters/pedagogy-pass-2.md` targets only the issuing record ("IR") and D-185 with its note. Every one of its 19 `Location:` lines is in the IR or D185. It says: "Verbatim D1-D8, H1-H7, B1-B4 … were not judged".
- **Effect:** the hold may still be right on other grounds. D-138 is stopped pending Ed, D-185 is a decision-log draft, and those texts were superseded (contract refuter 3, S5). But the stated reason is false.

**F7 (nit): item 78 leaves out three headline verdicts.**
- **Location:** `00-activation-record.md:223-225`.
- **What is left out:**
  - `refuters/contract-refuter-2-astra.md:113` reads REFUTER: DISSENT. The record says "no BLOCKER", which is the refuter's own words.
  - `replay2/report.md:188` reads REPLAY: FAIL, with envelope status `blocked`.
  - `mutation2/report.md:88` reads MUTATION: GAPS.
- **Why it matters:** items 52 and 99 quote REPLAY: PASS verbatim, so the omission is asymmetric. Nothing is called a PASS here, so this is not an overstatement.

**F8 (nit): the PAUSED table is one item behind.**
- **Location:** `RUN_STATE.md:23`.
- The table says "items 1–127". The record now ends at 128 (commit `9e19a916`, which came after the RUN_STATE commit `1760f183`).

**F9 (nit): item 122 misstates condition 9's scope.**
- **Location:** `00-activation-record.md:408`.
- **The text:** "Both are within condition 9's cap of 11", said of 35 first-form IDs and 6 second-form IDs.
- **What condition 9 says:** it caps only `PARITY_SECOND_FORM_TEST_IDS` (`30-s1-repair/83-coldgate-pilot-ruling.md:286`). The 6 second-form IDs are within it. The first-form list has no such cap.

**F10 (nit): two email times are wrong.**
- **Item 72** (`:202`) says "(00:30 PDT)". The commit `f99ac2dc` is at 00:16:08, and Gmail ID `1a0e6ded…` decodes to 00:15:57.
- **Item 102** (`:302`) says "≈04:55 PDT". The commit `2e28487f` is at 04:26:55, earlier than the claimed send time, and ID `1a0e7c44…` decodes to 04:26:36.

**F11 (nit): the Completed row cites the wrong A2 section.**
- **Location:** `TASK_QUEUE.md:104`, the WALLCLOCK-STEP-SOURCE-01 row.
- It cites A2 §7 for the H4 discharge. The discharge text is in A2 §6 (`21-ruling.md:212`); §7 is H5–H7. The A3 §4.4 cite is correct.

**F12 (nit): the display alias A332 was reused.**
- Rank 332 moved from WALLCLOCK-STEP-SOURCE-01 to NETWORK-TIME-OFF-ENFORCE-01.
- The spec only requires ranks to be unique within a lane, which holds.
- Historical charges and rulings still say "A332 (WALLCLOCK-STEP-SOURCE-01)": `20-cap-council/00-consult-charge.md:13`, `20-coldgate-charge.md:3`, `30-addendum-charge.md:3` and `21-coldgate-fable-ruling.md:13`.

**Outside this range, not scored:** `RUN_STATE.md:333` holds 8 `{D}/…` template-placeholder links that are dead. They predate this range.

## Verified, with no finding (executed evidence)

- **Record numbering:** items 1–128 are contiguous. An awk check found no gaps; last = 128, count = 128.
- **Links:** the link checker (`p4/linkcheck.py`) checked 1,392 relative links in the record, RUN_STATE and TASK_QUEUE. The only misses are the four `.log` links (F5) and the out-of-range `{D}` placeholders. Misses in verbatim seat and judge artefacts are file:line links into worktrees, which are out of scope.
- **Cited hashes:** 46 distinct backticked hex tokens in record items 43–128 and in the added RUN_STATE lines were checked with `git cat-file -t`. 41 are commits. The other 5 are Gmail IDs and the sha256 prefix `dbad7cc7`.
- **Branch heads:** `git ls-remote` gives the following, and every one matches the PAUSED table and item 127:
  - `feat/2026-09-28-ntp-n1` = `36e8ba6e`
  - `fix/2026-09-28-s1-r3-{H3,A,L}` = `cdfb27ce`
  - `-B` = `d4345946`
  - `wip/…-A-partial` = `b0474eaa` (parent `cdfb27ce`)
  - `wip/…-L-partial` = `c1589d94` (parent `cdfb27ce`)
  - `docs/2026-09-27-d528efb2` = `5789cad3`
  - `main` = `9eab16f8`
- **Ancestry and composition:**
  - `9eab16f8` has parents `e7c8bcc6` and `e3baaf2d`.
  - `0f86b1a0` merges `fbf0007d`.
  - `0c469057` is `601a06c5` + `9eab16f8`.
  - `c1a11b9d` is `5283d7d0` + `9eab16f8`.
  - `e7c8bcc6` ⊂ `c81f65b8`; `9eab16f8` ⊂ `325d9f77`.
  - `b953f4b0` is one commit over `96852358`, touching only 3 test files.
  - `f0766620` ⊂ `cdfb27ce`, and 1d787877 gives 40 → 35 first-form IDs.
  - `c8995f4b` ⊂ `36e8ba6e`.
  - `bundle_read.py` at `601a06c5` has sha256 `c4039f22`.
- **Suite counts:** every filed summary matches its record item.
  - `c81f65b8`: 269 modules / 7,559 tests / 0 / 0
  - `325d9f77`: 7,559 / 0 / 0
  - `8458f797`: 270 / 7,575 / 1 failure
  - `b953f4b0`: 271 / 7,598 / 6 failures / 9 errors
  - `3ad82b43`: 7,601 / 1 failure
  - `0c469057`: 272 / 7,713 / 75 failures / 89 errors
  - `c1a11b9d` baseline: 120 bad; turned 44, whose per-module split equals item 86
  - census-proto: 7,575 / 5 failures
  - `test_run_night` at `c8995f4b`: 277 tests, 11 failures
- **Kernel arithmetic:** a Python diff of the kernel at `e3baaf2d` against `5789cad3` gives 281 → 285. It adds the 5 named lanes, removes WALLCLOCK-STEP-SOURCE-01 and changes only ESTIMATOR-CELL-CAP-RESIZE-01. This matches `TASK_QUEUE.md` "285 live tasks (281 previous + 5 registrations - 1 discharged…)" and `tests/test_gen_state.py` EXPECTED_IDS and the 285 assertion.
- **Kernel against TASK_QUEUE:** `python3 scripts/gen_state.py --check` gives rc=0, so both generated regions agree with the kernel.
- **Rulings claimed as issued:** each of the 7 rulings the record calls ISSUED (items 68, 70, 82, 97, 100, 112 and 115) has an `ISSUED` first line. No `71-ntp-design/48-*` exists, and nothing claims A2 issued; items 126–128 and the PAUSED block say it did not.
- **Refuter and lens verdicts:** the verdict lines match record items 61, 62, 64, 80, 81, 99 (INCOMPLETE, reported correctly), 101, 104, 107, 108, 114, 115 (AGREE-WITH-D1) and 124 (DELTA: PASS and DELTA: FINDINGS).
- **Round 2b:** the lead's round-2b ruling (item 118) matches the text of A1 §7.4 (`38-coldgate-fix2-ruling.md:362`).
- **The cap lane (A331):** it keeps H4's surviving clause, "record … abandoned bracket causes", so the WALLCLOCK discharge drops no obligation.

## Test tails (python3 = /opt/homebrew/bin/python3, Python 3.14.7, at 5789cad3)

`python3 -m unittest tests.test_docs_freshness tests.test_gen_state`:
```
Ran 75 tests in 2.751s

OK
```
`python3 -m unittest tests.test_build_site_parsers` (the other test that reads RUN_STATE/TASK_QUEUE):
```
Ran 30 tests in 0.000s

OK (skipped=30)
```
`python3 scripts/gen_state.py --check`: rc=0.

`tests.test_quiet_guard` also names these files, but it was not run: it touches powermetrics and sudo configuration and is outside the light tier. The worktree was clean after the runs.
