# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (41,858 entries, 00:01:53-02:50:33 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L001.a1 | yes | 00:37:16-00:55:58 | 2,679 | 0 | 0 | 0 | 6 | 0 | 0 |
| L002.a1 | yes | 00:55:58-01:16:44 | 4,122 | 0 | 0 | 0 | 51 | 16 | 3 |
| L003.a1 | yes | 01:16:44-01:33:02 | 2,574 | 0 | 0 | 0 | 0 | 0 | 3,651 |
| L004.a1 | yes | 01:33:02-01:52:17 | 3,219 | 0 | 0 | 0 | 9 | 0 | 0 |
| L005.a1 | yes | 01:52:18-02:08:39 | 2,613 | 0 | 0 | 0 | 27 | 0 | 0 |
| L006.a1 | no (redone: cpu_load) | 02:08:39-02:29:35 | 7,384 | 794 | 71 | 0 | 6 | 9 | 3,377 |
| L006.a2 | yes | 02:29:36-02:50:42 | 3,540 | 0 | 0 | 0 | 6 | 0 | 398 |

## By phase (named jobs with any entry)

- **L001.a1**
  - pre-G0 00:37:16-00:45:03: backupd 6, dasd 1,221
  - G0 00:45:03-00:48:24: dasd 436
  - G0->turn 00:48:24-00:48:24: none
  - turn 00:48:24-00:54:43: dasd 966
  - post-turn 00:54:43-00:55:58: dasd 56
- **L002.a1**
  - pre-G0 00:55:58-01:04:37: backupd 33, dasd 1,634, mobileassetd 3, softwareupdated 8
  - G0 01:04:37-01:07:59: backupd 12, dasd 839
  - G0->turn 01:07:59-01:07:59: none
  - turn 01:07:59-01:15:19: backupd 6, dasd 1,515, softwareupdated 8
  - post-turn 01:15:19-01:16:44: dasd 134
- **L003.a1**
  - pre-G0 01:16:44-01:23:56: dasd 1,284, mobileassetd 3,651
  - G0 01:23:56-01:26:21: dasd 382
  - G0->turn 01:26:21-01:26:21: none
  - turn 01:26:21-01:31:55: dasd 847
  - post-turn 01:31:55-01:33:02: dasd 61
- **L004.a1**
  - pre-G0 01:33:02-01:40:53: dasd 1,345
  - G0 01:40:53-01:44:34: backupd 6, dasd 736
  - G0->turn 01:44:34-01:44:34: none
  - turn 01:44:34-01:50:55: backupd 3, dasd 901
  - post-turn 01:50:55-01:52:17: dasd 237
- **L005.a1**
  - pre-G0 01:52:18-01:59:28: dasd 1,032
  - G0 01:59:28-02:01:59: dasd 226
  - G0->turn 02:01:59-02:02:00: none
  - turn 02:02:00-02:07:33: backupd 27, dasd 1,216
  - post-turn 02:07:33-02:08:39: dasd 139
- **L006.a1**
  - pre-G0 02:08:39-02:17:24: XProtect* 727, backupd 6, dasd 5,350, mds 71, mobileassetd 2,981, softwareupdated 9
  - G0 02:17:24-02:20:50: XProtect* 30, dasd 697, mobileassetd 217
  - after-G0 (turn+post; rejected attempt, turn stamps not read) 02:20:50-02:29:35: XProtect* 37, dasd 1,337, mobileassetd 179
