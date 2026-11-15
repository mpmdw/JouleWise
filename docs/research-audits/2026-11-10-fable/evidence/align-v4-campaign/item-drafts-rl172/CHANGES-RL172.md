# CHANGES-RL172: RL-172 and the Sol items-rl171 review, applied in place

Items builder, Sun 15 Nov 2026 00:40-00:50 PST (from `date`). Sources: RL-172 (`/Volumes/JW-EXT/scratch/fable-rl172.md`; audit branch `72414f3f9`), Sol's review (`/Volumes/JW-EXT/scratch/sol-items-rl171/REPORT.md`, FIX BEFORE ISSUE: 1 P1, 2 P2, 1 P3) and the lead's two messages. Nothing issued, committed or pushed; no SSH.

**How it is built.** `tools/build_*.py` re-create every item from the items-rl165 drafts. Then `tools/rl172.py` applies everything below in place. Rebuild order: `apply.py ../items-rl165/STANDING-F0.md STANDING-F0.md tools/edits_f0.py`, `build_hp01.py`, `build_dev02.py`, `build_dev03.py`, `build_dev0405.py`, `rl172.py`, then `lint.py`.

## Applied to every campaign item (hp01-s01 and dev02-s02 first; also dev02-s03, dev03-pilot, dev03-rest, dev04-s01, dev04-s02, dev05-s01, dev05-s02)

| Ruling or finding | Change |
|---|---|
| RL-172 §0 (the 300 s floor confirmed) | `QUIET_CAMPAIGN_S=300` is set, no longer a LEAD FILLS. It stays 1,200 s after F0, F2 or any other close. |
| RL-172 (f) | RL-165 §7's line `launch + WORST_S + 1200 <= SESSION_T0` and its `SESSION_T0` variable are removed. `SESSION_READY` now means the lead's READY record: the span cedes, and the session takes the next clean close. The prose and record lists are updated to match. |
| RL-172 (h) | A print-only line in Start and check computes the next OS batch from `sysctl -n kern.boottime`: boot + 12 h + 48 s + whole days, local. It is added to the arm record. Tested on the Air: boot 11-14 11:18:13 gives the next batch at 11-15 23:19:01. |
| Sol P1 (journal copy) | New `copy_gate`. After a campaign close (`LAST_CLOSE_KIND=campaign`), it finds the newest `runner_receipt.json` under `campaign-out` and derives its plan id (`cq-<span>-a1`). It requires `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok` and records the file's content; a missing marker is WAIT (exit 1). It runs in Start and check, before the kit and OUT exist, and in Run, right after the host-close census. After a Part C or F0 close it passes, because the Check covers that copy. The host-gate prose now says the lead writes the marker only after the copy is hash-verified, and that no SSH happens once a span is armed. |
| Sol P3 | When the band changes between Start and Run, the message is now "do not launch; mail the lead (a re-issue or a re-plan)". A stale argument is still refused. |
| Retry after a WAIT | `git worktree add` now runs only if the path does not exist. The KIT guard no longer stops on an existing file: the kit is re-written from git and its sha asserted. A WAIT (copy marker, close interval, day gate) can therefore be retried by running Start and check again. |

## RL-172 (a) day law (replaces the two-starts default; Sol P2)

- Every development item carries the day-law bullet: at most 12 mixed-size and at most 24 development legs per t0-date; qualification dates disjoint; hp-01, F0, F2 and sessions outside the count; a missed date is re-dated by the lead and never doubled up. The bullet names the item's own date.
- **New `day_gate`**, run in Start (before the kit) and in Run (after the census). It reads only the `started.epoch_s` and `roster` of the receipts under `campaign-out/cl-dev-0*/` whose t0 falls on today's local date. It refuses this span if it would exceed 24 development legs, or, for dev-03/04/05, 12 mixed-size legs. Synthetic test (`tmp/gatetest2/`): with dev-02-s03 and dev-03's 3 + 9 on the date, a mixed six-leg span is refused and a non-mixed one admitted, in both bash and zsh.
- **Windows re-dated.** Bands were regenerated, and every band end re-checked with the pinned `plan` (`plans/bands/verify-*.txt`, no BAD).

