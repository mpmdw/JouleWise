# Seat: opus-validity

## Bottom line

The v4 design is sound on paper, but four operational paths can produce a W1 that looks complete and still loses its scientific payload. Ranked by expected damage:

1. **Battery top-ups mid-window.** Pilot 10 lost 3 consecutive members to a top-up at 21-31 W. A charging span is an EXCLUDE_MEMBER, and the contrast keeps 2 runs per arm per template. One top-up inside ordinals 6-16 therefore makes a template INCONCLUSIVE. Over 16.5 h D windows, repeated top-ups would also cut D_k below the 6-per-pair per-session fit.
2. **G0 recovery after heavy D members.** R is captured after a 30B member. Every contrast arm has exactly one D predecessor, and the late replay (ordinal 18) follows D ordinal 17. If D heatsink recovery is longer than idle + the 600 s G0 cap, timeouts and deadman stops become systematic, not random.
3. **Power mode can drift silently.** The readiness row only greps `lowpowermode 0`. The R1 High Power restore fix sits on an unreviewed lane, and POWERMODE-PREFLIGHT-RECORD-01 has been queued since 09-09.
4. **R1's frozen slots can absorb background load.** The slots are δ from the soak SD, t_decline, N_chunk, the heavy class and the sensor picks. Background load comes from the daily batch, which was timed at 12:53 PDT before DST ended on Nov 1, and from XProtect and Spotlight respawns. The bias then carries into every window.

**Cheapest change for W1 that does not delay R1:** a battery arm rule. Arm W1 only within about 30 min after a top-up has completed: SoC at 99 % or more, IsCharging No, Optimized Battery Charging confirmed off. Have R1, which already journals B0AC at 1 Hz, report the D-load drain rate and the SoC that triggers a top-up. This needs no code. It turns a better-than-even chance that one top-up lands in the contrast block into roughly the 6.5 h clean run pilot 9 had. A charge hold through a narrow sudo rule, like the powermode one, is Ed's call before the D-series.

**Next most valuable change, also with no R1 delay:**
- extend R1's post-D-step cooldown until recovery is within δ, so the G0 timeout risk after D members is predicted before W1;
- swap W1 ordinals 17 and 18, so the D replay follows a 30B member like its original. This keeps the contrast position sums and predecessor balance unchanged.

## Expected MDE

**Contrast (W1, 30B, identical tokens):**
- Noise on d_t is about 2.1 J.
- The rule's decision sizes are |d| ≥ 10 J on both templates to confirm T, and |d| ≤ 6 J to reject. The 90 % CI of δ has 4 df (t = 2.13).
- An effect of roughly 6-10 J is resolvable only if all 8 runs survive and are token-identical. One lost run makes that template INCONCLUSIVE by rule.

**D identical work (U3):** the bar is 3 × max(2.97 J, 0.0011 × E_pair). For D episodes of about 20-40 kJ (guess: 6-8k decode tokens at about 4 J/token plus prefill), that is about 65-130 J.

**Hidden-work detection for D:**
- W1: none. There is no held-out D benign pool, and U4-U6 are not evaluable.
- After D3 (m ≈ 21 per pair, sample-maximum thresholds), a rough guess from scaling the 30B: v3 s_r/E was about 1-2 % (bank 45-58 J, spam 19-33 J on ~2.7 kJ episodes) and thresholds were 2.5-7 s_r. Applied to D, the minimum detectable hidden energy is about 0.7-4 kJ, which is about 200-1,000 hidden decode tokens per episode, on the order of one xhigh reasoning turn.
- Budget-truncated D episodes (about 2-4 turns) and per-session fits with at most 7 benign per pair could widen this a lot. Battery or thermal exclusions that push a pair below 6 benign per session make it worse.
- None of this is an FPR or power figure.

## Issues

