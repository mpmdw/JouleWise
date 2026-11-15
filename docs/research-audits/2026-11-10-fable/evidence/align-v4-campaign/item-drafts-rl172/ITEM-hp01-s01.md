TBD. **Laptop lead (interactive, Opus 5.5), drafted by the hp01-ready builder, finalized by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm the hp-01 HIGH POWER SMOKE (RL-155 §5.2, RL-157 §8, RL-165 §5 to §7): kit `cl-hp-01`, legs L001, L002, L003 only (the calendar's H001-H003), span `hp-01-s01`, runner kind `cadence-legs-v1`, on `dd206025abb30fd5c07515cd4b34b3e653174810` checked out detached in a fresh scratch worktree. One span: a fresh soak in Automatic, then AC powermode 2 (High Power) set by the runner, then three type-H legs (type A in High Power: 19,458-token step prompt, decode cap 4,096, band q0), then the close restores Automatic and proves it. The three legs are hp-01's counted smoke (RL-150 R5; kit rule `hp_smoke_counted`); hp-01 is description only, never in the fit. No other span, no queue extension, no session, no W1. EARLIEST: the close interval after `dev-01-s04` closed with its fence gone (RL-171 §6.1; no clock floor), and not before 00:00:00 PST Sun 15 Nov (epoch 1794729600). LAUNCH as soon as every gate holds, at any hour (RL-171: quiet is the per-leg process and load checks, not a clock window), up to 19:52:30 PST Sun 15 Nov (LIMIT, epoch 1794801150: worst-case end by 00:30, RL-165 §7, which RL-171 §2 keeps), except 10:50:00-13:15:00 (this pin's soak path waits out 11:45-13:15 unbudgeted). The batch-window argument follows the launch time (RL-171 §3): `13:14-13:15` before 02:35:00, `02:00-02:35` from 02:35:00. The launch is your LAST action and you exit at once. If you cannot, do not launch; mail the lead (the standing F0 item then applies, RL-165 §3).**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-16T01:55:00-08:00
on_early_or_refused: any failed line of "Start and check", any launch refusal (rc≠0 or no claimed fence), a High Power marker or a held host night lock at the arm, or a launch that cannot happen inside (dev-01-s04's close + the close interval) to 19:52:30 PST Sun 15 Nov (epoch 1794801150), outside 10:50:00-13:15:00: NOTHING of this item launches; mail the lead (a Monday smoke needs a re-issued item). The standing F0 item's refusal rule then applies, unless the stop is RESTORE_UNPROVEN or a host-state stop, which hold everything. A span that ran but ends with any named stop, a receipt rc≠0, restore_proven not true, a High Power marker present or AC powermode not 0 at the Check: nothing relaunches, nothing is re-run, nothing else arms (RESTORE_UNPROVEN holds everything, F0 included); run restore-owed ONLY under "Restore owed" below; mail the lead. Do not retry, do not extend, do not reuse OUT
next_observable: the next activation (after the fence is gone) runs "Check" below and reports, by email to Ed and the lead and as RUN_STATE TBD+1: the magistrate's own power reads (AC powermode 0, no marker, no lock holder), the receipt asserts with restore_proven and the close proof, the D1 lines (admitted per leg, high_power.revoked, high_power.before_restore), the desk bundle, the restore lines, measurement_mode verify again, the RL-157 §1 and §5 prints and the RL-150 R1 start-reference print (none of the prints gates)
```

- **Why.** RL-155 §5.2 makes H001-H003 hp-01's smoke, as their own span, counted as type H (RL-150 R5). RL-157 §8 puts it on Sun 15 Nov after dev-01's last span closes plus 20 min. RL-165 §2's Sunday order after `dev-01-s04`: **the R1 slot session if READY (RL-155 R-A), then hp-01's spans, then the dev-02 pull, then F0.** <LEAD FILLS: "the R1 slot session is not READY at issue (<why>)", or "the R1 slot session ran and closed at <epoch> (RUN_STATE <n>); PRIOR below is that session's close">. A leg's calendar day is the local date of its span's t0, so these are Sun 15 Nov legs.
- **No clock floor (Mythos and Sol schedule reviews; RL-157 §8's "about 07:00" was a forecast; RL-171 retires the 02:40 start).** The gate is `dev-01-s04`'s close + the close interval (RL-171 §6.1). Item 331 launches `dev-01-s04` at about 00:20 (expected close 02:56:45), so the forecast t0 is 03:01:45 with a 5-min interval, or 03:16:45 with 20 min.
- **Latest t0 (RL-165 §7, which replaces RL-157 §8's values for hp-01 only).** RL-171 §2 keeps this rule for its own reason, the lead's presence, not the batch: an hp-01 span launches only if its worst-case end is by 00:30, so the lead is reachable to clear a "restore unproven":

| Legs | Worst case | Latest t0 |
|---|---|---|
| 3 (this smoke) | 16,650 s | **19:52:30** |
| 4 | 19,350 s | 19:07:30 |
| 5 | 22,050 s | 18:22:30 |
| 9 | 32,850 s | 15:22:30 |

  The fence bound (fence end by 01:50) is retired (RL-171 §2), and `dd206025a` has the v1 launcher, with no fence check (checked on the Air: no `fence_problems` in `joulewise/cadence/legs.py`, `scripts/launch_cadence_span.py` or the runner; `b4b6aeb19` is its ancestor and `plan_span` is unchanged). No launch between 10:50 and 13:15: RL-171 calls it a defect of this pin, not a rule, but the bytes still carry the 11:45-13:15 soak window (`OS_BATCH_WINDOW_LOCAL` in `scripts/align_r1_rehearsal.py`), the runner holds the soak out of it, and the plan does not budget that wait. The 00:30 rule as written does not bound a small-hours t0 (a launch at 03:00 has its worst-case end at 07:37); the lead decides whether the lead's presence needs a morning bound too.
- **Gate (RL-155 §5.2's four lines, held on `dd206025a` per the Mythos delta seat's D6; and RL-165 §5, §6).**
  1. Row-1 review: ADMIT at `a95812f14` (code `d8ae17db2`, `/Volumes/JW-EXT/scratch/rev789/REVIEW.md`). On `dd206025a`: <LEAD FILLS: the row-1 delta reading for `dd206025a` (or the lead's record that the Mythos delta seat at `dd206025a` stands for it) and where it is recorded>. The builder's pre-qualification at `dd206025a` (nine modules OK, including `tests.cadence.test_high_power` 50 OK) is in `/Volumes/JW-EXT/scratch/hp01-ready/plans/tests-dd206025a.log`.
  2. The Mythos cold seat with no open finding, including RL-157 §2 conditions 1 and 3: first seat ADMIT WITH FIXES at `a95812f14` (F1-F9); delta seat at `dd206025a` (kit `7eaf2660…d2965`) ADMIT WITH FIXES: F1-F9 closed; D1 and D4 are the procedure lines in this item; D1's second line binds the remainder (After, below); D2, D3 and D5 go to the next re-pin; D6 is this gate list. Both reports are on audit/2026-11-10-fable at `4c38dce3b` (evidence/align-v4-campaign/mythos-hp01-789.md, mythos-hp01-789-delta.md).
  3. CI on the frozen commit: arm-record line 2 (RL-165 §5's four parts, with its one exception for this smoke).
  4. The recorded mock with a failing restore, on `dd206025a` with kit `7eaf2660…d2965`: `mock --fail-close-restore` rc 2, stops REFUSAL + RESTORE_UNPROVEN, close_proof `{ac_powermode 2, host_marker_present true, proven false}`, `restore_proven` false, restore attempts 3; the normal mock rc 0, no stops, `restore_proven` true. The Air desk at `dd206025a` with `--kit` fires RESTORE_UNPROVEN on a missing `span/result.json`; with `--adapter` it does not (D6). <LEAD FILLS: evidence path on audit/2026-11-10-fable, copied from `/Volumes/JW-EXT/scratch/hp01-ready/mock/`>.
  - D6 (c): no hp-01 span ran on the old kit `bd7c8711…` (`d8ae17db2`): RUN_STATE on origin/main through item 325 (`1e753e327`) names `cl-hp-01` in no item.
  - Line 9 (RL-165 §6): `dev-01-s03`'s desk is final (arm-record line 9).
- **dev-01's last span (the gate before this one):** <LEAD FILLS: `dev-01-s04` (RUN_STATE <n>): RECEIPT OK or not, legs run and admitted of 5, no named stop open, restore lines clean (powermode 0, network time Off, frequency word 0, no marker, no fence), receipt `ended.epoch_s` <epoch>, fence seen gone at <epoch>>. If any named stop is open on it, this item is NOT issued until the lead clears it (REFUSAL holds campaign spans, RL-155 §3.1; hp-01 is a campaign block).
- **PREFLIGHT READ of the pmset sudo rule (Mythos schedule review, "Not checked").** At your first activation after this item is issued with NO fence up and nothing armed (for example in the close interval after `dev-01-s04` closes, or earlier between runs), read once: `sudo -n -l 2>&1 | grep -F 'powermode'`, and record whether both `/usr/bin/pmset -c powermode 0` and `/usr/bin/pmset -c powermode 2` are listed. It is read-only and changes nothing. If either is missing, mail the lead at once: the smoke would refuse at `powermode_guard`, and installing a sudo rule is a host change outside measurement_mode that only the lead makes. The same two lines are checked again in "Start and check".
- **Alarm (the lead's watcher, RL-165 §7).** At issue the lead arms an alarm at this span's worst-case end, t0 + 16,650 s (at t0 03:01:45: 07:39:15; at 19:52:30: 00:30:00), that fires if the fence is still up or no Check is reported, and a second at the fence end, t0 + 18,110 s. The magistrate records t0 so the lead can set it.
- **Counted.** The three legs count as type-H legs of hp-01 under the kit's inclusion rules (RL-149 §2.3, §2.4 as amended by RL-150 R7 and R8, RL-157 §4): rule 6 is the block's mode, so a leg is admitted only if it recorded AC powermode 2 at its episode start and was not withdrawn. The smoke has passed when RL-150 R9's four conditions hold, with rule 6 meaning High Power (design doc §13.2.1). hp-01 has no reserve (RL-157 §4): an excluded type-H leg is not replaced.
- **L004-L012 are NOT queued.** They are appended only after the lead's hand-read of this span (RL-150 R5, RL-161 §2: the first queue holds the smoke span only).
- **Bytes.** Measured from `dd206025abb30fd5c07515cd4b34b3e653174810` (PR #789, branch `align/2026-11-14-hp01`, off PR #775's head `8bd31ae5a`). The kit is NOT the in-tree copy at that commit (that one is the superseded draft `bd7c8711…`, pinned at `d8ae17db2` with master seed 2026111403): it is `cl-hp-01.json` from `bbd34dc87` (the same blob at the branch head `2a8deb7b9`), sha256 `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965`, copied outside the checkout. Its `frozen` block names `dd206025a` and 37 paths; all 37 hashes equal the blobs at `dd206025a`, `bbd34dc87` and `2a8deb7b9`. Master seed 2026111404 (RL-161 §4). **No rebase onto a #777 commit (RL-165 §5):** the base-equality reading of line 2 is extended to this pin and ends at the qualification re-pin.
- **Condition-13 sources are byte-identical to the base** (`v4_registration.R1_EXECUTED_SOURCES`, the ten paths, identical at `fe907d0d3` and `dd206025a`). `verify_r1_executed_sources` must return the full sha.
- **What the runner does** (docs/process/cadence_queue_design.md §13 and §13.2 at `dd206025a`): preflight (HEAD = frozen commit; frozen paths' working-tree bytes = kit; night agents; AC; condition 13; **`host_lock`: takes `/Users/Shared/JouleWise/host-power/night.lock` and holds it to the close, refusing if another holder has it; `high_power_marker_absent`: refuses on any marker present**; agent census, KM003C and volume feeds; powermode 0 read back; **`powermode_guard`: the narrow sudo rule listed and an Automatic restore proved**; display sleep and 300 s dwell); the plan; ONE fresh soak in Automatic (the night's own soak path, cap 1,950 s); **`high_power`: powermode must still read 0, the marker is written FIRST (R1 crash tag, owner `cadence span`, campaign `cl-hp-01`, kit sha, OUT, the restore command and when it is safe), then `pmset -c powermode 2`, read back 2**; L001-L003 in seeded order, **each attempt preceded by `L00n.aK-powermode` (powermode reads 2 and the marker is this span's, else the span stops and the leg finished since the last good check is withdrawn, rule 6)**, each its own G0 under the 1,200 s R1 timeout, then one turn; per-leg load redo (RL-72 E2 rule, quota 2 per span); no leg starts inside the batch-window argument (`$ARG`: 02:00-02:35 or 13:14-13:15, chosen by the launch time, RL-171 §3); **close on every exit path the process survives: `power_last_look` (a failed look withdraws the last leg), `restore` (up to three attempts 2 s apart unless deferred), `power_proof` (powermode and the marker path read again), `host_lock_release`**, then feeds stopped and hashed, `runner_receipt.json` (with `high_power.close_proof`), `desk-bundle/` (`span/result.json` carries `restore_proven`). It reads and writes no energy. Of the KM003C stream it decodes only the header and trailer lines (RL-150 R8).
- **Timing.** Plan for this roster (`plan` at `dd206025a` with both arguments, blackout_clear true, every band end checked; Air 2026-11-15, `/Volumes/JW-EXT/scratch/items-rl171/plans/bands/verify-hp01-s01.txt` and `probe/plan/`): expected 6,903 s (1.9 h), worst case 16,650 s (4.6 h), budget_s 1,251 per leg. The launcher refuses a deadline under worst case + 560 s (17,210 s); this item sets the fence deadline at launch + 18,110 s (900 s start slack).
  - **Bands (RL-171 §3; the `pick_arg` function below):** 00:00:00-02:34:59 `13:14-13:15` (`02:00-02:35` refuses every t0 from 21:22:31 to 02:34:59 for three legs, because the worst case meets the window); 02:35:00-10:50:00 `02:00-02:35`; none 10:50:01-13:14:59; 13:15:00-19:52:30 `02:00-02:35`. `validate-kit` is ok with either argument. A mock span at t0 00:30 with `13:14-13:15` (three legs, L003 across 02:00): rc 0, 3 legs, no stops, no wait step (`/Volumes/JW-EXT/scratch/items-rl171/mock/hp01-s01-alt-00:30/`). The mock does not model the soak path's 11:45-13:15 wait (its deps carry no soak window).
  - Forecast t0 03:01:45 (s04's expected close 02:56:45 + 5 min), argument `02:00-02:35`: expected end 04:56:48, worst end 07:39:15, fence end 08:03:35.
  - t0 10:50:00: worst end 15:27:30, fence end 15:51:50. t0 13:15: 17:52:30 and 18:16:50.
  - t0 19:52:30: worst end **00:30:00**, fence end 00:54:20 (RL-165 §7). 19:52:31 is refused by this item.
  - RL-157 §5: the Automatic time model stays; the calendar is safe because the fence uses the 2,700 s process cap and the 1,200 s G0 cap, which High Power does not change.
  - Pointer deadline = latest fence end (00:54:20 Mon) + 1 h.
- **Conditions.**
  - No agent session on the MBP during the span: you exit at once after the launch. No lead SSH, desk job or R12 process until the fence is gone.
  - Restore before the launch and again in "Check": AC, powermode 0, network time OFF, kernel frequency word 0 (item 251's remedy if not), no stray `km003c_monitor.py` / `hazard_monitor.py` / root `powermetrics`, no High Power marker. `sudo -n -l /bin/kill` rc 0. Leave `night.lock` as found (the runner takes and releases it itself).
  - **High Power preflight (design doc §13.2.1; Mythos D1/F2):** `pmset -g custom` reads AC powermode 0; no file and no link at `/Users/Shared/JouleWise/host-power/high-power.marker`; `sudo -n -l` lists both `/usr/bin/pmset -c powermode 0` and `/usr/bin/pmset -c powermode 2`; the host night lock has no holder; `JOULEWISE_HOST_STATE_DIR` is unset.
  - Every `validate-kit`, `plan` and `launch` passes `--batch-window "$ARG"`, chosen once in Start and check by the launch time and re-checked in Run; the arm record shows the plan's `batch_windows` (RL-150 §2 F2; RL-171 §3).
  - The arm record states the host is in measurement_mode as applied 11-13 23:47 and network time is off, checked remotely (RL-150 §2 F5; RL-161 §3: every arm record keeps the measurement_mode line).
  - Output root `/Users/edr/campaign-out/cl-hp-01/` is outside every v4 registration and custody root (RL-149 §2.8 line 4; dev-01 F6 as deferred by RL-161 §3).
- **RESTORE_UNPROVEN holds everything (Mythos F1; design doc §13.2.1; RL-165 §3 rule 8).** For this span it is: no receipt, no `span/result.json`, or anything but `restore_proven: true`. Unlike REFUSAL under RL-155 §3.1, it holds every later arm (campaign spans, sessions, Part C and the standing F0, fillers) until the lead records the restore.
- **RL-157 §2 condition 2.** If the receipt names a leg attempt whose process group was not proven stopped, the span's REFUSAL stands whatever the power proof says, and it holds the standing F0 (RL-165 §3 rule 8). Only the lead clears it, with the group shown gone (pid and start time) and powermode read 0 again at that moment; `restore_proven` true does not clear it.
- **LEG_OVERTIME on hp-01 goes to the RESEARCH LEAD, not the lead (RL-157 §5, amending RL-149 §2.4 for this block).** Two legs over 1.5 × 1,251 s would mean High Power moved G0 or decode time by minutes a leg; the research lead decides whether the remainder runs as planned.
- **Blinding.** Open no energy, power, meter-sample, transcript or slot file. From each leg bundle read ONLY `outputs/align_window_reference.json` and `outputs/align_thermal.jsonl` (thermal journal values and the G0 gate row, RL-150 R1 part 3 and RL-157 §1), with the scripts below. Never print a KM003C stream line; never open `powermetrics*`, `hazards/`, `align_episode.json`, `telemetry*` or anything under `runs/*/outputs/` other than those two files. The span-level files you read are `runner_receipt.json`, `chain-stages.jsonl` (stage stamps), `legs/*/leg_record.json`, `soak/soak_reference.json`, the soak's sensors journal and `desk-bundle/`; the host state you read is `pmset -g custom`, the marker path and (only under "Restore owed") the marker's owner record. None carries energy.
- **May run:** this span, once. **May NOT:** L004-L012 (any span of them), dev-02, any other campaign span, any session, W1, any filler, and `restore-owed` while this span is armed or its fence is live.
- **High Power marker at the arm:** if `/Users/Shared/JouleWise/host-power/high-power.marker` exists, STOP and report. Do not run `restore-owed` at the arm; the lead decides (it is someone else's owed restore).

- **Host gate and R1 reservation, immediately before the launch (Sol items review P1-1, P1-2; RL-155 R-B; RL-165 §7).** Separate from this item's campaign dependency: the Check of the latest close of ANYTHING on this host (any span, Part C or F0, slot session or W1) reported every restore line OK; no desk fence; no night or smoke agent loaded; no High Power marker; at least GAP seconds since that latest close (RL-171 §6.1, amending RL-155 R-B's 20 minutes: GAP is QUIET_CAMPAIGN_S after a campaign span's close, 300 s, confirmed by RL-172 §0; GAP is 1,200 s after a Part C or F0, F2, a slot session or W1) (the newest `runner_receipt.json` under `/Users/edr/campaign-out` and `/Users/edr/code/jw-wt`, from a census that stops on a missing root, any lookup error or an empty result, with fractional mtimes rounded up; or a session's close given as OTHER_CLOSE_EPOCH, a whole epoch or an explicit 0); and, after a CAMPAIGN close, that close's journal copy complete and hash-verified, shown by the lead's marker `/Users/Shared/JouleWise/desk-copy/<plan-id>.ok`, written only after the copy is verified (Sol items-rl171 P1; a missing marker is WAIT; no SSH once a span is armed). Read fresh at the launch: if a v4 slot session is READY and staged for this slot, this span cedes; RL-172 (f) retires RL-165 §7's worst-case reservation: from the lead's record that a v4 session is READY nothing of lower priority arms, and the session takes the next clean close; before that record this span arms as usual.

**RL-149 §2.8 arm-record lines (record each, with its evidence):**
1. Kit `ruling` is `RL-149 §2`. Kit `cl-hp-01` `7eaf2660…d2965` on `dd206025a`: (i) Mythos 5.2 cold seat on `a95812f14` (kit `bd7c8711…`) ADMIT WITH FIXES (evidence/align-v4-campaign/mythos-hp01-789.md, audit branch `4c38dce3b`); (ii) Mythos 5.2 delta seat on `dd206025a` ADMIT WITH FIXES, F1-F9 closed, D1 and D4 closed in this item's text, D1's second line in "After", D6 in the Gate list (evidence/align-v4-campaign/mythos-hp01-789-delta.md, audit branch `4c38dce3b`); (iii) row-1 review ADMIT at `a95812f14` with RL-157 §2 conditions 1 and 3 confirmed in code (§5 of `/Volumes/JW-EXT/scratch/rev789/REVIEW.md`), and the `dd206025a` reading of Gate line 1; (iv) the `validate-kit` line and the `plan` below. RL-157 rules the builder's seven questions; RL-161 §4 moves the master seed to 2026111404. Hand confirmation (dev-01 F11, RL-161 §3): `kit.model` `mlx-community/Qwen3.8-27B-8bit` agrees with the frozen `configs/campaigns/align_v4/registration/inputs.json` (`model_source` …/mlx-community/Qwen3.8-27B-8bit) and `configs/align/v4/qwen38-27b-8bit-hf-pins.json` (`repo` mlx-community/Qwen3.8-27B-8bit). The kit's `stop_rules.notes` carry the campaign-scope stop text (dev-01 F5).
2. Line 2, in RL-165 §5's four parts (the base-equality reading, extended to this pin by RL-165 §5; it ends at the qualification re-pin):
   1. **Same bytes.** The full suite ran on bytes equal to `dd206025a` on all 37 frozen paths. The run that stands is CI `ci` run 43673985768 on the branch head `2a8deb7b9` (started 2026-11-14 19:48 PST; frozen-path diff against `dd206025a` empty: `2a8deb7b9` differs from `dd206025a` only in the kit file, the design doc, `tests/cadence/test_high_power.py` and `tests/host_command_sites.json`, none frozen). <LEAD FILLS: its conclusion and red set>. **Exception (RL-165 §5, this smoke only):** if that run has not finished when `dev-01-s04` closes, the smoke may arm on CI `ci` run 43664752637 on `bbd34dc87` (frozen-path diff against `dd206025a` empty), whose red set is the base plus one test, `test_host_command_sites.HostCommandSiteTests.test_tracked_command_sites_match_reviewed_allowlist`, with the recorded local pass of `tests/test_host_command_sites.py` at `2a8deb7b9`: Air, 2026-11-14 20:18:04-20:18:29 PST, `python3.13 -B -m unittest -v tests.test_host_command_sites`, 2 tests OK including `test_tracked_command_sites_match_reviewed_allowlist`, log `/Volumes/JW-EXT/scratch/items-rl165/evidence/host_command_sites-2a8deb7b9.log` (<LEAD FILLS: its audit-branch copy>). The fix touched unfrozen test data only. **The finished run must show base + 0 before hp-01's second span arms.** <LEAD FILLS: which run this arm cites>.
   2. **Red set.** It equals `fe907d0d3`'s (CI `ci` run 43600776368, `base-red.txt` on audit/2026-11-10-fable at `4c38dce3b`), the 12 tests of RL-155a §4, test for test (or base + the one allowlist test under the exception). **An added red is fixed and re-run, not accepted on an explanation** (RL-165 §5).
   3. **Each of the 12 passes at a #777 head:** CI `ci` run 43601158271 on #777 head `ae340d3da` (success, full suite; `pass-at-777-head/` in rl152-redset).
   4. **Recorded diff (RL-165 §5 part 4).** Against `b4b6aeb19`, over the 37 frozen paths, five files differ: `joulewise/cadence/desk.py`, `kit.py`, `legs.py`, `stops.py` and `scripts/cadence_legs_runner.py` (472 insertions, 43 deletions; the High Power path). The meter driver `joulewise/b5/driver.py` (blob `ff4fd76a`) and `scripts/km003c_monitor.py` (blob `7d6acc98`) are identical at `fe907d0d3`, `b4b6aeb19`, `8bd31ae5a`, `dd206025a`, `bbd34dc87` and `2a8deb7b9`. Evidence: `/Volumes/JW-EXT/scratch/items-rl165/evidence/frozen-path-diffs-vs-b4b6aeb19.txt` and `/Volumes/JW-EXT/scratch/hp01-ready/LINE2.md`.
3. Queue `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-hp-01-dd206025a.json` on audit/2026-11-10-fable at `3de39e06a`, sha256 `90e042edf25c1a9858f08547ca25c1d5cdcbeed8a7fa9a1038a360a658ed39ed` (`validate-queue` ok with `--kits-root` set to the PR #789 checkout at `bbd34dc87`; plan id `cq-hp-01-s01-a1`): finite (`expires_at` 2026-11-21T23:59-08:00; committed at `3de39e06a`. `validate-queue` needs `--kits-root` at a checkout of `bbd34dc87`, where the kit is `7eaf2660…`; the in-tree kit at `dd206025a` is the superseded `bd7c8711…`), pins `cl-hp-01` by sha `7eaf2660…d2965`, one span (`hp-01-s01`, legs L001-L003, not_before 2026-11-15), append-only. The remainder is appended only after the hand-read. Do NOT run `cadence_queue.py next`; this item names the span.
4. `validate-kit` passes (its `deny_scan` refuses any condition/slot/instruction key or label); OUT is outside every v4 registration and custody root (check below). RL-150 R6: the constant `benign` inside member-bundle configs is the stated exception.
5. The per-span checks of design doc §4 and §13.2.1 pass at the arm (Start and check) and at the close (Check). Do NOT run `cadence_queue.py checklist`: its `span_window` line encodes the kit template's fixed 13:20 t0 that RL-149 §2.9 item 6.3 removed (cold check reading 4).
6. No named stop, veto or halt open: no open `directive` issue by `mpmdw` whose title or first line starts STOP/NO/HALT/VETO, no open `cadence-stop` issue (gh on the MBP runs in the GUI context: `launchctl asuser`), and no RESTORE_UNPROVEN open from any span or Part C run.
7. Results-ref watcher live within 24 h: <LEAD FILLS: the Air results watcher (`com.joulewise.air-watch`) heartbeat stamp, which must be under 24 h old at the arm; name pid and commit>.
8. Not applicable: this span is hp-01's smoke (RL-150 R5). The smoke's pass and the lead's hand-read gate the remainder (RL-157 §8).
9. Line 9, counted across blocks in the order the machine ran them (RL-165 §6; "not applicable: first span" is withdrawn). Campaign spans: 1 = dev-01 pilot, 2 = `dev-01-s03`, 3 = `dev-01-s04`; **this smoke is campaign span 4**, so span 2's desk must be final: `dev-01-s03`'s desk is FINAL: <LEAD FILLS: the desk's stamp and where it is recorded (`/Volumes/JW-EXT/cadence-desk/cq-dev-01-s03-a1/`)>. If the R1 slot session or an F0 ran between, it does not count (RL-155 §3.4).

**Start and check (while you are still alive).** From a FRESH scratch worktree detached at the full sha (NOT the canonical clone's checkout, not another smoke worktree, not a dev-01 worktree at `b4b6aeb19`), own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `python3.13 -B -m unittest`, one module at a time; all must be OK: `tests.cadence.test_high_power`, `tests.cadence.test_legs_runner`, `tests.cadence.test_kit`, `tests.cadence.test_stops_desk`, `tests.cadence.test_runner_guards`, `tests.align.test_r1_smoke_launcher`. (At `dd206025a` the in-tree kit is the superseded draft `bd7c8711…`; the armed kit is checked by `validate-kit` below.) Any failure: nothing launches; mail the lead.

```sh
git -C /Users/edr/code/JouleWise fetch origin align/2026-11-14-hp01
test -e /Users/edr/code/jw-wt/cadence-hp01-s01 || git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/jw-wt/cadence-hp01-s01 dd206025abb30fd5c07515cd4b34b3e653174810   # reused on a retry after a WAIT
cd /Users/edr/code/jw-wt/cadence-hp01-s01
test "$(git rev-parse HEAD)" = dd206025abb30fd5c07515cd4b34b3e653174810 || { echo "STOP: HEAD"; exit 1; }
test -z "$(git status --porcelain)" || { echo "STOP: dirty tree"; exit 1; }
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"                 # must show the claude process
: "${PRIOR_CLOSE_EPOCH:?Set to the later of dev-01-s04 runner_receipt ended.epoch_s and the epoch its desk fence was seen gone (or the R1 slot session close, if it ran first)}"
QUIET_CAMPAIGN_S=300    # RL-171 §6.1, confirmed by RL-172 §0: 300 s after a campaign close; 1,200 s after F0, F2 or any other close
: "${LAST_CLOSE_KIND:?Set to campaign if the latest close of anything on this host was a campaign span, else other (Part C/F0, F2, slot session, W1)}"
case "$LAST_CLOSE_KIND" in campaign) GAP=$QUIET_CAMPAIGN_S;; other) GAP=1200;; *) echo "STOP: LAST_CLOSE_KIND must be campaign or other"; exit 1;; esac
echo "close interval GAP $GAP s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)"
# ONE newest-close selection over both roots, used by the host gate and by copy_gate (Sol RL-172 re-check 1)
close_census() {
  CENSUS="$("$PY" -I -B - /Users/edr/campaign-out /Users/edr/code/jw-wt <<'PY'
import math, os, sys
def fail(e):
    raise e
newest, path, count = None, None, 0
for root in sys.argv[1:]:
    if not os.path.isdir(root):
        sys.exit(f"STOP: receipt root missing: {root}")
    base = root.rstrip("/").count("/")
    for dirpath, dirnames, filenames in os.walk(root, onerror=fail):
        if dirpath.count("/") - base >= 3:
            dirnames[:] = []          # receipts at depth <= 4, as `find -maxdepth 4`
        if "runner_receipt.json" in filenames:
            p = os.path.join(dirpath, "runner_receipt.json")
            m = os.stat(p).st_mtime
            count += 1
            if newest is None or m > newest:
                newest, path = m, p
if count == 0:
    sys.exit("STOP: the receipt census found no runner_receipt.json; receipts are expected on this host")
if "\n" in path:
    sys.exit("STOP: newline in a receipt path")
print(math.ceil(newest))
print(path)
print(f"census: {count} receipts, newest mtime {newest!r} {path}", file=sys.stderr)
PY
)" || return 1
  CENSUS_EPOCH="$(printf '%s\n' "$CENSUS" | sed -n 1p)"
  NEWEST_RECEIPT="$(printf '%s\n' "$CENSUS" | sed -n 2p)"
  case "$CENSUS_EPOCH" in ''|*[!0-9]*) echo "STOP: the receipt census gave no close epoch"; return 1;; esac
  test -n "$NEWEST_RECEIPT" || { echo "STOP: the receipt census gave no receipt path"; return 1; }
}
# The effective close, computed ONCE per gate (Sol confirm P1): max of the census and OTHER_CLOSE_EPOCH, with its path or label.
# The host gate's GAP and copy_gate's kind check both use EFF_EPOCH / EFF_PATH from the same call.
effective_close() {
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) of a session/W1 close, or an explicit 0"; return 1;; esac
  close_census || return 1
  EFF_EPOCH=$CENSUS_EPOCH; EFF_PATH="$NEWEST_RECEIPT"
  if test "$OTHER_CLOSE_EPOCH" -gt "$CENSUS_EPOCH"; then
    EFF_EPOCH=$OTHER_CLOSE_EPOCH; EFF_PATH="OTHER_CLOSE_EPOCH $OTHER_CLOSE_EPOCH (a session or W1 close outside the census roots)"
  fi
}
# Sol items-rl171 P1 and Sol RL-172 re-check 1: the newest close of anything (the census above, or OTHER_CLOSE_EPOCH for a
# session/W1 close outside its roots) must agree with LAST_CLOSE_KIND. After a CAMPAIGN close, that receipt's journal copy must be
# complete and hash-verified on the Air: the lead copies by SSH, verifies, and only then writes
# /Users/Shared/JouleWise/desk-copy/<plan-id>.ok (the copy manifest's sha256 and a `date` stamp). No SSH once a span is armed.
# A marker is only ever derived from a campaign receipt path; after a Part C, F0, F2, session or W1 close the Check covers the copy.
copy_gate() (   # a subshell: it reads EFF_PATH (from effective_close) and LAST_CLOSE_KIND and changes nothing the host gate reads
  test -n "${EFF_PATH:-}" || { echo "STOP: copy_gate needs effective_close first"; exit 1; }
  if printf '%s\n' "$EFF_PATH" | grep -Eq '^/Users/edr/campaign-out/cl-[a-z0-9-]+/cq-[a-z0-9-]+-a[0-9]+-[0-9]{8}T[0-9]{6}Z/runner_receipt\.json$'; then
    newkind=campaign
  else
    newkind=other
  fi
  test "$newkind" = "$LAST_CLOSE_KIND" || { echo "STOP: contradictory LAST_CLOSE_KIND ($LAST_CLOSE_KIND): newest close is $EFF_PATH; mail the lead"; exit 1; }
  if test "$newkind" = other; then
    echo "copy gate: newest close is non-campaign ($EFF_PATH); its Check covers the copy"; exit 0
  fi
  plan_id="$(basename "$(dirname "$EFF_PATH")" | sed -E 's/-[0-9]{8}T[0-9]{6}Z$//')"
  case "$plan_id" in cq-*-a[0-9]*) ;; *) echo "STOP: no campaign plan id in $EFF_PATH"; exit 1;; esac
  copy_ok="/Users/Shared/JouleWise/desk-copy/$plan_id.ok"
  test -s "$copy_ok" || { echo "WAIT: no journal-copy marker $copy_ok for the newest close, campaign span $plan_id ($EFF_PATH): the lead's hash-verified copy is not done; retry at the next activation"; exit 1; }
  echo "journal copy of $plan_id: $(cat "$copy_ok")"     # record this line
)
# The launch bands (EARLIEST 1794729600 Sun 00:00:00; LIMIT 1794801150 Sun 19:52:30, the 00:30 rule; none 10:50:01-13:14:59)
pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794729600 ] && [ "$n" -le 1794738899 ]; then echo 13:14-13:15   # Sun 15 Nov 00:00:00 .. Sun 15 Nov 02:34:59
  elif [ "$n" -ge 1794738900 ] && [ "$n" -le 1794768600 ]; then echo 02:00-02:35   # Sun 15 Nov 02:35:00 .. Sun 15 Nov 10:50:00
  elif [ "$n" -ge 1794777300 ] && [ "$n" -le 1794801150 ]; then echo 02:00-02:35   # Sun 15 Nov 13:15:00 .. Sun 15 Nov 19:52:30
  else echo NONE; fi
}
NOW=$(date +%s); test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval ($GAP s) after the prior span's close"; exit 1; }
ARG="$(pick_arg "$NOW")"
test "$ARG" != NONE || { echo "STOP: no admitted launch band now (outside this item's window, or inside 10:50-13:15 where this pin cannot launch); mail the lead"; exit 1; }
export ARG; echo "ARG $ARG (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)"
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"   # the watchdog's fence root (fence + launch spec only)
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
# must print dd206025abb30fd5c07515cd4b34b3e653174810