| Item | t0-date | Window (local / epoch) | Bands | Pointer deadline |
|---|---|---|---|---|
| dev02-s02 | Sun 15 Nov | 00:00:00-23:59:59 (1794729600-1794815999), unchanged | unchanged | Mon 08:17 |
| dev02-s03 | Mon 16 Nov | 00:00:00-23:59:59 (1794816000-1794902399), unchanged | unchanged | Tue 12:47 |
| dev03-pilot | **Mon 16 Nov** | 00:00:00-23:59:59 (1794816000-1794902399) | alt to 02:34:59; default 02:35-10:50, 13:15-20:48:10; alt after | Tue 06:02 |
| dev03-rest | **Mon 16 Nov** | same | alt to 02:34:59; default 02:35-10:50, 13:15-16:18:10; alt after | Tue 10:32 |
| dev04-s01, s02 | **Tue 17 Nov** | 00:00:00-23:59:59 (1794902400-1794988799) | alt to 02:34:59; default 02:35-10:50, 13:15-18:33:10; alt after | Wed 08:17 |
| dev05-s01, s02 | **Wed 18 Nov** | 00:00:00-23:59:59 (1794988800-1795075199) | as dev-04 | Thu 08:17 |

- New forecasts:
  - dev-04-s01: Tue 00:00:00 with `13:14-13:15`, expected end 02:55:07, worst end 06:52:30.
  - dev-04-s02: Tue 03:00:07 with `02:00-02:35`, expected end 06:21:18.
  - dev-05-s01: Wed 00:00:00 with `13:14-13:15`, expected end 03:14:40.
  - dev-05-s02: Wed 03:19:40 with `02:00-02:35`, expected end 06:21:18.
- Each item's text states that the queues' `not_before` values are lower bounds only. **The queue files were not touched:** dev-05's committed 11-17 is a lower bound under its Wednesday window.
- dev-04 and dev-05's "Why" lines now cite RL-172 (a) in place of RL-165 §1's "follow at their first legal t0". dev-04-s02's "Next" and dev-03-rest's "Next" name the new dates.

## STANDING-F0

- `QUIET_CAMPAIGN_S=300` (RL-172 §0).
- Rule 3's R-A is replaced by RL-172 (f): from the lead's READY record, nothing lower arms. The `SESSION_T0` check is removed from the gate's Python.
- `copy_gate` runs inside `f0_eligible` after a campaign close.
- **RL-172 (h) restart hold:** new required variable `RESTART_PENDING`. While it is `yes`, F0 is held after 12:00 until the lead records the restart done (rule 8 text).
- The batch-time print is in Start and check.

## PLAN.md and plans/chain.py

- **Day map:** Sat 7, Sun 11, Mon 18, Tue 12, Wed 12. The restart is modelled at Sun 14:08 (20 min assumed), with no F0 after 12:00 before it.
- **Gaps:** 300 s after a campaign close, 1,200 s after F0, F2 or the restart (Sol P2: the F2 forecast now uses 1,200 s after every F0 or F2 close).
- The F0 ladder now rolls over to the next 02:35, or the next day when three F0s have run.
- **Idle, Sun to Wed:** 40.16 h, against 52.13 h for the RL-165 chain (11.97 h saved). 25.29 h of it is idle for day balance and 1.52 h the restart. With F2 if READY: 31.90 h, of which 17.02 h is day balance. Development ends Wed 06:21:18.

## Checks

- `tools/lint.py`: every `sh` block passes `bash -n` and `zsh -n`, and every Python heredoc compiles (BAD 0).
- `plans/bands.py` re-ran the CLI `plan` at every band start, end and end + 1 s for the re-dated items (asserts pass).

## Still open for the lead

- Write the `desk-copy` markers, from the first campaign close on. Item 331's s04 close is the first one the hp-01 smoke needs (`cq-dev-01-s04-a1.ok`).
- Set `RESTART_PENDING` in the F0 activation and record the restart host event.
- If a slipped date leaves a block without a date, re-date it with a new item.
- hp-01-s02 and hp-01-s03 items are still not drafted. They need the same copy gate, (f) and (h) lines.

