# JouleWise Run State

This is a log of typed items written by `scripts/run_state_add.py`.
Instructions live in `docs/process/RULES.json`, `docs/process/mbp/QUEUE.json`,
and `scripts/mbp_sched.py`.

<!-- RUN_STATE TYPED ITEMS: newest first. Add with scripts/run_state_add.py; never edit by hand. -->

431. **Kill census blockers, never wait on them (owner directive, standing): pre-arm kill + immediate zero-capture retry; KILL-NEEDED escalates to the lead**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794990961, "number": 431, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **Owner directive (Ed, 2026-11-18 00:47):** "kill the processes on the mbp blocking the windows if it can't". Any process that would make the agent census refuse a start is killed, not waited on. A census refusal that measured nothing is retried at once.
- **Standing procedure.** Run it immediately before every Start and check, and again after any zero-capture `start-agents` / `night_refused_agent_present` refusal.
  1. **List** census hits with the runner's own census patterns (measurement_mode.zsh and the runner's start-agents check).
  2. **Never kill:**
     - your own process tree (the magistrate's claude, its shell and MCP children);
     - launchd jobs `com.joulewise.*` and `local.jwbench.*`;
     - the measurement runner, powermetrics and the meter reader of a span that is armed or closing.
  3. **Kill everything else the census names:** SIGTERM, then after 5 s SIGKILL. That includes `codex app-server` daemons (`codex app-server daemon stop` first), stray `codex exec`, other `claude` sessions (the owner's interactive ones included), Ollama/LM Studio servers, and Spotlight/backup helpers only if the census names them.
  4. **Re-run the census.** If it is clear, launch. A refused attempt with zero capture relaunches immediately as `rerun_of` (retry class: Ed 2026-09-16; RL-179 row 21), at most two retries per span. Then the kit is held and the lead is told.
  5. **Record** the pids, names and the signal used in the item.
- **If you cannot kill** (permission refused, or a root-owned process): put `KILL-NEEDED` and the pids in the item heading and push at once. The lead's watcher reads every magistrate commit and will kill them over ssh. The span's Check is on main at that point, so ssh is allowed. Then go on with the ladder; do not wait.
- **Scope:** this is about the census only. Host stops (restore unproven, disk, meter missing) and item 423's maintenance marker still bind. The marker means the owner is working on purpose: never kill around it.

430. **dev-05-s02 re-issued for Wed: pred_gate reads a2, day_gate counts measured legs only (a1 zero-capture = 0); standing pre-arm codex daemon stop**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794990930, "number": 430, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **dev-05-s02 (item 394) is re-issued for Wed 18 Nov, as issued, with two input corrections and nothing else.** a1 (`cq-dev-05-s01-a1-20261118T082155Z`) was a zero-capture `start-agents` refusal: 0 of 6 legs, nothing measured (item 429).
  1. **`pred_gate`:** dev-05-s01's output is the a2 directory. a1's directory is a refused attempt, not a second run, so ignore it. s01 counts as CLEAN only if a2's Check is clean.
  2. **`day_gate`:** count legs that started measuring. A zero-capture refused attempt contributes 0. a1 contributes 0 of its 6, so Wed's count is a2's 6 plus s02's 6, which is 12 of 12.
- **Authority:**
  - Ed's standing ruling of 2026-09-16: zero-capture `agent_present` refusals are retry class.
  - RL-179 row 21: a refusal holds a kit only until its input changes.
  - The day rule protects the number of development legs measured on a date (validity). A leg that never started is not measured.

  This is the lead's bookkeeping call. It goes to the research lead in the next batch for the record, and no wait is attached.
- **Window:** Wed 18 Nov, as item 394 states. Launch at a2's close proven (RL-179 F-2: no timed gap). Then R1 as issued (items 397 and 398).
- **New standing pre-arm step (SAFETY: the agent census; item 429's cause).** Codex 0.170 starts a managed app-server daemon (`codex app-server ... --managed-daemon` plus a `pid-update-loop`) whenever codex runs on this Mac. Immediately before every Start and check, run:
  - `codex app-server daemon stop 2>/dev/null`;
  - then `pgrep -lf '[c]odex app-server'`. If anything is still listed, SIGTERM it and check again.

  Record the result in the item. This replaces nothing; the runner's own census still decides.

429. **Magistrate 2c5d1d02 (headless, Opus 5.5), 2026-11-18 00:29-00:40 PST (`date`): dev-05-s01 attempt 1 REFUSED at start (agent census: Codex 0.170 managed daemon left by the owner update; 0/6 legs, zero capture); daemon stopped; a1 copied; ATTEMPT 2 Start and check rc 0 and launches as the last act; dev-05-s02 needs a lead re-issue**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794990875, "number": 429, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [{"at_epoch_s": 1794990875, "item": 427, "status": "CLOSED"}], "status": "ISSUED", "supersedes": []}
```

- **What happened to attempt 1.** `cq-dev-05-s01-a1-20261118T082155Z` (launched 00:21:56 by magistrate 68797558, item 427) was refused by the runner's own agent census at `start-agents` at 00:22:08: `night_refused_agent_present`. The two processes were Codex 0.170.0's managed app-server daemon: pid 56751 (`codex app-server daemon pid-update-loop`, started 00:13) and pid 57060 (`codex app-server --listen unix:// --managed-daemon`, started 00:18). Codex moved 0.169.0 -> 0.170.0 between 00:04 and 00:18 (`~/.codex/packages/app-server-daemon/selection-history` 00:18:40); Claude Code is now 2.1.327 (was 2.1.322). This is item 423's owner update, done without the MAINTENANCE marker, and the same fault class as items 78 and 158. Receipt: rc 2, REFUSED, 0/6 legs, no soak, no meter file, every close step rc 0. **Zero capture: no data was taken and nothing can be biased.**
- **Check of a1 (item 393 "Check", custody `cadence-dev05-s01-postcheck-2c5d1d02.sh`, output `-postcheck-out-2c5d1d02.txt`, 00:31:40):** RECEIPT NOT CLEAN (first assert fails: no soak step; the R1 print stops on the missing `soak_reference.json`). Steps: deadline 0, frozen 0, night_agents 0, ac_power 0, condition13 0, start-agents 2, restore 0, stop-volumes 0, stop-meter 0, stop-agents 0, close-volumes 0. Maintenance log 00:21:55-00:22:08: 19 lines (backupd 3, mds 6, softwareupdated 9). Restore lines all pass: no desk fence, no align-r0 label, powermode 0, Network Time Off, kernel frequency word 0, no High Power marker, no stray monitor or root powermetrics, AC, not charging; free 273 GiB. measurement_mode verify: the one FAIL is this session's own children (codex MCP adapter 57600/57603/57608, pdf MCP 57601).
- **Cure.** `codex app-server daemon stop` (stopped 57060), then SIGTERM to 56751; `pgrep -lf '[c]odex'` afterwards shows only this session's MCP children, which end with it.
- **Copy (RL-179 row 14, at once).** a1 offloaded encrypted to iCloud Drive `JouleWise-offload/cq-dev-05-s01-a1`, round trip 10 entries, enc sha256 `1087af3a…d365`, manifest `87e7608e…84ac` (7 files); marker `/Users/Shared/JouleWise/desk-copy/cq-dev-05-s01-a1.ok` written 00:33:32. Scripts `offload-dev05-s01a1-{,run-}2c5d1d02.sh`. (Slip: the brctl and poll lines were appended to the old `offload-dev04-s02-{brctl,poll}-c3cdda76.txt` files; cosmetic.)
- **Decision I made: attempt 2 now, `rerun_of` cq-dev-05-s01-a1.** Item 393's line "a span that ran but ends with ... a receipt rc≠0: nothing relaunches ... a re-run ... needs a ruling" is not applied as written. Authorities: Ed's standing ruling of 2026-09-16 (zero-capture `agent_present` refusals are retry class: nothing was measured, so a retry cannot bias anything); RL-179 row 21 (a launcher refusal holds that kit or block only until an input changes; the input changed: the daemon is stopped); item 422's on_early_or_refused (apply the rest, record which and why, mail the lead, never idle the Mac); CLAUDE.local.md "physics refuses; everything else is a flag". The physical hazard (an agent alive) was real and refused correctly; it is now gone. The t0-date stays Wed 18 Nov, so dev-05's date holds. If the lead disagrees, a2's legs can be ruled out of the count; nothing else is touched.
- **Attempt 2 Start and check (dry run, no launch) 00:34:01-00:34:03, rc 0** (custody `cadence-dev05-s01a2-check-2c5d1d02.sh`, output `cadence-dev05-s01a2-out-2c5d1d02.txt`; inputs `cadence-dev05-s01a2-inputs-2c5d1d02.sh`: MAGISTRATE_PID 57586, LAST_CLOSE_KIND campaign (GAP 300 s after a1's close 00:22:08), HOST_RESTORE_OK 1 from the a1 Check, OTHER_CLOSE_EPOCH 0, SESSION_READY no, PRIOR_CLOSE_EPOCH unchanged). ARG `13:14-13:15`; journal copy of a1 present; t0-date development legs already launched 6 (a1's roster, mixed 6) + this span 6 = 12, at the RL-172 (a) cap; PRED CLEAN dev-04-s02; expiry 12:32:46; validate-kit ok; next OS batch 02:08:39 (rule 5's redo covers it). Unit tests not re-run: same worktree at `2d347f721`, clean, 26 min after item 427's eight modules passed.
- **Deviation from item 427's scripts (one line each):** the OUT suffix `-a1-` -> `-a2-`, the inputs file and the output and launcher-JSON file names. Launch script `cadence-dev05-s01a2-launch-2c5d1d02.sh`.
- **Item 423:** no MAINTENANCE marker at 00:29 or 00:33. Versions now `claude` 2.1.327, `codex-cli` 0.170.0. Loaded: `com.joulewise.magistrate`, `local.jwbench.keepawake`.
- **dev-05-s02 (item 394) will need the lead.** Its `pred_gate` STOPs when `dev-05-s01` has two output directories ("a re-run needs the lead"), and its `day_gate` will count a1's roster (6 legs that never ran) and refuse at 18 > 12. Both are bookkeeping, not physics; the lead should re-issue s02 for Wed 18 Nov (window to 23:59:59, outside 10:50-13:15) or rule the count, while a2 runs.
- **Next exact action:** the launch is this activation's last act (`cadence-dev05-s01a2-launch-2c5d1d02.sh`, which re-runs Start and check, then the host gate, then launches). After the fence is gone (deadline in `cadence-dev05-s01a2-launch-2c5d1d02.json`), the next activation runs item 393's Check on the a2 OUT (copy `cadence-dev05-s01-postcheck-2c5d1d02.sh`, OUT -> the a2 directory), copies it at once, and reports (email to Ed and the lead, RUN_STATE). Then dev-05-s02 only under a lead re-issue or ruling; otherwise the filler ladder (item 422).
- Activation 2c5d1d02 (00:29:20): notice_pending []; no unread mail from Ed; directives the standing seven, no stop; no standdown request. Canonical ff'd 668f20e3a -> 530c6cc36 (no night label or plist). Supersedes nothing; closes 427.

428. **F2 instrument roster as one-leg spans available (RL-179 (b)): 33 drafts at audit e26a566c1; finite filler rung**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794990040, "number": 428, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **What:** the rest of the F2 instrument roster, split into one-leg spans (RL-179 (b) AMEND): 33 drafts with queue entries, on `origin/audit/2026-11-10-fable` at `e26a566c1` (branch `align/2026-11-18-f2-pieces`). They replace the multi-leg ITEM-f2-p01..p04 drafts.
  - Same kits, same runner pin `2d347f721`.
  - `f2-inst-01` starts at L004. Items 407 and 411 record L001–L003 as done.
  - The `f2-inst-02` and `-03` drafts are marked "run status unknown": skip any leg your records show as run.
- **Ladder rung:** finite fillers, after the first f2-stab leg of each date and before hp-02 (RL-179; item 425). A non-clean predecessor voids only later legs of the same kit (RL-179 F-6).
- **Issue** under item 418 (d) from the committed drafts.
- **Sealing** is as item 425: no leg counts or enters a fit.
- **Hand checks:** piece 1's hand-read (item 411) is owed before a look reads it, not before the next arm (RL-179 F-3).

427. **Magistrate 68797558 (headless, Opus 5.5), 2026-11-18 00:10 PST (`date`): dev-05-s01 (item 393) PRE-LAUNCH: Start and check rc 0 at 00:08:47, predecessor dev-04-s02 CLEAN, ARG 13:14-13:15; Run block launches at or after 00:21:22 (F0 run 11 close + 1,200 s) as the last act; next: Check after the fence, then dev-05-s02 (item 394)**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794989427, "number": 427, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **Item 393 as issued (item 422: "run as issued"; item 418 (e) not needed: 24 h expiry Wed 12:32:46 is later than the planned t0).** Span `dev-05-s01`, legs L001-L006, kit `cl-dev-05.v1.1` `2747381b…ca1a`, runner `cadence-legs-v1.1`, pin `2d347f721` in the fresh worktree `/Users/edr/code/jw-wt/cadence-dev-05-s01` (created by this activation; HEAD and clean tree asserted).
- Scripts: custody `cadence-dev05-s01-check-68797558.sh` and `-launch-68797558.sh` = lines 3-300 / 3-335 of `dev05-issue-c6a5728a/blocks-s01.sh` (item 393's code blocks), inputs in `-inputs-68797558.sh`. Deviation (one line, as d9ae12c0): the three canonical-root `git fetch` lines are replaced by object-presence checks of `2d347f721`, `fecaf73f3`, `b7a0d9882` (all local).
- Inputs: MAGISTRATE_PID 54753; PRIOR_CLOSE_EPOCH 1794923630 (dev-04-s02 receipt 05:51:03, fence seen gone 05:53:50 by c3cdda76); LAST_CLOSE_KIND other (newest close = F0 run 11, 00:01:22; GAP 1,200 s, so earliest 00:21:22 = 1794990082); OTHER_CLOSE_EPOCH 0; HOST_RESTORE_OK 1 (item 426); SESSION_READY no (item 397).
- Tests (fresh worktree, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, python3.13, one module at a time): test_kit_v11 30 OK, test_span_reference 19 OK, test_legs_runner 42 OK, test_kit 18 OK, test_stops_desk 14 OK, test_runner_guards 8 OK, test_launch_cadence_span 12 OK, test_r1_smoke_launcher 58 OK (custody `cadence-dev05-s01-tests-68797558.txt`).
- Start and check 00:08:45-00:08:47 PST, rc 0 (output `cadence-dev05-s01-out-68797558.txt`): ARG `13:14-13:15` (launch time in 18:33:11-02:34:59); `verify_r1_executed_sources` = full `2d347f721…`; copy gate non-campaign (newest close F0 run 11); t0-date 2026-11-18 development legs already launched 0, this span 6 mixed-size; **PRED CLEAN dev-04-s02** (rc 0, 6/6, MEASURED_OK COMPLETE, close steps rc 0, overtime 0, contaminated redos 0); expiry valid to 12:32:46; validate-kit ok (cl-dev-05, frozen 2d347f721, frozen_paths_verified, kit sha, legs 12); queue sha `391f4382…afbb` at `b7a0d9882` OK; measurement_mode verify: one FAIL, "agent process present", PIDs 54768 (codex MCP adapter), 54769 (pdf MCP server), 54771/54772 (codex app-server), all children of 54753 (this session; RL-150 F5 line: proceed); WARN battery charge limit none, WARN softwareupdate schedule on (known, item 201); Network Time Off; next OS batch Wed 02:08:39 PST (print only); no High Power marker; night.lock no holder; no desk fence; sudo kill rc 0; no r12; no stray monitor; no root powermetrics; no night/smoke agent; powermode 0; preflight ac_power true, free 284.5 GB; plan batch_windows ["13:14-13:15"], expected 11,680 s, worst 24,750 s, blackout_clear true, budgets as the item (1156/1467/1642/1076/1642/1547).
- **RL-149 §2.8 lines:** 1-5 and 8 as the item states (evidence above and in item 393); 6: no open `cadence-stop` issue, directives the standing seven with no stop, no RESTORE_UNPROVEN, no High Power `revoked` hold; 7: watcher FLAG (item 387), `watch_gate` returns 0; 9: as run, this is campaign span 13 (dev-04-s01/s02 were 11/12; F0 and F2 spans are not campaign); span 11's desk `dev-04-s01` is FINAL (item 393 line 9).
- **Item 423:** no `/Users/Shared/JouleWise/MAINTENANCE` marker at the check; the Run block re-checks nothing else for it, so this activation re-checks the marker immediately before the launch. The owner's Claude/Codex update did not happen in the gap (versions unchanged at 2.1.322 / 0.169.0); the next gap is after this span's close (expected ~03:36, worst ~07:15 PST).
- Batch: with `13:14-13:15` the span may run through 02:00-02:35 (OS batch ~02:08); rule 5's redo covers it (item 393 Check note).
- Launch: the Run block (re-runs Start and check on fresh state, then the host gate) at or after 00:21:22 PST, as the last act; output and launcher JSON go to `cadence-dev05-s01-out-68797558.txt` and `cadence-dev05-s01-launch-68797558.json`. A STOP, WAIT, or LAUNCH_RC other than 0 there means nothing ran.
- **Next exact action:** after the fence is gone (deadline in the launcher JSON), the next activation runs item 393's "Check" with ARG `13:14-13:15` and reports it (email to Ed, RUN_STATE item); then `dev-05-s02` (item 394) as issued.

426. **Magistrate 68797558 (headless, Opus 5.5), 2026-11-18 00:05-00:06 PST (`date`): STANDING-F0 run 11 (item 346; pre-launch item 421) CHECK: RECEIPT OK, verdict pass, every judged line equal to run 10; restore lines pass; closes 421; next: dev-05-s01 (item 393) at 00:21:22**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794989391, "number": 426, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [{"at_epoch_s": 1794989391, "item": 421, "status": "CLOSED"}], "status": "CLOSED", "supersedes": []}
```

- F0 standing notice: run 11, trigger (b) NOT_READY `dev-05-s01-not-before-wed-0000-item418` (item 421). t0 22:02:34 PST Tue (1794981754); receipt 00:01:22 PST Wed (1794988882; span 7,128 s). The align-r0 label and fence were gone; this activation spawned 00:04:17, after the receipt, so no agent was alive during the run.
- Receipt rc 0; parts `{"C": true}`, `parts_requested` "C", fresh soak; every step rc 0; one `close-volumes`; every feed proven stopped and hash-checked: RECEIPT OK. Soak rc 0, sha256 `efe9eee59c04306dd9c7774cc531ae857b8c1d4c59fb5a6c4d6ceb7de714d883`. Part-C rc 0.
- smoke_part_c.json (evaluation only): verdict `pass`; disposition as printed. Lines, with run 10 (item 416) beside: `d_bank_mechanics` pass (pass), `d_bank_start_state` pass (pass; 4 samples, level 0, Nominal, fresh), `step_d` pass (pass; g0_wait 202.96 s, slope -0.180 C/min, 0.359 C over reference), `x_g` pass (pass; no G1 timeout, no x7). `admitted_turns` not judged: "not_applicable: episode returned at turn 1" (own stop, value 2 of 3). gate_time 200.38 s of limit 389.14 s; h_records match. Log: "three-turn clause not evaluated: one D run". N_chunk 4096; T_dead 972.846 s. No line differs from run 10, so rule 10 routes nothing.
- printed_not_judged (print only): turn-1 last-512 clock ratio 0.923, inside the predicted 0.83-0.93 band (run 10 0.933); first off-nominal pm Moderate at token 1,581 (run 10 1,678); token-rate ratio null in this print; tv1h_trigger does not fire (2 unequal rows outside gate windows of 1,149). Desk verdict member excluded on `thermal.powermetrics_non_nominal` (turn 1), as before.
- Maintenance (log show rc 0, 46,881 lines, 22:02:31-00:01:22): dasd 18,987 total; **a software-update burst at 23:00-23:10** (`softwareupdated` 3,018 + 46 lines, `mobileassetd` 2,021 + 34, `XProtect` 56, `XProtectPluginService` 843, all in the 23:00 bucket), otherwise `softwareupdated` 8 at 22:10 and 22:50, `backupd` 6-30 per 10 min, `mobileassetd` 122 at 23:50. X_G still passes. Run 10 had no XProtect lines; print only, for the research lead's reading of the series.
- Restore lines all pass: no desk fence; no align-r0 label; plist ProcessType Interactive; powermode 0; Network Time Off; ntp_adjtime freq word 0; no High Power marker; no stray monitor or root powermetrics; AC connected, not charging, 0 mA.
- Copy: an F0 close is non-campaign; this Check covers the copy. Commit nothing from `$OUT`.
- Closes 421 (pre-launch record). Script and output: custody `standing-f0/check-68797558/` (`check.sh`, `out.txt`).
- Activation 68797558 (00:04:17): notice_pending []; no unread mail from Ed; open directives unchanged (the standing seven; no stop); no cadence-stop issue; no standdown request; no `/Users/Shared/JouleWise/MAINTENANCE` marker (item 423). Canonical ff'd 7aa674717 -> 668f20e3a (items 421-425; no night label loaded, no night plist on disk). Versions now: `claude` 2.1.322, `codex-cli` 0.169.0 (item 423 asks for these after the maintenance; recorded now since the marker never appeared before this arm).
- **Item 424 not done:** the commit of `measurement_mode.zsh` (sha256 `4d93d690096eda30d23c69cba194b73232ae442986ea6bbb972258105d5a4593`, 513 lines; secret scan clean: no tokens, passwords, key material or email addresses; lines 24 and 113 describe the host's sudoers NOPASSWD setup) to public main was refused by this session's permission classifier ("Unsanctioned Communication"). Not retried; item 424 says skip rather than delay an arm. The lead (or Ed) should do the copy from an interactive session or grant the permission.

425. **f2-stab-01..14 available as standing fillers (RL-179 F-4, RL-180 row 13): 168 one-leg drafts at audit f9b03c33d**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794988890, "number": 425, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **What:** 14 stability kits, `f2-stab-01..14`, each with 12 single-leg spans. That is 168 unissued drafts with queue entries. They sit on `origin/audit/2026-11-10-fable` at `f9b03c33d`, under `docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/` (MANIFEST.md lists each kit's sha256 and seed).
  - Runner pin: `2d347f721`, unchanged.
  - Worst case per span: 5,850 s.
  - Every kit matches `f2-inst-01` cell for cell (RL-180 row 13). The validator check is in `f2-stab/tools/validate_kit.py`.
- **Ladder (RL-179 F-4, item 422):**
  1. the first f2-stab leg of each local date;
  2. the remaining f2-inst pieces;
  3. hp-02;
  4. further f2-stab legs;
  5. F0, the last rung, until R1 closes.

  Counted entries (dev-05, R1) keep their priority as issued.
- **Issue:** under item 418 (d) from these committed drafts. Before each issue, check the kit's sha256 against MANIFEST.md and run `validate_kit.py` against f2-inst-01.
- **Status:** sealed under RL-169 §3 and RL-179. No leg is campaign data, enters a fit, or counts anywhere (RL-180 restored row). Close and copy as for any span.
- **Item 423 still binds:** nothing arms while `/Users/Shared/JouleWise/MAINTENANCE` exists.

424. **Copy measurement_mode.zsh into the repo (Brief D): read-only, at a close, never delays an arm**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794987662, "number": 424, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **Ask (Brief D, process audit O-11 / X-18):** `/Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh` runs at every arm and close but is in no commit.
- **At your next activation with no span armed** (after F0 run 11's Check, or during the owner's maintenance hold under item 423), do the following. It is a read-only copy and changes nothing on the host.
  1. Run `shasum -a 256` on the installed file.
  2. Scan it for secrets: tokens, passwords, key material, email addresses. If any are present, stop and report only the line numbers. The repo is public.
  3. If it is clean, commit the exact bytes to main as `ops/host/measurement_mode.zsh`, and the hash line as `ops/host/measurement_mode.zsh.sha256`.
  4. Add one line to your next item giving the sha256.
- **The lead's builder then adds** the matching check and a README. It never changes the script's bytes.
- **Priority:** this never delays an arm. If it would, skip it and do it at the next close.

423. **Owner maintenance marker (standing SAFETY predicate): while /Users/Shared/JouleWise/MAINTENANCE exists, arm nothing; owner updating Claude Code and Codex after F0 run 11**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794987211, "number": 423, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **What:** the owner will update Claude Code and Codex on this Mac and relaunch its LaunchAgents. He will do it in the gap after STANDING-F0 run 11 closes and before dev-05-s01 arms.
- **Standing SAFETY predicate (Register class SAFETY: no unpredictable process during a measured span; RL-171, "quiet means processes"):** while `/Users/Shared/JouleWise/MAINTENANCE` exists, the host is not quiet.
  - Arm nothing.
  - Re-check every 60 s.
  - When the file is gone, re-run the start check and arm the next eligible entry at once.
  - The file is the owner's to create and remove. No agent creates it.
  - It blocks only arming. It does not block a Check or a close.
- **After the owner removes the marker,** the next activation records `claude --version` and `codex --version` in its first item and confirms that every LaunchAgent the magistrate depends on is loaded (`launchctl list`). It does this before arming dev-05-s01.
- **A relaunch of the magistrate's agents during the maintenance** may end a waiting activation. That is expected. The next activation resumes from RUN_STATE.
- **dev-05-s01 has slack.** COUNTED_LATEST is Wed 17:02:29 (item 421), so a short maintenance gap costs no date.

422. **Laptop lead (interactive, Opus 5.5), 2026-11-17 22:09:24 PST: RL-179 IN FORCE: no timed close gaps (close proven), copy waits at most 600 s, no caps or ages, High Power any hour, pre-notice hold withdrawn, filler ladder f2-stab then f2-inst then hp-02 then F0 until R1; dev-05 and R1 run as issued**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-20T23:59:00-08:00
on_early_or_refused: apply RL-179's Register from your next activation as this item states; dev-05 and R1 (items 393, 394, 397, 398) run as issued; if a point cannot be applied as written, apply the rest, record which and why, mail the lead, and never idle the Mac waiting for an answer
next_observable: the first pre-launch record that arms with no timed close gap (close proven), and each record naming the RL-179 rows it used
```

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794982164, "number": 422, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": ["420"]}
```

- **RL-179 (Fable 5.2) is committed** on `audit/2026-11-10-fable` at `163fa6194` (RESEARCH-LEAD-DECISIONS.md, verbatim; the Mythos audit beside it under `evidence/process-audit-1117/`). Its Register (rows 1-29) **is in force from this item**. The lead ports the rows to `docs/process/RULES.json` with the scheduler PR; until then the Register table in the ruling is the list. Item 418 stands except where this item amends it.
- **Run as issued:** items 393, 394, 397 and 398 (dev-05 and R1), every line, with item 418 (e). Their own gap lines stay because they are issued bytes.
- **For everything else, from now:**
  - **Close gaps (row 4).** No timed 300 s or 1,200 s gap. A successor arms when the previous close is proven (Check done: receipt OK, fence gone, restore lines pass) and no foreign process is alive. The soak's own slope test and G0 release are the start-state rule (row 5); nothing is added on top.
  - **Copy (row 14).** Stop the copy before the next soak. The arm waits for an unfinished copy up to **600 s**, then proceeds whatever the provider says. Mail the lead if a close is still uncopied at 2 h, and daily after. No original is deleted until two verified copies and the key exist off the MBP (row 15). dev-01 to dev-05 originals stay raw (row 16).
  - **Stops (rows 17-21).** Only restore unproven or an unowned High Power marker (one retry of the pinned restore, then halt and mail), disk under the floor, and meter or collector absent stop all work. CONTAMINATED_REDOS holds counted and v4 entries until one clean span. LEG_OVERTIME, a non-clean close or a launcher refusal makes only that kit or block ineligible until an input changes.
  - **No caps or ages (F-6).** No three-ahead cap, no 24 h item expiry, no seven-day queue expiry.
  - **High Power at any hour (F-9).** The pre-notice hold (RL-175 A.3) is withdrawn (F-10); a READY record still does not take effect between the two spans of a qualification block (row 23).
  - **Dated blocks (rows 1-2).** A filler arms only if every span of each pending dated block can still take its t0 on its date. Development and qualification spans keep their date rules; a missed date is re-dated by the same rule, not by the lead.
- **The filler ladder (F-4 c), when nothing counted can arm now:** (1) the first `f2-stab` leg of the local date, once its kits exist; (2) `f2-inst-01`'s remaining legs as one- or two-leg spans, then `f2-inst-02` and `-03`; (3) hp-02, only if `lm-hp-01` has not run; (4) further `f2-stab` legs; (last, until R1's post-close Check) F0. After R1's post-close Check, F0 leaves the ladder; one Part C runs at each W1-line pin change. Extra development-shaped legs are never fillers. Item 418 (d)'s permission to issue F2 and hp-02 entries from the committed drafts stands.
- **Lead lanes started:** `f2-stab` kit family (Sol builder, data only); the PR #795 spec under F-12 (to the research lead once, before the build); porting the protected clauses of RL-1 to RL-178 into the register (row 29); the scheduler PR carries the rows.

421. **Magistrate c047c9dc (headless, Opus 5.5), 2026-11-17 22:02 PST (`date`): STANDING-F0 run 11 pre-launch under item 418 (a), (f), (h): spacing deleted; rule 7 bound to dev-05's Wed date; Start and check rc 0; launch follows; next: Check, then dev-05-s01**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794981725, "number": 421, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- Relaunch at 21:59 PST: notice_pending []; no unread owner mail; directives #587, #422, #421, #417, #416, #408, #405 unchanged (nothing new). Canonical ff'd 344473346 -> 7aa674717 (items 418-420; no night label loaded, no night plist on disk).
- **Item 418 points used: (a), (f), (h).** (a): rule 5 spacing deleted from the scripts (last F0 t0 1794971221 printed only), the W1-head VOID and the age expiry made print-only. (f): without this F0 the Mac sat idle ~2 h to dev-05-s01's 00:00 earliest with no physical reason. No higher item can arm now: dev-05-s01 not before 00:00 Wed; F2 p02-p04 and hp-02 are not issued and cannot be filled before rule 6's 22:40 end.
- Scripts: custody `f0-startcheck-c047c9dc.sh`, `f0-run-c047c9dc.sh` = e0552b22's cap-free templates with the three item-418 (a) edits and the header (MAGISTRATE_PID 45571, TRIGGER not_ready, TRIGGER_SPAN dev-05-s01-not-before-wed-0000-item418, OUTSTANDING_REFUSAL none, HOST_RESTORE_OK 1, UNPROVEN_GROUP 0, HOLDING_STOP none, OTHER_CLOSE_EPOCH 0, LAST_CLOSE_KIND other, SESSION_READY no (item 397: READY only from dev-05-s02's launch record), RESTART_PENDING no).
- **Rule 7, COUNTED_LATEST = 1795050149 (Wed 18 Nov 17:02:29 PST).** Derivation: rule 7's text binds the latest legal t0 of a counted span; dev-05's date window ends 1795075199 (Wed 23:59:59, item 393 LIMIT; item 418 (e) makes that the expiry); minus dev-05-s01 worst case 24,750 s and the 300 s campaign close gap gives the latest s01 t0 that still leaves dev-05-s02 a Wed t0. Item 412's stricter "before 00:00" reading belonged to that waiver, which item 418 supersedes. Cost: dev-05-s01 starts at this F0's close + 1,200 s instead of 00:00 (expected ~00:20, worst ~01:45 Wed); s01 worst end ~08:40, s02 and R1 (window to Sat 21 Nov) keep their dates.
- Start and check 22:01:24-22:01:29 PST, rc 0: W1-line head b2e01464d unchanged; 17 hashes match; verify_r1_executed_sources = b2e01464d...; RL-89 Mac check OK (60/16/44); launcher test OK; census 26 receipts, newest = F0 run 10 receipt (1794978344, other, gap 1,200 s met); copy gate non-campaign; night.lock no holder; sudo kill rc 0; no r12, no campaign span, no stray monitor, no root powermetrics; only agent processes are this session and its own codex MCP adapter children (in tree 45571, NOTE 1); Network Time Off; powermode 0; preflight ac_power true, free 285.7 GB; ntp_adjtime offset 0, rate +0.743 ppm; battery ExternalConnected Yes, IsCharging No, InstantAmperage 0. Batch print: next OS batch Wed 02:08:39 PST. Output `f0-startcheck-out-c047c9dc.txt`.
- Launch follows this commit as the last act (Run re-checks eligibility); its output goes to `r1-partc-f0-out-c047c9dc.txt` and the ledger. No email: item 418 (g) (no mail per F0 run) and no notice pending.
- **Next exact action:** after the fence is gone, the next activation runs F0 run 11's Check (item 346) and records it; then `dev-05-s01` (item 393) at the later of 00:00:00 Wed and this F0's close + 1,200 s (LAST_CLOSE_KIND other), with item 418 (e) if the 24 h line is the only failing line.

420. **Laptop lead (interactive, Opus 5.5), 2026-11-17 21:54:08 PST: eleven process questions plus PR #795's release rule to the research lead as one batch (RL-179); F-5 to F-11 take effect Thu 19 Nov 20:00 unless RL-179 objects; nothing on the MBP waits**

```item
{"expires_epoch_s": 1795147200, "issued_epoch_s": 1794981248, "number": 420, "owner": "research_lead", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **Sent to the research lead (Fable 5.2) as one batch:** the eleven questions of `/Volumes/JW-EXT/scratch/mythos-process-audit/CUT.md` section 3, with RULES.md as the evidence. Nothing in the batch asks her to change a registered estimator, an inclusion rule or a date already run.
- **Wait for an answer (they touch what the paper may say):** F-1 the date rules bind only the entries they name, and whether later kits may use a separation in hours instead of a calendar date; F-2 what physical quantity the 300 s and 1,200 s close gaps protect beyond each span's own soak and G0 gate; F-3 hand gates and desk-final move from "before span k+2 arms" to "before a look reads span k", with the automatic Q1 print and L002/L005 read accepted; F-4 F0 retires as the standing filler after R1, and a ranked list of product-bearing fillers the lead may queue.
- **Proceed unless she objects by the deadline:** F-5 the copy is a debt with a deadline, not a gate; F-6 no three-ahead cap, no 24 h item expiry, no seven-day queue expiry, and a named stop holds the kit that raised it; F-7 the qualification batch rule is a predicate on qualification spans and its 2 h 35 min is filled; F-8 each ruling ends with a Register block and a clause without one is commentary; F-9 High Power spans launch at any hour; F-10 a READY session whose arm refuses releases the ladder, and the pre-notice becomes a hint; F-11 smokes only on a runner-pin change ahead of a session over three hours, cold seats only on an unruled leg type.
- **Until RL-179:** every rule in F-1 to F-4 stays in force exactly as ruled. None of them idles the Mac in the meantime, because fillers are not bound by them.
- F-12 (added by the lead): PR #795's interim-look release rule, after Astra's round-10 BLOCK (keyed-residual disclosure through public coefficients). #795 stops building until RL-179 sets the rule.

419. **Laptop lead (interactive, Opus 5.5), 2026-11-17 21:53:28 PST: process audit ADOPTED: rule register (PHYSICS, VALIDITY or SAFETY only, no waivers), queue plus scheduler replace standing items; PR #800, #799, #807 and #811 parked; #804 reduced to copy-only; four builder briefs issued**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794981208, "number": 419, "owner": "lead", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "CLOSED", "supersedes": []}
```

- **Decision (lead, under Ed's standing permission of 2026-11-17).** The structure in `/Volumes/JW-EXT/scratch/mythos-process-audit/STRUCTURE.md` is adopted: a queue file, a rule register, one scheduler function and a short typed log replace standing items and per-span items. Nothing on the MBP changes by this item; the PHYSICS-ONLY SCHEDULING item posted before this one already carries tonight's changes.
- **Rules.** A rule exists only as a row of `docs/process/RULES.json` with class PHYSICS, VALIDITY or SAFETY, the quantity or claim it protects, an owner and a review date. A paragraph with no row is not executed. No waivers: a rule that needs one is retired or changed.
- **Parked, with their branches kept:** PR #800 (queue controller), #799 (desk-final transport), #807 (close-offload and retention) and #811 (their contract). Reason: they implement, as code, rules this audit removes (three-ahead and 24 h expiry, the watcher line, k+2 desk debt, F0 spacing and cap, copy as a gate, automatic retirement). No further review round is spent on them. They are revisited after the paper.
- **Reduced and merged at tier 1:** PR #804 as a copy-only tool (its deleting `close` verb removed). Nothing deletes an original on the arm path; the lead packs old spans by hand at a block boundary when free space nears the floor.
- **Builder briefs issued** (`/Volumes/JW-EXT/scratch/mythos-process-audit/briefs/`): A scheduler, read-only (tier 1); B scripted close (tier 1); C RUN_STATE archive, add-tool limits and the magistrate prompt (tier 0 and 1); D `measurement_mode.zsh` into the repository (tier 1). Brief E, the W1-line change that removes F0's 22:40 window with the #809 evaluator fix, waits for R1's close as RL-171 already schedules.
- **PIPELINE.md edits (tier 0, lead):** tier 2 narrowed to four cases; kits on an admitted pin are tier 0; one accept instead of two; a finding must cite a frozen acceptance scenario or carry a reproduction. Retired by name: paired Sol and Opus builds for every block design (item 220, item 221 rule 6), "two Sol seats for every step", and a research-lead cold review of everything.
- **Retired standing text:** item 346 rules 4, 5, 8 (restart clause) and 10 (mail per run); item 348; item 395 (A); item 396's pre-notice as a hold; the Air-state hand-off items as a practice (the lead's lanes go in TASK_QUEUE.md).
- **To the research lead, one batch:** CUT.md section 3, questions F-1 to F-11. F-1 to F-4 wait for her answer; the rest proceed unless she objects.
- **Ed is told after,** in one plain mail: what was cut, the hours it recovers, and the two things that still need him (none on the measurement path).

418. **Laptop lead (interactive, Opus 5.5), 2026-11-17 21:52:49 PST: PHYSICS-ONLY SCHEDULING (standing; the process audit's ruling): F0 spacing and age expiry removed; nothing waits for a person, the Air or a count; the MBP copies at once, always; product fillers before F0; items 393, 394, 397 and 398 run as issued**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-20T23:59:00-08:00
on_early_or_refused: dev-05-s01 (item 393), dev-05-s02 (item 394) and R1 (items 397, 398) run exactly as issued; this item changes only what runs when none of them can arm. If any point below cannot be applied as written, apply the rest, record which point and why, and mail the lead; never idle the Mac to wait for an answer
next_observable: each pre-launch and Check item names the points of this item it used; the first F0 or F2 launched less than 14,400 s after the previous F0 t0; no gap over 30 min with nothing armed that lacks a physical reason in the record
```

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794981169, "number": 418, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": ["348", "395", "409", "412", "413", "415"]}
```

- **Authority.** Ed, 2026-11-17: the only limits on how much the MBP measures are physical (item 415). The Mythos 5.2 process audit Ed asked for is done (`/Volumes/JW-EXT/scratch/mythos-process-audit/`: RULES.md, CUT.md, STRUCTURE.md, MIGRATION.md) and the lead adopts it. Ruling (lead; scheduling rules only, blind; deviation recorded). Item 415 left item 346's spacing, window and rule 7 "until the process audit rules on them"; this is that ruling.
- **What does not change.** Items 393, 394, 397 and 398 run as issued, every line, except point (e). Blinding. Every pin and hash. Item 346 rule 6 (02:35:00 to 22:40:00 is what the bytes at `b2e01464d` do), rule 7 (a filler never costs a counted span its date), rule 9 (a running span is never aborted). The 300 s and 1,200 s close gaps (with the research lead). Every host-state stop: restore unproven, High Power marker, a live fence, a foreign process, power, disk, meter.
- **(a) F0 spacing is removed.** Item 346 rule 5 is deleted whole: no 14,400 s between F0 t0s and no daily count. Delete the spacing test from the Start-and-check and Run script as item 415 deleted the cap. The t0 ledger stays as a record. Item 346 no longer expires by age (its Sun 22 Nov 11:51 expiry is withdrawn), and a moved W1-line head does not stop F0 at `b2e01464d`: it runs at that commit until the lead names a new pin. F0 is eligible whenever rule 6 and rule 7 hold, the close gap has passed, the host-state lines pass and nothing higher can arm now.
- **(b) Nothing waits for a person after a refusal.** Item 346 rule 4's 20-minute wait for the lead's reply is deleted. After a refused arm of any span or session: record it, mail the lead once, and continue down the ladder at the next close gap. A lead reply that clears the refusal is acted on at the next close. A READY session whose arm refuses is not READY until a new READY record (item 397's clause 6 already says this for R1).
- **(c) The MBP copies at once at every campaign close, permanently.** Item 348's 30-minute wait and item 395 (A)'s choice of copy owner by Air state are withdrawn. Item 409 no longer ends when R1 arms. The Air's state changes nothing on the MBP; the lead pulls copies afterwards. Originals stay in place (items 396, 399).
- **(d) The ladder puts product before diagnostics.** When no counted span or READY session can arm now: an issued F2 piece or hp-02 span first, then F0. The magistrate may fill and issue F2 p02 to p04 and hp-02 from the committed drafts in any gap (item 388 fallback 4), reading any date window in those drafts as "any date" (they are outside every count, RL-175 D.3). An F2 or hp-02 item issued under this point does not expire by age; it is void only if its pin or kit hash changes. If piece 1's hand-read is not on main when p02 is the next eligible filler, the magistrate does it with the template as interim lead (item 388 fallback 6) in that gap; it holds nothing else.
- **(e) Expiry by age, dev-05 only, used only if the chain slips.** The expiry of items 393 and 394 is the end of their date window (Wed 18 Nov 23:59:59 PST), not issue + 24 h. If the 24 h line is the only failing line of a Start and check or Run, record "EXPIRY BY AGE SUSPENDED (this item)" and proceed with every other line as issued. Item 397's clause (4) reads "item 394 goes VOID" on that basis. If the chain runs on time this point is never used.
- **(f) No idle without a physical reason.** If at any close nothing can launch within 30 minutes, write the reason in one line. If the reason is not one of: power, disk, meter, an unclean host, a live foreign process, a refusal by the pinned launcher itself, or a registered date or batch window with no eligible filler that fits, then launch the lowest eligible filler and mail the lead the rule that stood in the way. This generalises item 415's last instruction.
- **(g) Mail.** Counted spans and R1: one mail per close, as now. F0 and F2 closes: no mail per run; one summary a day, unless a judged verdict line changes from the previous run, which is mailed at once.
- **(h) Record.** Each pre-launch and Check item says in one line which of points (a) to (g) it used. Nothing else is added to the per-run record.
- **Lead lanes started by this item:** the ladder is stocked tonight (F2 queue b; F2 p02 to p04; hp-02); eleven questions go to the research lead as one batch (CUT.md section 3); three builder briefs (MIGRATION.md section 4).

417. **Magistrate e0552b22 (headless, Opus 5.5), 2026-11-17 ~21:25 PST (`date`): item 415 APPLIED: F0 three-per-day check deleted from item 346 scripts (cap-free templates in custody); spacing, window and rule 7 kept; no F0 lawful before dev-05-s01**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794978679, "number": 417, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "CLOSED", "supersedes": []}
```

- Item 415 (lead, standing) applied at this activation: the three-per-day F0 check is deleted from item 346's start-and-check and run scripts. Cap-free templates in custody: `f0-startcheck-template-e0552b22.sh` and `f0-run-template-e0552b22.sh` (each = ab1dae5c's script minus the `today = ...` line and the `CAP`/`len(today)` check, replaced by one comment naming item 415; `zsh -n` ok). Item 412's waiver line is gone with it. The t0 ledger stays (spacing reads it).
- Exercised: the cap-free eligibility block run on the real ledger at 21:2x PST printed `WAIT: F0 spacing, 4 h after the last Part C t0 1794971221 (rule 5)`, rc 1, as expected (next spacing-eligible t0 23:07:01, after rule 6's 22:40 window end; so no F0 tonight before `dev-05-s01`).
- The next F0 launcher copies these templates and sets only the header values (MAGISTRATE_PID, TRIGGER_SPAN, COUNTED_LATEST, LAST_CLOSE_KIND and the rest as before); rules 5 (14,400 s spacing), 6 (02:35:00-22:40:00) and 7 stay.
- Other per-day quotas met so far: item 393's day law (RL-172 (a): at most 12 mixed-size and 24 development legs per t0-date). Its stated reason is the t0-date as the design's day unit (a leg's calendar day is its span's t0 date), not pacing alone, so it is kept; it does not bind `dev-05-s01` (only dev-05's 12 legs on Wed 18 Nov). Flagged for the process audit (item 415).
- Item 415 stays ISSUED: its standing clause on other pacing-only quotas still applies to later activations.
- **Next exact action (unchanged from item 416):** `dev-05-s01` (item 393) from Wed 18 Nov 00:00:00 PST; after its close, F0 under item 346 with the cap-free templates when rules 5-7 hold.

416. **Magistrate e0552b22 (headless, Opus 5.5), 2026-11-17 21:08-21:20 PST (`date`): STANDING-F0 run 10 (item 346; pre-launch item 414, item 412 waiver) CHECK: RECEIPT OK, verdict pass, every judged line equal to run 9; restore lines pass; closes 412-414; next: dev-05-s01 (item 393) from Wed 00:00**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794978628, "number": 416, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [{"at_epoch_s": 1794978628, "item": 412, "status": "CLOSED"}, {"at_epoch_s": 1794978628, "item": 413, "status": "CLOSED"}, {"at_epoch_s": 1794978628, "item": 414, "status": "CLOSED"}], "status": "CLOSED", "supersedes": []}
```

- F0 standing notice: run 10, trigger (c) NO_STAGED `after-f2-p01-close-item412-waiver` (item 414), launched under item 412's one-time day-cap waiver. t0 19:07:01 PST (1794971221); receipt 21:05:43 PST (span 7,122 s). The align-r0 label and fence were gone; this activation spawned 21:08:54, after the receipt, so no agent was alive during the run.
- Receipt rc 0; parts `{"C": true}`, `parts_requested` "C", fresh soak; every step rc 0; one `close-volumes`; every feed proven stopped and hash-checked: RECEIPT OK. Soak rc 0, sha256 `c7a8f3207ac4084624954bd17c13f0cf969ec5810fb967f07ccbc28d5cc9a0dd` (the receipt's soak result carries no band keys; as runs 8-9). Part-C rc 0.
- smoke_part_c.json (evaluation only): verdict `pass`; disposition as printed ("Mechanics and start state hold. The no-hold TV1h design is adopted ..."). Lines, with run 9 (item 405) beside: `d_bank_mechanics` pass (run 9 pass), `d_bank_start_state` pass (pass), `step_d` pass (pass; g0_wait 200.69 s, slope -0.188 C/min), `x_g` pass (pass; X_G ran, no G1 timeout, no x7). `admitted_turns` not judged: "not_applicable: episode returned at turn 1" (own stop). gate_time 198.14 s of limit 393.93 s; no_g1_timeout pass (no turns); h_records match. Log: "three-turn clause not evaluated: one D run". N_chunk 4096; T_dead 984.829 s. No line differs from run 9, so nothing goes to the research lead under rule 10.
- printed_not_judged (print only): turn-1 last-512 clock ratio 0.933, 0.003 above the predicted band 0.83-0.93 (run 9 0.922, run 8 0.912); first off-nominal pm Moderate at token 1,678 (run 9 1,700); token-rate ratio 0.977 (run 9 0.978); tv1h_trigger does not fire (3 unequal rows outside gate windows of 1,145). Desk verdict member excluded on `thermal.powermetrics_non_nominal` (turn 1), as before. Nothing reads these.
- Maintenance (log show rc 0, 30,144 lines, 19:06:58-21:05:43): dasd steady (950-2,730 per 10 min); `mobileassetd` 125/220/178/70 lines in 19:50-20:30; `softwareupdated` 8 at 19:10 and 8 at 20:10; `backupd` 6-27 per 10 min; no XProtect lines. X_G still passes.
- Close interval: latest close before t0 was F2 p01 (18:34:14, kind other, GAP 1,200 s). Previous F0 t0 14:29:10 (run 9); this t0 19:07:01; 00:00 not inside the span.
- Restore lines all pass: no desk fence; no align-r0 label; plist ProcessType Interactive; powermode 0; Network Time Off; ntp_adjtime freq word 0; no High Power marker; no stray monitor or root powermetrics; AC connected, not charging, 0 mA.
- Copy: an F0 close is non-campaign; this Check covers the copy (item 409: the MBP owns copies tonight; F0 OUT stays in place, nothing offloaded). Commit nothing from `$OUT`.
- Closes 412 (waiver used once), 413 (its pointer) and 414 (pre-launch record). Script and output: custody `standing-f0/check-e0552b22/` (`check.sh`, `out.txt`).
- Activation e0552b22: no pending notices; no unread mail from Ed; open directives unchanged (the standing seven); no standdown request.
- **Next exact action:** `dev-05-s01` (item 393) arms from Wed 18 Nov 00:00:00 PST under item 393 as issued, with this F0 as the latest close (kind other, 21:05:43, GAP 1,200 s, met from 21:25:43). Nothing else is lawful before then: F0's waiver was one-time, and rule 5's spacing from 19:07:01 runs past rule 6's 22:40 window end.

415. **Laptop lead (interactive, Opus 5.5), 2026-11-17 21:10 PST: F0 per-day cap REVOKED (standing): only physical limits bound measurement; process audit dispatched**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-18T23:59:00-08:00
on_early_or_refused: apply the revocation at your next activation: delete the three-per-day check from item 346's script; F0 eligibility is spacing (rule 5), window (rule 6) and rule 7 only; record it in your next item
next_observable: the magistrate's next item recording the cap removed, and any F0 launched after dev-05-s01's close without a day cap
```

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794978620, "number": 415, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **Directive (Ed, 2026-11-17 ~21:20): the only limits on how much measurement the MBP does are physical ones** (the model does not fit, the host runs too hot to measure, a run would contend with a counted span). Calendar quotas on science are not allowed.
- **Ruling (lead; scheduling rule, blind; deviation recorded):** item 346 rule 5's clause "and at most three F0 t0s in one local calendar day" is **REVOKED, standing, from now**. Item 412's one-time waiver is superseded. Rule 5's 14,400 s spacing, rule 6's window and rule 7 (counted spans' arms are protected) stay in force until the process audit below rules on them.
- **Script:** the check `if len(today) >= 3: sys.exit("STOP: three F0 t0s already today (rule 5)")` (item 346's start-and-check script) is deleted, not raised to a bigger number. The ledger of t0s stays (spacing reads it).
- **Any other per-day, per-calendar or count quota** on measurement that the magistrate meets in an item: treat it as suspended if its only stated reason is pacing, record that you did, and keep every rule that names a physical or measurement-validity reason.
- **Process audit:** a Mythos 5.2 xhigh seat is auditing every meta rule and process now, with Ed's standing permission to restructure. Its result will arrive as a later item.

414. **Magistrate ab1dae5c (headless, Opus 5.5), 2026-11-17 ~19:10 PST (`date`): STANDING-F0 (item 346) IS LAUNCHING its tenth run under item 412's one-time day-cap waiver, on `b2e01464d`; trigger (c) NO_STAGED after F2 p01's close; every Start-and-check line passed; dev-05-s01's 00:00 arm protected (worst case + close ends ~22:53)**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794971186, "number": 414, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- Item 412's one-time waiver of rule 5's three-per-day cap, used once: the fourth F0 t0 of Tue 17 Nov. Rule 5's 14,400 s spacing (run 9 t0 14:29:10), rule 6's window (to 22:40) and rule 7 (`dev-05-s01`'s 00:00 arm: COUNTED_LATEST 1794988800, latest launch 20:17:00) all held.
- Trigger (c) NO_STAGED after F2 p01's close (18:34:13, item 411). SESSION_READY no (R1 effective only from `dev-05-s02`'s launch record). No refusal outstanding. Activation: no pending notices, no unread mail from Ed, directives unchanged, no standdown request; canonical fast-forwarded to `11874d2a8` with nothing loaded.
- Start-and-check 19:05:23-19:05:28 PST, every line passed (head `b2e01464d` by ls-remote; 17 hashes; RL-89 MAC CHECK OK; Network Time Off; powermode 0; frequency word 0; AC not charging; 288 GB free; only this magistrate and its MCP children). `F0 ELIGIBLE at 1794971126; host last close 1794969254 (other, gap 1200 s)`.
- Script changes from run 9's: header values, COUNTED_LATEST, and the day cap 4 on 2026-11-17 only. Record: `docs/process_traces/2026-11-15-standing-f0/MAGISTRATE-LAUNCH-ab1dae5c.md`; launch output in custody `r1-partc-f0-out-ab1dae5c.txt`.
- Expected end ~21:10; worst case ~22:33; fence ~23:10. No email: F0 is a diagnostic launched under a standing item, and Ed hears at the Check.
- **Next exact action:** the first activation after the fence runs item 346's Check of run 10, reports it (G1 and F0-series rows, item 396), closes items 412-413, then `dev-05-s01` (item 393) from Wed 00:00:00 with this F0 as the latest close (other, 1,200 s).

413. **Laptop lead (interactive, Opus 5.5), 2026-11-17 18:58:25 PST (`date`): MAGISTRATE pointer for item 412 (F0 run 10 tonight, if rules 5-7 hold)**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-17T22:40:00-08:00
on_early_or_refused: launch STANDING-F0 run 10 under item 346 with item 412's one-time cap waiver only if rules 5 (spacing), 6 (window to 22:40) and 7 (dev-05-s01's 00:00 arm protected) hold and every Start-and-check line passes; otherwise NOTHING launches, record why, and dev-05-s01 arms at 00:00 under item 393 as issued
next_observable: the STANDING-F0 run 10 pre-launch record (or the no-launch record), then its Check after the fence is gone; dev-05-s01's pre-launch record at 00:00
```

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794970705, "number": 413, "owner": "lead", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- Pointer for item 412's waiver, so that the next magistrate activation picks it up. The terms are item 412's; nothing else changes. After this pointer, `dev-05-s01` (item 393) arms at 00:00 as issued.

412. **Laptop lead (interactive, Opus 5.5), 2026-11-17 18:57:59 PST (`date`): ONE-TIME WAIVER of item 346 rule 5's three-F0-per-day cap so STANDING-F0 run 10 fills tonight's idle gap before dev-05-s01 (spacing, window and rule 7 unchanged)**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794970679, "number": 412, "owner": "lead", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **Why:** Ed (18:55) asked why the MBP waits more than 5 h. After F2 p01's close (item 411) nothing is lawful until `dev-05-s01`'s Wed 00:00 arm:
  - F0 has used its three t0s for Tue (06:23, 10:24 and 14:29);
  - F2 p2 lacks piece 1's hand-read and queue b;
  - hp-02 is not issued.
- **Ruling (lead; scheduling rule, blind; deviation recorded):** item 346 rule 5's "at most three F0 t0s in one local calendar day" is waived ONCE, for one more F0 t0 today (Tue 17 Nov).
  - Everything else in item 346 holds: rule 5's 14,400 s spacing from the last F0 t0 (14:29:10, so 18:29:10 or later; met); rule 6's launch window, to 22:40; rule 7's protection of `dev-05-s01`'s 00:00 arm, with this F0's worst case plus its 1,200 s close before 00:00, else no launch; every Start-and-check line; the Check; and the copy.
  - The ladder is unchanged: if anything higher becomes armable, it goes first.
- **Science:** F0 is a diagnostic. A fourth run adds an evening point to the F0 series table (item 396) and judges the same lines. Nothing counted or registered reads it.
- **MAGISTRATE:** on your next activation, launch STANDING-F0 run 10 under item 346 with this waiver, if rules 5-7 hold. If not, record why and do nothing.
- **Lead follow-up:** RL-178 is to ask the research lead to make idle-gap filling standing (cap removed, spacing kept), so the lead does not have to waive each gap.

411. **Magistrate 053aa5c3 (headless, Opus 5.5), 2026-11-17 18:38-18:55 PST (`date`): F2 p01 (item 406) CHECK PASS: 3/3 legs complete, every restore/stop step rc 0, meter clean; encrypted cloud copy verified and marker written at once (item 409); item 410 first-token count = 0 missing on every held Turn record; next: dev-05-s01 (item 393) from Wed 00:00**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794970561, "number": 411, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [{"at_epoch_s": 1794970561, "item": 406, "status": "CLOSED"}], "status": "CLOSED", "supersedes": []}
```

- **Activation 053aa5c3** spawned 18:38:42 PST, after F2 p01's span had closed (receipt ended.epoch_s 1794969253.13 = 18:34:13; launcher fence pid 26577 gone; no `com.joulewise.align-r0` label loaded; no night label or plist). No pending notices, no unread mail from Ed, directive list unchanged (standing 587/422/421/417/416/408/405), no standdown request. Canonical fast-forwarded `7ec56d2b2` → `2d82e24d2` (items 408-410) with no night label loaded and none on disk.
- **Check (item 406's block, verbatim asserts; script and output in custody `f2p01-check-053aa5c3/check.sh`, `out.txt`, 18:40:06-18:40:08 PST): RECEIPT OK.**
  - Receipt: rc 0, error none, legs 3/3 finished, span_result `MEASURED_OK` / `COMPLETE` / "3/3 legs run", fault false, batch window `02:00-02:35`, kit sha and frozen commit `2d347f721` asserted, mock false.
  - Steps (25), all rc 0: deadline, frozen, night_agents, ac_power, condition13, start-agents/meter/volumes, read_power, display, dwell, plan, soak, L001.a1, L002.a1, L003.a1 (with before-volume censuses), **restore 0**, stop-volumes 0, stop-meter 0, stop-agents 0, close-volumes 0.
  - Feed stops: agents, meter, volumes all `proven_stopped` true; meter supervisor starts 1, restarts 0, gaps 0, errors 0, group census empty and reaped. Meter operational: present, 31,196 polls, 0 bad polls, 0 USB errors, elapsed 6,239 s.
  - Legs (leg_record / leg_summary only): L001 complete, G0 released (wait 201 s), one quiet span 600 s, decode 512 (cap reached), prefill 19,458, wall 1,568 s vs budget 1,553 s (1.010x; under the 1.5x overtime bar), 0 contaminated redos. L002 complete, G0 released (94 s), quiet 600 s, decode 512 (cap), **realized prefill 284** (kit 256), wall 1,252 s vs 1,361 s. L003 complete, G0 released (142 s), quiet 600 s, decode 512 (cap), prefill 2,024 (kit 2,000), wall 1,314 s vs 1,378 s. All walls under 2,700 s. No named stop (no REFUSAL, INSTRUMENT_FAULT, CONTAMINATED_REDOS, LEG_OVERTIME).
  - Host readback: measurement_mode verify's only FAIL is this magistrate's own MCP children (33748/33749/33752); network time Off; powermode 0; frequency word 0 (ntp_adjtime status 0x2081); AC, not charging; 268 GiB free; no desk fence, High Power marker, runner/monitor group, root powermetrics or night.lock holder. Two standing WARNs (charge limit syntax; softwareupdate schedule non-persistent, item 201).
  - Maintenance print (16:49:54-18:34:13, 48,080 lines; full log `OUT/maintenance-log.txt`): dasd ~1,400-1,800 per 10 min throughout; cloudd peaks 1,812 (17:30) and 1,001 (17:00); softwareupdated 2,570 and mobileassetd 2,195 in the 17:00 bucket (L001 window); XProtectPluginService 843 at 17:00; backupd ≤30 per bucket; bird ≤9. A print only.
- **Copy (item 409: MBP copy owner at once; item 347 offload):** encrypted cloud offload of the span, 124 files, round-trip decrypt lists 169 tar entries; enc sha256 `50ac16f7…4687a`, manifest sha256 `e48abce7…30a85`; iCloud Drive `JouleWise-offload/cq-f2-inst-p1-a1`; brctl 18:41:19 no needs-upload, idle, caught-up, last-sync 18:40:55 after the 18:40:38 copy. Marker `/Users/Shared/JouleWise/desk-copy/cq-f2-inst-p1-a1.ok` written 18:41:19. Originals retained (items 396/399). Scripts `offload-f2p01-053aa5c3.sh`, `offload-f2p01-run-053aa5c3.sh`; output `offload-f2p01-out-053aa5c3.txt`.
- **Close for the ladder:** latest close = F2 p01 at 1794969253.13 (kind other, 1,200 s): next arm earliest 18:54:14 PST. Item 406 → CLOSED. Piece 1's hand-read (L002's short realized prefill 284 vs 256, and L001's 1.01x wall, to be judged there) and queue b are the lead's; this item crosses neither.
- **Item 410 (RL-177 §H item 4), structure-only first-token coverage count.** Files key-scanned by name first; only `outputs/align_episode.json` (`joulewise.align.records.Turn` lists) loaded; printed counts only. Every episode file on the MBP outside `~/Library`: 114 files, 390 turns, 390 with `decode_tokens >= 1`, **0 with `decode_tokens >= 1` and no `first_token_ns`** (0 missing in any turn).

  | kind | runs | files | turns | decode ≥1 | decode ≥1 and no first_token_ns |
  |---|---|---|---|---|---|
  | Part C rehearsals (smoke 11-14, w1line, c3f4, F0 runs 1-9) | 12 | 48 | 324 | 324 | 0 |
  | campaign legs (dev-01..dev-04, hp-01, F2 p01; incl. 3 rejected attempts) | 13 spans | 66 | 66 | 66 | 0 |

  Per-run table in custody `f2p01-check-053aa5c3/rl177-ftcount.txt`. Search: `find /Users/edr -xdev` pruning `~/Library`, `.git`, `node_modules`, for `align_episode.json*` and `align_turns.jsonl*` (248 files, none compressed). The 134 `outputs/align_turns.jsonl` files are a different runtime row (keys `turn` = index, `generation`, `start_stamp`, `end_stamp`, `clock_mapping`, `flags`) with no `first_token_ns` field in their schema, so they are not `Turn` records and are not counted; 114 of them are twins of the episode files above. The other 20 (52 rows) are the R1 follow-up rehearsals of 11-12/11-13 in `/Users/edr/code/jw-wt/lead-handoff-1113/r1fu-1113-desk/` (`in/` 4 files, `in2/1112` 8, `in2/1113` 8), held on the MBP only in that row form, with no `align_episode.json`: **not covered** by this count. Also not covered: the align pilot-v0..v6 trees (offloaded 11-04 to the iCloud archive `JouleWise-archive/2026-11-04-align-pilots/*.tar.zst`; only `.OFFLOADED.json` stubs remain locally; not extracted). Missing count is zero, so no mail to the lead.
- **Next exact action:** dev-05-s01 (item 393), first legal t0 Wed 18 Nov 00:00:00 PST, band outside 10:50:00-13:15:00, item expiry Wed 12:32:46 PST; stage a fresh detached worktree on `2d347f721` and run item 393's Start and check with this F2 close as the latest close (NONCAMPAIGN copy = this item). F0 is daily-capped for Tue; nothing else can arm before 00:00.

410. **Laptop lead (interactive, Opus 5.5), 2026-11-17 18:32:03 PST (`date`): RL-177 committed (S on decode-only rows; Q from turn 0's first token; cells R1-R5 gate the S amendment); magistrate structure-only first-token coverage count in a gap**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794969123, "number": 410, "owner": "lead", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **RL-177** (Fable 5.2, audit `aeadb9122`, committed verbatim). The counted prompt offset (bank +1,219, spam +768 tokens) makes S's prefill rows unsound:
  - S is now scored on decode-only rows; the prefill rows print as `S_pf`, with no word;
  - Q's outcome starts at turn 0's first stamped token; `Q_total` prints;
  - five synthetic cells (R1-R5) must clear fixed bars before the S amendment merges, which is before W1 signs.
  
  **Nothing in the chain changes and it costs zero MBP minutes:** dev-05, R1, freeze 2 and qualification read no S score and no prompt.
- **MAGISTRATE, in a gap with nothing armed (RL-177 §H item 4, a structure-only count):** on the v4 rehearsal and pilot turn records you hold, count the turns with `decode_tokens >= 1` and no `first_token_ns` (absent or null). These are the `joulewise.align.records.Turn` records, as a W1 episode run writes them.
  - Load only those record files.
  - Print counts only: files, turns, turns with decode tokens, turns missing `first_token_ns`, each by run.
  - Print no timestamp values, energies or texts. Key-scan file names first.
  - Post the table as an item. If the missing count is not zero, mail the lead: it goes to the research lead before the amendment merges.
- **Lead lanes:** Astra on the R1-R5 cells; the Sol #813 builder gets RL-177's code changes when its current run ends.

409. **Laptop lead (interactive, Opus 5.5), 2026-11-17 18:22:50 PST (`date`): COPY OWNER TONIGHT = MBP AT ONCE (no 30-minute wait at the F2 p01, dev-05-s01 and dev-05-s02 closes); the Air pulls afterwards**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794968570, "number": 409, "owner": "lead", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "CLOSED", "supersedes": []}
```

- **Rule (amends item 408's first line and item 395 (A) for these closes):** from now until R1 arms, the MBP is the copy owner AT ONCE at every close: F2 p01, `dev-05-s01` and `dev-05-s02`. It runs item 347's cloud offload and writes the marker right after the Check, with no 30-minute wait for the Air. The Air is online, but waiting costs MBP time between `dev-05-s01`'s close and `dev-05-s02`'s arm, and before R1 (GPT 6.2 Astra window-schedule audit, throughput idea 2). Ed (11-17 18:15): "accelerate work however you can".
- **The Air's part:** after each marker exists, the lead pulls the verified copy to the SSD (iCloud, or LAN while the Macs share Wi-Fi). It never holds an arm. This changes nothing about raw retention (items 396/399: originals stay in place until "interim look complete").
- **After R1 arms,** item 395 (A) applies as written, by the latest Air-state record.

408. ****Laptop lead (interactive, Opus 5.5), 2026-11-17 18:20:56 PST (`date`): AIR RESUMED (Ed, ~18:15: SSD plugged back in, same Wi-Fi as the MBP for about a day; accelerate)****

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794968456, "number": 408, "owner": "lead", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "CLOSED", "supersedes": []}
```

- Item 395 (A) is now in the "Air resumed" state: item 348 stands (the lead copies at close; the MBP falls back at close + 30 min). The Air's three agents run again. The Air and the MBP are on the same Wi-Fi for about a day, which makes LAN copies fast. Any lead SSH still waits for the armed span's Check item (no SSH while armed).
- **The lead takes back item 402's items 3-6, as updated by item 404.** The MBP keeps items 1-2 (the chain; dev-05 desks and Q1 records in gaps).
- **The interim lead's work since item 404 is adopted:** #810 merged and typed items initialized (cutover 405); F0 runs 1-9 re-read clean for both #809 holes (item 405); F2 p01 issued and launched (items 406-407).
- **Lead lanes now:**
  - Fable on the RL-176 prefill cell (0.455 false-signature rate versus .035);
  - Sol 6.2 on #795, #813 and the cluster merge order (#804 onto the #811 contract);
  - Astra 6.2 adversarial audits of #809's hole fix, #811 and #812.

407. **Magistrate b7aad16d (headless, Opus 5.5), 2026-11-17 ~16:50 PST (`date`): ITEM-f2-p01 (item 406) IS LAUNCHING: span `f2-inst-p1`, legs L001-L003, kit `f2-inst-01.v1.1`, on `2d347f721` in the fresh worktree `/Users/edr/code/jw-wt/cadence-f2-inst-p1`, batch window `02:00-02:35`. Every Start-and-check line passed 16:48:58. Expected end ~18:55, worst case ~19:58, fence ~20:22. Launch is this activation's last action.**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794962964, "number": 407, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [{"at_epoch_s": 1794962964, "item": 406, "status": "ARMED"}], "status": "CLOSED", "supersedes": []}
```

- Scripts (custody `f2p01-b7aad16d/`): `inputs.sh` (every value with its evidence), `startcheck.sh` and `launch.sh` = item 406's Start-and-check and Run blocks verbatim with the inputs sourced first. Outputs `startcheck-out.txt`, `launch-out.txt` (t0, OUT, DEADLINE, launcher JSON, LAUNCH_RC).
- **Start-and-check PASSED 16:48:56-16:48:58 PST:** expiry, watch, admission, pred_gate `dev-03-s02` CLEAN (close_epoch 1794856579), copy (NONCAMPAIGN, F0 run 9 Check), CLOSE OK (latest 1794961678, other, 1,200 s), F2 TRIGGER (F0 daily_cap; no higher rung), window `02:00-02:35` (13:15:00-22:18:10 default band); Network Time Off; powermode 0; measurement_mode's one FAIL = this magistrate's own MCP children (NOTE 1); validate-kit ok (f2-inst-01, frozen_paths_verified, 12 legs); plan: batch_windows ["02:00-02:35"], expected 7,442 s, worst case 11,250 s, blackout_clear true; next OS batch Wed 02:08:39 PST (print only); OUT `/Users/edr/campaign-out/f2-inst-01/cq-f2-inst-p1-a1-<t0 UTC>` (the Run block re-runs every gate and recomputes OUT).
- Trial at 16:40:15: expiry, watch, admission, pred (`dev-03-s02` CLEAN, close_epoch 1794856579), copy (NONCAMPAIGN route, F0 run 9's Check) passed; close gate WAIT (1,200 s after 16:28:41). The full Start-and-check result is in `startcheck-out.txt`; launch follows it in the same minute.
- Expected end ~t0 + 2 h 4 min; worst case t0 + 3 h 8 min; fence t0 + 12,710 s. NEXT_COUNTED_EPOCH Wed 00:00:00 (dev-05-s01) stays protected (13,010 s horizon).
- Agent processes at launch: only this magistrate and its MCP children (NOTE 1). The #809 fix runs as a Codex Cloud task (thread `6afcf344-7d28-8191-bc0f-7aea3ac98017`, `gpt-6.1-sol` xhigh, read back): this MBP's permission classifier refused a model-override copy of `codex-cloud-run.mjs` for `gpt-6.2-sol`, so the stock launcher (6.1) ran; it COMPLETED at 16:48 (report `cloud-809-b7aad16d/out/report.md`): pushed `7cb6eb95a` (merge of origin/main) and `441bccdd9` (hole 1: timeout detection honours both sources for D_bank and X_G; regression fails on `bc4671106`, passes after; `tests.test_part_c_gate_evidence` + `tests.test_gen_current` 61 OK). **Hole 2 BLOCKED at WRITE_SCOPE:** the runner discards run status when evidence reading fails; the fix needs `scripts/align_r1_followup_kit.py` (not in the brief's scope). Next activation: grant that file in a new task (same brief, scope + that path), then review and one Astra re-review.
- **Next exact actions (first activation after the fence):**
  1. Item 406's Check of `f2-inst-p1` (its Check blocks verbatim, OUT from `launch-out.txt`); F2 is a non-campaign close, so the Check covers the copy (item 395 A, "Air paused"). Then piece 1's hand-read (lead-owned; item 388 fallback 6 if the Air is still paused).
  2. #809: new cloud task for hole 2 with `scripts/align_r1_followup_kit.py` granted; review the pushed diff, run the touched modules, one Astra re-review (item 404 b), merge if no VERIFIED HIGH; STANDING-F0 renewal (before Sun 22 Nov 11:51) uses the fixed pin (item 404 c).
  3. Item 402 §3 freeze-2 packet (due Thu 08:00): F0 series table now runs 1-9 (item 405 has the 404 (a) table). #795 (`align/2026-11-14-fit-interim`, head `d3fb89dfd`, newer than item 402's `0b93be9f7`) continues as Codex Cloud thread `6afcf427-6b2c-8191-9048-660a72677012` (gpt-6.1-sol xhigh, read back; brief `cloud-795-b7aad16d/BRIEF.md`; re-attach `--out cloud-795-b7aad16d/out`). The RL-176 builder continuation is not launched yet.
  4. `dev-05-s01` from Wed 00:00:00 under item 393 (close interval 1,200 s after this F2 close).
- No mail from Ed (16:29); no new directive; notice queue empty.

406. **Magistrate b7aad16d (headless, Opus 5.5) as interim lead, drafted by Sol 6.1 (audit branch `27cc1338b`), ISSUED 2026-11-17 16:38:58 PST (epoch 1794962338; `date`) under item 395 (B) and item 388 fallback 4: MAGISTRATE: arm F2 instrument-characterization piece 1 only, span `f2-inst-p1`, kit `f2-inst-01.v1.1` (sha256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), runner `cadence-legs-v1.1`, detached pin `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster L001,L002,L003; fresh soak, then three legs; expected 7,442 s, worst case 11,250 s. Instrument legs, outside every campaign count and look. Predecessor `dev-03-s02` must have a clean close receipt or this item is VOID. EARLIEST Tue 17 Nov 00:00:00 PST; LIMIT Tue 17 Nov 23:59:59 PST; protected next-arm 20:22:02 keeps `dev-05-s01` (Wed 00:00) first. F2 is a filler: it cedes to all armable counted work and a READY v4 session. Launch is the last action; exit immediately. Nothing else is authorized.**

```pointer
owner: magistrate
wait: none
deadline: 2026-11-17T23:59:59-08:00
on_early_or_refused: WAIT if predecessor has not closed or a higher rung can arm; VOID if predecessor is not clean, the date window is missed, or 24 h has elapsed since issue. No retry after a launcher/runner refusal; report to the lead. Never skip a predecessor, reuse OUT, re-run a leg, or queue another piece on this item's authority
next_observable: after the fence is gone, Check below reports operational receipt/leg records, feeds, restore and copy; piece 1's hand-read is lead-owned
```

```item
{"expires_epoch_s": 1794988799, "issued_epoch_s": 1794962338, "number": 406, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "ISSUED", "supersedes": []}
```

- **Issue record (magistrate b7aad16d as interim lead).** Filled and issued under item 395 (B) and item 388 fallback 4 from the draft `ITEM-f2-p01.md` at `origin/audit/2026-11-10-fable` `27cc1338b` (byte-equal to the draft below apart from the two fills). Lead prerequisites per item 395 (B): the recorded F2 re-check (`evidence/fix-2026-11-16/bash/kit-recheck.json`, `9ef385b9f`) and dev-03's class A/L002 hand-gate release (item 365), both adopted by the lead. Staging: `stage_mbp_span.sh f2-inst-p1` (from the audit branch; repo arg a linked worktree, so no git operation in the canonical root) at 16:33:53 PST: worktree `/Users/edr/code/jw-wt/cadence-f2-inst-p1` detached clean at `2d347f721`; kit sha256 `651d1815…6f2b`, queue a sha256 `ca61c3bc…2892` from `1f683fc63`. Dry tests in that worktree: eight modules, 201 tests OK. Line 7: AIR FALLBACK (item 388) fallback 3 (WATCH_UNTIL below). Line 9: F2 neither adds nor pays; dev-04-s01/s02 desks FINAL (item 387). Copy key: second copy in the Air custody root, sha256 prefix `6c294d1b` equal (item 353; re-read today on the MBP).



- **Admission and authority (RL-169; RL-169a).** Data only; frozen pin and all 38 path hashes unchanged. The committed queue a at `1f683fc6` contains this piece only. Require the independent executing re-check, dev-03's first span closed on this same pin with all restore lines passed, line 2 carried from the dev-03 item by frozen-path equality (RL-165 §5), every applicable checklist line, watcher line 7 and campaign line-9 debt. F2 neither adds to nor pays down line 9. Record the evidence for each `*_OK` value below; a yes without its evidence is not authority. STATUS.md lists unfilled prerequisites. Nothing is issued across a class A, L002 or L005 hand gate (RL-173 D.4).
- **Issued ahead (RL-173 D).** Own predecessor `dev-03-s02`, own date and own `pick_arg`; expires 24 h after ISSUED_EPOCH, checked twice. At most three counted spans ahead plus standing F0. No F2 item grants standing authority or authority to issue another item. Pieces 2–4 are not issuable before the piece-1 hand gate and queue-b commit.
- **Exact ladder.** READY v4 session takes the next clean close from the lead's READY record (RL-172 (f); no reservation at a merely intended session t0). Preserve the applicable counted development order: dev-03 pilot/remainder and dev-04/dev-05 dated spans are never displaced. RL-174 B's current ladder is READY v4, counted work (including qualification), F0, F2 (inst-01, -02, -03), hp-02, then DESIGN_QUEUE_LOW. The historical hp-01/P work must also be closed or unavailable; no pending higher rung is displaced. F2 is eligible only when no counted item can arm within its worst case and ensuing close, hp-01 and P cannot arm, and F0 is ineligible under its own spacing, daily-cap or launch-window rule. `priority_gate` encodes that trigger and blocks unknown state, unresolved refusal, open F2 stop, or pending host-event disposition. Re-read all current issued/staged counted items and READY counted work awaiting staging twice; set NEXT_COUNTED_EPOCH to the earliest legal arm including the next day's spans. Do not omit a known item merely because staging is pending. Unknown gate readiness stops the arm. An explicit 0 requires a recorded complete empty census. This conservative check protects 13,010 s: 11,250 work + 560 launcher/runner reserve + 1,200 close; it also clears the 12,710 s fence. A new READY record before launch cedes immediately. Nothing aborts an already running span.
- **Day law.** F2 may run on any date, including a qualification date; it is outside development/day/cap counts (RL-172 (a); RL-174 B). This item's date is a bounded scheduling choice, not a new development date; a missed window needs a newly dated item from the lead. No shortening/re-cutting of the admitted four-piece layout is needed for the forecast gaps.
- **Bands verified at the pin:** 00:00:00–02:34:59 alternate `13:14-13:15`; 02:35:00–10:50:00 default `02:00-02:35`; 10:50:01–13:14:59 no launch; 13:15:00–22:18:10 default; 22:18:11–23:59:59 alternate. RL-171 retires RL-169a's 22:13:10/02:40 clock rules. The pin admits exactly 10:50:00; both arguments refuse one second later. `evidence/fix-2026-11-16/verify-f2-p01.txt` checks endpoints and adjacent seconds, including the alternate's 09:32:10/09:32:11 limit. All validate-kit, plan and launch commands name the same argument and explicit roster.
- **Close and copy.** 300 s after a campaign span close; **1,200 s after F2, F0 or any other close**, from the actual close with fence gone (RL-171 §6.1; RL-172 (d)). The latest close census reads only each receipt's recorded ended.epoch_s, selects its identity before rounding fractional epochs up, and stops on missing roots, unreadable/missing/invalid close stamps, equal latest epochs or no receipt. File mtime never selects a marker. Latest-close restore and process-group absence are proven. After a campaign close require that exact span's verified encrypted cloud offload `.ok` or Air `.air.ok` marker; after F0/F2/Part C/session/W1 the non-campaign Check covers the copy, with NONCAMPAIGN_COPY_OK=yes, NONCAMPAIGN_COPY_CLOSE_EPOCH equal to EFF_EPOCH, NONCAMPAIGN_COPY_RECEIPT equal to EFF_PATH and NONCAMPAIGN_COPY_RECORD pointing to the actual Check and verified copy. No F0 marker is manufactured; a failed/unverified offload holds every next arm, F0 included (RL-173 A). The writer guarantees plaintext manifest hash, ciphertext hash/size and provider confirmation, upload finished before soak; the key is safe off the MBP and originals retained. This item never manufactures a marker. For an out-of-census session supply OTHER_CLOSE_EPOCH and the same Check/copy proof with NONCAMPAIGN_COPY_RECEIPT=OTHER. A mere `.ok` existence is trusted only because the authorized writer writes it after verification, as in the dev-03 pilot.
- **Quiet and host event.** Quiet is agent/process census and rule 5, not the retired night clock. No MBP agent, SSH, analysis, build or test during a span. Same measurement_mode, Automatic, network time OFF, frequency word 0, no night/smoke job, monitor, High Power marker, lock holder or desk fence. RL-172 (h), amended by RL-173 and RL-174 C: the host runs as it is; no completed restart/service-stop is required. A pending/unresolved event still holds the arm; no password/physical step by an agent; service-stop readback or restart disposition is lead-owned, last point before freeze 2. Each arm prints boot + 12 h + 48 s batch time, a print only.
- **Blinding.** F2 measures only its own instrument streams. Neither this magistrate item nor its tests read campaign/v4 energy, power, meter samples, powermetrics, transcripts, slots or custody. F2's own energy is sealed until freeze 2; only the single analyst using frozen `lm-inst-01` may read it once. The operational Check reads only receipts, leg records and leg-summary projections. Recovery beyond the rails' 1 s tail is censored per RL-169a; no F2 number enters a fit, coefficient, threshold or score.
- **Stops.** Any F2 REFUSAL, INSTRUMENT_FAULT, CONTAMINATED_REDOS (three loaded legs) or LEG_OVERTIME (two above 1.5× budget) stops its queue; an open cadence-stop holds every queue. A G0 timeout alone, or one/two loaded legs, is recorded. No running span is aborted. Only the lead disposes a stop under RL-169a §4, with a new queue for unrun pieces; no member-bearing leg is repeated and unbundled legs of a stopped piece are dropped. Second stops go to the research lead. Restore unproven holds everything. A failed piece-1 hand-read leaves queue b uncommitted.

**Start and check** (on the MBP only after issue, by the magistrate; the builder never executes these blocks).

The lead stages `stage_mbp_span.sh f2-inst-p1` in a clean close interval and supplies the arm-record observations used below. Stage and reuse one detached v1.1 worktree only; never stage the v1.1a variant. `QUEUE_FILE` is the staged queue path and `QUEUE_SHA` its committed hash. For piece 1 use queue-a's committed bytes; for later pieces use the lead's post-hand-read queue b. The watcher placeholders below are exactly the dev-03 pilot's. This item uses the hand-stamped watcher observation of RL-173 C.5, re-read at every arm; an API watcher would instead require C.4's completed run newer than the previous close.

```sh
set -eu
set -o pipefail
cd /Users/edr/code/jw-wt/cadence-f2-inst-p1
PIN=2d347f721552fe03bdd19f113e7bad7a7c24908e
test "$(git rev-parse HEAD)" = "$PIN" && test -z "$(git status --porcelain)" || exit 1
git symbolic-ref -q HEAD >/dev/null && exit 1
REPO="$PWD"
: "${PY:?existing pinned measurement-venv interpreter}"
: "${MAGISTRATE_PID:?this magistrate own process PID}"
KIT=/Users/edr/campaign-out/kits/f2-inst-01.v1.1-1f683fc63.json
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = 651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b || exit 1
QUEUE_FILE=/Users/edr/campaign-out/queues/f2-inst-01.v1.1.queue-a.json
QUEUE_SHA=ca61c3bc09d8a594a60ec058b86d378012a165b44334f4309b4cd7546e842892
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
PIECE=1; SPAN=f2-inst-p1; LEGS=L001,L002,L003; PRED_CAMP=cl-dev-03; PRED_SPAN=dev-03-s02; PRED_KIT_SHA=0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b; PRED_ROSTER=L004,L005,L006,L007,L008,L009,L010,L011,L012
pick_arg() {
  n=$1
  if [ "$n" -ge 1794902400 ] && [ "$n" -le 1794911699 ]; then echo 13:14-13:15
  elif [ "$n" -ge 1794911700 ] && [ "$n" -le 1794941400 ]; then echo 02:00-02:35
  elif [ "$n" -ge 1794950100 ] && [ "$n" -le 1794982690 ]; then echo 02:00-02:35
  elif [ "$n" -ge 1794982691 ] && [ "$n" -le 1794988799 ]; then echo 13:14-13:15
  else echo NONE; fi
}
# Included verbatim in each item by build_items.py; no production command runs here.
# BEGIN TESTABLE GATES
ISSUED_EPOCH=1794962338   # magistrate b7aad16d issue, 2026-11-17 16:38:58 PST (item 395 B under item 388 fallback 4)
WATCH_UNTIL_EPOCH=1795048587   # AIR FALLBACK (item 388): fallback 3, RUN_STATE 405 (F0 run 9 Check, commit 2f9e8b6f6, committed 1794962187) + 86,400 s; email to Ed at launch
EXPIRES_EPOCH=$((ISSUED_EPOCH + 86400))
expiry_gate() {
  now=$(date +%s)
  test "$ISSUED_EPOCH" -le "$now" && test "$now" -lt "$EXPIRES_EPOCH" && test "$now" -lt 1795325340 \
    || { echo 'VOID: future issue, 24 h expiry, or kit expiry (RL-173 D.5; RL-169a)'; return 1; }
}
watch_gate() {
  now=$(date +%s)
  test "$now" -lt "$WATCH_UNTIL_EPOCH" && test "$WATCH_UNTIL_EPOCH" -le $((now + 86400)) \
    || { echo 'STOP: watcher observation missing, stale or in the future (RL-173 C.5)'; return 1; }
}
pred_gate() {
  PRED_LINE="$("$PY" -I -B - /Users/edr/campaign-out "$PRED_CAMP" "$PRED_SPAN" "$PRED_ROSTER" "$PRED_KIT_SHA" <<'PY'
import json, math, os, re, sys
root, camp, span, roster, kit_sha = sys.argv[1:]; roster = roster.split(',')
def stop(s): sys.exit(s)
d = os.path.join(root, camp)
if not os.path.isdir(d): stop('WAIT: predecessor has not run')
pat = re.compile('cq-' + re.escape(span) + r'-a\d+-\d{8}T\d{6}Z')
hits = sorted(n for n in os.listdir(d) if pat.fullmatch(n))
if not hits: stop('WAIT: predecessor has not run')
if len(hits) != 1: stop('STOP: multiple predecessor outputs; lead must resolve')
out = os.path.join(d, hits[0]); p = os.path.join(out, 'runner_receipt.json')
if not os.path.isfile(p): stop('WAIT: predecessor has not closed')
try:
    r = json.load(open(p)); bad = []
    num = lambda x: isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x)
    if r.get('rc') != 0 or r.get('error') not in (None, '') or r.get('mock') not in (None, False): bad.append('receipt status/mock')
    if r.get('roster') != roster or r.get('legs_planned') != len(roster) or r.get('legs_finished') != len(roster): bad.append('roster/count')
    k = r.get('kit') or {}
    if (r.get('runner_kind') != 'cadence-legs-v1.1' or k.get('campaign_id') != camp or k.get('sha256') != kit_sha
            or k.get('frozen_commit') != '2d347f721552fe03bdd19f113e7bad7a7c24908e'): bad.append('kit/runner identity')
    sr = r['span_result']
    if sr.get('outcome') != 'MEASURED_OK' or sr.get('chain_outcome') != 'COMPLETE' or sr.get('fault') is not False: bad.append('span result')
    steps = r['steps']; close = [s for s in steps if s['name'] == 'restore' or s['name'].startswith(('stop-', 'close-'))]
    if any(sum(s['name'] == name for s in close) != 1 for name in ('restore','stop-agents','stop-meter','stop-volumes')) or any(s['rc'] != 0 for s in close): bad.append('restore/close')
    if set(r.get('feeds') or {}) != {'agents','meter','volumes'} or any(f.get('stop', {}).get('proven_stopped') is not True for f in r['feeds'].values()): bad.append('feed stop unproven')
    m = r.get('meter') or {}
    if m.get('present') is not True or m.get('proven_stopped') is not True or m.get('bad_polls') != 0 or m.get('usb_errors') != 0: bad.append('meter operational fault')
    ended = r['ended']['epoch_s']
    if not num(ended) or ended <= 0: bad.append('close stamp')
    over = redos = 0
    for leg in roster:
        s = json.load(open(os.path.join(out, 'desk-bundle', 'legs', leg, 'leg_summary.json')))
        w, b, c = s['wall_s'], s['budget_s'], s['contaminated_redos']
        if not (num(w) and w >= 0 and num(b) and b > 0 and type(c) is int and c >= 0): raise ValueError('summary fields')
        over += w > 1.5 * b; redos += c
    if over >= 2: bad.append('LEG_OVERTIME')
    if redos >= 3: bad.append('CONTAMINATED_REDOS')
except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
    stop('VOID: unreadable predecessor operational evidence: ' + str(e))
if bad: stop('VOID: predecessor did not close clean: ' + ', '.join(bad) + '; never skip (RL-173 D.2)')
print(math.ceil(ended))
PY
)" || return 1
  PRED_CLOSE_EPOCH=$PRED_LINE
  case "${PRIOR_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo 'STOP: PRIOR_CLOSE_EPOCH must be an epoch'; return 1;; esac
  test "$PRIOR_CLOSE_EPOCH" -ge "$PRED_CLOSE_EPOCH" || { echo 'STOP: PRIOR before predecessor close'; return 1; }
  echo "PRED CLEAN $PRED_SPAN close_epoch $PRED_CLOSE_EPOCH"
}
effective_close() {
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo 'STOP: OTHER_CLOSE_EPOCH required, explicit 0 if none'; return 1;; esac
  CENSUS="$("$PY" -I -B - /Users/edr/campaign-out /Users/edr/code/jw-wt <<'PY'
import json, math, os, sys
def fail(e): raise e
found = []
for root in sys.argv[1:]:
    if not os.path.isdir(root): sys.exit('STOP: missing receipt root: ' + root)
    base = root.rstrip('/').count('/')
    for d, dirs, files in os.walk(root, onerror=fail):
        if d.count('/') - base >= 3: dirs[:] = []
        if 'runner_receipt.json' in files:
            p = os.path.join(d, 'runner_receipt.json')
            if '\n' in p: sys.exit('STOP: bad receipt path')
            try:
                with open(p) as handle: ended = json.load(handle)['ended']['epoch_s']
                if (isinstance(ended, bool) or not isinstance(ended, (int, float))
                        or not math.isfinite(ended) or ended <= 0):
                    raise ValueError('invalid ended.epoch_s')
            except (OSError, ValueError, KeyError, TypeError) as e:
                sys.exit('STOP: unreadable receipt close stamp: ' + p + ': ' + str(e))
            found.append((ended, p))
if not found: sys.exit('STOP: empty receipt census')
latest = max(t for t, p in found)
newest = [p for t, p in found if t == latest]
if len(newest) != 1: sys.exit('STOP: ambiguous newest receipt close epoch')
print(math.ceil(latest)); print(newest[0])
PY
)" || return 1
  EFF_EPOCH="$(printf '%s\n' "$CENSUS" | sed -n 1p)"
  EFF_PATH="$(printf '%s\n' "$CENSUS" | sed -n 2p)"
  if test "$OTHER_CLOSE_EPOCH" -gt "$EFF_EPOCH"; then
    EFF_EPOCH=$OTHER_CLOSE_EPOCH; EFF_PATH=OTHER
  fi
}
copy_gate() (
  # RL-171 §6.1/RL-173 A: campaign marker, or exact latest non-campaign Check's copy proof.
  case "$EFF_PATH" in
    /Users/edr/campaign-out/cl-*/cq-*/runner_receipt.json)
      id="$(basename "$(dirname "$EFF_PATH")" | sed -E 's/-[0-9]{8}T[0-9]{6}Z$//')";;
    *)
      test "${NONCAMPAIGN_COPY_OK:-}" = yes && test "${NONCAMPAIGN_COPY_CLOSE_EPOCH:-}" = "$EFF_EPOCH" \
        && test "${NONCAMPAIGN_COPY_RECEIPT:-}" = "$EFF_PATH" && test -n "${NONCAMPAIGN_COPY_RECORD:-}" \
        || { echo 'WAIT: exact latest non-campaign Check/copy proof missing (RL-171 §6.1; RL-173 A)'; exit 1; }
      case "$NONCAMPAIGN_COPY_RECORD" in *'<LEAD '*) echo 'WAIT: unfilled non-campaign Check/copy record'; exit 1;; esac
      echo "COPY CHECK VERIFIED receipt $EFF_PATH close $EFF_EPOCH: $NONCAMPAIGN_COPY_RECORD"; exit 0;;
  esac
  case "$id" in ''|*[!a-zA-Z0-9_.-]*) echo 'STOP: missing/invalid copy plan id'; exit 1;; esac
  for marker in "/Users/Shared/JouleWise/desk-copy/$id.ok" "/Users/Shared/JouleWise/desk-copy/$id.air.ok"; do
    if test -s "$marker"; then echo "COPY VERIFIED $id: $(cat "$marker")"; exit 0; fi
  done
  echo "WAIT: no verified cloud .ok or Air .air.ok copy marker for $id (RL-173 A)"; exit 1
)
close_gate() {
  test "${HOST_RESTORE_OK:-}" = 1 && test "${GROUPS_ABSENT:-}" = 1 \
    || { echo 'STOP: restore or process-group absence unproven'; return 1; }
  effective_close || return 1
  copy_gate || return 1
  case "$EFF_PATH" in
    /Users/edr/campaign-out/cl-*/cq-*/runner_receipt.json) actual=campaign; gap=300;;
    *) actual=other; gap=1200;;
  esac
  test "${LAST_CLOSE_KIND:-}" = "$actual" || { echo 'STOP: contradictory LAST_CLOSE_KIND'; return 1; }
  # Even though the F2 files live in campaign-out, F2 is OTHER: always 1,200 s.
  now=$(date +%s)
  test "$now" -ge $((EFF_EPOCH + gap)) && test "$now" -ge $((PRIOR_CLOSE_EPOCH + gap)) \
    || { echo "WAIT: close interval $gap s"; return 1; }
  echo "CLOSE OK latest $EFF_EPOCH kind $actual interval $gap"
}
priority_gate() {
  # Freshly read the lead's current items/READY records at EACH invocation.
  # NEXT_COUNTED_EPOCH covers ALL issued/staged counted items and READY counted
  # work awaiting staging, including next-date dev-03/04/05. Do not omit a known
  # item just because staging is pending. Unknown gate readiness stops; 0 requires
  # an explicit complete no-armable-span record.
  for pair in "SESSION_READY:${SESSION_READY:-}" "HP_READY:${HP_READY:-}" "P_READY:${P_READY:-}"; do
    case "$pair" in *:no) ;; *:yes) echo "CEDE: higher-priority $pair"; return 1;; *) echo "STOP: unknown $pair"; return 1;; esac
  done
  test "${F0_ELIGIBLE:-}" = no || { echo 'CEDE: eligible or unknown F0'; return 1; }
  case "${F0_REASON:-}" in spacing|daily_cap|launch_window) ;; *) echo 'STOP: F0 ineligibility needs a lawful reason'; return 1;; esac
  test "${OUTSTANDING_REFUSAL:-}" = none && test "${F2_STOPS_CLEAR:-}" = yes \
    || { echo 'STOP: unresolved refusal or F2 cadence-stop'; return 1; }
  test "${RESTART_PENDING:-}" = no || { echo 'STOP: host-event disposition/readback pending'; return 1; }
  case "${NEXT_COUNTED_EPOCH:-}" in ''|*[!0-9]*) echo 'STOP: counted armable-time census required'; return 1;; esac
  test -n "${PRIORITY_EVIDENCE:-}" || { echo 'STOP: missing priority evidence record'; return 1; }
  now=$(date +%s)
  # Work worst case 11,250 + runner/launcher reserves 560 + close interval 1,200.
  # This also clears the pin's fence end (t0 + 12,710).
  if test "$NEXT_COUNTED_EPOCH" != 0 && test "$NEXT_COUNTED_EPOCH" -lt $((now + 13010)); then
    echo 'CEDE: a counted span can arm within F2 worst case and close interval'; return 1
  fi
  echo "F2 TRIGGER: no higher-priority arm; F0 $F0_REASON; $PRIORITY_EVIDENCE"
}
admission_gate() {
  for proof in "F2_RECHECK_OK:${F2_RECHECK_OK:-}" "DEV03_SMOKE_CLOSED:${DEV03_SMOKE_CLOSED:-}" "LINE2_OK:${LINE2_OK:-}" "LINE9_OK:${LINE9_OK:-}" "CHECKLIST_OK:${CHECKLIST_OK:-}" "QUEUE_AUTHORIZED:${QUEUE_AUTHORIZED:-}" "COPY_KEY_SAFE:${COPY_KEY_SAFE:-}"; do
    case "$proof" in *:yes) ;; *) echo "STOP: admission/checklist evidence absent: $proof"; return 1;; esac
  done
  if test "$PIECE" -gt 1; then
    test "${F2_HAND_READ:-}" = PASS && test "${QUEUE_B_COMMITTED:-}" = yes \
      || { echo 'WAIT: piece-1 hand-read and lead-committed queue b required'; return 1; }
  fi
}
window_gate() {
  now=$(date +%s)
  picked="$(pick_arg "$now")"
  test "$picked" != NONE && test "$picked" = "$ARG" \
    || { echo 'STOP: outside date/launch band or argument changed; re-plan'; return 1; }
}
all_gates() {
  expiry_gate && watch_gate && admission_gate && pred_gate && close_gate && priority_gate && window_gate
}
# END TESTABLE GATES

ARG="$(pick_arg "$(date +%s)")"; export ARG
all_gates || exit 1
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
test ! -e "$CUSTODY/desk_fence.json" || exit 1
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker || exit 1
test ! -L /Users/Shared/JouleWise/host-power/high-power.marker || exit 1
sudo -n -l /bin/kill >/dev/null || exit 1
sudo -n systemsetup -getusingnetworktime  # Off
pmset -g | grep -i powermode             # 0; frequency word 0, AC power checked by checklist
MODE_VERIFY_RC=0
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify || MODE_VERIFY_RC=$?
echo "measurement_mode verify rc $MODE_VERIFY_RC"
# Only own-process-tree agent FAIL lines may be present, as dev-03's arm record; any other FAIL stops.
# Inspect the exit status and lines; CHECKLIST_OK=yes is set only with every applicable line proven.
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG" || exit 1
# validate-queue during staging uses the kit at its committed relative path in a temporary kits-root.
# Here compare the staged committed queue hash/roster: never run `next` or `checklist` to grant authority.
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG" || exit 1
# expected_s 7442, worst_case_s 11250, blackout_clear true, batch_windows [ARG]. Record complete output.
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*$/\1/')"
case "$BOOT" in ''|*[!0-9]*) echo 'batch print: boot unreadable';; *) NEXT_BATCH=$((BOOT+43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH+86400)); done; echo "next OS batch epoch $NEXT_BATCH";; esac
OUT=/Users/edr/campaign-out/f2-inst-01/cq-${SPAN}-a1-$(date -u '+%Y%m%dT%H%M%SZ')
test ! -e "$OUT" || exit 1
```

**Run.** Re-read the issued/staged counted items, NEXT_COUNTED_EPOCH, v4 READY record, hp-01/P/F0 eligibility, all stop/restore records, copy marker and the watcher observation now. Update the observations; do not reuse a cached eligibility answer. A prior date's expired item is never counted as armable. Run once, then exit immediately.

```sh
all_gates || exit 1
test ! -e "$CUSTODY/desk_fence.json" || exit 1
# The pinned launcher rechecks host/checklist state, condition-13 and its process census under its lock.
DEADLINE="$("$PY" -I -B -c 'import time; print(time.time()+12710)')"
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" --kit "$KIT" --legs L001,L002,L003 --batch-window "$ARG" \
  --output "$OUT" --disk-path "$REPO" --custody-root "$CUSTODY" \
  --magistrate-pid "$MAGISTRATE_PID" --deadline "$DEADLINE" \
  --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

**Check.** Only on the next activation, after the shared fence is gone. Read no stream, member output, feed file or custody content. This operational print is not the analyst read and never prints measured power/energy. All queue stops are judged by the pinned desk's operational projection and the lead; nothing is automatically re-armed.

Maintenance is print-only (RL-174 B.5 and D.1). Query the span's interval for the same processes as qualification. Earlier checks whose predicates lacked the three cloud jobs recorded them as unobserved.

```sh
(
  START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\1/')"
  START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")" || exit 1
  END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')" || exit 1
  echo "maintenance window $START_LOCAL .. $END_LOCAL"
  sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \
    --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd","bird","cloudd","fileproviderd"}' \
    > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err" || exit 1
  wc -l < "$OUT/maintenance-log.txt" || exit 1
  # per 10-minute bucket and process: "HH:M0 process count"
  awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
) || echo 'maintenance log unavailable; record as unobserved'
```

```sh
"$PY" -I -B - "$OUT" "$LEGS" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); roster = sys.argv[2].split(',')
r = json.loads((root/'runner_receipt.json').read_text())
assert r['roster'] == roster and r['runner_kind'] == 'cadence-legs-v1.1'
assert r['kit']['sha256'] == '651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b' and r['kit']['frozen_commit'] == '2d347f721552fe03bdd19f113e7bad7a7c24908e'
assert r['kit']['campaign_id'] == 'f2-inst-01' and r.get('mock') in (False,None)
print({k:r.get(k) for k in ('rc','error','legs_planned','legs_finished','span_result','ended','batch_windows')})
print('steps', [(x['name'],x['rc']) for x in r['steps']])
print('feed stops', {k:v.get('stop') for k,v in r['feeds'].items()})
print('meter operational', r.get('meter'))
assert r.get('feeds') and all(f.get('stop',{}).get('proven_stopped') is True for f in r['feeds'].values())
assert any(s['name']=='restore' for s in r['steps'])
assert all(s['rc']==0 for s in r['steps'] if s['name']=='restore' or s['name'].startswith(('stop-','close-')))
for leg in roster:
    rec = json.loads((root/'legs'/leg/'leg_record.json').read_text())
    result = rec.get('result') or {}
    keys = ('leg_status','g0_outcome','g0_wait_s','quiet_spans_ns','decode_tokens','decode_cap_reached','prefill_tokens')
    print(leg, {k:result.get(k) for k in keys}, 'attempt walls', [a.get('wall_s') for a in rec.get('attempts',[])])
    summary = json.loads((root/'desk-bundle'/'legs'/leg/'leg_summary.json').read_text())
    print(leg, {k:summary.get(k) for k in ('wall_s','budget_s','contaminated_redos','admitted','g0_outcome')})
print('RECEIPT OK' if r['rc']==0 and r['legs_finished']==3 else 'NOT CLEAN: report to lead; no retry')
PY
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify
sudo -n systemsetup -getusingnetworktime   # Off
pmset -g | grep -i powermode               # 0; report frequency word 0 and process-group absence
```

Report receipt/desk lines, named stops, actual close/fence-gone epochs, every restore line, feed-stop proof, copy/offload status, watcher observation, and the host-mode readback. Never hash/open stream files as an agent. The lead's deterministic desk uses `2d347f721552fe03bdd19f113e7bad7a7c24908e` and the leg-summary projection only. The lead records Check and the verified copy before any next soak. No commit from OUT.

**After (lead).** Piece 1's hand-read uses only leg_record and runner_receipt: every leg complete or g0_unreleased, at least two complete; each complete leg has a quiet span ≥600 s and reached 512; meter present/clean, all feeds stopped and restore passed. Record each wall against 2,700 s and the 256-token leg's realized prefill. Keep and flag any short decode; a short 256 leg goes to the research lead before queue b. Only a PASS permits the lead to commit queue b and issue pieces 2–4. This item cannot cross that gate. Later pieces run once in order under their own issued items; after piece 4 F2 leaves the ladder. An issue after 24 h or a missed date needs a new item. No early energy read; `lm-inst-01` and its cold pass gate only the later analyst read, not these runs.

405. **Magistrate b7aad16d (headless, Opus 5.5, interim lead), 2026-11-17 16:28-16:50 PST (`date`): STANDING-F0 run 9 (item 346; pre-launch item 401) CHECK: RECEIPT OK, verdict pass, every judged line passes; item 404 (a) re-read of F0 runs 1-9 finds neither #809 hole; #810 merged and typed items initialized**

```item
{"expires_epoch_s": null, "issued_epoch_s": 1794962185, "number": 405, "owner": "magistrate", "schema": "joulewise.run_state_item.v1", "sets": [], "status": "CLOSED", "supersedes": []}
```

- Receipt rc 0; parts `{"C": true}`, fresh soak; soak rc 0, sha256 `1cd69e24229a583c585003b2c7eb1bc332ebe7ad4a38cf31237e6d4db402f972`; part-C rc 0. t0 14:29:10 PST, receipt 16:27:57 PST (span 7,127 s). The align-r0 label was gone at 16:28; this activation spawned 16:28:34, after the receipt, so no agent was alive during the run.
- smoke_part_c.json: evaluation `pass` (`d_bank_mechanics`, `d_bank_start_state`, `step_d`, `x_g` all pass, as runs 7 and 8); N_chunk 4096; T_dead 987.475 s; gate_time 200.62 s of limit 394.99 s; no_g1_timeout pass (no turns).
- Restore lines all rc 0; host after close: no desk fence, no align-r0 label, ProcessType Interactive, powermode 0, Network Time Off, frequency word 0, no High Power marker, no stray monitor or root powermetrics, AC not charging.
- Printed only: turn-1 last-512 clock ratio 0.922 (predicted band 0.83-0.93; run 8 0.912); first off-nominal (pm Moderate) at token 1,700; token-rate ratio 0.978. Maintenance (log show, 45,750 lines): dasd steady; `mobileassetd` bursts at 14:47 (379 lines, soak), 15:53 (122, D_bank) and 16:23-16:24 (5,358, inside X_G_contrast 16:08-16:27); `softwareupdated` 8 lines at 15:11 and 16:11 and 1 at 16:00; XProtectPluginService 2 at 16:00. X_G still passes. OS build unchanged.
- Copy: an F0 close is non-campaign; this Check covers the copy (items 346/347, F2 draft copy_gate NONCAMPAIGN route). No offload.
- **Item 404 (a) re-read of F0 runs 1-9 (both #809 holes on the F0 pin):**

| run | OUT (UTC start) | verdict | `gate_timeout` in any part-c .json/.jsonl | X_G dir / runtime_result readable | x_g line present, pass | no_g1_timeout |
|---|---|---|---|---|---|---|
| 1 | 20261115T211611Z | pass | none | yes / yes | yes, pass | pass, [] |
| 2 | 20261116T011723Z | pass | none | yes / yes | yes, pass | pass, [] |
| 3 | 20261116T051844Z | pass | none | yes / yes | yes, pass | pass, [] |
| 4 | 20261116T133233Z | pass | none | yes / yes | yes, pass | pass, [] |
| 5 | 20261116T193440Z | pass | none | yes / yes | yes, pass | pass, [] |
| 6 | 20261117T021602Z | pass | none | yes / yes | yes, pass | pass, [] |
| 7 | 20261117T142329Z | pass | none | yes / yes | yes, pass | pass, [] |
| 8 | 20261117T182510Z | pass | none | yes / yes | yes, pass | pass, [] |
| 9 | 20261117T222907Z | pass | none | yes / yes | yes, pass | pass, [] |

  Hole (1) (pass with a recorded G1 timeout in episode_flags): no run has the string `gate_timeout` anywhere in its Part C JSON. Hole (2) (completed X_G with unreadable evidence omitted): every run has X_G_contrast, a readable runtime_result.json, and an `x_g` line that was judged. No verdict changes. Script and output: custody `standing-f0/check-b7aad16d/` (`reread-404a.txt`).
- **#810 merged** (item 404): all 41 checks green on head `442e37c49`; merge commit `5a301bd45`; `run_state_add.py init` on main gave cutover 405, `run_state_items.py check` exit 0 (commit `0aa2bb0a9`). From here items go through `run_state_add.py`.
- No mail from Ed (unread search empty at 16:29); no new directive; notice queue empty.

<!-- RUN_STATE LEGACY ITEMS: archived in docs/archive/RUN_STATE-legacy-2026-11-17.md; cutover 405; legacy_max 404 -->