- **L006.a2**
  - pre-G0 02:29:36-02:38:15: dasd 1,335, mobileassetd 1
  - G0 02:38:15-02:41:50: backupd 6, dasd 860
  - G0->turn 02:41:50-02:41:50: none
  - turn 02:41:50-02:49:10: dasd 1,082, mobileassetd 397
  - post-turn 02:49:10-02:50:42: dasd 263

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 00:00 | 1,642 | 0 | 6 | 0 | 15 | 8 | 0 |
| 00:10 | 1,851 | 0 | 0 | 0 | 6 | 8 | 3 |
| 00:20 | 1,612 | 0 | 0 | 0 | 0 | 0 | 0 |
| 00:30 | 1,288 | 0 | 0 | 0 | 0 | 0 | 0 |
| 00:40 | 1,580 | 0 | 0 | 0 | 6 | 0 | 0 |
| 00:50 | 1,763 | 0 | 0 | 0 | 33 | 8 | 3 |
| 01:00 | 1,590 | 0 | 0 | 0 | 12 | 0 | 0 |
| 01:10 | 2,018 | 0 | 0 | 0 | 6 | 8 | 0 |
| 01:20 | 1,646 | 0 | 0 | 0 | 0 | 0 | 3,651 |
| 01:30 | 1,672 | 0 | 0 | 0 | 0 | 0 | 0 |
| 01:40 | 1,644 | 0 | 0 | 0 | 9 | 0 | 0 |
| 01:50 | 1,444 | 0 | 0 | 0 | 0 | 0 | 0 |
| 02:00 | 5,175 | 0 | 0 | 0 | 27 | 1 | 1,323 |
| 02:10 | 3,267 | 757 | 71 | 0 | 6 | 8 | 1,875 |
| 02:20 | 1,659 | 37 | 0 | 0 | 0 | 0 | 180 |
| 02:30 | 1,659 | 0 | 0 | 0 | 0 | 0 | 0 |
| 02:40 | 1,618 | 0 | 0 | 0 | 6 | 0 | 397 |
| 02:50 | 260 | 0 | 0 | 0 | 0 | 0 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 22,116; not read further.

## Rule 5 placement and judgement (PROPOSED)

MAINTENANCE-OVERLAP.md (RL-171 section 5; print only, gates nothing). Judged by the template's rule 5: >0.5 core held 60 seconds (consecutive journal samples); no_drop_by_outcome, no log-count exclusion.
L003.a1: mobileassetd 3,651 entries at 01:21:26-01:21:44, wholly pre-G0 (01:16:44-01:23:56), before G0 01:23:56-01:26:21 and turn 01:26:21-01:31:55. Longest >0.5-core run 18 samples, 01:21:26-01:21:43 (282.1-299.1 s; run max 1.260 cores, attempt max 1.361); does not fire.
L006.a1: rejected cpu_load attempt 02:08:39-02:29:35, OS batch across pre-G0 02:08:39-02:17:24, G0 02:17:24-02:20:50, and after-G0 (turn+post) 02:20:50-02:29:35. Template does not open rejected attempt turn stamps, so exact rejected turn boundaries are not claimed. Attempt totals: dasd 7,384, mobileassetd 3,377, XProtect* 794, mds 71, softwareupdated 9, backupd 6. The 02:08-02:24 named burst sits within this rejected attempt (mobileassetd main activity begins 02:08:49; XProtect starts 02:11:03, ends 02:22:18). Longest >0.5-core run 232 consecutive samples, 587.1-818.1 s into attempt, 02:18:26-02:22:17 PST; run max 2.571 cores, attempt max 3.638. This run crosses G0 into after-G0; 232 >= 60: RULE 5 FIRES. Several other runs also fire (122, 131, 99 samples). Recorded contaminated true, redone true, redo_reason cpu_load; hand agrees. Redo correct, 1 of quota 2; a1 is not counted.
L006.a2: admitted 02:29:36-02:50:42; pre-G0 02:29:36-02:38:15, G0 02:38:15-02:41:50, turn 02:41:50-02:49:10. mobileassetd 379 entries in minute 02:46 (from 02:46:56) plus 18 in 02:47 (last 02:47:26), wholly inside turn (397 turn entries, plus 1 pre-G0). Longest >0.5-core run 32 samples 02:36:04-02:36:35, pre-G0, max 2.580 cores; other runs 16 and 3 samples, none reaches 60. Recorded clean; hand agrees; no further redo owed.
All counted attempts pass rule 5: L001 2, L002 4, L003 18, L004 1, L005 1, L006.a2 32 samples of 60; all load journals cover their attempts. No leg excluded, none refilled. Checks item 380 agrees: bursts are inside the named attempts; finer phase placement is recorded here.
