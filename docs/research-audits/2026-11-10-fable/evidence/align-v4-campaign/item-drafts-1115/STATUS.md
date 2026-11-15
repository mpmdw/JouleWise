# items-1115: campaign items after RL-173 D, status per item

Items builder, Sun 15 Nov 2026 15:13 PST (`date`). Inputs: the RL-171/172 drafts in `/Volumes/JW-EXT/scratch/items-rl171` (copied, never edited in place), RL-173 (verbatim at `f35483d41`), RL-172 (a), RUN_STATE 344-351 on origin/main (`718d1c3a3`). No SSH, no RUN_STATE edit, nothing issued. No energy, power, meter or custody file was opened; the gate tests use the items-rl171 MOCK spans only.

## Summary

| Item | Status | What is missing, and who owns it |
|---|---|---|
| ITEM-dev02-s03 (Mon 16 Nov, pred `dev-02-s02`) | **READY to issue now** except the issue-time fills | Lead, at issue: ISSUED + ISSUED_EPOCH; line 6 (stops of dev-01-s04, hp-01 s01-s03, dev-02-s02); line 7 + WATCH_UNTIL_EPOCH; line 9 (span 8; two back = `hp-01-s03`, desk FINAL at audit `05c681ac4`). Staging: `stage_mbp_span.sh dev-02-s03` |
| ITEM-dev03-pilot (Mon 16 Nov, pred `dev-02-s03`) | **READY to issue now** once the lead has made ONE decision (row 1) and the issue-time fills | Lead: (1) **row-1 delta reading at `2d347f721` is MISSING**: decide "Mythos delta seat stands as row 1's delta reading, as item 334", or order a row-1 delta seat; (2) ISSUED + ISSUED_EPOCH; slot-session READY line; line 6; line 7 + WATCH_UNTIL_EPOCH; line 9 (span 9; two back = `dev-02-s02`, whose desk is **not yet FINAL** on the audit branch: another lane owns that push, plus its Q1 completion record, RL-173 E); (3) run `stage_mbp_span.sh dev-03-s01` on the MBP in a close interval before Sun 23:30 |
| ITEM-dev03-rest (Mon 16 Nov, pred `dev-03-s01`) | **Text ready; NOT issuable ahead** (RL-173 D.4) | Lead: the pilot's hand-read (R9 PASSED + class A smoke MET, L002 released); then the fills in the item; staging `dev-03-s02` |
| ITEM-dev04-s01 (Tue 17 Nov, pred `dev-03-s02`) | **Text ready; NOT issuable ahead of the dev-03 pilot's hand-read** (RL-173 D.4) | Its gate needs dev-03's R9 PASSED and smoke MET, and its predecessor is the rest, itself behind the hand-read. After the hand-read it can be issued with ITEM-dev03-rest (the rest + dev-04-s01 = two ahead). Lead fills as listed in the item |
| ITEM-dev04-s02 (Tue 17 Nov, pred `dev-04-s01`) | **Text ready; waits on the L005 gate** (RL-173 D.4) | Lead: `dev-04-s01`'s Check (L005's G0 outcome, or dev-03's released-consumer count >= 4 of 5) |
| ITEM-dev05-s01, ITEM-dev05-s02 (Wed 18 Nov) | **Text ready; behind the L005 gate** (they follow `dev-04-s02`) | Lead: after the L005 gate; inside the three-ahead cap |

Tonight's issue-ahead set is therefore **two counted spans (dev-02-s03, dev-03 pilot) plus the standing F0**, inside RL-173 D.1's three. dev-04-s01, which the plan hoped to issue ahead, sits behind the pilot's class A hand-read (D.4). Expected effect: none on the chain if the lead issues the rest and dev-04-s01 together at the Mon ~05:00 hand-read, since dev-04 is dated Tuesday anyway.

## 1. Fills resolved here (host-independent)

