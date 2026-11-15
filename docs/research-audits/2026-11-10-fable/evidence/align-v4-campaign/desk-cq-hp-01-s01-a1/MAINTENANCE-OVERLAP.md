# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (18,020 entries, 03:05:27-04:44:29 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L001.a1 | yes | 03:42:39-04:03:17 | 3,276 | 0 | 0 | 0 | 54 | 0 | 125 |
| L002.a1 | yes | 04:03:18-04:24:10 | 3,844 | 0 | 5 | 0 | 39 | 8 | 419 |
| L003.a1 | yes | 04:24:11-04:44:59 | 3,731 | 0 | 0 | 0 | 30 | 0 | 1 |

## By phase (named jobs with any entry)

- **L001.a1**
  - pre-G0 03:42:39-03:51:15: backupd 27, dasd 1,297, mobileassetd 3
  - G0 03:51:15-03:54:33: dasd 729, mobileassetd 122
  - G0->turn 03:54:33-03:54:33: none
  - turn 03:54:33-04:01:52: backupd 27, dasd 995
  - post-turn 04:01:52-04:03:17: dasd 255
- **L002.a1**
  - pre-G0 04:03:18-04:11:56: backupd 15, dasd 1,803, softwareupdated 8
  - G0 04:11:56-04:15:27: backupd 24, dasd 723, mobileassetd 3
  - G0->turn 04:15:27-04:15:27: none
  - turn 04:15:27-04:22:47: dasd 1,081, mds 5, mobileassetd 416
  - post-turn 04:22:47-04:24:10: dasd 237
- **L003.a1**
  - pre-G0 04:24:11-04:32:48: dasd 1,840, mobileassetd 1
  - G0 04:32:48-04:36:12: dasd 532
  - G0->turn 04:36:12-04:36:12: none
  - turn 04:36:12-04:43:31: backupd 30, dasd 1,124
  - post-turn 04:43:31-04:44:59: dasd 235

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 03:00 | 1,071 | 0 | 6 | 0 | 3 | 8 | 0 |
| 03:10 | 1,729 | 0 | 0 | 0 | 6 | 8 | 3 |
| 03:20 | 1,643 | 0 | 0 | 0 | 0 | 0 | 0 |
| 03:30 | 1,495 | 0 | 0 | 0 | 0 | 0 | 0 |
| 03:40 | 1,770 | 0 | 0 | 0 | 33 | 0 | 3 |
| 03:50 | 1,581 | 0 | 0 | 0 | 27 | 0 | 122 |
| 04:00 | 1,695 | 0 | 0 | 0 | 9 | 0 | 0 |
| 04:10 | 1,893 | 0 | 0 | 0 | 30 | 8 | 3 |
| 04:20 | 1,768 | 0 | 5 | 0 | 0 | 0 | 417 |
| 04:30 | 1,852 | 0 | 0 | 0 | 24 | 0 | 0 |
| 04:40 | 802 | 0 | 0 | 0 | 6 | 0 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 9,167; not read further.
