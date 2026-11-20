# STANDING-F0 run 5 (item 346) pre-launch record, magistrate 1292492b (headless, Opus 5.5), 2026-11-16 11:34 PST

Trigger (c) NO_STAGED after `dev-03-s02` (dev-03's remainder, L004-L012) closed clean at 11:16:18 PST (RUN_STATE 370): the only staged counted item, 367 (`dev-04-s01`), cannot arm before Tue 00:00:00, more than 2 h 30 min after that close. Ladder (rule 3): no v4 session READY record, no hp-01 or P item staged; F0 is the rung. OUTSTANDING_REFUSAL none.

Scripts: custody `f0-startcheck-1292492b.sh` and `f0-run-1292492b.sh`, identical to d59960c1's except the header: MAGISTRATE_PID 10464, TRIGGER_SPAN after-dev-03-s02-close, own TMPDIR (diff: four lines). Output: custody `f0-startcheck-out-1292492b.txt`.

Start and check, 11:32:52-11:33:48 PST, every line passed:
- F0 ELIGIBLE at 1794857617; host last close 1794856579 (campaign, GAP 300 s; census 17 receipts, newest the dev-03-s02 receipt).
- Journal copy of `cq-dev-03-s02-a1`: the lead's marker, written 11:32:13 PST (files=324, manifest sha256 `284f6531…8b30`); the MBP offload waiter saw it and did nothing (custody `offload-dev03-s02-out-1292492b.txt`). A first Start-and-check at 11:23 stopped WAIT on the absent marker, as designed.
- W1-line head `b2e01464d` (fetched), not expired (2026-11-22 11:51:24), 17 hashes equal to the item's table, RL-89 MAC CHECK OK, `verify_r1_executed_sources` OK, plist test OK, `night.lock` no holder, sudo kill rc 0, no r12, no campaign span, no stray monitor or root powermetrics, Network Time Off, powermode 0, frequency word 0 (`ntp_adjtime` freq 0, status 0x2081), no night/smoke agent, AC (ExternalConnected Yes, IsCharging No, InstantAmperage 0), preflight ac_power true, free 67.1 GB.
- Agent-family processes: only this magistrate (10464) and its MCP children (NOTE 1).
- HOST_RESTORE_OK 1 (RUN_STATE 370's restore lines), UNPROVEN_GROUP 0, HOLDING_STOP none, OTHER_CLOSE_EPOCH 0, SESSION_READY no, RESTART_PENDING no, COUNTED_LATEST none.
- Spacing (rule 5): last F0 t0 1794835956 (Mon 05:32:36), so 14,400 s passed at 09:32:36; this is the second F0 t0 of Mon 16 Nov (cap 3). Launch window (rule 6) 02:35-22:40: inside. Rule 7: no counted span due Mon remains.
- Batch print: next OS batch Tue 17 Nov 02:08:39 PST.

Plan: fresh soak then Part C only on `b2e01464d` in `/Users/edr/code/jw-wt/partc-b2e01464d`; OUT (from Start and check) `.desk/r1-partc-f0-20261116T193338Z` (Run re-derives it; the custody out file has the one used); expected ~2 h (end ~13:35), worst case launch + 12,180 s (~14:58), fence launch + 14,400 s (~15:35).

Run: `f0-run-1292492b.sh` re-runs the whole eligibility check on fresh state and launches; t0, OUT, DEADLINE, rc and the launcher JSON go to custody `r1-partc-f0-out-1292492b.txt` (a "STOP", "WAIT", "HOLD" or LAUNCH_RC other than 0 there means nothing ran). The launch is this activation's last action.