- **Line 2, dev-03 to dev-05 (one result for the pin):** CI `ci` 43664825578 on `9cbb365a6` completed Sat 14 Nov 20:47:37 PST, conclusion **failure** (shards 2, 3, 5-9, 11, 12 red). Shard 11 was slow, not stalled (`tests.test_bytes_analysis` 9,107 s, passed). **Final red set = `fe907d0d3`'s 12 tests (CI 43600776368), test for test, no added red**: both sets re-derived from every failed job's log today (`evidence/LINE2-dev03-final.md`, `line2-dev03-red-9cbb365a6.txt`, `line2-base-red-fe907d0d3.txt`).
- **Queues:** all already committed on audit/2026-11-10-fable at **`b7a0d98822865a01e67fc3cc1833c9b186be2181`** (Sun 00:22): dev-03 pilot `403e53f9…7da2` (sha verified), dev-03 append-both `366662ce…`, dev-04 `69131963…`, dev-05 `391f4382…`, dev-02 6+6 append `ad0212ae…`. `validate-queue` re-run today at `2d347f721` on the committed bytes: all four 2d347f721 queues ok (`evidence/validate-queue-1115.log`). No new queue commit was needed. QCOMMIT is filled in every item.
- **Row 1 at `2d347f721` (pilot READY line 1): MISSING, not invented.** PR #788 has no review or comment; the audit evidence holds only the two Mythos seats (first `4c38dce3b`, delta ADMIT `5b8d23727`); `rev788/REVIEW.md` is the `17f478675` review. Precedent: item 334 recorded the Mythos delta seat as hp-01's row-1 delta reading. The item now states this and leaves a single LEAD FILLS for the decision.
- **Kits:** shas re-verified from git (`0f535774…e14b` at `9cbb365a6`; `1cc6673d…2228` and `2747381b…ca1a` at `fecaf73f3`). dev-04/05's Mythos seat audit copy filled: `evidence/align-v4-campaign/mythos-dev04-05.md` at `da8b855b6` (byte-identical to the scratch report).
- **Desk checkout (pilot "After", D1):** `/Volumes/JW-EXT/jw-wt/desk-final-pin-2d347f721`, detached at the pin, clean; or the MBP's deterministic desk (RL-173 B).
- **dev-02-s03:** `RAN=dev-02-s02` fixed in the script (RUN_STATE 349: RECEIPT OK 6/6; dev-02-s01 withdrawn unarmed by item 344); line 1 F6 and line 3's notice filled as item 344 did.

## 2. RL-173 applied (every counted item)

- **D.2 predecessor + clean receipt:** each item names its predecessor (`dev-02-s02` -> s03 -> pilot -> rest -> dev-04-s01 -> s02 -> dev-05-s01 -> s02) and runs `pred_gate` in Start and check and in Run. It reads only the predecessor's `runner_receipt.json` (rc, error, mock, roster, leg counts, span_result outcome/chain/fault, restore/stop/close steps, ended time) and its desk-bundle `leg_summary.json` (wall vs 1.5 x budget, contaminated redos: RL-149 §2.4's LEG_OVERTIME and CONTAMINATED_REDOS). No receipt = WAIT; not clean = **VOID, not skipped**; two output dirs = STOP. `PRIOR_CLOSE_EPOCH` must not precede the receipt close.
- **D.3:** the date windows and `pick_arg` were already in the drafts (unchanged).
- **D.4:** each item states whether it may be issued ahead (table above).
- **D.5 expiry:** `ISSUED_EPOCH` (LEAD FILLS at issue) + 86,400 s, `expiry_gate` in Start and check, in Run, and last before the launch; heading and pointer say VOID on expiry.
- **A (copy):** the copy-gate text now names the MBP's verified cloud offload marker (items 347/348) as a valid writer of `desk-copy/<plan-id>.ok`; code unchanged (same path).
- **C 5 (line 7):** `WATCH_UNTIL_EPOCH` (line 7 stamp + 86,400 s, LEAD FILLS) re-checked by `watch_gate` just before the launch.
- Tests: `tests/test_rl173_gates.py` (17 cases x bash and zsh, per item, on mock spans with the mock flag cleared): **FAILS 0 for all seven items** (`evidence/test-rl173-gates-*.log`). `tools/lint.py`: every sh block passes `bash -n`/`zsh -n`, every heredoc compiles, BAD 0.

## 3. MBP staging (task 3)