# Sol P1 and RL-172 (a): before the KIT and OUT exist, so a WAIT here is retried cleanly at the next activation
effective_close || { echo "STOP: the receipt census failed; mail the lead"; exit 1; }
copy_gate || exit 1
# The kit: from PR #789's bbd34dc87 (same blob at the branch head 2a8deb7b9), OUTSIDE the checkout, sha asserted
mkdir -p /Users/edr/campaign-out/kits
KIT=/Users/edr/campaign-out/kits/cl-hp-01-bbd34dc87.json
test ! -e "$KIT" || echo "KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted"
git -C /Users/edr/code/JouleWise show bbd34dc876001786c3603d9c4583391639284253:docs/process/cadence/kits/cl-hp-01.json > "$KIT"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = 7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965 || { echo "STOP: kit sha"; exit 1; }
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG"
# must print ok true, campaign_id cl-hp-01, frozen_commit dd206025abb30fd5c07515cd4b34b3e653174810,
# frozen_paths_verified true, kit_sha256 7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965, legs 12

# Output root outside every v4 registration and custody root
OUT=/Users/edr/campaign-out/cl-hp-01/cq-hp-01-s01-a1-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')
test ! -e "$OUT" || { echo "STOP: OUT exists"; exit 1; }
case "$OUT" in */restricted/*|*/night-*|*/jw-b5-*|"$REPO"/*|*/configs/campaigns/align_v4*) echo "REFUSE OUT"; exit 1;; esac

