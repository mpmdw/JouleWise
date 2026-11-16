# Per-leg OS maintenance overlap (RL-171 §5; print only, gates nothing)

Source: `maintenance-log.txt` (20,885 entries, 03:38:30-05:09:57 PST). Only process name, time and count were read. Counts are log entries, not CPU time.

| leg.attempt | counted | wall (PST) | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|---|---|
| L001.a1 | yes | 04:13:47-04:29:57 | 2,610 | 0 | 0 | 0 | 0 | 0 | 0 |
| L002.a1 | yes | 04:29:58-04:50:50 | 3,266 | 0 | 0 | 0 | 6 | 0 | 3 |
| L003.a1 | yes | 04:50:50-05:10:06 | 3,377 | 612 | 0 | 0 | 36 | 2,598 | 2,217 |

## By phase (named jobs with any entry)

- **L001.a1**
  - pre-G0 04:13:47-04:20:58: dasd 1,013
  - G0 04:20:58-04:23:14: dasd 342
  - G0->turn 04:23:14-04:23:14: none
  - turn 04:23:14-04:28:46: dasd 810
  - post-turn 04:28:46-04:29:57: dasd 445
- **L002.a1**
  - pre-G0 04:29:58-04:38:37: dasd 1,353
  - G0 04:38:37-04:42:06: backupd 6, dasd 621
  - G0->turn 04:42:06-04:42:06: none
  - turn 04:42:06-04:49:26: dasd 1,039, mobileassetd 3
  - post-turn 04:49:26-04:50:50: dasd 253
- **L003.a1**
  - pre-G0 04:50:50-04:58:40: dasd 1,221
  - G0 04:58:40-05:02:21: backupd 24, dasd 507
  - G0->turn 05:02:21-05:02:21: none
  - turn 05:02:21-05:08:41: backupd 9, dasd 1,097, mobileassetd 173
  - post-turn 05:08:41-05:10:06: XProtect* 612, backupd 3, dasd 552, mobileassetd 2,044, softwareupdated 2,598

## 10-minute buckets (named jobs)

| bucket | dasd | XProtect* | mds | mdworker* | backupd | softwareupdated | mobileassetd |
|---|---|---|---|---|---|---|---|
| 03:30 | 318 | 0 | 6 | 0 | 3 | 8 | 0 |
| 03:40 | 1,419 | 0 | 0 | 0 | 6 | 0 | 0 |
| 03:50 | 1,599 | 0 | 0 | 0 | 24 | 0 | 122 |
| 04:00 | 1,587 | 0 | 0 | 0 | 9 | 0 | 0 |
| 04:10 | 1,959 | 0 | 0 | 0 | 6 | 8 | 3 |
| 04:20 | 1,693 | 0 | 0 | 0 | 0 | 0 | 0 |
| 04:30 | 1,689 | 0 | 0 | 0 | 0 | 0 | 0 |
| 04:40 | 1,327 | 0 | 0 | 0 | 6 | 0 | 3 |
| 04:50 | 1,587 | 0 | 0 | 0 | 0 | 0 | 0 |
| 05:00 | 2,040 | 612 | 0 | 0 | 36 | 2,598 | 2,217 |

Other process names in the query output: none. Lines without a leading timestamp (continuation lines of multi-line messages, and the header): 18,678; not read further.
