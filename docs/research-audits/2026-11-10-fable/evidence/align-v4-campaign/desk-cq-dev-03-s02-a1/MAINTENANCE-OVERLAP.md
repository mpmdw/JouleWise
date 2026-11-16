# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (43,677 entries, 07:52:04-11:15:58 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L004.a1 | yes | 08:27:22-08:46:15 | 2,844 | 0 | 0 | 0 | 6 | 0 | 1 |
| L005.a1 | yes | 08:46:16-09:02:38 | 2,645 | 0 | 0 | 0 | 24 | 0 | 0 |
| L006.a1 | yes | 09:02:39-09:23:34 | 5,082 | 0 | 32 | 0 | 15 | 8 | 1,360 |
| L007.a1 | yes | 09:23:35-09:42:46 | 3,046 | 0 | 0 | 0 | 6 | 0 | 37 |
| L008.a1 | yes | 09:42:47-09:59:10 | 2,307 | 0 | 0 | 0 | 24 | 0 | 3 |
| L009.a1 | yes | 09:59:11-10:20:06 | 3,751 | 0 | 0 | 0 | 15 | 8 | 0 |
| L010.a1 | yes | 10:20:07-10:36:21 | 2,645 | 0 | 0 | 0 | 0 | 0 | 3 |
| L011.a1 | yes | 10:36:21-10:57:18 | 2,947 | 0 | 0 | 0 | 6 | 0 | 69 |
| L012.a1 | yes | 10:57:19-11:16:17 | 3,511 | 612 | 0 | 0 | 42 | 2,613 | 2,060 |

## By phase (named jobs with any entry)

- **L004.a1**
  - pre-G0 08:27:22-08:35:12: dasd 993, mobileassetd 1
  - G0 08:35:12-08:38:37: dasd 651
  - G0->turn 08:38:37-08:38:37: none
  - turn 08:38:37-08:44:55: backupd 6, dasd 960
  - post-turn 08:44:55-08:46:15: dasd 240
- **L005.a1**
  - pre-G0 08:46:16-08:53:25: dasd 1,174
  - G0 08:53:25-08:55:58: dasd 235
  - G0->turn 08:55:58-08:55:58: none
  - turn 08:55:58-09:01:31: backupd 24, dasd 1,124
  - post-turn 09:01:31-09:02:38: dasd 112
- **L006.a1**
  - pre-G0 09:02:39-09:11:18: backupd 9, dasd 1,786
  - G0 09:11:18-09:14:42: backupd 6, dasd 861, softwareupdated 8
  - G0->turn 09:14:42-09:14:42: none
  - turn 09:14:42-09:22:02: dasd 2,030, mds 32, mobileassetd 1,360
  - post-turn 09:22:02-09:23:34: dasd 405
- **L007.a1**
  - pre-G0 09:23:35-09:31:25: dasd 1,307, mobileassetd 34
  - G0 09:31:25-09:35:06: dasd 398
  - G0->turn 09:35:06-09:35:06: none
  - turn 09:35:06-09:41:26: dasd 1,100, mobileassetd 3
  - post-turn 09:41:26-09:42:46: backupd 6, dasd 241
- **L008.a1**
  - pre-G0 09:42:47-09:49:58: dasd 1,036
  - G0 09:49:58-09:52:28: backupd 24, dasd 459, mobileassetd 3
  - G0->turn 09:52:28-09:52:28: none
  - turn 09:52:28-09:58:00: dasd 765
  - post-turn 09:58:00-09:59:10: dasd 47
- **L009.a1**
  - pre-G0 09:59:11-10:07:51: backupd 9, dasd 1,530
  - G0 10:07:51-10:11:22: dasd 682
  - G0->turn 10:11:22-10:11:22: none
  - turn 10:11:22-10:18:42: backupd 6, dasd 1,489, softwareupdated 8
  - post-turn 10:18:42-10:20:06: dasd 50
- **L010.a1**
  - pre-G0 10:20:07-10:27:16: dasd 1,188, mobileassetd 3
  - G0 10:27:16-10:29:41: dasd 425
  - G0->turn 10:29:41-10:29:41: none
  - turn 10:29:41-10:35:14: dasd 754
  - post-turn 10:35:14-10:36:21: dasd 278
- **L011.a1**
  - pre-G0 10:36:21-10:45:00: backupd 6, dasd 1,423, mobileassetd 69
  - G0 10:45:00-10:48:31: dasd 377
  - G0->turn 10:48:31-10:48:31: none
  - turn 10:48:31-10:55:51: dasd 1,110
  - post-turn 10:55:51-10:57:18: dasd 37
- **L012.a1**
  - pre-G0 10:57:19-11:05:07: backupd 33, dasd 1,452
  - G0 11:05:07-11:08:40: dasd 457
  - G0->turn 11:08:40-11:08:40: none
  - turn 11:08:40-11:15:00: XProtect* 612, backupd 9, dasd 1,334, mobileassetd 2,060, softwareupdated 2,613
  - post-turn 11:15:00-11:16:17: dasd 268

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 07:50 | 1,154 | 0 | 6 | 0 | 27 | 8 | 122 |
| 08:00 | 3,152 | 0 | 0 | 0 | 9 | 0 | 218 |
| 08:10 | 1,757 | 0 | 0 | 0 | 6 | 8 | 166 |
| 08:20 | 1,596 | 0 | 0 | 0 | 0 | 0 | 182 |
| 08:30 | 1,311 | 0 | 0 | 0 | 0 | 0 | 0 |
| 08:40 | 1,585 | 0 | 0 | 0 | 6 | 0 | 0 |
| 08:50 | 1,744 | 0 | 0 | 0 | 24 | 0 | 0 |
| 09:00 | 2,076 | 0 | 0 | 0 | 9 | 0 | 0 |
| 09:10 | 1,716 | 0 | 0 | 0 | 6 | 8 | 0 |
| 09:20 | 2,786 | 0 | 32 | 0 | 0 | 0 | 1,394 |
| 09:30 | 1,406 | 0 | 0 | 0 | 0 | 0 | 3 |
| 09:40 | 1,574 | 0 | 0 | 0 | 6 | 0 | 0 |
| 09:50 | 1,511 | 0 | 0 | 0 | 24 | 0 | 3 |
| 10:00 | 1,602 | 0 | 0 | 0 | 9 | 0 | 0 |
| 10:10 | 1,904 | 0 | 0 | 0 | 6 | 8 | 0 |
| 10:20 | 1,671 | 0 | 0 | 0 | 0 | 0 | 3 |
| 10:30 | 1,498 | 0 | 0 | 0 | 0 | 0 | 69 |
| 10:40 | 1,521 | 0 | 0 | 0 | 6 | 0 | 0 |
| 10:50 | 1,504 | 0 | 0 | 0 | 24 | 0 | 0 |
| 11:00 | 1,603 | 612 | 0 | 0 | 12 | 2,573 | 2,045 |
| 11:10 | 1,311 | 0 | 0 | 0 | 6 | 40 | 15 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 29,705; not read further.