`/Volumes/JW-EXT/scratch/items-1115/stage_mbp_span.sh [--dry-run] <span>` (spans dev-02-s03, dev-03-s01, dev-03-s02, dev-04-s01/s02, dev-05-s01/s02). The lead runs it over SSH **between spans only**. It refuses on a live `desk_fence.json` or a live runner/monitor process; fetches the item's refs; asserts pin, kit and queue objects and shas; creates the fresh **detached** worktree at the exact path the item reuses (`/Users/edr/code/jw-wt/cadence-dev03-s01` for the pilot; refuses an existing one that is not at the pin, not detached or dirty); copies the kit to the item's KIT path under `/Users/edr/campaign-out/kits/` and the queue to `/Users/edr/campaign-out/queues/`, sha asserted, never overwriting a different file; writes `/Users/edr/campaign-out/staged/<span>.staged.txt`. No Python, no test, no energy file.
- Air test against a local shared clone (`JW_REPO`, `JW_WT_ROOT`, `JW_OUT_ROOT`, `JW_CUSTODY`, `JW_NO_FETCH=1`): dry-run, real, idempotent re-run, dev-02-s03 and dev-04-s01 real, the other four dry; negatives: live fence, tampered kit, worktree at the wrong pin, dirty worktree, live runner, unknown span: all refused (`evidence/stage-test-air.log`). The live-runner guard also tripped on another Air lane's real `cadence_legs_runner.py plan`, as intended.
- On the MBP: `ssh mbp-ts zsh -s -- dev-03-s01 < stage_mbp_span.sh` (or copy it to the MBP first). **Not run against the MBP by this builder.**

## 4. Owed by the lead (not research-lead questions)

1. **Row-1 decision for `2d347f721`** (above). Blocks the pilot's READY line 1.
2. **dev-02-s02 desk FINAL and its Q1 completion record** (RL-172 (c), RL-173 E: span k's Q1 record before span k+2 arms): needed for the pilot's line 9 at issue. Not on the audit branch at 15:12.
3. **RL-173 A 1, the offload key's second copy off the MBP:** an offload marker counts without it only until Mon 16 Nov 11:58 PST (epoch 1794859080). The pilot's window runs past that; if dev-02-s03's (or the pilot's) copy comes from the MBP offload after 11:58, the key copy must exist. The items cannot check this; record it before issue.
4. **RL-173 E, Time Machine:** "if automatic backups can be turned off remotely with a readback, do it at the next span boundary before dev-03's first span". With items issued ahead, the boundaries before the pilot are the F0 closes tonight and dev-02-s03's close interval (300 s, no SSH once armed). Do it tonight between F0 runs, or record that it waits for freeze 2.
5. Staging: `stage_mbp_span.sh dev-02-s03` and `dev-03-s01` on the MBP in a close interval before Sun 23:30 (an F0 run may be armed; the script refuses then).
6. Issue-time fills only: ISSUED / ISSUED_EPOCH, slot-session READY line (pilot), PRIOR (magistrate env at arm), lines 6, 7 (+ WATCH_UNTIL_EPOCH) and 9.

## 5. Notes (no ruling requested; listed for the lead)

- **RL-161 §2 and the remainder's queue:** `QUEUE-cl-dev-03-2d347f721-append-both.json` was committed at `b7a0d9882` on Sun 00:22, before the pilot's hand-read; RL-161 §2 says the remainder's entry is appended after it. Nothing reads it before ITEM-dev03-rest is issued (no `cadence_queue.py next`), and that item names `b7a0d9882`. If the lead wants the order on record, a hand-read note naming `b7a0d9882` as the append suffices; no research-lead ruling seems needed.
- **Line 6 for items issued ahead** can only list spans closed at issue. The predecessor's named stops computable from its bundle (LEG_OVERTIME, CONTAMINATED_REDOS) and its receipt faults are covered by `pred_gate`; REFUSAL, restore-unproven, disk/watcher-down and INSTRUMENT_FAULT show in the receipt (rc, outcome, fault, close steps). A stop that only the desk's full `stops.json` would show is not read by the magistrate. If the lead wants that closed, the MBP deterministic desk (RL-173 B) could write `stops.json` in the close interval and `pred_gate` could require it empty; that is an engineering choice for the lead, not done here.
- RL-173 C 4 (the Actions watcher) is not wired: line 7 still reads the Air watcher stamp. Switching needs a re-issue that reads the watcher's latest completed run via the API.
- The pilot's "Order" bullet still lists hp-01's unrun spans and P; both are complete (RUN_STATE 343, and P is dev-02). Left as text.

## Files

- Finalized items: `ITEM-dev02-s03.md`, `ITEM-dev03-pilot.md`, `ITEM-dev03-rest.md`, `ITEM-dev04-s01.md`, `ITEM-dev04-s02.md`, `ITEM-dev05-s01.md`, `ITEM-dev05-s02.md` (built by `tools/rl173.py` from the items-rl171 drafts; reproducible).
- `stage_mbp_span.sh`; `tools/rl173.py`, `tools/lint.py`; `tests/test_rl173_gates.py`, `tests/run_all_gates.sh`; `evidence/`.
- In git: audit/2026-11-10-fable, `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1115/`.
