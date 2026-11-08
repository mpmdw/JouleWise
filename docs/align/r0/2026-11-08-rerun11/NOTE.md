# ALIGN v4 R0 re-run 11 (2026-11-07 21:41-23:45 PST): PASS, complete_r0 true, first run under R0-L3

- Record: `/Users/edr/night-align/r0-v4-20261108T0550Z` (created 05:41:15Z, finished 07:45:12Z; 7,436.8 s wall). Status `pass`, `complete_r0` true, `decisions_pending_lead_action` empty.
- Measurement checkout `9c40e4e5d` (R0-L3, #699), clean. Launched from canonical `31a19f79a` (#700). Launch id `904f09e216de43acad59d1b4f634c1f1`, deadline 04:30 PST (`1794141000`).
- Agents: activation 5bcfa84e exited 21:36:15 PST (watchdog event 6462, same second as `pmset displaysleepnow`); desk fence 21:38:21 (event 6463); the run's dwell ended 21:41:15; activation 17ca7bed spawned 23:48:30 (event 6465), after the run finished. No agent session was alive during the run.
- `report.json` sha256 `58b11e76998ceb8d9110cfe3e8509acd9e1e358845a08fff042092916443e2df`; `report.md` sha256 `392d25795cc1ccce546706c578c6a8fac988f666f1ff5408313798728c729e9c`.
- SMC journal `smc/samples.jsonl`, 98,573,955 bytes, sha256 `79998635cc29caa2810389584a895810413ff1cbd550a0182dae7bed32804b94`; `smc/r0.json` sha256 `e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b`; `smc/summary.md` sha256 `8366b6cba5d9326b20b01a841d60240b9f53d48feb81eb10a973d0401a2fb55e` (kept on the Mac, not committed).

## Checks
| Check | Status | Wall s |
|---|---|---|
| smc | pass (picks PROVISIONAL) | 1,896.3 |
| host | pass | 0.7 |
| disk | diagnostic (report-only) | 20.5 |
| host-identity | pass (Mac15,9, 137,438,953,472 B) | 0.7 |
| model-load (D) | pass | 14.1 |
| load (D) | pass | 88.6 |
| template (D) | diagnostic | 0.9 |
| generated (D) | pass (12 real turns, 0 off-spec echo) | 54.6 |
| checkpoint (D) | not_required (B7: rewind fraction 0.0 over 12 eligible transitions) | 0.9 |
| memory (D) | pass, peak 37,025,365,084 B (limit 45,000,000,000), swap unchanged | 744.4 |
| ladder (D) | pass, selected `medium` (xhigh failed: bad-cap fraction 0.25; medium 0.20) | 1,265.0 |
| long-decode (D) | pass, 38,912 decode tokens, KV trend 655,287,438 B per 10k | 3,316.9 |
| tool-envelopes (D) | pass, 28/28 parsed | 0.9 |

- SMC: `s_fast` = `TV0h` (alias `TV1h`), `s_slow` = `Tf08`; heat-ordering reference `TVh0`; 17 keys excluded from heat ordering; readability bar met.
- Load: NLL 11.0368 nats/token against the HF float32 reference 11.0642 (delta −0.0274); largest 256-target bin delta 0.207; no non-finite losses; reasons empty. Generation: greedy, 109 tokens, the requested tool `analyze_spam_patterns` called.
- D pins (`align_v4_verify_d_pins.py`): PASS, D @ `815b83c0…9ef9`, 19 files, 7 LFS sha256 matched (41 `.cache/huggingface/` bookkeeping files ignored, item 179).

## Contention (R0-L3: recorded, not fatal)
SMC capture not contended: 0 redos, 0 flagged intervals. Two guard flags, both in long-decode (D): `softwareupdated` pid 547 at 0.254 and 0.286 CPU-s/s over two overlapping 30 s intervals (monotonic 2,106,081-2,106,127 s, about 23:10 PST: the 23:09 softwareupdated scan on the known schedule). Below the 0.5-core redo bar; flags only.

## Display
Launcher `pmset displaysleepnow` exit 0 at 21:36:15 PST; dwell 300 s (constant 300 s), so the run is admissible under item 209. Display off at start, no transitions, no SMC display wake. `pmset -g log`: last "Display is turned off" 18:08:12 PST 11-07, no "Display is turned on" since.

## Other
- Spotlight: corespotlightd 716 and spotlightknowledged 73957 both `S` after the run.
- Launch agent `com.joulewise.align-r0.904f…` no longer loaded.

## Why the reports are not committed
GitHub push protection refused `report.json` (line 531,321): a model-generated tool-output string in the long-decode/ladder text contains a Stripe-test-key-shaped token. It is benchmark fixture text, not a credential, but push protection is not bypassed. `report.json` and `report.md` stay on the Mac at the record path above, pinned by the sha256 values above.
