# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (30,800 entries, 03:23:32-05:51:02 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L007.a1 | yes | 03:58:47-04:14:46 | 3,084 | 0 | 0 | 0 | 48 | 8 | 0 |
| L008.a1 | yes | 04:14:47-04:35:38 | 3,779 | 0 | 0 | 0 | 0 | 0 | 3 |
| L009.a1 | yes | 04:35:39-04:54:39 | 3,007 | 0 | 0 | 0 | 6 | 0 | 0 |
| L010.a1 | yes | 04:54:39-05:10:56 | 2,806 | 899 | 0 | 0 | 42 | 2,619 | 2,056 |
| L011.a1 | yes | 05:10:57-05:31:56 | 3,417 | 0 | 0 | 0 | 6 | 9 | 4 |
| L012.a1 | yes | 05:31:57-05:51:02 | 3,088 | 0 | 0 | 0 | 6 | 0 | 129 |

## By phase (named jobs with any entry)

- **L007.a1**
  - pre-G0 03:58:47-04:05:56: backupd 12, dasd 1,133
  - G0 04:05:56-04:08:08: backupd 30, dasd 493
  - G0->turn 04:08:08-04:08:08: none
  - turn 04:08:08-04:13:41: backupd 6, dasd 1,220, softwareupdated 8
  - post-turn 04:13:41-04:14:46: dasd 238
- **L008.a1**
  - pre-G0 04:14:47-04:23:25: dasd 1,409
  - G0 04:23:25-04:26:50: dasd 505
  - G0->turn 04:26:50-04:26:50: none
  - turn 04:26:50-04:34:11: dasd 1,772, mobileassetd 3
  - post-turn 04:34:11-04:35:38: dasd 93
- **L009.a1**
  - pre-G0 04:35:39-04:43:27: backupd 6, dasd 1,174
  - G0 04:43:27-04:47:00: dasd 699
  - G0->turn 04:47:00-04:47:00: none
  - turn 04:47:00-04:53:21: dasd 829
  - post-turn 04:53:21-04:54:39: dasd 305
- **L010.a1**
  - pre-G0 04:54:39-05:01:49: backupd 27, dasd 901
  - G0 05:01:49-05:04:17: dasd 305
  - G0->turn 05:04:17-05:04:17: none
  - turn 05:04:17-05:09:50: XProtect* 899, backupd 15, dasd 1,132, mobileassetd 2,045, softwareupdated 2,597
  - post-turn 05:09:50-05:10:56: dasd 468, mobileassetd 11, softwareupdated 22
- **L011.a1**
  - pre-G0 05:10:57-05:19:36: backupd 6, dasd 1,461, mobileassetd 1, softwareupdated 9
  - G0 05:19:36-05:23:11: dasd 466
  - G0->turn 05:23:11-05:23:11: none
  - turn 05:23:11-05:30:33: dasd 1,131, mobileassetd 3
  - post-turn 05:30:33-05:31:56: dasd 359
- **L012.a1**
  - pre-G0 05:31:57-05:39:45: dasd 1,271
  - G0 05:39:45-05:43:22: backupd 6, dasd 593
  - G0->turn 05:43:22-05:43:22: none
  - turn 05:43:22-05:49:43: dasd 907, mobileassetd 129
  - post-turn 05:49:43-05:51:02: dasd 317

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 03:20 | 1,334 | 0 | 6 | 0 | 3 | 9 | 0 |
| 03:30 | 1,477 | 0 | 0 | 0 | 0 | 0 | 69 |
| 03:40 | 1,468 | 0 | 0 | 0 | 6 | 0 | 0 |
| 03:50 | 1,549 | 0 | 0 | 0 | 0 | 0 | 122 |
| 04:00 | 1,741 | 0 | 0 | 0 | 42 | 0 | 0 |
| 04:10 | 1,730 | 0 | 0 | 0 | 6 | 8 | 0 |
| 04:20 | 2,116 | 0 | 0 | 0 | 0 | 0 | 3 |
| 04:30 | 1,758 | 0 | 0 | 0 | 0 | 0 | 0 |
| 04:40 | 1,559 | 0 | 0 | 0 | 6 | 0 | 0 |
| 04:50 | 1,478 | 0 | 0 | 0 | 0 | 0 | 0 |
| 05:00 | 1,787 | 899 | 0 | 0 | 42 | 2,597 | 2,045 |
| 05:10 | 1,714 | 0 | 0 | 0 | 6 | 31 | 12 |
| 05:20 | 1,542 | 0 | 0 | 0 | 0 | 0 | 3 |
| 05:30 | 1,680 | 0 | 0 | 0 | 0 | 0 | 0 |
| 05:40 | 1,723 | 0 | 0 | 0 | 6 | 0 | 129 |
| 05:50 | 94 | 0 | 0 | 0 | 0 | 0 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 24,717; not read further.

## Rule 5 placement and judgement (PROPOSED)

MAINTENANCE-OVERLAP.md (RL-171 section 5; print only, gates nothing). Judged by the template's rule 5: >0.5 core held 60 seconds (consecutive journal samples); no_drop_by_outcome, no log-count exclusion.
L010.a1: software-update / MobileAsset scan 05:08-05:09 begins 05:08:45; XProtect and XProtectPluginService finish 05:09:03. Wholly inside L010 turn 05:04:17-05:09:50 (attempt 04:54:39-05:10:56; G0 05:01:49-05:04:17). Within turn: softwareupdated 2,597, mobileassetd 2,045, XProtect* 899 = XProtectPluginService 843 + XProtect 56. This agrees with item 382, whose 843 count explicitly names XProtectPluginService; the template groups both under XProtect*. Tails: mobileassetd 11 and softwareupdated 22 during L010 post-turn (05:09:50-05:10:56), and sparse entries later in L011 pre-G0 (05:13), shown in minute output. Longest >0.5-core run is 4 samples, 05:09:53-05:09:56 (914.2-917.2 s), post-turn; run max 1.013 cores, attempt max 2.361. Does not fire; recorded clean; no redo owed.
All six counted attempts pass: L007 3, L008 2, L009 1, L010 4, L011 3, L012 2 samples of the 60 required. All load journals cover their attempts. No redo, no leg excluded, none refilled; maintenance overlap does not independently exclude a leg.