### [CRITICAL] macOS battery top-ups exclude members mid-window; the contrast has no redundancy and D windows are long
- owner: mechanical; blocks: W1
- evidence: RUN_STATE item 175: pilot 10 spam ordinals 8-10 excluded by a top-up at 21-31 W from 17:52, after the pack sagged to about 95 %. About 18 kJ drained outside the measured requests, and request-phase assists were only about 300 J. joulewise/hazards/battery.py smc_span_findings: charging above +200 mA gives battery.member_span (EXCLUDE_MEMBER). FINAL-DESIGN §2.5 rule: INCONCLUSIVE when a template has fewer than 2 token-identical runs in either arm, and each arm has exactly 2 runs. X8: no replacement. FINAL-DESIGN §3.1.4 only requires battery ≥ 95 % at arm, which is about the top-up trigger. W1 span is about 7.5 h and is heavier than v3; D_k windows are 58,260 s with 7 benign per pair.
- recommendation: For W1 (mechanical):
- Arm only within about 30 min after a top-up completes: `pmset -g batt` at 99 % or more, IsCharging No, Optimized Battery Charging verified off.
- Copy the ioreg battery block into the arm record.

For R1 (no extra time):
- Report the SoC drain rate in %/h under D and the 30B, and the SoC at which charging resumes.
- Use these to predict top-ups per window.

Before the D-series (Ed):
- Decide on a charge hold, e.g. a narrow sudo SMC charge-inhibit helper like the powermode rule, set at arm and restored on every exit path.
- Otherwise accept and pre-declare the expected losses.
- Pre-declare whether a battery-excluded contrast run counts toward the 2-run rule.

### [HIGH] G0 may systematically time out after heavy D members (window reference is post-30B)
- owner: lead ruling; blocks: R1
- evidence: WP14(b) and A1: R is the median over the last 60 s of member 5's idle, and member 5 follows anchor 4 (30B). G0 cap is 600 s; on cap the run is flagged, proceeds, and is excluded (X2). WP14(a) allows a heatsink τc up to 300 s, so a heavy D turn needs about 3τ (~900 s) to return within δ ≥ 1 °C. The available time is 300 s idle + warmup + 600 s G0. A1 predecessor table: each contrast arm has exactly one D predecessor (6, 9, 12, 15), and replay 18 follows D 17. workload.py:416-419: G0 shares the deadman slack ('Reserve no additional G0 allowance'), so a long G0 also shortens the D episode before the deadman. U1(d) allows at most 1 G0 timeout per model per window.
- recommendation: In R1 (adds minutes, not a delay):
- Extend the cooldown after D's planning-turn step until S_slow is within δ of the soak reference, or 1,500 s.
- Record the full recovery curve from it.

Before freezing W1, the lead predicts G0 duration for each D→X and D→D transition:
- If the predicted wait exceeds 600 s, apply escalation step 1 (idle 300→450 s, or a D-successor idle) now, under the fit rule.
- Do not wait for W1 to fail U1.

Also rule whether X2-flagged contrast runs count toward the contrast's 2-run minimum.

### [HIGH] Power mode can silently differ from the frozen series lever
- owner: mechanical; blocks: W1
- evidence: configs/gates/physics_rows.json:2133: the readiness regex only finds 'lowpowermode 0' anywhere in `pmset -g custom`, so powermode 2 (High) passes. POWERMODE-PREFLIGHT-RECORD-01 in docs/process/state_kernel.json is still 'queued' (2026-09-09). The WP7 MEDIUM 'exec drops the High Power restore trap' is fixed only on lane/2026-11-06-v4-r1-fixes-wp7 `9c92e685a`, which its commit message calls unreviewed. FINAL-DESIGN §2.2: once adopted, a lever is never changed within the series.
- recommendation: - Get an Opus executing review of the WP7 lane before R1.
- Kit v4 freezes the series AC powermode (0 or 2) in r1_slots.
- Every arm, and every member's bundle, records `pmset -g custom` AC powermode.
- Arm refuses on a mismatch, and the desk sets instrument_ok false on any member mismatch.
- Promote POWERMODE-PREFLIGHT-RECORD-01 for ALIGN v4 (this does not touch the b5 registered rows).

