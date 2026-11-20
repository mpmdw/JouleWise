# STANDING-F0 run 6: launch record (magistrate ade002e9, 2026-11-16)

Activation ade002e9 (headless, Opus 5.5), relaunched 18:11:34 PST Mon 16 Nov.

## Why now
- Item 374's hold on STANDING-F0 was lifted by the lead's item 376 (18:01:50 PST, "offload window closed").
- Trigger (c) NO_STAGED after F0 run 5's close (13:33:56): item 367 (`dev-04-s01`) cannot arm before Tue 00:00:00.
- Rule 5: last F0 t0 1794857683 (11:34:43); 14,400 s later is 15:34:43; this is the third F0 t0 of Mon 16 Nov.
- Rule 6: inside 02:35:00-22:40:00. Rule 7: no counted span due Mon (COUNTED_LATEST none).
- Rule 8: RESTART_PENDING no; HOST_RESTORE_OK 1 (item 373's restore lines clean); UNPROVEN_GROUP 0; HOLDING_STOP none.
- R-A: no v4 session READY record (SESSION_READY no). OUTSTANDING_REFUSAL none. OTHER_CLOSE_EPOCH 0; LAST_CLOSE_KIND other (F0 run 5), GAP 1,200 s.
- Item 374's packer condition: item 376 records the packer finished and `com.joulewise.icloudjob` removed; the census here shows no packer, tar/zstd, brctl or SSH session.

## Start and check (custody `f0-startcheck-out-ade002e9-2.txt`, 18:14:31 PST)
F0 ELIGIBLE; W1-line head `b2e01464d`; 17 hashes equal to the table (and to run 5's output line by line); `verify_r1_executed_sources` full sha; RL-89 MAC CHECK OK with the expected line exactly; plist test OK; night.lock no holder; sudo kill rc 0; no r12; no campaign span; no stray monitor or root powermetrics; Network Time Off; powermode 0; frequency word 0; no night/smoke agent; AC, not charging; free disk 330 GB. Agent-family processes are all in this magistrate's tree (NOTE 1).

## Deviation: where the RL-89 check reads r0.json
The first start-and-check (custody `f0-startcheck-out-ade002e9.txt`, 18:13:19) printed a FileNotFoundError for
`/Users/edr/night-align/r0-v4-20261108T0550Z/smc/r0.json`: the lead's 11-16 offload (item 376) packed that directory into
`r0-v4-20261108T0550Z.tar.zst` (iCloud `JouleWise-archive/mbp-packed/night-align/` and the Air SSD). The script carried on because it
has no errexit, so the RL-89 line was silently missing; the first output was not used.

Decision (mine; the check is a content check, and the bytes are what it tests):
1. Downloaded the archive; its sha256 `55d35336…5535` equals its receipt's `archive_sha256`.
2. Extracted only `smc/r0.json` to custody `standing-f0/r0-restore-ade002e9/r0.json` (12,015,502 bytes, sha256 `e6231a8f…769b`, the value the check expects). Re-evicted the archive. Nothing was written into `night-align`.
3. Pointed the check's `R0=` at that copy in both of this activation's scripts, and made the check fatal (`|| { echo STOP; exit 1; }`).
4. Re-ran start-and-check: RL-89 MAC CHECK OK with item 346's exact line.

Part C's runtime does not read `night-align`, `night-archive`, `night-b5` or `night-b6` (grep over the 17 pinned paths at `b2e01464d`; the only hit is `configs/align/v4/w1_smoke.json`, a W1 list Part C does not use). The Check script (`standing-f0/check-*/check.sh`) does not read them either.

**For the lead:** item 346's text names the old path. Later activations should reuse `f0-{startcheck,run}-ade002e9.sh` (or re-extract the same way). The start-and-check script has no errexit: a failing Python assert prints a traceback and the script still ends rc 0, so every line must be read, not the rc.

## Launch
`f0-run-ade002e9.sh` re-runs the full eligibility check and launches as this activation's last action. t0, OUT, DEADLINE, rc and launcher JSON: custody `r1-partc-f0-out-ade002e9.txt` (a STOP, WAIT, HOLD or LAUNCH_RC other than 0 there means nothing ran).
Expected about 2 h (end ~20:20 PST); worst case launch + 12,180 s (~21:45); fence launch + 14,400 s (~22:20).

## Next
The first activation after the fence is gone runs item 346's Check (reuse `standing-f0/check-d4b2584f/check.sh` with the new OUT and r0-launches plist id), compares it line by line with item 373's run, and reports it. Then item 367 (`dev-04-s01`) from Tue 00:00:00 under its own gates, close interval 1,200 s after this F0's close.