# measurement_mode (RL-149 §2.4 campaign-scope stop; RL-150 §2 F5): record every FAIL/WARN line
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify; echo "verify rc $?"
# RULE (lead, RL-150 F5 line): proceed only if every FAIL line is the "agent process present" line and every PID it names is
# in MAGISTRATE_PID's own process tree (record the lines); ANY other FAIL line: STOP, mail the lead. WARN lines are recorded, not gates.
sudo -n systemsetup -getusingnetworktime                 # must say Off
# RL-172 (h): the OS daily batch time computed from the boot time (boot + 12 h + 48 s, then every 24 h). PRINT ONLY: it gates nothing
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*$/\1/')"
case "$BOOT" in
  ''|*[!0-9]*) echo "batch print: kern.boottime unreadable";;
  *) NEXT_BATCH=$((BOOT + 43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH + 86400)); done
     echo "boot $(date -r "$BOOT" '+%Y-%m-%d %H:%M:%S %Z'); next OS batch $(date -r "$NEXT_BATCH" '+%Y-%m-%d %H:%M:%S %Z') (boot + 12 h + 48 s + whole days)";;
esac      # record this line in the arm record
# kernel frequency word: read it as item 308 did; must be 0 (else item 251's remedy, then re-read)
test ! -e "$CUSTODY/desk_fence.json" || { cat "$CUSTODY/desk_fence.json"; echo "STOP: live fence"; exit 1; }
sudo -n -l /bin/kill >/dev/null; echo "sudo kill rc $?"  # must be 0
pgrep -fl 'b6_r12|r12' || echo "no r12"
pgrep -fl 'claude|codex|mcp-server|mcp_server|modelcontextprotocol' | grep -v "^$MAGISTRATE_PID " || echo "no other agent"
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo "no stray monitor"
pgrep -u root -fl powermetrics || echo "no root powermetrics"
launchctl list | grep -E 'com\.joulewise\.(night|align-r0)' || echo "no night/smoke agent"
pmset -g | grep -i powermode                              # 0
"$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO"     # ac_power true