### [HIGH] R1's frozen slots can be biased by background OS activity (daily batch, XProtect, Spotlight, DST shift)
- owner: mechanical; blocks: R1
- evidence: RUN_STATE item 17 timed the daily batch at 12:53:29-12:54:02 local on 10-08 to 10-10, which was PDT. DST ended Sunday 2026-11-01, so its PST time is unverified (it is 12:53 or 11:53 depending on the scheduler). Item 14: the XProtectRemediator scan has no fixed time and runs at about 2 cores. FINAL-DESIGN §2.6: δ_k = max(1.0 °C, 3×SD) over R1's 30-min soak (S5); t_decline, N_chunk and the heavy class come from R1 step tests. WP14(a): R1 selects S_fast and S_slow on D's step. All of these are frozen for the series.
- recommendation: - Before R1, re-time the daily batch in PST from any existing census or CPU journal; pilot 7 ran 08:51-15:22 PST on 11-04.
- Schedule the R1 soak and step tests to avoid 11:45-13:15 local.
- Journal per-second CPU load and the census during the soak and steps. Redo a segment if CPU busy exceeds a pre-declared threshold, e.g. above 0.5 core sustained for 60 s.
- Compute SD on the detrended last 20 min, and require the soak slope |slope| ≤ 0.2 °C/min before the SD window opens.

### [HIGH] Deadman margin at xhigh is thin; the time-based stop can break D's only W1 identical-work pair
- owner: lead ruling; blocks: W1
- evidence: T_dead = (1,750 − I_D)/1.13544. The 1.13544 multiplier was fitted on 30B members (sizing_b5). The code only checks deadman_s < 1800/1.13544 (workload.py:155) and never checks it against I_D. G0, G1 and hold waits all count against the deadman (workload.py:416-428). An admitted turn keeps its full 4,096 cap, so the last turn can run to B_D + 4,095 tokens, about 930 s at about 11 tok/s. Replay 18 follows heavy D 17, while original 5 follows a 30B anchor. A deadman stop at a different turn means the pair is not token-identical (X5), so U3 for D is not evaluable in W1 (A3.4).
- recommendation: - R1's two back-to-back gated D runs record per-member tail time (episode end → process exit), G0 duration, and total hold and G1 time.
- The kit asserts I_D + 1.13544·T_dead + max observed tail + 60 s ≤ 1,800.
- Size B_D so that worst-case R1 G0 + holds + the last admitted turn fits T_dead with margin.
- Swap W1 ordinals 17 and 18, so the replay follows X-G 16 (30B) like its original. Contrast position sums and predecessors are unchanged, and the fit rule's first drop simply truncates the tail.

### [MEDIUM] Ambient is unobserved (72 F thermostat only), and U4, U5, U6 and G0 timeouts cannot be attributed
- owner: needs Ed; blocks: D-series
- evidence: FINAL-DESIGN §3.1.3 asks for a logger or a thermometer read at arm and desk; there is none. Kit configs carry run_metadata.ambient_temp_c None. U4 has a ±0.25 % cross-window mean bar and U6 a ±0.37 % early-to-late bar. U5's β_T is fitted from SMC temperatures that include ambient. D_k windows of 58,260 s cross day and night, so thermostat cycling, night setback or sun can shift the idle state relative to the window-local R.
- recommendation: Ed:
- Confirm the thermostat is in permanent hold (no schedule or setback) and note vent airflow at the Mac.
- Buy a $15-25 1/min logging thermometer, placed 30 cm from the intake. It is not needed for R1 or W1, but needed by D1.

Mechanical, now: designate one R0/R1 record-only chassis key (τc > 300 s) as an ambient proxy, and print its member-start idle value and R − R1-soak per member (print only).

