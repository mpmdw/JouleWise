# Items for the research lead's next batch (lead's running list)
- 2026-11-15 01:3x: RL-172a's "look prints retried soaks by refusal kind": the runner receipt at 6010985a3 does not record the kind (slope vs load; `refused` text is generic). Lead decided the look reads receipt fields only (no soak stderr logs; open-allowlist kept tight), so kind prints "kind not recorded". Ask: add a `soak_refusals: [{kind}]` receipt field at the next runner pin?
- trace_coverage print (Mythos #9) still unruled; twin lacks it.
- Mythos #6 coefficient writer / predict path: needs ruling.
- Q11 drift threshold 0.04 vs ruled 0.08.
- RL-172 (h) restart: FileVault likely blocks unattended login; lead to probe remotely between spans.
- PR #798 (W1 line CI fix after #774; head fcb7f536f, CI green): row 4 needed; 436f0b202 touches strict-tier scripts/align_v4_w1_synthetic.py (synthetic harness). AND the carry question: #774 also changed km003c.py, align_v4_session.py, align_v4_thermal_desk.py, align_pilot_session.py, align_v4_u3_export.py (Part C static closure); lead's RUN_STATE 329 note said one line. Sol executing seat on Part C dynamic execution vs #774 diff: /Volumes/JW-EXT/scratch/sol-798-carry/.
- UPDATE 01:5x: Sol (sol-798-carry) — carry HOLDS (Part C calls no #774-changed body, never imports v4_desk_seal; condition 13 returns c3f4bacd8). Lead's note 329 conclusion right, evidence incomplete (17-path census vs imported closure) — lead corrects in next RUN_STATE lead note. #798 needs public PILOT.json parse restored (builder fixing), then row 4.
- Second Part C (c3f4bacd8) info-only observations (desk builder, evidence partc2-c3f4-desk at c9fc0339d): (a) step-D free sensor pick moved to Tf3B/Tf0B (TV0h/Tp1G first run), binding confirmation ok both; (b) OS state stale 41 Heavy rows up to 43 s after hot turn; (c) one TV1h snap 90.0 outside gates; (d) token-rate ratio 0.976 < predicted 0.98 again, clock ratio 0.930 at edge.
- RL-171 §5 item 3 count: legs overlapping maintenance that passed rule 5: L010 (mobileassetd before G0, backupd in turn), L012.a2 (batch tail before G0).
- Process note: subagent report-file writes are blocked by the harness; lead records verdicts in RUN_STATE notes instead.
- Look package Mythos N7 (GPU rail integrates across a power_trace.csv hole): analyst built the refusal behind fit.gpu_trace_hole_refusal (default OFF); quantification /Volumes/JW-EXT/scratch/fit-interim/gpu-hole/quantify.json (6 s hole in a 20.6 s hot block flips a synthetic GPU verdict); question /Volumes/JW-EXT/scratch/fit-interim/Q-gpu-hole.md (threshold; refuse vs exclude).
- Twin-spec: trace_coverage, soak_retries, ledger_gate set aside in twin comparison — rule in or keep out.
- hp-01-s02 L004 (first High Power leg of the span): OS reported Moderate 29 / Heavy 36 readings 313-377 s into the turn (os_level_max 2, pm_nominal false); the smoke's L001 stayed level 0. Description only (no_drop_by_outcome). Evidence desk-cq-hp-01-s02-a1 at 37afda2a4.
- Desk-final sample draw (PR #799): seed 2026111501, one span per block of four within kit×G0-shape group per queue — the desk builder's choice, research lead to confirm.
- Controller (#800 b21d312e9): (1) remaining ms close-side handoff window needs a watchdog interlock in scripts/magistrate_watchdog.py, which is in W1's registered closure → registration change: rule whether to build it or accept the window (controller's standing fence + agent census as backstop). (2) Sol R10: RL-149 "watcher live within 24 h" vs RL-172 (g)7 "never reused" — controller re-reads one <24 h stamp each arm; rule. (3) Sol R12: RL-158 Q1 print — completion record + hold, or print only?
- hp-01 block complete (11-15): 12/12 admitted over 3 spans, 0 redo, 0 stops, restore proven ×3. First leg of each High Power span (L001? no: L004, L008) reached OS level 2 / Heavy ~312-377 s into the turn; others Nominal. Desks: e7859778 (s01), 37afda2a4 (s02), 05c681ac4 (s03). Description only.

## Batch added 2026-11-15 17:3x (lead; held for quota, none blocks the MBP chain)
### Look package #795 (round 6, head 66fa7c452; handoff /Volumes/JW-EXT/scratch/look-r6/HANDOFF.md)
1. Clock-fit excess is measured two-sided about the fitted line: confirm.
2. N2 residual: hidden holes with clock-fit excess between 1 and 2 s still integrate: accept?
3. Trace clauses judged on energy-fit intervals, not rule 3/4's G0-to-last-token interval: confirm.
4. An undecodable stream excludes every leg of its span; a `.zst` stream/trace refuses the look: confirm.
5. Each typo correction of a published stage-1 hash needs a ruling id in the ledger (`stage1_superseded`): confirm.
6. Is cadence custody ever desk-compressed?
7. Q11 applied as 0.08 (10k reps: 0.0280 SE .0017; 0.0231 SE .0015); GPU backstop now mandatory in the validator; the "five-world sentence" is still open.
### Controller #800 / desk #799 (handoff /Volumes/JW-EXT/scratch/ctl-r4/HANDOFF.md)
8. Mythos N12: reference record hash bound only by capture-run name (frozen pins record no hash).
9. Gate-3 T13: an informational page (e.g. PLAN_REFUSED_AT_T0 stall) releases the fence until acknowledged: within RL-173 E's continuous fence?
10. L002 not released: halt every arm (fallback included) until the lead's L002 release record, no lift by disposition: intended?
11. Hand-armed prior v1.1 spans that count for line 9 need Q1 records written by the lead at switch-over: confirm.
12. Switch-over: a legacy one-line copy marker reads OFFLOAD_FAILED, so the lead writes a typed marker first: acceptable?
13. Only scheduled runs of the Actions watcher on `main` of this repository count (C.4): confirm.
### Lead notes
14. RUN_STATE 353: one `ssh mbp-ts true` probe ~15:10 during F0 run 1 (verdict pass, no differing line). Recorded; no action proposed.
15. Host events (RL-173 E): spotlightknowledged stopped; corespotlightd respawns on demand; `tmutil disable` needs Full Disk Access (no TM destination configured). Both deferred to Ed-at-machine before freeze 2.
16. Ed 11-15 17:46 chose iCloud Drive as the offload provider ("use icloud, no? why would you not use icloud"). Proposed permanent A.3 tool: #804's icloud backend — synchronous brctl wait, then evict + re-download + sha256 equal to the ciphertext as the provider readback; bird/cloudd/fileproviderd in the maintenance line. Rule: does this satisfy A.3 permanently?