## Added Sun 15 Nov 00:52 PST: ITEM-hp01-s02.md and ITEM-hp01-s03.md

- **Built by `tools/build_hp01_rem.py`**, run after `rl172.py`. They reuse the smoke item's Start, Run, Check and restore-owed blocks, with this span's roster, worktree, plan id, worst case and deadline:
  - s02: L004-L007, worst case 19,350 s, deadline launch + 20,810 s.
  - s03: L008-L012, worst case 22,050 s, deadline launch + 23,510 s.
- **Gates carried over from the smoke:** copy gate; RL-172 (f) cede; the (h) batch print; the 300 s / 1,200 s gap; the 00:30 rule.
- **No `day_gate`.** RL-172 (a) rule 4 puts hp-01 outside the development count and sets no hp-01 date. RL-149 §2.3 says "any day after dev-01".
- **Bands** (`plans/bands_hp.py`; each band end checked with the pinned `plan`, and each end set by the bytes refused 1 s later): Sun and Mon, `13:14-13:15` 00:30:01-02:34:59, `02:00-02:35` 02:35-10:50, and `02:00-02:35` from 13:15.
  - The 00:30 rule closes the evening at 19:07:30 for s02 and 18:22:30 for s03. Nothing launches from then until 00:30:00, nor 10:50-13:15.
  - LIMIT is Mon 19:07:30 (1794884850) for s02 and Mon 18:22:30 (1794882150) for s03. The pointer deadline is Tue 01:55 for both.
- **s02's own gates:** the smoke closed and checked; R9 PASSED and the lead's hand-read recorded; no `high_power.revoked` entry and no LEG_OVERTIME pending; line 2 base + 0 on `2a8deb7b9` (run 43673985768 has the same 12 reds as run 43600776368 at `fe907d0d3`); line 9 `dev-01-s04`'s desk FINAL; the mirror append committed.
- **s03's own gates:** s02 closed clean; line 9 the smoke's desk FINAL.
- **Queue:** `QUEUE-cl-hp-01-dd206025a-append-mirror-4plus5.json` (sha `01687bb7…`), not committed here.
  - Its first span equals the committed `90e042ed…` queue.
  - `validate-queue` is ok at `dd206025a`, with `--kits-root` set to a `bbd34dc87` checkout (`wt/bbd34dc87`, kit `7eaf2660`). Log: `queue/validate-queue-hp01.log`.
- **Lint:** BAD 0, including both new items.

## Sol RL-172 re-check (Sun 15 Nov 01:00-01:06 PST): both findings fixed through the pipeline

The whole build now runs as `zsh tools/build_all.sh`. The new gate texts live in `tools/rl172_gates.py`. Every item with the gates was rebuilt: hp01-s01/s02/s03, dev02-s02/s03, dev03-pilot/rest, dev04-s01/s02, dev05-s01/s02, and STANDING-F0 (`f0_eligible`).

1. **copy_gate is bound to one newest-close selection.**
   - A new `close_census` walks both roots (`campaign-out` and `jw-wt`) with the old census rules (missing root, lookup error or empty result all STOP; mtimes rounded up). It returns both the epoch and the receipt path.
   - The Run host gate and F0's eligibility check now call `close_census` in place of their old census, and `copy_gate` uses the same function.
   - **The newest close.** It is the census receipt, unless `OTHER_CLOSE_EPOCH` is later. `OTHER_CLOSE_EPOCH` is now required in Start too: a whole epoch or an explicit 0.
   - **Its kind.** It is campaign only if its path matches `^/Users/edr/campaign-out/cl-[a-z0-9-]+/cq-[a-z0-9-]+-a[0-9]+-[0-9]{8}T[0-9]{6}Z/runner_receipt\.json$`; anything else is other.
   - **A mismatch with `LAST_CLOSE_KIND` STOPs:** "contradictory LAST_CLOSE_KIND (...): newest close is <path>". The marker comes only from a campaign receipt's plan id (`cq-…-aN`, which is checked); after a non-campaign close the gate passes and the Check covers the copy.
