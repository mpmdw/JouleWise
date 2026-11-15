# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (27,256 entries, 07:24:52-09:45:39 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L008.a1 | yes | 08:01:21-08:22:15 | 4,937 | 0 | 0 | 0 | 15 | 8 | 385 |
| L009.a1 | yes | 08:22:15-08:43:11 | 3,310 | 0 | 0 | 0 | 6 | 0 | 182 |
| L010.a1 | yes | 08:43:11-09:04:09 | 3,255 | 0 | 0 | 0 | 24 | 0 | 4 |
| L011.a1 | yes | 09:04:09-09:24:59 | 4,958 | 0 | 3 | 0 | 15 | 8 | 1,467 |
| L012.a1 | yes | 09:25:00-09:45:50 | 3,254 | 0 | 0 | 0 | 6 | 0 | 1 |

## By phase (named jobs with any entry)

- **L008.a1**
  - pre-G0 08:01:21-08:09:59: backupd 9, dasd 2,844, mobileassetd 208
  - G0 08:09:59-08:13:24: backupd 6, dasd 869, mobileassetd 176, softwareupdated 8
  - G0->turn 08:13:24-08:13:24: none
  - turn 08:13:24-08:20:42: dasd 1,163, mobileassetd 1
  - post-turn 08:20:42-08:22:15: dasd 61
- **L009.a1**
  - pre-G0 08:22:15-08:30:53: dasd 1,261, mobileassetd 179
  - G0 08:30:53-08:34:25: dasd 700
  - G0->turn 08:34:25-08:34:25: none
  - turn 08:34:25-08:41:44: backupd 6, dasd 1,217, mobileassetd 3
  - post-turn 08:41:44-08:43:11: dasd 132
- **L010.a1**
  - pre-G0 08:43:11-08:51:49: dasd 1,303
  - G0 08:51:49-08:55:22: dasd 714
  - G0->turn 08:55:22-08:55:22: none
  - turn 08:55:22-09:02:41: backupd 24, dasd 1,146, mobileassetd 4
  - post-turn 09:02:41-09:04:09: dasd 92
- **L011.a1**
  - pre-G0 09:04:09-09:12:47: backupd 15, dasd 1,846, mobileassetd 69, softwareupdated 8
  - G0 09:12:47-09:16:17: dasd 702
  - G0->turn 09:16:17-09:16:17: none
  - turn 09:16:17-09:23:36: dasd 2,246, mds 3, mobileassetd 1,398
  - post-turn 09:23:36-09:24:59: dasd 164
- **L012.a1**
  - pre-G0 09:25:00-09:33:37: dasd 1,299, mobileassetd 1
  - G0 09:33:37-09:37:01: dasd 569
  - G0->turn 09:37:01-09:37:01: none
  - turn 09:37:01-09:44:20: backupd 6, dasd 1,070
  - post-turn 09:44:20-09:45:50: dasd 316

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 07:20 | 696 | 0 | 6 | 0 | 3 | 8 | 0 |
| 07:30 | 1,237 | 0 | 0 | 0 | 0 | 0 | 0 |
| 07:40 | 1,597 | 0 | 0 | 0 | 6 | 0 | 3 |
| 07:50 | 1,432 | 0 | 0 | 0 | 24 | 0 | 122 |
| 08:00 | 3,128 | 0 | 0 | 0 | 9 | 0 | 208 |
| 08:10 | 1,777 | 0 | 0 | 0 | 6 | 8 | 177 |
| 08:20 | 1,544 | 0 | 0 | 0 | 0 | 0 | 179 |
| 08:30 | 1,565 | 0 | 0 | 0 | 0 | 0 | 3 |
| 08:40 | 1,693 | 0 | 0 | 0 | 6 | 0 | 0 |
| 08:50 | 1,586 | 0 | 0 | 0 | 24 | 0 | 4 |
| 09:00 | 1,727 | 0 | 0 | 0 | 9 | 0 | 69 |
| 09:10 | 1,726 | 0 | 0 | 0 | 6 | 8 | 3 |
| 09:20 | 2,845 | 0 | 3 | 0 | 0 | 0 | 1,396 |
| 09:30 | 1,486 | 0 | 0 | 0 | 0 | 0 | 0 |
| 09:40 | 921 | 0 | 0 | 0 | 6 | 0 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 13,379; not read further.
