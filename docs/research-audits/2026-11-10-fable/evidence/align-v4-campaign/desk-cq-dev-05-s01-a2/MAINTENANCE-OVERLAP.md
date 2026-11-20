# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (38,183 entries, 00:35:20-03:19:39 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L001.a1 | yes | 01:10:42-01:30:12 | 2,745 | 0 | 0 | 0 | 6 | 8 | 3,658 |
| L002.a1 | yes | 01:30:13-01:46:27 | 2,964 | 0 | 0 | 0 | 51 | 0 | 0 |
| L003.a1 | yes | 01:46:28-02:07:20 | 2,222 | 0 | 0 | 0 | 51 | 0 | 0 |
| L004.a1 | no (redone: cpu_load) | 02:07:21-02:23:45 | 7,643 | 794 | 71 | 0 | 36 | 9 | 3,360 |
| L004.a2 | yes | 02:23:45-02:40:03 | 2,324 | 0 | 0 | 0 | 0 | 0 | 179 |
| L005.a1 | yes | 02:40:04-03:01:00 | 2,273 | 0 | 0 | 0 | 6 | 0 | 398 |
| L006.a1 | yes | 03:01:01-03:20:07 | 3,387 | 0 | 0 | 0 | 21 | 8 | 0 |

## By phase (named jobs with any entry)

- **L001.a1**
  - pre-G0 01:10:42-01:18:33: backupd 6, dasd 1,139, mobileassetd 3, softwareupdated 8
  - G0 01:18:33-01:22:30: dasd 660, mobileassetd 3,652
  - G0->turn 01:22:30-01:22:30: none
  - turn 01:22:30-01:28:49: dasd 899, mobileassetd 3
  - post-turn 01:28:49-01:30:12: dasd 47
- **L002.a1**
  - pre-G0 01:30:13-01:37:23: dasd 1,485
  - G0 01:37:23-01:39:50: backupd 45, dasd 270
  - G0->turn 01:39:50-01:39:50: none
  - turn 01:39:50-01:45:22: backupd 6, dasd 730
  - post-turn 01:45:22-01:46:27: dasd 479
- **L003.a1**
  - pre-G0 01:46:28-01:55:06: dasd 746
  - G0 01:55:06-01:58:36: backupd 36, dasd 580
  - G0->turn 01:58:36-01:58:36: none
  - turn 01:58:36-02:05:55: backupd 15, dasd 867
  - post-turn 02:05:55-02:07:20: dasd 29
- **L004.a1**
  - pre-G0 02:07:21-02:14:37: XProtect* 745, backupd 36, dasd 6,303, mds 71, mobileassetd 2,600, softwareupdated 9
  - G0 02:14:37-02:17:02: XProtect* 12, dasd 235, mobileassetd 525
  - after-G0 (turn+post; rejected attempt, turn stamps not read) 02:17:02-02:23:45: XProtect* 37, dasd 1,105, mobileassetd 235
- **L004.a2**
  - pre-G0 02:23:45-02:30:55: dasd 1,004, mobileassetd 179
  - G0 02:30:55-02:33:23: dasd 119
  - G0->turn 02:33:23-02:33:23: none
  - turn 02:33:23-02:38:56: dasd 678
  - post-turn 02:38:56-02:40:03: dasd 523
- **L005.a1**
  - pre-G0 02:40:04-02:48:45: backupd 6, dasd 1,021, mobileassetd 379
  - G0 02:48:45-02:52:17: dasd 525, mobileassetd 18
  - G0->turn 02:52:17-02:52:17: none
  - turn 02:52:17-02:59:36: dasd 704, mobileassetd 1
  - post-turn 02:59:36-03:01:00: dasd 23
- **L006.a1**
  - pre-G0 03:01:01-03:08:50: backupd 15, dasd 1,484
  - G0 03:08:50-03:12:28: backupd 6, dasd 1,070, softwareupdated 8
  - G0->turn 03:12:28-03:12:28: none
  - turn 03:12:28-03:18:47: dasd 810
  - post-turn 03:18:47-03:20:07: dasd 23

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 00:30 | 767 | 0 | 6 | 0 | 3 | 8 | 0 |
| 00:40 | 1,283 | 0 | 0 | 0 | 6 | 3 | 6 |
| 00:50 | 1,309 | 0 | 0 | 0 | 33 | 0 | 1,014 |
| 01:00 | 1,363 | 0 | 0 | 0 | 18 | 0 | 0 |
| 01:10 | 1,358 | 0 | 0 | 0 | 6 | 8 | 3 |
| 01:20 | 1,537 | 0 | 0 | 0 | 0 | 0 | 3,655 |
| 01:30 | 1,784 | 0 | 0 | 0 | 45 | 0 | 0 |
| 01:40 | 1,328 | 0 | 0 | 0 | 6 | 0 | 0 |
| 01:50 | 1,201 | 0 | 0 | 0 | 36 | 0 | 0 |
| 02:00 | 5,407 | 306 | 23 | 0 | 45 | 1 | 2,426 |
| 02:10 | 2,664 | 488 | 48 | 0 | 6 | 8 | 933 |
| 02:20 | 1,409 | 0 | 0 | 0 | 0 | 0 | 180 |
| 02:30 | 1,328 | 0 | 0 | 0 | 0 | 0 | 0 |
| 02:40 | 1,076 | 0 | 0 | 0 | 6 | 0 | 397 |
| 02:50 | 1,209 | 0 | 0 | 0 | 0 | 0 | 1 |
| 03:00 | 1,720 | 0 | 0 | 0 | 15 | 0 | 0 |
| 03:10 | 1,687 | 0 | 0 | 0 | 6 | 8 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 13,142; not read further.