2. **day_gate validates what it reads.**
   - It reads only `started.epoch_s` and `roster`.
   - Unreadable JSON, a non-object, or a missing or non-numeric (or boolean) `started.epoch_s` STOPs with "receipt started.epoch_s unreadable: <path>".
   - A counted receipt's roster must be a non-empty list of unique strings matching `^L\d{3}$`. Anything else STOPs with "receipt roster unreadable: <path>", never zero.
   - **Also added (RL-172 (a) rule 3, Sol's diagnostic):** a same-date `cl-qual-*` receipt STOPs any development span ("qualification t0-date").

**Tests.**
- **`tests/gates_test.py`, run on the built items in bash and zsh: 30 of 30 as expected.** Sol's four states:
  - wrong kind with the old marker: STOP;
  - wrong kind with the wrong marker: STOP;
  - stale kind with an F0 receipt under `jw-wt`: STOP;
  - correct `other`: PASS.
  - Further cases: campaign with marker PASS, without marker WAIT, `other` with a newest campaign close STOP, a non-campaign dir under `campaign-out` STOP, a newer session with kind `other` PASS and with kind `campaign` STOP, unset `OTHER_CLOSE_EPOCH` STOP, empty census STOP.
  - day_gate cases: valid PASS, cap exceeded STOP; roster missing, null, `{}`, string, empty, duplicate, bad id or integer all STOP; started missing, no epoch, string or bool all STOP; another date ignored; non-JSON STOP; qualification same date STOP, other date PASS.
  - Results: `tests/gates-results-*.json`.
- **Sol's replay harness** was copied to `tests/sol-recheck-copy/` (its own results are untouched). In my copy, one line was patched so the extractor also picks up `close_census`. **115 replays: 109 match Sol's expectations.**
  - The six that differ are hp01-s01 and dev02-s02 `copy-other`, `gap-other-1200` and `gap-other-1201`. Their fixtures set `LAST_CLOSE_KIND=other` while the newest close is a campaign receipt; under the binding rule they now STOP as contradictory, and that is the intended change.
  - All four of Sol's wrong-kind and stale-kind replays now stop with no launch, and `newest-f0-correct-other` launches.
  - `run-day-roster-missing` and `run-day-qualification-conflict` now stop with no launch.
- **Lint:** BAD 0.

## Sol confirm-pass P1 (Sun 15 Nov 01:10-01:15 PST): copy_gate no longer touches the host gate's variables

- **`close_census`** now writes only `CENSUS`, `CENSUS_EPOCH` and `NEWEST_RECEIPT`.
- **New `effective_close`** computes the newest close once: the larger of the census and `OTHER_CLOSE_EPOCH` (validated), as `EFF_EPOCH` and `EFF_PATH`.
  - The Run host gate and F0's eligibility check call it once, then set `HOST_LAST_CLOSE=$EFF_EPOCH`. That value drives GAP, and copy_gate's kind check reads the same `EFF_PATH`.
  - Start calls `effective_close` and then `copy_gate`.
- **`copy_gate`** is a subshell function, `copy_gate() ( ... )`. It reads `EFF_PATH` and `LAST_CLOSE_KIND` and writes nothing the host gate reads; its locals are lower-case.
- **Tests: `tests/gates_test2.py`**, on the built items in bash and zsh with a fixed `date +%s`: **43 of 43 OK.** (It replaces `gates_test.py`, whose extractor predates the subshell form.) The 43 cases are, for both hp01-s01 and dev02-s02:
  - Sol's four states, plus campaign with marker PASS, without marker WAIT, and a newer session with kind `campaign` STOP.
  - **The Run excerpt** (`effective_close` → `HOST_LAST_CLOSE` → `copy_gate` [→ `day_gate`] → the GAP check):

    | Close | Elapsed | Result |
    |---|---|---|
    | Campaign close | 299 s | WAIT |
    | Campaign close | 300 s | PASS |
    | `OTHER_CLOSE_EPOCH` close | 1 s (Sol's bug case) | WAIT |
    | `OTHER_CLOSE_EPOCH` close | 1,199 s | WAIT |
    | `OTHER_CLOSE_EPOCH` close | 1,200 s | PASS |
    | F0 receipt under jw-wt | 1,199 s | WAIT |
    | F0 receipt under jw-wt | 1,200 s | PASS |
    | `OTHER_CLOSE_EPOCH` newer, kind `campaign` | – | STOP |

  - **day_gate's roster, started and qualification cases** (on dev03-pilot): all as expected.
- **Sol's harness copy** (`tests/sol-recheck-copy/`): the extractor now also takes `effective_close` and the subshell form, and its copy-only cases call `effective_close && copy_gate`. **115 replays: 109 match**, and the same six intentional differences remain (the `copy-other` and `gap-other-*` fixtures with a contradictory kind).
- **Lint:** BAD 0.

## STANDING-F0 re-pinned to the W1-line head b2e01464d (Sun 15 Nov 04:00-04:11 PST; RL-172b condition 3, RL-172c)

The new step `tools/repin_f0.py` runs in `build_all.sh` after `rl172.py`. The pre-re-pin text is saved as `plans/STANDING-F0.at-c3f4bacd8.md` and the diff as `plans/STANDING-F0.repin.diff`. All RL-172 gates are kept: `effective_close`, `copy_gate`, `RESTART_PENDING`, rule 9's 20 min after F0, and the 300 s / 1,200 s gap.

- **Pin.** `b2e01464d6d4fbf2901ff4d4154df9455104a12a` (merge of PR #790). Parents are `e5b4f4f7f` (#798's merge) and `ca02c76e3` (#790's head). Its tree is `c904864e46879a4adfbdf0b467d4da1ee5928285`, equal to `ca02c76e3`'s: RL-172c's tree.
  - The worktree is now `/Users/edr/code/jw-wt/partc-b2e01464d`.
  - The VOID test and the HEAD checks name the new sha.
  - The tree check is now `HEAD^{tree}` = `c904864e…`. It replaces "tree equals #783's head", which no longer holds.
  - Ancestor checks added for `c3f4bacd8`, `e5b4f4f7f` and `ca02c76e3`, next to the old three.
- **Hashes.** All 17 were recomputed at `b2e01464d` (`probe/hashes-b2e01464d.txt`). Sixteen are unchanged. `joulewise/align/apple/v4_registration.py` changed from `6815d1b6…` to `28caceeb…`: one added line, `EXECUTED_CLOSURE` gaining `v4_desk_seal.py`. `R1_EXECUTED_SOURCES` is unchanged and `verify_r1_executed_sources` returns the new sha.
  - Checked on the Air: the item's table equals its HASHES heredoc, every hash matches the worktree, the tree matches, and all six ancestors hold.
- **Re-derived from the bytes** (`probe/b2e01464d-derived.txt`):
  - `OS_BATCH_WINDOW_LOCAL` is still 02:00-02:35.
  - The soak child still refuses a soak start in (22:50:40, 02:35:00): 22:50:40 admitted, 22:50:41 refused, 02:34:59 refused, 02:35:00 admitted. Span = 1,800 + 9,560 = 11,360 s.
  - `r1_minimum_seconds('C', fresh_soak=True)` is still 12,180 s, and `MAX_DESK_SECONDS` is 43,200 s.
  - Rule 6's window is unchanged at 02:35:00-22:40:00, so the latest launch is still 22:40:00.
  - The launcher has no dry or plan path. I did not run `launch`, because it bootstraps a LaunchAgent. The numbers come from the launcher's own functions at the pin.
- **The six dry-check modules ran on the Air at `b2e01464d`:** all OK (1, 31, 15, 58, 24 and 24 tests; one skip; `probe/tests-b2e01464d.log`). Item 325's `c3f4bacd8` result no longer lets the MBP skip them: the marker file is now `tests-ok-b2e01464d`.
- **Line 2.** CI `ci` 43706817774 on `ca02c76e3`: success. That tree is `b2e01464d`'s, so the diff is empty over every path.
  - The push run on `b2e01464d` itself (43712204542) was still queued at 04:11. It is a LEAD FILLS for its conclusion.
  - The frozen-path diff `c3f4bacd8` → `b2e01464d` over the 17 paths is `v4_registration.py` only (+1 line).
- **Part C carry.** Item 325's counted pass at `c3f4bacd8` carries under RL-172b §2 and RL-172c, so F0 runs here are diagnostics compared with it.
