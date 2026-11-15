# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (41,055 entries, 00:00:02-02:41:44 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L008.a1 | yes | 00:36:42-00:57:27 | 3,331 | 0 | 0 | 0 | 39 | 0 | 72 |
| L009.a1 | yes | 00:57:28-01:18:16 | 3,945 | 0 | 0 | 0 | 15 | 8 | 172 |
| L010.a1 | yes | 01:18:17-01:39:09 | 3,006 | 0 | 0 | 0 | 264 | 0 | 3,652 |
| L011.a1 | yes | 01:39:10-02:00:06 | 3,241 | 0 | 0 | 0 | 30 | 0 | 0 |
| L012.a1 | no (redone: cpu_load) | 02:00:06-02:21:00 | 8,900 | 794 | 73 | 0 | 15 | 9 | 3,362 |
| L012.a2 | yes | 02:21:01-02:41:44 | 3,351 | 0 | 0 | 0 | 0 | 0 | 180 |

## By phase (named jobs with any entry)

- **L008.a1**
  - pre-G0 00:36:42-00:45:20: backupd 6, dasd 1,386, mobileassetd 69
  - G0 00:45:20-00:48:40: dasd 459, mobileassetd 3
  - G0->turn 00:48:40-00:48:41: none
  - turn 00:48:41-00:55:59: backupd 33, dasd 1,126
  - post-turn 00:55:59-00:57:27: dasd 360
- **L009.a1**
  - pre-G0 00:57:28-01:06:07: backupd 9, dasd 1,434, mobileassetd 163
  - G0 01:06:07-01:09:31: dasd 542, mobileassetd 8
  - G0->turn 01:09:31-01:09:31: none
  - turn 01:09:31-01:16:50: backupd 6, dasd 1,576, mobileassetd 1, softwareupdated 8
  - post-turn 01:16:50-01:18:16: dasd 393
- **L010.a1**
  - pre-G0 01:18:17-01:26:57: dasd 1,363, mobileassetd 3,652
  - G0 01:26:57-01:30:24: dasd 415
  - G0->turn 01:30:24-01:30:24: none
  - turn 01:30:24-01:37:44: backupd 264, dasd 1,191
  - post-turn 01:37:44-01:39:09: dasd 37
- **L011.a1**
  - pre-G0 01:39:10-01:47:47: backupd 6, dasd 1,610
  - G0 01:47:47-01:51:18: dasd 423
  - G0->turn 01:51:18-01:51:18: none
  - turn 01:51:18-01:58:38: backupd 24, dasd 1,128
  - post-turn 01:58:38-02:00:06: dasd 80
- **L012.a1**
  - pre-G0 02:00:06-02:08:45: backupd 9, dasd 2,922, mobileassetd 3
  - G0 02:08:45-02:12:16: XProtect* 600, dasd 3,838, mds 37, mobileassetd 2,399, softwareupdated 1
  - after-G0 (turn+post; rejected attempt, turn stamps not read) 02:12:16-02:21:00: XProtect* 194, backupd 6, dasd 2,140, mds 36, mobileassetd 960, softwareupdated 8
- **L012.a2**
  - pre-G0 02:21:01-02:29:41: dasd 1,438, mobileassetd 179
  - G0 02:29:41-02:32:53: dasd 424, mobileassetd 1
  - G0->turn 02:32:53-02:32:53: none
  - turn 02:32:53-02:40:13: dasd 1,174
  - post-turn 02:40:13-02:41:44: dasd 315

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 00:00 | 1,810 | 0 | 9 | 0 | 27 | 9 | 0 |
| 00:10 | 1,986 | 0 | 0 | 0 | 9 | 8 | 0 |
| 00:20 | 1,660 | 0 | 0 | 0 | 0 | 0 | 0 |
| 00:30 | 1,515 | 0 | 0 | 0 | 0 | 0 | 69 |
| 00:40 | 1,665 | 0 | 0 | 0 | 6 | 0 | 3 |
| 00:50 | 1,499 | 0 | 0 | 0 | 33 | 0 | 0 |
| 01:00 | 1,843 | 0 | 0 | 0 | 9 | 0 | 171 |
| 01:10 | 1,877 | 0 | 0 | 0 | 6 | 8 | 1 |
| 01:20 | 1,644 | 0 | 0 | 0 | 0 | 0 | 3,652 |
| 01:30 | 1,561 | 0 | 0 | 0 | 264 | 0 | 0 |
| 01:40 | 1,607 | 0 | 0 | 0 | 6 | 0 | 0 |
| 01:50 | 1,293 | 0 | 0 | 0 | 24 | 0 | 0 |
| 02:00 | 5,857 | 591 | 20 | 0 | 9 | 1 | 2,212 |
| 02:10 | 2,994 | 166 | 53 | 0 | 6 | 8 | 1,150 |
| 02:20 | 1,495 | 37 | 0 | 0 | 0 | 0 | 179 |
| 02:30 | 1,370 | 0 | 0 | 0 | 0 | 0 | 1 |
| 02:40 | 626 | 0 | 0 | 0 | 6 | 0 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 20,898; not read further.
