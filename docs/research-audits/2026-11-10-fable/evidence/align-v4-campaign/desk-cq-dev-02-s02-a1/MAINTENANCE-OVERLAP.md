# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (33,630 entries, 10:00:23-12:42:18 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L001.a1 | yes | 10:37:35-10:58:27 | 3,407 | 0 | 0 | 0 | 9 | 0 | 178 |
| L002.a1 | yes | 10:58:28-11:19:19 | 3,760 | 1,186 | 0 | 0 | 48 | 2,629 | 2,060 |
| L003.a1 | yes | 11:19:20-11:40:12 | 3,337 | 0 | 0 | 0 | 0 | 0 | 6 |
| L004.a1 | yes | 11:40:13-12:01:07 | 3,533 | 0 | 0 | 0 | 64 | 0 | 122 |
| L005.a1 | yes | 12:01:08-12:21:53 | 4,018 | 0 | 0 | 0 | 15 | 8 | 3 |
| L006.a1 | yes | 12:21:54-12:42:44 | 3,241 | 0 | 0 | 0 | 6 | 0 | 0 |

## By phase (named jobs with any entry)

- **L001.a1**
  - pre-G0 10:37:35-10:46:12: backupd 6, dasd 1,515, mobileassetd 178
  - G0 10:46:12-10:49:42: backupd 3, dasd 479
  - G0->turn 10:49:42-10:49:42: none
  - turn 10:49:42-10:57:01: dasd 1,153
  - post-turn 10:57:01-10:58:27: dasd 260
- **L002.a1**
  - pre-G0 10:58:28-11:07:06: backupd 39, dasd 1,523
  - G0 11:07:06-11:10:31: XProtect* 1,186, backupd 3, dasd 629, mobileassetd 2,044, softwareupdated 2,596
  - G0->turn 11:10:31-11:10:31: none
  - turn 11:10:31-11:17:51: backupd 6, dasd 1,571, mobileassetd 16, softwareupdated 33
  - post-turn 11:17:51-11:19:19: dasd 37
- **L003.a1**
  - pre-G0 11:19:20-11:27:59: dasd 1,342, mobileassetd 3
  - G0 11:27:59-11:31:26: dasd 458
  - G0->turn 11:31:26-11:31:26: none
  - turn 11:31:26-11:38:45: dasd 1,051
  - post-turn 11:38:45-11:40:12: dasd 486, mobileassetd 3
- **L004.a1**
  - pre-G0 11:40:13-11:48:51: backupd 10, dasd 1,619
  - G0 11:48:51-11:52:20: backupd 27, dasd 536
  - G0->turn 11:52:20-11:52:20: none
  - turn 11:52:20-11:59:39: backupd 27, dasd 1,197, mobileassetd 122
  - post-turn 11:59:39-12:01:07: dasd 181
- **L005.a1**
  - pre-G0 12:01:08-12:09:47: backupd 9, dasd 1,565, mobileassetd 3
  - G0 12:09:47-12:13:11: backupd 6, dasd 1,110, softwareupdated 8
  - G0->turn 12:13:11-12:13:11: none
  - turn 12:13:11-12:20:30: dasd 1,188
  - post-turn 12:20:30-12:21:53: dasd 155
- **L006.a1**
  - pre-G0 12:21:54-12:30:32: dasd 1,480
  - G0 12:30:32-12:33:57: dasd 424
  - G0->turn 12:33:57-12:33:57: none
  - turn 12:33:57-12:41:17: dasd 1,150
  - post-turn 12:41:17-12:42:44: backupd 6, dasd 187

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 10:00 | 1,493 | 0 | 6 | 0 | 12 | 9 | 0 |
| 10:10 | 1,928 | 0 | 0 | 0 | 6 | 8 | 0 |
| 10:20 | 1,481 | 0 | 0 | 0 | 0 | 0 | 0 |
| 10:30 | 1,459 | 0 | 0 | 0 | 0 | 0 | 174 |
| 10:40 | 1,592 | 0 | 0 | 0 | 9 | 0 | 4 |
| 10:50 | 1,481 | 0 | 0 | 0 | 0 | 0 | 0 |
| 11:00 | 2,025 | 1,186 | 0 | 0 | 42 | 2,596 | 2,044 |
| 11:10 | 1,920 | 0 | 0 | 0 | 6 | 33 | 16 |
| 11:20 | 1,259 | 0 | 0 | 0 | 0 | 0 | 3 |
| 11:30 | 1,782 | 0 | 0 | 0 | 0 | 0 | 0 |
| 11:40 | 1,839 | 0 | 0 | 0 | 10 | 0 | 3 |
| 11:50 | 1,653 | 0 | 0 | 0 | 54 | 0 | 122 |
| 12:00 | 1,663 | 0 | 0 | 0 | 9 | 0 | 3 |
| 12:10 | 1,976 | 0 | 0 | 0 | 6 | 8 | 0 |
| 12:20 | 1,720 | 0 | 0 | 0 | 0 | 0 | 0 |
| 12:30 | 1,489 | 0 | 0 | 0 | 0 | 0 | 0 |
| 12:40 | 495 | 0 | 0 | 0 | 6 | 0 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 24,665; not read further.