### [MEDIUM] High Power A-B-A rule is underdetermined and order-biased; adopting it changes what the contrast tests
- owner: lead ruling; blocks: R1
- evidence: FINAL-DESIGN §2.2 and the Ed ruling in the V4 plan: one step per condition, 10-min cooldowns, adopt on ≥ 25 % longer t_decline. A 10-min cooldown is about 2τ for τc ≤ 300 s, so A1→B→A2 accumulates heat and biases B and A2 short. There is no rule for A1 and A2 disagreeing, or for t_decline = ∞ in either arm. The contrast (§2.5) attributes pilot 7's turn accumulation under Automatic; a cooler High Power setup makes T REJECTED more likely regardless of pilot 7's cause.
- recommendation: - Start each A-B-A step only after a G0-style release against the soak reference.
- Pre-declare: adopt only if t_decline(B) ≥ 1.25 × max(A1, A2). If B = ∞ and both A are finite, adopt. If all are ∞, do not adopt (no decline to fix). If A1 and A2 differ by more than 25 %, the result is inconclusive and the setting stays Automatic.
- If adopted, protocol v4 discloses that the contrast's attribution (a) is conditional on the v4 setup.

### [MEDIUM] R0 effort ladder at T=1.0 uses about 8-12 turns; a lucky xhigh pass can make W1 D screen-only
- owner: lead ruling; blocks: R1
- evidence: FINAL-DESIGN §2.2: 2 episodes per rung, pass if ≤ 20 % of turns are capped with unclosed reasoning and median reasoning ≤ 2,048. So 1 capped turn in 8 passes. A3.7: if D makes no state-changing action on some pair in any benign W1 episode, there is no D in this phase and the lead must pick a new cell, which is selection data again. B_D of 6,144-8,192 gives about 2-4 xhigh turns.
- recommendation: At the R0 dispositions, from data R0 already has (no rerun):
- Add a capability proxy: each ladder episode must make a state-changing tool call within its first 6,144 decode tokens.
- Report the capped-turn fraction with its exact binomial CI.
- If the proxy fails at xhigh, step to medium before R1, so R1's step tests and slots are measured at the rung W1 will use.

### [MEDIUM] Contrast token identity is verified only for X; prompt-path changes could make Y diverge
- owner: mechanical; blocks: W1
- evidence: V4 plan WP19: a laptop replay shows X matches b-e25. R1 step 3 runs one X-G only. The integration changed shared render paths (WP2 `unsplit(*, add_generation_prompt=True)`; WP7 review of add_generation_prompt through the XML, reasoning_content and JSON paths). A Y divergence makes Y's arms non-identical and the verdict INCONCLUSIVE.
- recommendation: In WP19, also render Y's (b-e18, index 14) turn-0..k prompt bytes and token ids on the laptop and compare them with pilot 7's recorded prompts. This needs no model, only the tokenizer.

If feasible, swap R1's X-G run for one X-G plus a short Y-S run with max_turns 2, or confirm Y at the W1 desk before any contrast read.

### [MEDIUM] Disk headroom, offload and the borrowed SSD gate W1; SSD activity during a window is an unmeasured load
- owner: needs Ed; blocks: W1
- evidence: V4 plan Q1/E1: W1 needs about 117 GB free at arm against about 66-80 GB now. Pilots 8-10 offload only via the #665 runbook with a second copy on the borrowed SSD, available by day only from 11-07. The Flash-Next gold run needs about 120 GB at peak. D_k needs 52.9 GB for two copies. Only corespotlightd and spotlightknowledged are paused, so mds_stores and mdworker would index a newly mounted volume.
- recommendation: Ed answers E1 (order: W1 or Flash-Next gold first).

Arm rules:
- No external volume is mounted during an armed window (census check `diskutil list external`).
- The SSD is never attached or detached between t0 and the terminal record.
- Offloads and gold-run work happen only by day between windows.

### [MEDIUM] Checkpoints are off for the series; capped and unclosed turns can trigger full dense-cache rebuilds and create outlier calibration rows
- owner: mechanical; blocks: D-series
- evidence: V4 plan ruling 2 and the align_v4 README: `hybrid_checkpoint_limit=0` throughout, superseding A3.6. The R0 bar counts rewrites only on closed-reasoning turns. The ladder allows up to 20 % capped turns, whose history the template closes with '\n</think>\n\n' (endpoint.py:421-470), so a boundary retokenization can force a whole-prefix re-prefill of 10-30k tokens. Thresholds are the sample maximum at m = 20-21, so one rebuild-heavy benign trajectory sets the threshold.
- recommendation: - R0 reports rewrites for all transitions, split into closed and capped/unclosed.
- The A3.6 5 % trigger is computed on all transitions.
- The desk prints per-trajectory `cache.rebuilt_untrimmable` counts beside residuals, plus a labelled sensitivity without rebuild trajectories. This is print only and is not used to choose.

