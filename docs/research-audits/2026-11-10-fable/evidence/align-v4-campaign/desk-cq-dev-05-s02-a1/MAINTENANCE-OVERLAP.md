# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (28,269 entries, 03:32:00-06:00:00 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L007.a1 | yes | 04:07:23-04:28:11 | 3,311 | 0 | 0 | 0 | 6 | 8 | 169 |
| L008.a1 | yes | 04:28:11-04:44:24 | 2,773 | 0 | 0 | 0 | 36 | 2 | 5 |
| L009.a1 | yes | 04:44:25-05:03:48 | 2,071 | 0 | 0 | 0 | 0 | 0 | 0 |
| L010.a1 | yes | 05:03:49-05:20:02 | 3,087 | 612 | 0 | 0 | 24 | 2,636 | 2,125 |
| L011.a1 | yes | 05:20:03-05:40:51 | 2,610 | 0 | 0 | 0 | 27 | 0 | 0 |
| L012.a1 | yes | 05:40:52-06:00:00 | 2,675 | 0 | 0 | 0 | 6 | 0 | 3 |

## By phase (named jobs with any entry)

- **L007.a1**
  - pre-G0 04:07:23-04:16:01: backupd 6, dasd 1,372, mobileassetd 169, softwareupdated 8
  - G0 04:16:01-04:19:27: dasd 463
  - G0->turn 04:19:27-04:19:27: none
  - turn 04:19:27-04:26:45: dasd 1,212
  - post-turn 04:26:45-04:28:11: dasd 264
- **L008.a1**
  - pre-G0 04:28:11-04:35:20: backupd 30, dasd 1,285, mobileassetd 3
  - G0 04:35:20-04:37:43: dasd 499
  - G0->turn 04:37:43-04:37:43: none
  - turn 04:37:43-04:43:16: backupd 6, dasd 921, mobileassetd 2, softwareupdated 2
  - post-turn 04:43:16-04:44:24: dasd 68
- **L009.a1**
  - pre-G0 04:44:25-04:52:15: dasd 790
  - G0 04:52:15-04:56:02: dasd 582
  - G0->turn 04:56:02-04:56:02: none
  - turn 04:56:02-05:02:21: dasd 659
  - post-turn 05:02:21-05:03:48: dasd 40
- **L010.a1**
  - pre-G0 05:03:49-05:10:59: XProtect* 612, backupd 18, dasd 1,734, mobileassetd 2,113, softwareupdated 2,602
  - G0 05:10:59-05:13:21: backupd 6, dasd 402, mobileassetd 11, softwareupdated 33
  - G0->turn 05:13:21-05:13:21: none
  - turn 05:13:21-05:18:54: dasd 703, mobileassetd 1, softwareupdated 1
  - post-turn 05:18:54-05:20:02: dasd 248
- **L011.a1**
  - pre-G0 05:20:03-05:28:42: dasd 1,164
  - G0 05:28:42-05:32:09: dasd 616
  - G0->turn 05:32:09-05:32:09: none
  - turn 05:32:09-05:39:28: dasd 728
  - post-turn 05:39:28-05:40:51: backupd 27, dasd 102
- **L012.a1**
  - pre-G0 05:40:52-05:48:40: backupd 6, dasd 1,324
  - G0 05:48:40-05:52:21: dasd 514, mobileassetd 3
  - G0->turn 05:52:21-05:52:21: none
  - turn 05:52:21-05:58:40: dasd 770
  - post-turn 05:58:40-06:00:00: dasd 67

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 03:30 | 1,588 | 0 | 6 | 0 | 3 | 9 | 0 |
| 03:40 | 1,493 | 0 | 0 | 0 | 6 | 0 | 0 |
| 03:50 | 1,177 | 0 | 5 | 0 | 0 | 0 | 559 |
| 04:00 | 1,346 | 0 | 0 | 0 | 48 | 0 | 166 |
| 04:10 | 1,680 | 0 | 0 | 0 | 6 | 8 | 4 |
| 04:20 | 1,934 | 0 | 0 | 0 | 0 | 0 | 0 |
| 04:30 | 1,535 | 0 | 0 | 0 | 30 | 0 | 3 |
| 04:40 | 1,477 | 0 | 0 | 0 | 6 | 2 | 2 |
| 04:50 | 1,275 | 0 | 0 | 0 | 0 | 0 | 0 |
| 05:00 | 1,695 | 612 | 0 | 0 | 18 | 2,595 | 2,110 |
| 05:10 | 1,266 | 0 | 0 | 0 | 6 | 41 | 15 |
| 05:20 | 1,412 | 0 | 0 | 0 | 0 | 0 | 0 |
| 05:30 | 1,332 | 0 | 0 | 0 | 0 | 0 | 0 |
| 05:40 | 1,448 | 0 | 0 | 0 | 33 | 0 | 0 |
| 05:50 | 1,305 | 0 | 0 | 0 | 0 | 0 | 3 |
| 06:00 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 19,547; not read further.