# High Power preflight (design doc §13.2.1; record every line)
test -z "${JOULEWISE_HOST_STATE_DIR:-}" || { echo "STOP: JOULEWISE_HOST_STATE_DIR is set"; exit 1; }
HP_MARKER=/Users/Shared/JouleWise/host-power/high-power.marker
{ test ! -e "$HP_MARKER" && test ! -L "$HP_MARKER"; } || { echo "STOP: High Power marker present; do NOT run restore-owed; mail the lead"; exit 1; }
"$PY" -B -c 'from joulewise.align.apple import powermode as p; v = p.observe_ac_powermode(); print("pmset -g custom AC powermode", v); raise SystemExit(0 if v == 0 else 1)' \
  || { echo "STOP: AC powermode is not 0"; exit 1; }
SUDO_LIST="$(sudo -n -l 2>&1)"
for c in '/usr/bin/pmset -c powermode 0' '/usr/bin/pmset -c powermode 2'; do
  case "$SUDO_LIST" in *"$c"*) echo "sudo rule listed: $c";; *) echo "STOP: sudo rule missing: $c"; exit 1;; esac
done
lsof -- /Users/Shared/JouleWise/host-power/night.lock 2>/dev/null && { echo "STOP: the host night lock has a holder"; exit 1; } || echo "night.lock: no holder"