### [LOW] Window reference R has no sanity bound; a warm capture makes every gate permissive without any flag
- owner: mechanical; blocks: W1
- evidence: WP14(b): R is a single 60 s median from member 5's idle, verified for custody but not for plausibility. U2 checks only the spread of G0 release values within a model, not their level against an external reference.
- recommendation: The desk prints R − R1 soak median for S_fast and S_slow, plus the ambient proxy. If it exceeds δ, set a printed `thermal.reference_warm` diagnostic and pass it to the lead before D1. Print only.

### [LOW] Cross-session token determinism for dense qwen3_5 at T=1.0 is untested, and the sentinel design (U4) depends on it
- owner: mechanical; blocks: D-series
- evidence: A2 and U4: sentinels replay W1 ordinal 5 across windows and days. R1 tests identity only within one session (2 back-to-back D runs). The gated-delta and hybrid kernels differ from the 30B MoE path that pilots 4-10 validated. X5 makes a pair non-identical.
- recommendation: At the W1 desk, before D1 is frozen, explicitly compare R1's D spam/benign s1 tokens with W1 ordinals 5 and 18 (cross-day). If they diverge, U4 is not evaluable; rule on the sentinel design before spending held-out seeds.

### [LOW] Spotlight pause scope and overnight OS jobs for 16.5 h D windows
- owner: mechanical; blocks: D-series
- evidence: RUN_STATE item 169/173 recipe: `kill -CONT 716 47361` by pid; the WP10 launcher stops only corespotlightd and spotlightknowledged. A respawned daemon or mds_stores/mdworker indexing new bundle files is not covered. A 58,260 s chain starting at or after 13:10 must cross 00:00, where the /tmp walk rule (item 4: < 1 GiB and < 1,000 entries) applies. Automatic macOS update installs or restarts overnight are not mentioned in the v4 docs.
- recommendation: - Pause the daemons by name at each stage start and record their pids in the census.
- Verify the runs root is on Spotlight's Privacy list.
- Make the /tmp rule and automatic-update-install off (`softwareupdate --schedule`, plus a check of the System Settings auto-install toggle) arm preconditions for D windows.


## Cannot claim
- No false-positive rate or power claim: thresholds are the sample maximum at m = 20-21 per pair, with 2-3 held-out sabotage per pair, from the frozen per-session LOO 7fbd95e31.
- W1 supports no detection claim for Qwen3.8-27B: there are no held-out D benign trajectories, and U4-U6 are not evaluable in W1.
- No cross-model or cross-architecture monitoring claim until Flash-Next (FN) is admitted; the series has one production model.
- The 30B contrast verdict does not certify dense D. D is heavy by protocol, and the contrast governs only light cells and the pilot 8-10 disclosure.
- If High Power is adopted, the contrast tests heat accumulation under the v4 setup, not under pilot 7's Automatic conditions. Attributing pilot 7's signature is then conditional.
- Gated and held energy is energy at a reference thermal state, not production agent energy. Production agents do not pause.
- No ambient-controlled claim: with no thermometer, cross-window (U4) and early-to-late (U6) shifts cannot be separated from room-temperature changes.
- No continuity claim for the 30B anchor bridge across the new physical setup; the K-session offset is printed only.
- D episodes are cut off by the token budget B_D (about 2-4 xhigh turns): no claim about full-length SHADE task completion or monitoring of full-length episodes, and the capability gate is minimal (any state-changing action).
- Known-H tamper curves describe detection of a known log omission with measured joules held fixed. They are not a causal effect of sabotage or of real omitted reasoning.
- Excluded members (battery charging, X1-X7) are not replaced. Coverage claims hold only for non-excluded spans, and exclusion is not shown to be independent of thermal state or episode length.
- High Power adoption rests on one A-B-A comparison (n = 1 per condition); no general claim about power-mode effects.