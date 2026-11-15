# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (20,693 entries, 05:09:57-07:09:28 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L004.a1 | yes | 05:46:30-06:07:11 | 3,215 | 0 | 0 | 0 | 33 | 0 | 3 |
| L005.a1 | yes | 06:07:12-06:28:01 | 3,532 | 0 | 0 | 0 | 6 | 8 | 0 |
| L006.a1 | yes | 06:28:01-06:48:50 | 3,404 | 0 | 0 | 0 | 30 | 0 | 176 |
| L007.a1 | yes | 06:48:51-07:09:38 | 3,627 | 0 | 0 | 0 | 48 | 0 | 4 |

## By phase (named jobs with any entry)

- **L004.a1**
  - pre-G0 05:46:30-05:55:07: dasd 1,392, mobileassetd 3
  - G0 05:55:07-05:58:28: backupd 24, dasd 451
  - G0->turn 05:58:28-05:58:28: none
  - turn 05:58:28-06:05:46: backupd 9, dasd 1,235
  - post-turn 06:05:46-06:07:11: dasd 137
- **L005.a1**
  - pre-G0 06:07:12-06:15:49: backupd 6, dasd 1,806, softwareupdated 8
  - G0 06:15:49-06:19:17: dasd 474
  - G0->turn 06:19:17-06:19:17: none
  - turn 06:19:17-06:26:36: dasd 1,131
  - post-turn 06:26:36-06:28:01: dasd 121
- **L006.a1**
  - pre-G0 06:28:01-06:36:39: backupd 24, dasd 1,170, mobileassetd 3
  - G0 06:36:39-06:40:03: dasd 732
  - G0->turn 06:40:03-06:40:03: none
  - turn 06:40:03-06:47:22: backupd 6, dasd 1,281, mobileassetd 165
  - post-turn 06:47:22-06:48:50: dasd 221, mobileassetd 8
- **L007.a1**
  - pre-G0 06:48:51-06:57:29: backupd 24, dasd 1,338, mobileassetd 4
  - G0 06:57:29-07:00:53: dasd 415
  - G0->turn 07:00:53-07:00:53: none
  - turn 07:00:53-07:08:12: backupd 24, dasd 1,437
  - post-turn 07:08:12-07:09:38: dasd 437

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 05:00 | 18 | 0 | 6 | 0 | 3 | 17 | 21 |
| 05:10 | 2,122 | 0 | 0 | 0 | 6 | 37 | 12 |
| 05:20 | 1,610 | 0 | 0 | 0 | 0 | 0 | 0 |
| 05:30 | 1,677 | 0 | 0 | 0 | 24 | 0 | 0 |
| 05:40 | 1,704 | 0 | 0 | 0 | 6 | 0 | 3 |
| 05:50 | 1,499 | 0 | 0 | 0 | 24 | 0 | 0 |
| 06:00 | 1,485 | 0 | 0 | 0 | 9 | 0 | 0 |
| 06:10 | 1,914 | 0 | 0 | 0 | 6 | 8 | 0 |
| 06:20 | 1,503 | 0 | 0 | 0 | 0 | 0 | 0 |
| 06:30 | 1,382 | 0 | 0 | 0 | 24 | 0 | 3 |
| 06:40 | 1,752 | 0 | 0 | 0 | 6 | 0 | 173 |
| 06:50 | 1,676 | 0 | 0 | 0 | 24 | 0 | 4 |
| 07:00 | 1,911 | 0 | 0 | 0 | 24 | 0 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 10,688; not read further.