# The plan (record it whole; batch_windows must be ["$ARG"])
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG"
# expect legs L001 L002 L003, budget_s 1251 each, expected_s 6903, worst_case_s 16650, blackout_clear true
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+18110)')"
```

NOTE 1 (ADOPTED by the lead; the rule is in the verify line above). `measurement_mode.zsh verify` fails a line "agent process present" for ANY `claude`/`codex`/MCP process (`pgrep -x claude`), which includes this magistrate. While the magistrate runs, verify cannot print "verify OK". Rule: proceed only if every FAIL line is that one agent line and the PIDs it names are the magistrate's own process tree (record the lines); any other FAIL means STOP. WARN lines (battery limit syntax, softwareupdate schedule) are recorded, not gates.

NOTE 2 (ADOPTED by the lead: the fence root stays the watchdog's; all campaign data under OUT). `--custody-root` is the watchdog's fence root (`/Users/edr/night-custody/magistrate`): the launcher writes the fence, the plist, `runner.json` and the LaunchAgent logs there, as every R1 smoke did. All campaign data (soak, legs, receipt, desk bundle) go under OUT.

**Run (your last action):**

```sh
WORST_S=16650
# HOST GATE, immediately before the launch (P1-1). This is separate from the campaign dependency above: it reads the
# latest close of ANYTHING on this host (campaign span, Part C or F0, slot session, W1), not only this item's predecessor.
: "${HOST_RESTORE_OK:?Set to 1 only if the Check of the latest close of anything on this host reported every restore line OK}"
: "${OTHER_CLOSE_EPOCH:?Set to the close epoch (whole seconds, rounded up) of the latest run whose receipt is outside campaign-out and jw-wt/*/.desk (a slot session or W1), or an explicit 0}"
test "$HOST_RESTORE_OK" = 1 || { echo "STOP: the latest close's restore is not proven (restore unproven holds everything); mail the lead"; exit 1; }
test ! -e "$CUSTODY/desk_fence.json" || { echo "STOP: a desk fence is up"; exit 1; }
launchctl list | grep -qE 'com\.joulewise\.(night|align-r0)' && { echo "STOP: a night or smoke agent is loaded"; exit 1; }
{ test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || { echo "STOP: High Power marker"; exit 1; }
case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) or an explicit 0"; exit 1;; esac
# The receipt census: every runner_receipt.json at depth <= 4 under both roots, fractional mtimes, ROUNDED UP.
# Any lookup error, a missing root, or no receipt at all STOPS: missing evidence never becomes 0 (Sol re-check 2, 3).
effective_close || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; exit 1; }
HOST_LAST_CLOSE=$EFF_EPOCH    # the effective close (max of the census and OTHER_CLOSE_EPOCH), computed once (Sol confirm P1)
echo "host last close $HOST_LAST_CLOSE"
copy_gate || exit 1
test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval ($GAP s) after the latest close of anything on this host (RL-171 §6.1)"; exit 1; }
# R1 RESERVATION, fresh at the launch (RL-165 §7; RL-155 R-A; P1-2). Re-read the staged items and RUN_STATE now.
: "${SESSION_READY:?Set to yes if the lead has recorded a v4 session (R1 or W1) as READY, else no (RL-172 (f))}"
test "$SESSION_READY" = no || { echo "CEDE: a READY v4 session takes the next clean close (RL-172 (f); RL-155 R-A); do not launch; mail the lead"; exit 1; }
# RL-172 (f): RL-165 §7's worst-case reservation (launch + worst + 1,200 s <= SESSION_T0) is retired.
# The band and the campaign dependency, last of all
NOW=$(date +%s); test "$(pick_arg "$NOW")" = "$ARG" \
  || { echo "STOP: the clock left ARG $ARG's band (or this item's window) since Start and check; do not launch; mail the lead (a re-issue or a re-plan): the argument chosen in Start and check no longer belongs to the launch time"; exit 1; }
