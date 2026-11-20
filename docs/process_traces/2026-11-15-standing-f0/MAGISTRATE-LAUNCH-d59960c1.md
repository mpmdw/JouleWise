# STANDING-F0 run 4 (item 346) pre-launch record, magistrate d59960c1 (headless, Opus 5.5), 2026-11-16 05:31 PST

Trigger (c) NO_STAGED after the dev-03 counted pilot `dev-03-s01` closed clean at 05:10:07 PST (RUN_STATE 363): no staged counted item remains (items 354 and 355 are used; dev-03's remainder L004-L012 needs the lead's hand-read and its own item), so no staged gate can hold within 2 h 30 min of that close. Ladder (rule 3): no v4 session READY record, no hp-01 or P item staged; F0 is the rung. OUTSTANDING_REFUSAL none.

Scripts: custody `f0-startcheck-d59960c1.sh` and `f0-run-d59960c1.sh`, identical to c93b67ee's (themselves item 346's text verbatim after the header; the item text on `origin/main` `cd1c9bdeb` is unchanged, `grep -vxF` leaves only the header and print lines in the scripts and only the Check-section lines in the item) except the header: MAGISTRATE_PID 81977, TRIGGER_SPAN after-dev-03-s01-close, LAST_CLOSE_KIND campaign, own TMPDIR. Output: custody `f0-startcheck-out-d59960c1.txt`.

Start and check, 05:31:10-05:31:13 PST, every line passed:
- F0 ELIGIBLE at 1794835871; host last close 1794834608 (campaign, GAP 300 s; census 15 receipts, newest the dev-03-s01 receipt).
- Journal copy of `cq-dev-03-s01-a1`: the lead's marker, written 05:22:53 PST (files=123, manifest sha256 `0489daf0…41eb`); the MBP offload waiter saw it and did nothing.
- W1-line head `b2e01464d` (fetched), not expired (2026-11-22 11:51:24), 17 hashes equal to the item's table (diff empty), RL-89 MAC CHECK OK, `verify_r1_executed_sources` OK, plist test OK, `night.lock` no holder, sudo kill rc 0, no r12, no campaign span, no stray monitor or root powermetrics, Network Time Off, powermode 0, frequency word 0 (`ntp_adjtime` freq 0, status 0x2081), no night/smoke agent, AC (ExternalConnected Yes, IsCharging No, InstantAmperage 0), preflight ac_power true.
- Agent-family processes: only this magistrate (81977) and its MCP children (NOTE 1).
- HOST_RESTORE_OK 1 (RUN_STATE 363's restore lines), UNPROVEN_GROUP 0, HOLDING_STOP none, OTHER_CLOSE_EPOCH 0, SESSION_READY no, RESTART_PENDING no (the launch is before 12:00 in any case), COUNTED_LATEST none.
- Spacing (rule 5): last F0 t0 1794806327 (Sun 21:18:47), so 14,400 s passed at 01:18:47; first F0 t0 of Mon 16 Nov (cap 3). Launch window (rule 6) 02:35-22:40: inside.
- Batch print: next OS batch Tue 17 Nov 02:08:39 PST.

Disk: before the arm, 7.3 GB of already-uploaded iCloud archive (`JouleWise-archive/2026-11-04-align-pilots`, `2026-10-05`) was evicted locally with `brctl evict` (client idle, caught-up, needs-upload 0; cloud copies kept; no measurement output, receipt or custody file touched); free disk 62 → 69 GiB. Log: custody `evict-archive-d59960c1.txt`.

Plan: fresh soak then Part C only on `b2e01464d` in `/Users/edr/code/jw-wt/partc-b2e01464d`; OUT (from Start and check) `.desk/r1-partc-f0-20261116T133111Z` (Run re-derives it; the custody out file has the one used); expected ~2 h (end ~07:35), worst case launch + 12,180 s (~08:55), fence launch + 14,400 s (~09:35).

Run: `f0-run-d59960c1.sh` re-runs the whole eligibility check on fresh state and launches; t0, OUT, DEADLINE, rc and the launcher JSON go to custody `r1-partc-f0-out-d59960c1.txt` (a "STOP", "WAIT", "HOLD" or LAUNCH_RC other than 0 there means nothing ran). The launch is this activation's last action.
