# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (44,357 entries, 00:02:53-03:05:54 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L007.a1 | yes | 00:39:55-01:00:39 | 3,201 | 0 | 0 | 0 | 36 | 0 | 0 |
| L008.a1 | yes | 01:00:39-01:21:30 | 3,854 | 0 | 0 | 0 | 15 | 8 | 2,116 |
| L009.a1 | yes | 01:21:31-01:42:27 | 3,264 | 0 | 0 | 0 | 6 | 0 | 1,291 |
| L010.a1 | yes | 01:42:28-02:03:25 | 3,028 | 0 | 0 | 0 | 24 | 0 | 3 |
| L011.a1 | no (redone: cpu_load) | 02:03:26-02:24:05 | 8,866 | 794 | 73 | 0 | 15 | 9 | 3,568 |
| L011.a2 | yes | 02:24:06-02:45:07 | 3,252 | 0 | 5 | 0 | 6 | 0 | 615 |
| L012.a1 | yes | 02:45:07-03:06:03 | 3,454 | 0 | 0 | 0 | 33 | 8 | 404 |

## By phase (named jobs with any entry)

- **L007.a1**
  - pre-G0 00:39:55-00:48:34: backupd 6, dasd 1,214
  - G0 00:48:34-00:51:55: dasd 461
  - G0->turn 00:51:55-00:51:55: none
  - turn 00:51:55-00:59:14: dasd 1,116
  - post-turn 00:59:14-01:00:39: backupd 30, dasd 410
- **L008.a1**
  - pre-G0 01:00:39-01:09:20: backupd 9, dasd 1,353
  - G0 01:09:20-01:12:42: backupd 6, dasd 892, softwareupdated 8
  - G0->turn 01:12:42-01:12:42: none
  - turn 01:12:42-01:20:02: dasd 1,265
  - post-turn 01:20:02-01:21:30: dasd 344, mobileassetd 2,116
- **L009.a1**
  - pre-G0 01:21:31-01:30:10: dasd 1,174, mobileassetd 1,291
  - G0 01:30:10-01:33:34: dasd 435
  - G0->turn 01:33:34-01:33:34: none
  - turn 01:33:34-01:40:54: dasd 1,239
  - post-turn 01:40:54-01:42:27: backupd 6, dasd 416
- **L010.a1**
  - pre-G0 01:42:28-01:51:07: dasd 1,087
  - G0 01:51:07-01:54:38: backupd 24, dasd 480, mobileassetd 3
  - G0->turn 01:54:38-01:54:38: none
  - turn 01:54:38-02:01:59: dasd 1,103
  - post-turn 02:01:59-02:03:25: dasd 358
- **L011.a1**
  - pre-G0 02:03:26-02:12:08: XProtect* 600, backupd 15, dasd 5,949, mds 37, mobileassetd 3,003, softwareupdated 1
  - G0 02:12:08-02:15:20: XProtect* 54, dasd 1,229, mds 21, mobileassetd 347, softwareupdated 8
  - after-G0 (turn+post; rejected attempt, turn stamps not read) 02:15:20-02:24:05: XProtect* 140, dasd 1,688, mds 15, mobileassetd 218
- **L011.a2**
  - pre-G0 02:24:06-02:32:45: dasd 1,155, mds 5, mobileassetd 614
  - G0 02:32:45-02:36:20: dasd 392, mobileassetd 1
  - G0->turn 02:36:20-02:36:20: none
  - turn 02:36:20-02:43:40: backupd 6, dasd 1,347
  - post-turn 02:43:40-02:45:07: dasd 358
- **L012.a1**
  - pre-G0 02:45:07-02:53:46: backupd 24, dasd 1,219, mobileassetd 404
  - G0 02:53:46-02:57:17: dasd 471
  - G0->turn 02:57:17-02:57:17: none
  - turn 02:57:17-03:04:37: backupd 9, dasd 1,376, softwareupdated 8
  - post-turn 03:04:37-03:06:03: dasd 388

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 00:00 | 1,249 | 0 | 6 | 0 | 12 | 8 | 0 |
| 00:10 | 1,609 | 0 | 0 | 0 | 6 | 8 | 3 |
| 00:20 | 1,559 | 0 | 0 | 0 | 0 | 0 | 0 |
| 00:30 | 1,684 | 0 | 0 | 0 | 0 | 0 | 3 |
| 00:40 | 1,624 | 0 | 0 | 0 | 6 | 0 | 0 |
| 00:50 | 1,448 | 0 | 0 | 0 | 30 | 0 | 0 |
| 01:00 | 1,854 | 0 | 0 | 0 | 9 | 0 | 0 |
| 01:10 | 1,799 | 0 | 0 | 0 | 6 | 8 | 0 |
| 01:20 | 1,518 | 0 | 0 | 0 | 0 | 0 | 3,652 |
| 01:30 | 1,433 | 0 | 0 | 0 | 0 | 0 | 0 |
| 01:40 | 1,693 | 0 | 0 | 0 | 6 | 0 | 0 |
| 01:50 | 1,569 | 0 | 0 | 0 | 24 | 0 | 3 |
| 02:00 | 5,620 | 594 | 21 | 0 | 9 | 1 | 2,805 |
| 02:10 | 2,893 | 163 | 52 | 0 | 6 | 8 | 762 |
| 02:20 | 1,538 | 37 | 0 | 0 | 0 | 0 | 179 |
| 02:30 | 1,532 | 0 | 5 | 0 | 0 | 0 | 437 |
| 02:40 | 1,600 | 0 | 0 | 0 | 6 | 0 | 400 |
| 02:50 | 1,748 | 0 | 0 | 0 | 24 | 8 | 4 |
| 03:00 | 1,064 | 0 | 0 | 0 | 9 | 0 | 0 |

Other process names in the query output: XprotectService 3. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 22,702; not read further.