test "$NOW" -ge $((PRIOR_CLOSE_EPOCH + GAP)) || { echo "STOP: under the close interval after the prior span's close"; exit 1; }
{ test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || { echo "STOP: marker"; exit 1; }
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" \
  --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG" \
  --output "$OUT" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"; date +%s    # t0: the lead's alarm is t0 + 16,650 s (worst-case end) and t0 + 18,110 s (fence end)
```

Require exit 0, `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`), and the launch output's `plan.batch_windows` equal to `["$ARG"]`, the argument chosen in Start and check (else report it; the span is not counted until the lead rules). The launcher itself refuses a deadline under the plan's worst case plus reserves, a missing kit and malformed `--legs` / `--batch-window`. Record ARG, LAST_CLOSE_KIND, GAP, the journal-copy line (plan id and marker content), the batch-time print, PRIOR_CLOSE_EPOCH, PY, MAGISTRATE_PID, KIT and its sha256, OUT, DEADLINE, HOST_RESTORE_OK, OTHER_CLOSE_EPOCH, the host last close printed, SESSION_READY, the launch time (t0), the measurement_mode lines, the High Power preflight lines, the preflight sudo read and the plan in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/cadence-hp01-s01-out-<activation>.txt`, (the lead's watcher reads t0 from it for the alarm). Then exit at once, with no other `claude` or `codex` process running.

**Check (next activation, after the fence is gone).** Run the magistrate's own power reads FIRST, so they stand even if a receipt assert fails:

```sh
cd /Users/edr/code/jw-wt/cadence-hp01-s01      # the same checkout at dd206025a (D4: restore-owed exists only at or after it)
test ! -e "$CUSTODY/desk_fence.json"; launchctl list | grep -c 'com.joulewise.align-r0' || true   # expect 0
HP_MARKER=/Users/Shared/JouleWise/host-power/high-power.marker
"$PY" -B -c 'from joulewise.align.apple import powermode as p; print("pmset -g custom AC powermode", p.observe_ac_powermode())'   # must be 0
{ test ! -e "$HP_MARKER" && test ! -L "$HP_MARKER"; } && echo "no High Power marker" || echo "HIGH POWER MARKER PRESENT"
lsof -- /Users/Shared/JouleWise/host-power/night.lock 2>/dev/null || echo "night.lock: no holder"
pmset -g | grep -i powermode                                            # 0
sudo -n systemsetup -getusingnetworktime                                # Off
# kernel frequency word: 0 (item 251 remedy if not)
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo "no stray monitor"
pgrep -u root -fl powermetrics || echo "no root powermetrics"
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify; echo "verify rc $?"   # record lines (NOTE 1 applies)
```

**Maintenance line, after the power reads (RL-171 §5 item 1; as item 331). Print only: it gates nothing and is not a stop.** Set `ARG` to the batch-window argument recorded at the arm (`export ARG=...`); the receipt assert below compares with it. Then one read-only system-log query over the span's interval (from OUT's UTC launch stamp to the receipt's mtime) for the OS maintenance processes, saved BESIDE the journals as `$OUT/maintenance-log.txt`, plus a per-10-minute count printed for the report. Report the counts and which legs' intervals they overlap (from each `leg_summary.json`'s start and end, if present; else say "overlap left to the desk"). A leg hit by a maintenance job is judged by rule 5 as before (RL-171 §2 item 2). With `13:14-13:15` a leg may run through 02:00-02:35 (dasd about 02:08; XProtect to about 02:28): that is the case rule 5 exists for (one redo of about 21 min, quota 2).

```sh
: "${ARG:?Set ARG to the batch-window argument recorded at the arm}"; export ARG
START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\1/')"
START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")"
END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')"
echo "maintenance window $START_LOCAL .. $END_LOCAL"
sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \
  --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd"}' \
  > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err"; echo "log show rc $?"
wc -l < "$OUT/maintenance-log.txt"
# per 10-minute bucket and process: "HH:M0 process count"
awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
```


Then the receipt. It asserts `restore_proven` true in `span/result.json` and in the receipt's `span_result`, the close proof (`high_power.close_proof`: `proven` true, `ac_powermode` 0, `host_marker_present` false, `pmset_error` null, the production marker path), `restore.ok` true and every power step rc 0. It prints the D1 lines (`high_power.revoked`, `high_power.before_restore`) before any assert:

```sh
"$PY" -I -B - "$OUT" L001,L002,L003 /Users/Shared/JouleWise/host-power/high-power.marker <<'PY'
import hashlib, json, sys
from pathlib import Path
root, roster, marker = Path(sys.argv[1]), sys.argv[2].split(","), sys.argv[3]
KIT_SHA = "7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965"
FROZEN = "dd206025abb30fd5c07515cd4b34b3e653174810"
r = json.loads((root / "runner_receipt.json").read_text())
print(json.dumps({k: r.get(k) for k in ("rc", "runner_kind", "roster", "batch_windows", "legs_planned",
                                        "legs_finished", "load_redos_used", "span_result", "meter", "error",
                                        "late_signals")}, sort_keys=True))
print([(s["name"], s["rc"]) for s in r["steps"]])
hp = r.get("high_power") or {}
# D1: the withdrawal and the last look are printed BEFORE any assert, so a failed assert still shows them
print("high_power.revoked", json.dumps(hp.get("revoked")))
print("high_power.before_restore", json.dumps(hp.get("before_restore"), sort_keys=True))
print("high_power.restore", json.dumps(hp.get("restore"), sort_keys=True))
print("high_power.close_proof", json.dumps(hp.get("close_proof"), sort_keys=True))
bundle = root / "desk-bundle"
result = json.loads((bundle / "span/result.json").read_text())
print("result", json.dumps(result, sort_keys=True))
assert r["runner_kind"] == "cadence-legs-v1" and r["roster"] == roster
assert r.get("mock") is False
assert r["kit"]["sha256"] == KIT_SHA and r["kit"]["campaign_id"] == "cl-hp-01"
assert r["kit"]["frozen_commit"] == FROZEN
assert r["batch_windows"] == [__import__("os").environ["ARG"]], r["batch_windows"]   # ARG as recorded at the arm (RL-171)
names = [s["name"] for s in r["steps"]]
for once in ("soak", "frozen", "host_lock", "high_power_marker_absent", "powermode_guard", "high_power",
             "power_last_look", "restore", "power_proof", "host_lock_release"):
    assert names.count(once) == 1, (once, names.count(once))
assert all(s["rc"] == 0 for s in r["steps"] if s["name"] in (
    "frozen", "condition13", "host_lock", "high_power_marker_absent", "read_power", "powermode_guard", "soak",
    "high_power", "power_last_look", "restore", "power_proof", "host_lock_release")), "a power or preflight step rc != 0"
# The High Power close (RL-155 §5.2; design doc §13.2.1): restore proven, the close proof, no marker
assert hp.get("block_power_mode") == 2
assert hp.get("host_marker") == marker, hp.get("host_marker")
cp = hp.get("close_proof") or {}
assert cp.get("proven") is True and cp.get("ac_powermode") == 0 and cp.get("host_marker_present") is False \
    and cp.get("pmset_error") is None and cp.get("host_marker") == marker, cp
assert (hp.get("restore") or {}).get("ok") is True, hp.get("restore")
assert result.get("restore_proven") is True, result
assert (r.get("span_result") or {}).get("restore_proven") is True
for name, feed in r["feeds"].items():
    assert feed["stop"]["proven_stopped"]
    if name == "meter":
        continue   # RL-150 R8: only the runner hashes KM003C stream files; the magistrate does not open them
    for f in feed["files"]:
        with (root / f["path"]).open("rb") as h:
            assert hashlib.file_digest(h, "sha256").hexdigest() == f["sha256"]
files = sorted(p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file())
assert files == [f"legs/{x}/leg_summary.json" for x in roster] + ["span/meter.json", "span/result.json"], files
revoked = {e["leg_id"] for e in (hp.get("revoked") or [])}
for leg in roster:
    s = json.loads((bundle / "legs" / leg / "leg_summary.json").read_text())
    rec = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    mode = (rec.get("result") or {}).get("ac_powermode")
    # D1: admitted is read from the leg summary, never recomputed from the leg record (a withdrawn leg's record
    # still says ac_powermode 2). RL-157 §5's print: g0_s, wall_s, budget_s.
    print(leg, "admitted", s.get("admitted"), "revoked", leg in revoked, "leg_record.ac_powermode", json.dumps(mode),
          "g0_s", s.get("g0_s"), "wall_s", s.get("wall_s"), "budget_s", s.get("budget_s"),
          "over_1.5x", (s.get("wall_s") or 0) > 1.5 * (s.get("budget_s") or 0))
    print(leg, json.dumps(s, sort_keys=True))
print("meter", (bundle / "span/meter.json").read_text().strip())
clean = (r["rc"] == 0 and r["legs_finished"] == len(roster) and not revoked and result.get("restore_proven") is True)
print("RECEIPT OK" if clean else "RECEIPT NOT CLEAN: report in full")
PY

# RL-157 §1 print (gates nothing): seconds from the `high_power` step's end (stage journal) to L001's G0 start
# (the G0 gate row's entry_epoch_s in L001's outputs/align_thermal.jsonl).
"$PY" -I -B - "$OUT" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
rows = [json.loads(line) for line in (root / "chain-stages.jsonl").read_text().splitlines()]
ends, starts = {}, {}
for d in rows:
    (ends if d.get("event") == "end" else starts).setdefault(d["stage_id"], d)
hp_end = (ends.get("high_power") or {}).get("ended_epoch_s")
soak_end = (ends.get("soak") or {}).get("ended_epoch_s")
rec = json.loads((root / "legs" / "L001" / "leg_record.json").read_text())
n = len(rec.get("attempts") or [])
leg_start = (starts.get(f"L001.a{n}") or {}).get("started_epoch_s")
g0_entry = None
bname = (rec.get("result") or {}).get("bundle")
if bname:
    p = root / "legs" / "L001" / "runtime" / bname / "outputs" / "align_thermal.jsonl"
    if p.is_file():
        for line in p.read_text().splitlines():
            d = json.loads(line)
            g = (d.get("values") or {}).get("gate") or {}
            if d.get("module") == "temperature" and d.get("kind") == "align_thermal_gate" and g.get("kind") == "G0":
                g0_entry = g.get("entry_epoch_s"); break
def diff(a, b):
    return None if a is None or b is None else round(a - b, 1)
print("RL-157 §1", json.dumps({"soak_end_epoch_s": soak_end, "high_power_end_epoch_s": hp_end,
      "L001_attempts": n, "L001_attempt_start_epoch_s": leg_start, "L001_g0_entry_epoch_s": g0_entry,
      "soak_end_to_mode_set_s": diff(hp_end, soak_end),
      "mode_set_to_L001_attempt_start_s": diff(leg_start, hp_end),
      "mode_set_to_L001_G0_start_s": diff(g0_entry, hp_end)}, sort_keys=True))
PY

# RL-150 R1 part 3 print (gates nothing): soak reference; each leg's own reference; its G0 release reading;
# TV0h, TV1h, Tf08. Thermal journal values only: soak_reference.json, the soak's sensors journal,
# each leg's outputs/align_window_reference.json and outputs/align_thermal.jsonl. Nothing else is opened.
"$PY" -I -B - "$OUT" <<'PY'
import json, statistics, sys
from pathlib import Path
root = Path(sys.argv[1])
KEYS = ("TV0h", "TV1h", "Tf08")
def rows(path):
    out = []
    for line in path.read_text().splitlines():
        d = json.loads(line)
        if d.get("module") == "temperature" and d.get("kind") in ("reading", "align_thermal_gate"):
            out.append(d)
    return out
def reading(d):
    return d["started"]["monotonic_ns"], (d["values"].get("sensors") or {})
soak = json.loads((root / "soak" / "soak_reference.json").read_text())
sj = [reading(d) for d in rows(root / "soak" / "idle_soak" / "sensors" / "align_thermal.jsonl") if d["kind"] == "reading"]
end = sj[-1][0]
tail = [s for t, s in sj if t > end - 1200 * 10**9]
tf08 = [s["Tf08"] for s in tail if isinstance(s.get("Tf08"), (int, float))]
print("soak_reference", {k: soak["sensors_c"].get(k) for k in ("TV0h", "TV1h")},
      "Tf08_last1200s_mean", statistics.fmean(tf08) if tf08 else None)
for leg in ("L001", "L002", "L003"):
    rec = json.loads((root / "legs" / leg / "leg_record.json").read_text())
    bname = (rec.get("result") or {}).get("bundle")
    if not bname:
        print(leg, json.dumps({"no_bundle": True, "leg_status": rec.get("leg_status")})); continue
    out = root / "legs" / leg / "runtime" / bname / "outputs"
    j = rows(out / "align_thermal.jsonl")
    reads = [reading(d) for d in j if d["kind"] == "reading"]
    ref = json.loads((out / "align_window_reference.json").read_text())
    lo, hi = ref["span_ns"]
    ref_tf08 = [s["Tf08"] for t, s in reads if lo <= t <= hi and isinstance(s.get("Tf08"), (int, float))]
    g0 = next((d["values"]["gate"] for d in j if d["kind"] == "align_thermal_gate"
               and d["values"].get("gate", {}).get("kind") == "G0"), None)
    at = next((s for t, s in reads if g0 and t == g0.get("exit_sample_ns")), {})
    print(leg, json.dumps({
        "own_reference": {"status": ref["status"], "TV0h": ref["fast_c"], "TV1h": ref["slow_c"],
                          "Tf08_median": statistics.median(ref_tf08) if ref_tf08 else None},
        "g0": None if g0 is None else {"outcome": g0["outcome"], "duration_s": g0["duration_s"],
                                       "row_reference": g0.get("reference"), "row_release": g0.get("release"),
                                       "release": {k: at.get(k) for k in KEYS}}}, sort_keys=True))
PY
```

The receipt also carries the runner's own close steps (`power_last_look`, `restore`, `power_proof`, `host_lock_release`, `stop-*`, `close-*`); report them as the restore lines. Do not open `hazards/`, any `stream-*.jsonl`, any `powermetrics*` file or any `align_episode.json`.

**Restore owed (Mythos D4 and D3; design doc §13.2.1, §13.2.3).** Only if the Check shows AC powermode not 0, or a marker present, or no receipt / no `span/result.json`:
- **When it is safe (all must hold; record each):** the span's LaunchAgent job has exited (`launchctl list | grep -c com.joulewise.align-r0` prints 0) and its desk fence is gone or stale; no other span, session or night is running or loaded (no `desk_fence.json` under `$CUSTODY`, no `com.joulewise.(night|align-r0)` job: an Automatic span or a plan-0 night holds no lock, so the command cannot see one, D3); `lsof` shows no holder of `night.lock`; the marker's owner names this span (`head -c 4000 "$HP_MARKER"`: R1 crash tag, `writer` `cadence span`, `campaign_id` `cl-hp-01`, `output` = `$OUT`). If the marker is a W1 session's, or names anything else, do NOT run it: mail the lead.
- **The command (D4: from a checkout at or after `dd206025a`; this span's own worktree is one. The dev-01 and dev-02 worktrees at `b4b6aeb19` have no `restore-owed` and exit 2 on usage):**
  ```sh
  cd /Users/edr/code/jw-wt/cadence-hp01-s01 && "$PY" -B scripts/cadence_legs_runner.py restore-owed; echo "restore-owed rc $?"
  ```
  It takes the host night lock without waiting (it defers if anything holds it), runs the narrow rule's `pmset -c powermode 0`, reads 0 back, removes the marker only then, refuses a W1 session's marker, and exits 0 only when powermode 0 and no marker read back. Never a bare `sudo pmset`, never outside the lock. Then read `pmset -g custom` and the marker path again by hand and record both.
- Whatever it prints, RESTORE_UNPROVEN stays open and nothing arms: mail the lead. Only the lead clears the stop, with a RUN_STATE line (and, for an unproven leg child, under RL-157 §2 condition 2).

**Report** (by email to Ed and the lead, and as RUN_STATE TBD+1):
- the magistrate's own power reads (AC powermode, marker present or not, `night.lock` holder) and, if run, the restore-owed output with its "when safe" lines;
- the receipt line, the step list and RECEIPT OK (or the receipt in full if not clean);
- **D1:** each leg's `admitted` from its `leg_summary.json` (never from the leg record), the receipt's `high_power.revoked` and `high_power.before_restore`, as printed;
- each leg's `leg_summary.json` line; `span/result.json` (with `restore_proven`) and `span/meter.json`;
- RL-150 R9 with rule 6 meaning High Power: (1) three closes with complete records; (2) admitted count; (3) for any excluded leg, the rule it fell under (from `g0_outcome`, `contaminated_redos`, `leg_status`/decode cap, the leg's `ac_powermode`, and `high_power.revoked`); (4) left to the lead's hand-read; and whether any named stop would fire (the Air desk builds `stops.json` from the bundle);
- whether two legs ran over 1.5 × `budget_s` (LEG_OVERTIME: goes to the RESEARCH LEAD, RL-157 §5);
- the RL-157 §1 print and the RL-150 R1 print, as printed;
- the restore lines and the measurement_mode verify lines;
- whether the span crossed 00:00 (the `/private/tmp` walk; not a gate).

The magistrate reports; it never decides. Commit nothing from `$OUT`. Nothing is re-run and nothing else is queued.

**After (the lead, at the desk; not the magistrate).**
- **The Air desk (D6):** copy the desk bundle to the Air (`/Volumes/JW-EXT/cadence-desk/cq-hp-01-s01-a1/input`) and build the table from a checkout at or after `dd206025a`, WITH the kit, never `--adapter` (with `--adapter` the block mode is 0 and RESTORE_UNPROVEN is inert):
  `python3.13 -B scripts/air/cadence_desk.py build --plan-id cq-hp-01-s01-a1 --input /Volumes/JW-EXT/cadence-desk/cq-hp-01-s01-a1/input --out /Volumes/JW-EXT/cadence-desk/cq-hp-01-s01-a1/desk --kit <kit 7eaf2660… copied outside the checkout>`.
- **The hand-read (RL-150 R5; RL-157 §1, §5; Mythos D1, D5):** read the journal table once by hand beside the automatic desk.
  - **D1:** take `admitted` from each leg summary (the desk table has no `admitted` column yet, dev-01 F8), and read the receipt's `high_power.revoked` and `high_power.before_restore`.
  - **D5:** after a SIGKILL the last finished leg keeps `admitted: true` on disk with no later observation; rule 6 excludes it, and the hand-read says so.
  - RL-157 §1's print (mode set to L001's G0 start) and §5's print (each leg's `g0_s`, `wall_s`, `budget_s`), with RL-150 R1 part 3's print.
  - Record the smoke's verdict (RL-150 R9's four conditions with rule 6 meaning High Power), and restate the remainder's expected time from the three measured wall times, for the calendar only (RL-157 §5).
- **D1's second line (binds the remainder):** any `high_power.revoked` entry holds the next hp-01 span until the research lead rules, as a REFUSAL would. LEG_OVERTIME also goes to the research lead before the remainder arms.
- **Only then** append the remainder to the queue (RL-157 §3, §8). `dev-01-s03` ran L004-L007 and `dev-01-s04` L008-L012, so the default is the mirror file `QUEUE-cl-hp-01-dd206025a-append-mirror-4plus5.json` (sha256 `01687bb7b1206c82657ff018130f8761f249b64b5fa6524f4b3914d0c81a00a5`, in `/Volumes/JW-EXT/scratch/hp01-ready/queue/`): `hp-01-s02` L004-L007, then `hp-01-s03` L008-L012. Record in a RUN_STATE line which file was chosen and why.
- **The remainder's gates (RL-165 §5, §6, §7).**
  - **Line 2:** the finished CI run on `2a8deb7b9` (43673985768) shows the base set plus 0, test for test, before `hp-01-s02` arms. If it shows any added red, that red is fixed and re-run; nothing arms on an explanation.
  - **Line 9:** `hp-01-s02` is campaign span 5 and needs `dev-01-s04`'s desk final (span 3); `hp-01-s03` is span 6 and needs this smoke's desk final (span 4).
  - **Latest t0 (worst-case end by 00:30; RL-165 §7, kept by RL-171 §2):** four legs **19:07:30**, five legs **18:22:30**; never 10:50-13:15 on this pin. The argument follows the launch time as here: `13:14-13:15` before 02:35:00 (`02:00-02:35` refuses four legs from 20:37:31 and five legs from 19:52:31 to 02:34:59), `02:00-02:35` from 02:35:00. The 02:40 starts are retired (RL-171).
  - **Forecast** (Air `plan` at `dd206025a`, `/Volumes/JW-EXT/scratch/items-rl171/plans/chain-new.txt`): smoke 03:01:45-04:56:48 expected; `hp-01-s02` at 05:16:48 (after a 20-min hand-read) expected end 07:32:42, worst 10:39:18; `hp-01-s03` at 07:37:42 (s02's close + 5 min) expected end 10:14:27, worst 13:45:12; all three on `02:00-02:35`. A remainder not READY by 10:50 waits for 13:15.
  - **Alarm:** the lead's watcher alarms at each remainder span's worst-case end too (RL-165 §7).
  - **Then (RL-165 §2):** the dev-02 pull (`dev-02-s02`, L001-L006, any Sunday t0 outside 10:50-13:15; RL-171 retires its 18:33:10), then the standing F0.
