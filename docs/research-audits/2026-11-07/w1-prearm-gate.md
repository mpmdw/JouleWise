# ALIGN v4 W1 pre-arm blind gate: synthesis (2026-11-07)

**Track:** the blind Fable + Opus cold gate that protocol v4 and CHAIR ruling 22 require before the first W1 arm.
**Head gated:** `lane/2026-11-06-v4-r1-integrated` at `e901eb2a4`.
**Base:** `origin/lane/2026-11-05-align-pilot10-benign` at `5f817856b` (the merge base).
**Inputs:** two independent blind seat reports, seat 1 (Fable) and seat 2 (Opus), reproduced verbatim in the appendix.
**Synthesis method:** where the seats agree, the finding is stated once. Where they disagree, or only one seat raised a point, I re-checked it at `e901eb2a4`: I read the cited code and docs, re-ran both seats' kit probes, and ran targeted tests. Unless a line names another commit, every `path:line` below is at `e901eb2a4`. I opened no restricted path and inferred no Block-5 value.

## Executive summary

- **Verdict: do not arm W1 at `e901eb2a4`.** Today the kit cannot arm anyway: `registration/inputs.json` still has R0/R1 placeholders and `r1_slots.json` is pending. The findings below apply once R1 fills those slots.
- **1 BLOCKER: protocol v4 is still a draft, and the code never checks registration.**
  - The protocol says it is "not registered or authorized to arm".
  - Nine W1-blocking chair rulings are not installed.
  - WP19 does not exist.
  - `require_w1_ready` checks no registration or cold-gate receipt.
- **5 HIGH:**
  - CHAIR 4(a) battery arm rule is missing.
  - The 30B contrast is unprotected: the G0 cap can exceed the fixed 1,086 s contrast deadman, there is no contrast fit check, and the kit never asks whether R1's X-G run actually completed.
  - A failed duty bar admits W1 on a bare fallback record, and fallback steps 2 and 3 cannot be expressed in the kit at all.
  - The arm-time offload re-hash contradicts ruling 20.
  - Protocol WP14(a) describes a classifier that is not the merged #692 classifier R1 will run.
- **Also found:** 6 MEDIUM and 9 LOW. One of the MEDIUMs is a deterministic test regression at the gated head (Ruling 76 versus D8-1), which I confirmed red at the head and green at the base.
- **What holds up:** both seats found these sound, and my spot checks agree:
  - the run_night High Power admission, lock, close and restore paths;
  - the termination-proof deferral, the window deadline and the episode deadman wiring;
  - the window-reference capture/consume custody;
  - the roster, seeds and replays;
  - the L1, 1(f) and G0_cap_W1 re-derivations;
  - QuietGuard, which is R0-only.

## Decisions needed from the lead

1. **Registration path (BLOCKER-1).** Choose one, rule by rule:
   - install rulings 4, 5, 6, 9, 11, 15, 17, 18 and 20 in protocol v4 and in the desk, land WP19, and restate WP14(a) from #692 with the chosen D5 slow rule; or
   - drop a ruling with a public deviation-log entry (you own prereg rulings).

   Then decide whether `require_w1_ready` must also refuse without a registration receipt (protocol commit, both cold-gate verdicts, ruling-table state). Recommended: yes. It is a small change and turns a process step into a mechanical one.
2. **Battery 4(a) mechanism (HIGH-1).** Choose between:
   - code in `arm_checks`: read `pmset -g batt` and the `ioreg -r -c AppleSmartBattery` block, refuse unless ≥ 99 %, not charging and OBC off, and record the block (recommended; the parser `battery_float.IOREG_BATTERY_ARGV` exists); or
   - a signed manual checklist entry, with the ioreg block attached to each `staging/v4-arm-NNN.json`.

   Either way, fix protocol :698, which still says "battery ≥95%".
3. **30B contrast protection (HIGH-2).** First confirm that G0_cap_W1 applies to contrast members. The kit and the R7-12 integration note say it does; protocol :365 ("Every other G0 keeps 600 s") can be read otherwise. Then choose one:
   - (a) fail closed in the kit: require R1's X-G to have completed all WP18 turns with no deadman, and refuse when `G0_cap_W1 + (X-G wall − X-G G0) > CONTRAST_DEADMAN_S`;
   - (b) give contrast members their own G0 cap, sized to fit inside the deadman;
   - (c) accept the X7 risk and pre-declare the contrast verdict as conditional on it.
4. **Duty-bar fallback (HIGH-3).** Should the kit refuse fallback steps 2 and 3 until it can express them (450 s post-D idle; a 4-bit D identity)? Should step 1 require S6 ≠ S5 with its tuning receipt? Should an *inconclusive* duty bar need an R1 re-run, as R7-3 rules for inconclusive calibration segments? Recommended: yes to all three.
5. **Offloads against ruling 20 (HIGH-4).** Where will W1's configured offload destinations live? If they are on the external SSD, choose between:
   - a daytime offload-verification receipt (path, digest, timestamp, freshness bound) that the arm checks in place of a live re-hash (recommended); or
   - ruling the live offload re-hash out of the W1 arm gate.
6. **D seed-law tag (MEDIUM-1).** Choose between:
   - keep `qwen3.8-27b` for the whole D cohort, and record that CHAIR 25's quantization tag is a label only; or
   - change the seed-law tag to `qwen3.8-27b-8bit` now and regenerate the kit.

   This must be decided before the W1 arm. Afterwards only the first option remains without orphaning W1 ordinal 5, the sentinel/E_ref trajectory.
7. **U5 at R1.** `check_r1_evidence` accepts a U5 verdict of `pass`, `fail` or `inconclusive` (`scripts/align_v4_kit.py:171,271`). Protocol :467 says that a U5 failure means "state not controlled", but it states no W1 consequence. Should a U5 FAIL at R1 admit W1?
8. **An unobserved window reference at member 5 (MEDIUM-2).** Choose between:
   - accept the protocol as written: every later thermal member ends after its 300 s unobserved G0 wait (X4), and the window yields anchors only; or
   - add a chain-level stop at ordinal 6 on `thermal.window_reference_unobserved` or `_missing`. That stop is not outcome-dependent.

   Either way, correct the protocol sentence "`--max-failures 1` stops the stage".
9. **D8-1 against Ruling 76 (MEDIUM-3).** Choose between:
   - re-raise only `KeyboardInterrupt` in `_qualification_observe`; or
   - amend Ruling 76 and its test under recorded authority.

   The suite is red at the gated head until one is done.
10. **R1 against W1 inter-member schedule (MEDIUM-5).** R1's gated runs omit W1's cooldown-v2 gate and child-process start, so R1 overstates W1's G0 share. Choose between:
    - running R1's gated block through the same cooldown; or
    - recording the measured offset and accepting the conservative bias in G0_cap_W1, 1(f) and the duty bar.
11. **A delta gate after the post-R1 1(e)/1(f) ruling.** R8-8 expects that ruling to change W1's configuration (B_D, T_dead, possibly 4-bit). Does the changed kit need a fresh blind gate before arm? Recommended: yes, scoped to the kit diff, not a full council.

## Findings

### BLOCKER

**BLOCKER-1: protocol v4 cannot be registered for W1, and the arm path never checks registration** (seat 2; seat 1 noted only the row-4 part). I checked it.
- **The protocol:**
  - `docs/align/pilot_protocol_v4.md:3` reads: "DRAFT SKELETON — PROVISIONAL; not registered or authorized to arm."
  - Its ruling table (`:608-637`) marks W1-blocking rows 4, 5, 6, 9, 11, 15, 17, 18 and 20 as still lacking text.
  - Row 22 says this cold gate is still owed.
  - CHAIR 22 (`CHAIR.md:217-221`) requires rulings 2-6, 9-15 and 17 in protocol v4 before W1.
- **The desk still runs the pre-ruling rules:**
  - The U3 bar is still `3*max(2.97, .0011*energy)` (`joulewise/align/apple/thermal_desk.py:307`), so ruling 5 is not re-derived.
  - The protocol U5 row still states the old bar (`pilot_protocol_v4.md:421`), not L2's `|β_T|₉₀ × δ_slow ≤ 1.0·σ_pair`.
  - The deciding contrast still applies "same sign" (`thermal_desk.py:317,342`), with no delivery condition and no stage term (ruling 9).
  - The ruling 6/9/15/18 helpers `contrast_delivery`, `sentinel_admissibility` and `warm_reference_diagnostic` exist in `joulewise/align/apple/v4_estimands.py` (functions starting at lines 172, 236 and 250), but only their own tests reference them.
- **WP19 is missing.** No file in `joulewise/`, `scripts/`, `tests/` or `configs/` mentions WP19. This matters for two reasons:
  - `deciding_experiment` keeps only `pilot7_token_identical` runs (`thermal_desk.py:323`);
  - the v4 X configs changed the warmup from pilot 7's sabotage prompt to the benign prompt. At `45b47f7b6`, b-e25 has `warmup_condition: None, condition: sabotage`, and `workload.py:400` falls back to `condition`. The kit sets `warmup_condition='benign'` (`scripts/align_v4_kit.py:1014`).

  WP19 is the step that verifies the change keeps token identity.
- **No mechanical gate.** `require_w1_ready` (`scripts/align_v4_kit.py:890-898`) checks only inputs, D identity, R1, sizing and WP18. Once R1 lands, `prepare` and `install` would admit W1 against the draft protocol.

### HIGH

**HIGH-1: the CHAIR 4(a) battery arm rule is not implemented** (both seats). I checked it.
- **The rule.** CHAIR 4 (`CHAIR.md:69-81`) says "mechanical for W1": arm within about 30 min of a completed top-up, with `pmset -g batt` ≥ 99 %, IsCharging No and OBC off, and the ioreg block in the arm record.
- **What the code does.** `arm_checks` (`scripts/align_v4_session.py:123-157`) records only the AC powermode and the external volumes, and `_arm_and_install` (`:314-342`) adds the disk gate. Nothing in the arm or night path implements the rule:
  - no `pmset -g batt` read or ioreg read;
  - no OBC check;
  - `battery_float` in `run_night` serves the TRANSACTION_PACK calibration path, not this rule.
- **The protocol** still says "battery ≥95%" (`pilot_protocol_v4.md:698`).
- **Why it matters.** The contrast has exactly two runs per arm, and pilot 10 lost ordinals 8-10 to a top-up (CHAIR 4). One top-up inside the contrast block therefore makes the deciding contrast INCONCLUSIVE.
- **Fix:** see decision 2.

**HIGH-2: the 30B contrast is unprotected** (seat 1 HIGH, seat 2 MEDIUM; I classify it HIGH). The problem has three parts: the G0 cap can exceed the contrast deadman, there is no contrast fit rule, and the kit never consults whether R1's X-G completed.
- **The facts, all reproduced:**
  - Contrast members get the fixed `deadman_s = CONTRAST_DEADMAN_S = (1750 − 516.58)/1.13544 = 1,086.3 s` (`scripts/align_v4_kit.py:701,1034`).
  - Through `thermal_policy` → `gate_policy_fields` they also get the R1 policy's `g0_cap_s` (`:959-976,1035-1036`), which may be anywhere in [600, 1,200] s.
  - The deadman is armed at G0 entry (`joulewise/align/apple/workload.py:429-435`). The G0 loop checks `deadman.expired()` before the cap (`joulewise/align/apple/thermal_gates.py:533-538`). So a contrast cap above 1,086 s is unreachable: such a G0 always ends as an X7 deadman cut, never as an X2 timeout.
  - Under R7-12, an inconclusive X-G sets G0_cap_W1 to 1,200 s for every member (`scripts/align_v4_kit.py:451-454`).
  - Ruling 1(f) protects D only (`:469-524`).
- **The kit never checks that R1's X-G completed.** `x_g.status` is `measured` whenever the schedule reasons are empty (`scripts/align_r1_rehearsal.py:1770-1775`). The kit reads only `status`, `g0_outcome` and `g0_wait_s` (`scripts/align_v4_kit.py:445-459`). The X-G runtime kind records `admitted_turns` and `episode_flags` (`joulewise/align/apple/r1_runtime.py:1905-1921`), but the rehearsal drops both from `r1_slots.x_g`.
- **Correction to seat 1:** the `x7` field that seat 1 cites at `r1_runtime.py:1827-1830` belongs to the gated-D kind, not X-G. The fix therefore has to add the X-G completion fields to `r1_slots.x_g` first.
- **Probes, re-run at `e901eb2a4`** (seat probes copied unchanged except the root path):
  - With an X-G released at 900 s, the kit admits `g0_cap_s = 1125 > 1086.3`.
  - An `x_g` carrying `x7: true, admitted_turns: 3` is admitted.
  - The contrast policy carries `g0_cap_s = 1200` when the cap is 1,200 s.
- **Why HIGH:**
  - Each contrast arm has exactly one run after a D member (ordinals 6, 9, 12 and 15; roster at `scripts/align_v4_kit.py:63-82`) and only two runs per arm, with no retest (`pilot_protocol_v4.md:476-481`). One X7 makes the deciding contrast INCONCLUSIVE after about 2 h of contrast members.
  - R0 re-run 7 physics (LEAD-RULINGS-2:319) puts G0 settling at 840-1,040 s after load end. The R7-2 builder already reported that X-G "can never record a released G0 of 1,200 s" (LEAD-RULINGS-2:364).
- **Seat 2's mitigation is real but temporary.** At realistic 27B decode rates (about 20 tok/s), D's 1(f) refuses any G0_cap_W1 large enough to exceed 1,086 s. Re-running seat 1's probe P1 confirms this: it is refused by 1(f). Seat 2's admitting probe needs a decode rate of 200 tok/s. But R8-8 says the lead rules on the 1(e) fallback after R1, and that ruling is the path that unlocks W1, so the guard disappears at exactly that point. A late release below the cap can also leave too little deadman for 12 turns plus the G1 waits; only R1's X-G completion would show that.
- **Seat 1's wording toned down:** "every arm's D-predecessor run X7s by construction" overstates it. Whether that happens depends on R1's X-G numbers.
- **Stale guard test:** `tests/align/test_v4_w1_synthetic.py:53-60` asserts only `CONTRAST_DEADMAN_S > 600`. That invariant is stale since R7-2.
- **Fix:** see decision 3.

**HIGH-3: a failed duty bar admits W1 on a bare `lead_fallback.step`; steps 2 and 3 cannot be expressed** (seat 1 MEDIUM, seat 2 HIGH; I classify it HIGH).
- **The check.** `check_r1_evidence` accepts any `step in (1, 2, 3)` with a non-empty authority string (`scripts/align_v4_kit.py:176,294-298`). It never checks that the step took effect, and it never re-evaluates the bar.
- **Each step:**
  - Step 1: S6 tuning is checked only when S6 ≠ S5, and the suite admits step 1 with S6 = S5 (`tests/align/test_v4_kit.py:536-537`).
  - Step 2 (450 s idle after D) cannot be expressed. Every stage config carries `sampling.idle_seconds = 300`, `w1_inter_member_idle_s` requires one idle per role (`:306-324`), and the R6-1 schedule binding requires the bar's idle to equal it (`:289-293`).
  - Step 3 (4-bit) cannot be expressed: D is pinned to the 8-bit source, revision and quantization (`:50-53,1019-1021`).
- **Probes, re-run:** steps 1, 2 and 3 are each admitted with S6 = S5 = 1.5, idle {D: 300, X-G: 300} and the 8-bit D. An inconclusive bar plus a step-1 record is also admitted.
- **Why HIGH:** R8-8 records that the 1(e) fallback will be ruled after R1 on its numbers. That makes the fallback the expected path, and two of its three steps are no-ops in this kit. The 1(f) fit is still evaluated on the unchanged config, so it remains a partial backstop.
- **Fix:** see decision 4.

**HIGH-4: the arm-time offload re-hash contradicts ruling 20** (seat 2 only). I checked it.
- **Order inside `_arm_and_install`:**
  1. `arm_checks` runs first (`scripts/align_v4_session.py:316`). Its external-volume census (`:142-143`) refuses any mounted external volume. Network shares and FUSE count as external (`joulewise/align/apple/external_volume.py:183-190`).
  2. `w1_disk_check` runs next (`:340`). It re-hashes every configured offload destination (`joulewise/align/r0_host.py:425-434`), and `inventory` refuses a destination that is not a directory (`r0_host.py:325-327`).
- **Where offloads live.** The runbook puts `disk_path` on the measurement volume, separate from the offload volume (`docs/align/r0_desk_runbook.md:62-65`). If the offload volume is the borrowed external SSD, the two checks cannot both pass.
- **Effect.** W1 arms only with `offloads: []`, which passes vacuously: `all([])` at `r0_host.py:437`. That silently drops a protocol arm gate ("config-labelled offload hash verification are W1 arm gates", `pilot_protocol_v4.md:662-663`).
- **Not verified:** the repo does not say where the W1 offloads will live, so this is conditional on the SSD plan, hence decision 5.
- **Severity:** the failure is fail-closed or a silent gate drop, not a data risk. It is still certain to hit at the arm.

**HIGH-5: protocol WP14(a) describes a different classifier from the one R1 will run** (seat 2 only). I checked it.
- **Protocol** (`pilot_protocol_v4.md:229-230`): die (fast) is `t63 ≤5 s; τc ≤300 s`; heatsink (slow) is `30 s < τc ≤300 s`, chosen by the longest τc.
- **Merged #692 code** (`joulewise/align/apple/smc_enumeration.py:25-37` RULE; `:558-570`):
  - a releasability bar `τ·ln(rise/1 °C) ≤ 300 s`;
  - fast: `τ ≤ 60 s`, noise ≤ 1/3 °C;
  - slow: `60 < τ ≤ 300 s`, noise ≤ 0.15 °C, chosen by the longest band hold;
  - the D2 baseline: last-60 s median and OLS residual SD.
- **D5 is still provisional.** The rule must be chosen from R0 re-run 8 before R1 arms (LEAD-RULINGS-2 "Slow-pick rule before R1 arms").
- **Why it matters:** which sensors gate W1 is science-bearing, so the registered text must match the code. This is part of the BLOCKER-1 doc pass, kept separate here for traceability.

### MEDIUM

**MEDIUM-1: the D seed-law tag must be settled before W1, not at the D-series** (seat 1 HIGH; I classify it MEDIUM).
- **The facts:**
  - W1 D seeds use `D_TAG = 'qwen3.8-27b'` (`scripts/align_v4_kit.py:51,1053`; protocol :158-159).
  - CHAIR 25 (`CHAIR.md:231-236`, "Blocks: D-series") rules that the seed-law tag carries the quantization, and protocol row 25 says that replaces `qwen3.8-27b`.
  - W1 ordinal 5 is the trajectory that the D-series sentinels replay (protocol :139-141), and it feeds E_ref (CHAIR 6) and the ruling-26 token comparison.
- **The consequence:** changing the tag after W1 would give the D-series sentinels different seeds from W1's trajectory.
- **Why MEDIUM and not HIGH:** it cannot corrupt W1 energy data, and the "label only" ruling is a zero-cost way out at any time. It must still be decided before arm, because afterwards only that way remains (decision 6).

**MEDIUM-2: the protocol's "`--max-failures 1` stops the stage" is false for the W1 chain, and an unobserved capture loses the window** (seat 1 MEDIUM; seat 2 LOW-7 is refuted and its LOW-8 is merged here).
- **The chain rewrites the flag.** The HAZARD_PACK path renders the chain through `joulewise/b5/chain.py` (`joulewise/b5/driver.py:63`). That renderer replaces every collection stage's `--max-failures` value with the stage's `expected_count`: 9 for the episodes stages (`chain.py:248-249,515-520`; `configs/campaigns/align_v4/plan_tree.json:956`).
- **A failed stage does not stop the chain.** The chain's only early exits come before member 1 (`chain.py:958,1156,1175,1178`), and collection stages are bare `run_stage` lines (`chain.py:1133-1137,1198-1206`).
- **What that means:**
  - A G0 `ThermalFault` or a custody-integrity refusal fails only its own member.
  - The midpoint reference, episodes-b, the end references and the post-calibration bracket still run. This answers seat 2's open question.
  - Seat 2's LOW-7 ("that stops the stage") is wrong for this path.
- **An `unobserved` member-5 capture:** every later thermal member gets reference None. It waits the 300 s unobserved G0 limit (`thermal_gates.py:537`), then ends before turn 0 (`workload.py:444-445`) as X4. The window then yields anchors only.
- **Dropped:** both seats' "about 12 h" cost estimate. These members end after roughly their intercept plus 300 s; they do not run to the 1,800 s cap.
- **Fix:** correct protocol :304-309. Decision 8 covers the optional early stop.

**MEDIUM-3: D8-1 breaks Ruling 76, and the suite is red at the gated head** (seat 2; seat 1's log shows the same error). I confirmed it.
- **The failing test:** `tests.test_run_night.Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc` errors with `SystemExit: 19` at `e901eb2a4` and passes at `5f817856b`. I ran it in isolation at both commits.
- **Cause:** `_qualification_observe` re-raises `SystemExit` (`scripts/run_night.py:2589-2590`, per D8-1), but Ruling 76's test expects `SystemExit(19)` to be absorbed (`tests/test_run_night.py:7085-7099`).
- **Scope:** only TRANSACTION_PACK S1/S2 (`run_night.py:2594-2599`), not W1's HAZARD_PACK.
- **Other failures are environmental:**
  - Seat 1's NightProbe and CourierReaping failures pass in isolation at the head (18 tests OK, my run).
  - Seat 2 reports that `BindSupervisionProcessTests` fails on the base too. I did not re-check that.
- **Fix:** decision 9.

**MEDIUM-4: ruling 20's in-window rule is missing** (seat 2). I checked it.
- CHAIR 20 requires no external volume mounted "between t0 and the terminal record (`diskutil list external` in the census)".
- The census runs only at install (`scripts/align_v4_session.py:142`). Nothing in `scripts/run_night.py`, `joulewise/b5/`, `joulewise/hazards/` or `scripts/run_campaign.py` references `external_volume` or `diskutil`.
- R1 has an in-night `VolumeWatch` (`scripts/align_r1_rehearsal.py:1456-1482`); W1 does not.
- **Why it matters:** with the SSD in use "by day", a morning mount before the terminal record would put Spotlight and fseventsd I/O inside measured spans.
- **Fix:** mechanical. Add the census to the night's periodic census.

**MEDIUM-5: R1's gated runs do not reproduce W1's inter-member schedule** (seat 2). I checked it.
- **W1:** `run_campaign` runs `campaign_cooldown_before_member` before each physical member (`scripts/run_campaign.py:11105-11114`; body at `:6161`). The W1 plan binds `configs/campaign_policies/quiet_mac_p2_b5.json` (`plan_tree.json:47-48`), with cooldown-v2 `cap_s` 300 and idle admission enabled. Each member then starts a fresh child process.
- **R1:** runs gated members back to back, in process, through `run_benchmark` (`joulewise/align/apple/r1_runtime.py:1264-1278,1445-1453`).
- **The gap:** R6-1 requires "exactly W1's inter-member schedule", and R1 does not provide it.
- **Direction:** conservative. R1's G0 waits overstate W1's, which inflates G0_cap_W1, the 1(f) G0 term and the duty bar's G0 share. A W1 that would fit can be refused.
- **Fix:** decision 10.

**MEDIUM-6: `thermal_policy.sensors.r0_sha256` is checked for format only** (seat 1 MEDIUM, seat 2 LOW; I classify it MEDIUM).
- `joulewise/align/apple/thermal.py:33-34` checks only for 64 hex characters. The value appears in neither `scripts/align_v4_kit.py` nor `scripts/align_r1_rehearsal.py`.
- Re-run probe P4: `r0_sha256 = 'f'*64` is admitted.
- Protocol :251-253 says "WP16 must require both `r0_sha256` and the R1 classification digest". Only the digest is bound.
- **Why MEDIUM:** a wrong pin would sit in every W1 bundle and could not be corrected afterwards. It does not affect energy.
- **Fix:** mechanical. The R1 driver records the R0 record digest it loaded, and `check_r1_evidence` binds to it.

### LOW

1. **The night dead-man skips the High Power restore once the courier has been sent** (seat 2). I checked the code order:
   - `dead_man` returns at `scripts/run_night.py:5039-5043` when `courier.sent` exists, before its restore at `:5145`;
   - `_finish_reporting`, which sends the courier, runs inside `_run_night`, before the closers (`:4398-4404`).

   So after a D8-2 deferred close the host stays at mode 2 until the next session start or admission, which do restore it. That contradicts `docs/align/r1_runtime_contract.md:133`. It matters only under an adopted High Power. Fix: let the dead-man run the restore even when the courier has been sent, or correct the contract.
2. **Ruling 1(f) has no margin and is not a true worst case.**
   - It sums G0, holds, prefill+tool and decode only (`scripts/align_v4_kit.py:519-521`), with no inter-phase overhead (seat 2).
   - `prefill_tool_s` comes from the benign gated runs only, while W1 D sabotage members 11 and 14 carry a +755-token prompt (seat 1).

   The risk is X7, not corrupted data.
3. **I_D is measured on a different boundary from W1's member cap** (seat 2). R1 times an in-process `run_benchmark`; W1's cap applies to a `run_campaign` child. L1's 50 s reserve likely absorbs the difference. Calibrate it by comparing R1's 30B intercept with pilot 3's 516.58 s.
4. **S7 is computed from a single step-d recovery:** `g_turn = min(300, 3 × recovery_s)` (`r1_runtime.py:800`; `pick_s7` at `:873-875`). Protocol :381-382 says "3×R1 p95 recovery". Restate one or the other (seat 2).
5. **`fit_roster`'s docstring says "17 first"** (`scripts/align_v4_kit.py:920`), but the code drops 18 (`:938-940`) (seat 2).
6. **`install` does not re-run `kit.generate(check=True)`;** only `prepare` does (`scripts/align_v4_session.py:46` against `:208`). Drift is caught later by the config-sha checks, but the arm record does not say so (seat 1).
7. **Kit helpers resolve paths from the script's `ROOT`, not the measurement root:**
   - `d_turn_cap_tokens()` at `:515`;
   - `w1_g0_cap(r1_slots)` at `:518`;
   - `w1_inter_member_idle_s()` at `:289`.

   This is harmless when the session runs from the measurement checkout, as it does (seat 1).
8. **The W1 plan validator accepts any `member_s ≤ 1800`** (`scripts/validate_align_v4_w1_plan.py:195-196`). Fill D members' `member_s` with the L1 worst case so `_WindowDeadline` plans honestly. Seat 1's slack arithmetic (14,400 s budget against about 8,400 s worst case) is not verified here (seat 1).
9. **D members inherit `max_turns = 12` from anchor 1** (`scripts/align_v4_kit.py:1008`; confirmed in the generated stage configs). The protocol's D row does not state this, and CHAIR 10 names `max_turns` as a cohort key. Record it (seat 1).

## Resolved, dropped or corrected claims

- **Seat 1 LOW-1 is resolved; no finding.** WP18 `max_turns = 12` is the recorded pilot-7 count, not a leaked default. `scripts/align_v4_wp18_fixtures.py:105-128` derives `max_turns = len(turns)` from the authenticated `align_turns.jsonl` rows and cross-checks it against p7-PILOT's `per_turn_decode_tokens`. Both committed fixtures have 12 turn rows. Seat 2 agrees.
- **Seat 2 LOW-7 is refuted.** A G0 `ThermalFault` does not stop the episodes stage under `--max-failures 1`, because the chain passes `--max-failures 9` (MEDIUM-2).
- **Seat 1 HIGH-1's wording is corrected.** `x7` is not recorded for X-G (it is for gated D), and "X7 by construction" overstates it (HIGH-2).
- **Dropped:**
  - both seats' "about 12 h" cost of an unobserved capture;
  - seat 1's LOW-5 slack figures (unverified, recommendation kept);
  - seat 2's statement that `BindSupervisionProcessTests` also fails at the base (not re-run; it is environmental either way and not a W1 finding).
- **Verified sound by both seats, spot-checked here:**
  - anchors unchanged;
  - roster order including the 1(g) swap;
  - X/Y seeds and replays (12↔10, 13↔9, 15↔7, 16↔6, 17↔5);
  - the dev index-93 member at ordinal 18;
  - capture at member 5, every later thermal member consuming it;
  - the deadman armed once at G0 entry, with an unreleased G0 ending the member before turn 0;
  - High Power admission, lock inheritance, retake-before-restore and the D8-2 deferral;
  - the window deadline;
  - QuietGuard used only on the R0 path.

## Tests and probes run by the synthesis

All runs used `nice -n 19 taskpolicy -b` with `TMPDIR=/private/tmp/jwburn-synthw1/tmp`. Worktrees were created under `jw-wt/` at `e901eb2a4` and `5f817856b` and removed afterwards.

| Check | Head `e901eb2a4` | Base `5f817856b` |
|---|---|---|
| `Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc` | ERROR (`SystemExit: 19`) | OK |
| `CourierReapingTests.test_still_running_delivered_courier_…` + `NightProbeTests` (18 tests) | OK in isolation | not run |
| Seat 1 `probe_kit.py` (P0-P6) | P1 refused by 1(f) at realistic holds; P2 steps 2/3, P3 (x7 X-G) and P4 (`ffff…` r0 pin) ADMITTED; P5 refused; P6 contrast cap 1200 | n/a |
| Seat 2 `probe_fallback.py` | steps 1/2/3 ADMITTED with S6 = S5, idle 300, 8-bit; inconclusive + step 1 ADMITTED | n/a |
| Seat 2 `probe_contrast.py` | ADMITTED `g0_cap_s` 1125 > 1086.3 (at 200 tok/s, zero holds) | n/a |

## Appendix A: seat 1 report (Fable), verbatim

````text
TOP: ["HIGH-1: Contrast members get g0_cap_s = G0_cap_W1 (up to 1,200 s) but a fixed 1,086 s deadman armed at G0 entry; the kit has no contrast fit rule and admits an R1 X-G that was deadman-cut as 'measured' (probes P1b/P3 admitted). Each arm's D-predecessor run can X7 by construction, making the deciding contrast INCONCLUSIVE. scripts/align_v4_kit.py:700-701,1033-1036,445-459; thermal_gates.py:485,527-532; align_r1_rehearsal.py:1770-1775.","HIGH-2: CHAIR 4(a) battery arm rule (>=99 %, not charging, OBC off, ioreg block in the arm record) is absent from scripts/align_v4_session.py arm_checks (:131-156); a mid-window top-up excludes contrast members as in pilot 10.","HIGH-3: D seed-law tag 'qwen3.8-27b' (kit.py:51) vs CHAIR 25 'qwen3.8-27b-8bit' must be ruled before W1: ordinal 5 is the D-series sentinel/E_ref trajectory and cannot be re-seeded after W1.","MEDIUM-1: kit admits a failed duty bar on lead_fallback step 2 or 3 with the 8-bit/300 s configs unchanged (probe P2 admitted); steps 2-3 have no configuration binding (kit.py:176,294-298).","MEDIUM-2: protocol says '--max-failures 1 stops the stage' but the chain rewrites it to expected_count (chain.py:248,515-522); a deadman costs only itself (good) but an unobserved member-5 capture burns the whole window as X4.","MEDIUM-3: thermal_policy.sensors.r0_sha256 is format-checked only, never bound to the R0 record R1 used (probe P4 admitted 'ffff...').","Verified OK: anchors byte-identical to 83e2dac59; roster/seeds/custody roles; L1/1(f)/G0_cap_W1 bindings; run_night High Power admission/lock/close/termination-proof paths; window deadline; deadman arming; QuietGuard is R0-only. 10 of 12 targeted suites passed; run_night and wp18 suites still running at report time."]
OPEN: ["Did R1's X-G run (after D_spam b) complete all 12 pilot-7 turns under its 1,086 s deadman, and what was its G0 wait? The kit does not check this; the lead must before sizing W1's contrast.","Lead ruling needed before W1 arm: does CHAIR 25's quantization-bearing seed tag apply to the D cohort's seed law (then change it now) or only to labelling (then record that W1/D-series keep 'qwen3.8-27b')?","Who implements CHAIR 4(a) (battery arm rule) before the first W1 arm: code in arm_checks, or a recorded manual checklist with the ioreg block attached to staging/v4-arm-NNN.json?","Should the kit refuse lead_fallback steps 2-3 until the kit can represent 450 s post-D idle / a 4-bit D identity?","Confirm WP18 X/Y max_turns = 12 are the recorded pilot-7 counts (both equal the configured ceiling).","tests/test_run_night.py and tests/align/test_v4_wp18_fixtures.py had not finished when the report was forced (logs under /private/tmp/jwburn-fablew1/logs/); the audit worktree /Users/edr/code/CapstoneProject/jw-wt/fable-w1gate still needs 'git worktree remove'."]
# ALIGN v4 W1 pre-arm blind cold gate — Fable seat (2026-11-07)

**Target:** `lane/2026-11-06-v4-r1-integrated @ e901eb2a4` vs `origin/lane/2026-11-05-align-pilot10-benign @ 5f817856b` (merge-base = 5f817856b; 166 files, +29,529/−440). Worktree: `/Users/edr/code/CapstoneProject/jw-wt/fable-w1gate` (detached at e901eb2a4). All path:line cites below are at e901eb2a4 unless a commit is named. Nothing restricted was opened; no Block-5 outcome was inferred; no process outside this audit was touched; nothing was committed or pushed.

**Verdict: DO NOT ARM W1 on this head without three rulings/changes (HIGH-1..3).** Code quality of the arm/night path is high and the heavy failure modes the council worried about (deadman, High Power restore, chain termination proof, window deadline) are implemented and tested. The remaining gaps are mostly *design-to-code* gaps around the 30B contrast and the arm checklist, plus one seed-law decision that cannot be undone after W1.

---

## Findings

### HIGH-1 — The 30B contrast is unprotected: G0_cap_W1 can exceed the fixed 1,086 s contrast deadman, there is no contrast fit rule, and a deadman-cut R1 X-G is admitted as "measured" (a, b, c)

- Contrast members get `deadman_s = CONTRAST_DEADMAN_S = (1750 − 516.58)/1.13544 = 1,086.3 s` (`scripts/align_v4_kit.py:700-701, 1033-1034`) **and** the same thermal policy as D, including `g0_cap_s = G0_cap_W1` up to 1,200 s (`scripts/align_v4_kit.py:964-973, 1035-1036`; probe P6 prints `contrast policy g0_cap_s = 1200`).
- The deadman is armed at G0 entry and the gate loop checks `deadman.expired()` *before* the cap (`joulewise/align/apple/workload.py:429-447`; `joulewise/align/apple/thermal_gates.py:485, 527-532`). So any contrast G0 longer than 1,086 s ends as a deadman-cut `episode.g0_unreleased` (X7 class), never as an X2 at the cap; a cap above 1,086 s is unreachable for contrast members.
- Ruling 1(f) protects only D (`ruling_1f_fit`, `scripts/align_v4_kit.py:469-524`). Nothing checks `G0_cap_W1 + G1 waits + the 12-turn 30B episode ≤ 1,086 s` for X/Y members, and nothing inspects whether R1's own X-G run completed: `x_g.status` is `measured` whenever the schedule reasons are empty (`scripts/align_r1_rehearsal.py:1770-1775`), although the runtime records `x7` and `admitted_turns` for it (`joulewise/align/apple/r1_runtime.py:1827-1830`); the kit reads only `status/g0_outcome/g0_wait_s` (`scripts/align_v4_kit.py:445-459`).
- **Probes (run):** P1b — with a released R1 X-G wait of 900 s and a fitting 1(f), `require_ready` **ADMITS** `g0_cap_s = 1125 > 1086.3`. P3 — an R1 X-G record with `x7: true, admitted_turns: 3` is **ADMITTED**.
- **Why it matters:** by A1 design each contrast arm has exactly one run after a D member (6←5, 9←8, 12←11, 15←14) and only two runs per arm (`scripts/align_v4_kit.py:63-82`). R0 re-run 7 physics (LEAD-RULINGS-2:319) says no key reaches the G0 slope criterion until 840–1,040 s after load end. A D→30B G0 of that length plus any 30B episode exceeds 1,086 s, so the D-predecessor run of **every** arm becomes X7, and the deciding contrast is INCONCLUSIVE by construction ("fewer than two eligible token-identical runs per arm", `docs/align/pilot_protocol_v4.md:480-481`) while still spending ~2.2 h of the window. R1's X-G (after D_spam b, R7-1) is the only measurement of this and the kit does not consult its completion.
- **Fix (kit, fail closed):** require `x_g.x7 is False` and `x_g.admitted_turns == WP18.X.max_turns`; refuse when `g0_cap_w1.value_s + (R1 X-G member wall − its G0 wait) > CONTRAST_DEADMAN_S`, naming the lead; or the lead rules now that a D→30B G0 above the contrast deadman is an accepted X7 and the contrast is pre-declared conditional. `tests/align/test_v4_w1_synthetic.py:53-60` asserts only `CONTRAST_DEADMAN_S > 600` ("a G0 timeout must fit the deadman"), an invariant R7-2 silently broke.

### HIGH-2 — CHAIR ruling 4(a) battery arm rule is not in the arm path (b; blocks W1 per the chair)

- `arm_checks` records only AC powermode and external volumes (`scripts/align_v4_session.py:131-156`); `_arm_and_install` adds the disk gate (`:323-342`). No `pmset -g batt`/`ioreg` read, no ≥ 99 % / not-charging / OBC-off check, no ioreg block in `staging/v4-arm-NNN.json`. Repo-wide grep for `ioreg|IsCharging|top-up` in the arm/night scripts finds nothing; `joulewise/hazards/battery.py` is the in-window exclusion only.
- CHAIR 4(a) (`CHAIR.md:69-81`) is "mechanical for W1"; protocol v4 marks it "Blocks: W1 … not yet installed" (`pilot_protocol_v4.md:613`). A mid-window top-up excludes members (`battery.member_span`), and with two runs per contrast arm one exclusion makes that arm INCONCLUSIVE; pilot 10 lost ordinals 8–10 this way (CHAIR.md:74).
- **Fix:** add a battery arm check to `arm_checks` (read `pmset -g batt` and the `ioreg -rc AppleSmartBattery` block; refuse unless ≥ 99 %, not charging, OBC off; record the block), or the lead records a signed manual checklist item before each arm. Either way the arm record must carry the evidence.

### HIGH-3 — The D seed-law tag must be settled before W1, not in the D-series (c; irreversible after W1)

- W1 D seeds use `D_TAG = 'qwen3.8-27b'` (`scripts/align_v4_kit.py:51, 1053`; protocol `:159`). CHAIR 25 rules the tag carries the quantization (`qwen3.8-27b-8bit`, `CHAIR.md:231-236`), and protocol v4 lists it as a D-series item "replacing `qwen3.8-27b` above" (`pilot_protocol_v4.md:634`).
- W1 ordinal 5's trajectory is the D1–D3 early/late sentinel and part of E_ref (protocol `:139-141`, CHAIR 6/15/26). If the tag changes after W1, D_k sentinels get a different `episode_seed`, are not W1's trajectory, and U4 / the ruling-26 cross-day token comparison lose their reference. R1's D runs use the same kit configs, so R1↔W1 agree; only the D-series is at risk.
- **Fix:** lead rules before the W1 arm either "the tag stays `qwen3.8-27b` for the whole D cohort (ruling 25 applies to labelling only)" or changes the tag now and regenerates the kit (W1 seeds change; `seed_manifest.json` is non-claim).

### MEDIUM-1 — The kit admits a failed duty bar on `lead_fallback.step` 2 or 3 with no configuration change bound to it (b, c)

- `DUTY_FALLBACK_STEPS = (1, 2, 3)` and the check is `step in` + non-empty authority (`scripts/align_v4_kit.py:176, 294-298`). Step 1 is bound through the `s6_tuning` receipt; steps 2 ("idle 300→450 s after D predecessors") and 3 ("4-bit at the same rung") are not bound to anything: D configs hard-code the 8-bit source/pins (`:53, 1019-1021`), every stage config carries `sampling.idle_seconds = 300`, and `w1_inter_member_idle_s` requires one idle per role (`:306-324`), so step 2 cannot even be expressed in this kit. **Probe P2: both steps ADMITTED** with the 8-bit/300 s configs unchanged.
- **Fix:** refuse steps 2–3 until the kit can represent them (fail closed), or bind step 2 to per-member idle evidence and step 3 to a 4-bit identity unit.

### MEDIUM-2 — Protocol text vs chain: `--max-failures 1` does not stop a W1 stage (c; and an unobserved capture burns the whole window)

- `plan_tree.json` stage argv carries `--max-failures 1`, but the chain renderer rewrites it to the stage's `expected_count` (9) (`joulewise/b5/chain.py:248-249, 515-522`), and a non-zero stage rc does not stop the chain (`run_stage`, `chain.py:947-957`; collection block `:1198-1206`). Protocol v4 and WP14(b) say "`--max-failures 1` stops the stage" on a custody-integrity refusal (`pilot_protocol_v4.md:308`; WP14-RULINGS.md:250). Good news: a deadman member (AdapterFailure → `RunStatus.FAILED` → exit 3, `workload.py:792-800`, `cli.py:442`) costs only itself. Bad news: after a failed/absent member-5 capture, members 6–18 each refuse individually (fast, no model load) and an **`unobserved`** capture lets all 13 later members run to X4 for ~12 h with no stop (protocol `:304-306`).
- **Fix:** correct the protocol sentence; consider a chain-level stop on `thermal.window_reference_unobserved`/`_missing` at ordinal 6 (not outcome-dependent).

### MEDIUM-3 — `thermal_policy.sensors.r0_sha256` is format-checked only, never bound to the R0 record R1 ran under (c)

- `joulewise/align/apple/thermal.py:23-36` checks 64-hex; the kit never compares it to anything in `r1_slots` (grep: no `r0_sha256` in `align_v4_kit.py`/`align_r1_rehearsal.py`). **Probe P4: `r0_sha256 = 'ffff…'` ADMITTED.** Protocol WP14(a): "WP16 must require both `r0_sha256` and the R1 classification digest" (`pilot_protocol_v4.md:252-253`). The custody digest keeps it consistent across W1 members, but a wrong pin is registrable.
- **Fix:** have the R1 driver record the R0 record digest it loaded and bind `sensors.r0_sha256` to it in `check_r1_evidence`.

### LOW-1 — WP18 X and Y both carry `max_turns = 12`, the configured ceiling
`registration/inputs.json` WP18 and both fixtures have 12 turns (X output tokens 568…315, Y 533…137). The kit's own text says "never the configured 12-turn ceiling" (`scripts/align_v4_kit.py:126-134`). Consistent with the authenticated fixtures, but the lead should confirm pilot 7 b-e25/b-e18 really ran 12 turns rather than a default having leaked.

### LOW-2 — D members inherit `max_turns = 12` from anchor 1; protocol v4's D row does not state it
`scripts/align_v4_kit.py:1008` (deepcopy of anchor 1), stage configs. CHAIR 10 names `max_turns` as a cohort key; record it in the frozen-commit record and protocol.

### LOW-3 — `install` does not re-run `kit.generate(check=True)`
`prepare` does (`scripts/align_v4_session.py:45`); `install` only `require_w1_ready` (`:214`). Kit drift between prepare and install is caught later by config-sha checks, but the arm record would not say so.

### LOW-4 — Kit helpers read from the script's `ROOT`, not `measurement_root`
`r1_g0_timeout_s`, `d_turn_cap_tokens`, `w1_inter_member_idle_s` (`scripts/align_v4_kit.py:306, 402, 409`) are called without `root` from `check_r1_budget_and_policy`. Harmless when `align_v4_session.py` runs from the measurement checkout (it does).

### LOW-5 — W1 `member_s` semantics and the window deadline
The validator accepts any `member_s ≤ 1800` (`scripts/validate_align_v4_w1_plan.py:197-199`). If the magistrate fills typical R1 durations, deadman-bound D members can overrun the programmed span; the 7,200 + 7,200 s budgets (≈ 14,400 s slack) cover the plausible worst case (~8,400 s), so `_WindowDeadline` (`scripts/run_night.py:1157-1171`) should not cut ordinals 17/18. Recommend filling D `member_s` with the L1 worst case anyway.

### LOW-6 — 1(f) prefill term comes from benign runs only
`prefill_tool_s = max(prefill + tool)` over the three benign gated runs (`scripts/align_v4_kit.py:519-520`); W1 D sabotage members (11, 14) carry a +755-token prompt. Small, but the term is not a true worst case.

---

## Checked and found consistent (no finding)

- **Anchors** byte-identical to `83e2dac59` (sha256 compared for e01–e04); keep `max_episode_seconds: 120`, no D fields.
- **Roster/tags/seeds:** 18-member order incl. 1(g) swap; X seed 7655467588542005630, Y 8158640411307706161 match protocol; replay 17→5; dev 93 at 18; `warmup_condition='benign'` on all D/contrast; D heavy/per_turn; contrast per_turn only for G arms; `hybrid_checkpoint_limit=0`; `max_episode_seconds` popped.
- **Window reference:** member 5 captures, 6–18 consume bound to e05 run_id + bundle-config digest (`check_window_reference_roles`); custody loader verifies schema/canonical bytes/config digest/journal recomputation (`thermal_gates.py:137-205`).
- **Kit bindings:** L1 T_dead + member fit; B_D only lowered; S5/S6/S7/N_chunk/S5_fast bindings; changed-pick R9-2 re-derivation; alias refusals; classification digest; G0_cap_W1 re-derivation (R7-2/R7-12) and 1(f) G0 term — probe P5 confirms a 1,200 s cap with T_dead ≈ 1,013 s is refused by 1(f) for D.
- **run_night (HAZARD_PACK path):** powermode admission with marker restore under the host lock; plan-2 lock inheritance via `pass_fds`; close restores only after retake and only when termination is proven (D8-2 flag, `run_night.py:4175-4216`); malformed/rerun/launch_abandoned/pre-admission restores; window deadline computed once from the driver clock for both paths (`:1157-1171`); census abort and supervision stop terminate the group and prove it; interrupt path (R8-1).
- **Deadman:** armed at G0 entry (no extra G0 allowance); G0 that did not release ends the member before turn 0; `episode.deadman` is the primary stop; deadman members are failed executions with salvaged custody.
- **Session installer:** holds the host lock; R7-6 launchd census before High Power; TERM/HUP handlers; terminal-session refusal; external-volume census pinned `off`; disk gate (≥ 80 GB, offload re-hash).
- **QuietGuard (r0_host.py:66-330):** R0-only (`r0_runner.py:285`); not on the W1 arm/night path. Fails closed on armed night agents, loaded LaunchAgent, chains/powermetrics in the process table, cumulative-CPU contaminants; latches its first refusal. No defect affecting W1.
- **`--instrument-power-policy ac_high_power`** is the instrument/arm-readiness policy label (AC, external connected, low-power off; `controller.py:1131-1153`), not `pmset powermode 2`; no conflict with series Automatic.

## Tests run (nice 19, taskpolicy -b, TMPDIR under /private/tmp/jwburn-fablew1, one module per process, python3.13, unittest)

`test_v4_kit` OK · `test_v4_w1_plan` OK · `test_v4_w1_synthetic` OK (14 skipped: full WP22 run needs `JW_WP22_FULL=1`, which another seat was already running) · `test_v4_prequal` OK · `test_v4_powermode_record` OK · `test_thermal_gate` OK · `test_r1_round7_science` OK · `test_protocol_v4_doc` OK · `test_r1_round8` OK (real signals) · `test_r1_round7_power` OK · `tests/test_run_night.py` and `test_v4_wp18_fixtures` were still running when this report was forced (logs: `/private/tmp/jwburn-fablew1/logs/`). Probe scripts: `/private/tmp/jwburn-fablew1/probe/probe_kit.py`, `probe_p1b.py` (results quoted above).

## Housekeeping
The audit worktree `/Users/edr/code/CapstoneProject/jw-wt/fable-w1gate` was still present when the report was forced; remove with `git -C /Users/edr/code/CapstoneProject/jw-wt/handoff worktree remove --force /Users/edr/code/CapstoneProject/jw-wt/fable-w1gate`. No files were created in the home directory.
````

## Appendix B: seat 2 report (Opus), verbatim

````text
TOP: ["BLOCKER (c): pilot_protocol_v4.md:3 says it is a DRAFT that is not authorized to arm. Its table (:613-631) lists W1-blocking CHAIR rulings 4, 5, 6, 9, 11, 15, 17, 18 and 20 as not installed. The desk still has the old U3 bar (thermal_desk.py:307) and the 'same sign' contrast rule with no delivery or stage term (:317,342). The v4_estimands helpers are never called. WP19 does not exist, although deciding_experiment keeps only pilot-7-token-identical runs (:323). require_w1_ready (align_v4_kit.py:890) checks no registration or cold-gate receipt.","HIGH (b): a failed or inconclusive duty bar admits W1 on a bare lead_fallback.step 1/2/3 with any authority string (align_v4_kit.py:176,294-298). Nothing checks that the step was applied. Step 2 cannot be expressed (one idle per role, :306-322, :291), and neither can step 3 (D_SOURCE pinned 8-bit, :53). The probe admitted all three steps with S6=S5, idle 300 s and 8-bit D.","HIGH (b/c): the W1 offload gate and ruling 20 contradict each other. arm_checks refuses any mounted external or network volume (align_v4_session.py:142-143,316) before w1_disk_gate re-hashes the offload destinations (:340; r0_host.py:432-434). Those destinations are on the separate offload volume (runbook :63-65), and an unmounted one fails (probe). W1 can arm only with offloads: [], which drops a protocol arm gate (protocol :662-663).","HIGH (c): CHAIR ruling 4(a)'s battery arm rule (≥99 %, not charging, Optimized Battery Charging off, within about 30 min of a top-up, ioreg block in the arm record) is not implemented. arm_checks (align_v4_session.py:123-160) has no battery check, and protocol :698 still says battery ≥95%.","HIGH (c): protocol v4's WP14(a) class rules (:229-230) describe the old classifier. The merged PR #692 D1-D6 classifier R1 will run is different: it has a releasability bar, fast τ≤60 s, slow 60<τ≤300 s with noise ≤0.15, the slow pick by longest band hold, and the D2 baseline (smc_enumeration.py:25-37,558-570). The D5 slow rule is still provisional.","MEDIUM (b): contrast members inherit G0_cap_W1 (600-1,200 s; align_v4_kit.py:1035) but keep a fixed 1,086.3 s deadman armed at G0 entry (:700-701), and no contrast fit is checked. Above 1,086 s a contrast G0 can never time out (X2) and always ends as a deadman cut (X7); late releases also run out of deadman. The probe admitted a 1,125 s cap, and the WP22 F1 guard test (>600) is stale.","MEDIUM (c): a deterministic regression at the gated head. tests/test_run_night.py:7085 (Ruling 76: observer faults including SystemExit never change the chain rc) passes at 5f817856b and errors at e901eb2a4, because D8-1 re-raises SystemExit (run_night.py:2589). This is a TRANSACTION_PACK-only path, but the lead's D8-1 disposition and Ruling 76 conflict.","MEDIUM: ruling 20's in-window part (an external-volume census from t0 to the terminal record) is missing. Separately, R1 runs its gated runs in-process back to back without run_campaign's cooldown-v2 and process start (r1_runtime.py:1264-1278; run_campaign.py:11106). That breaks R6-1's 'exactly W1's schedule' and makes G0_cap_W1 and 1(f) pessimistic."]
OPEN: ["Where will W1's configured offload destinations live? If they are on the external SSD, how are ruling 20 (nothing mounted at arm) and the arm-time offload re-hash meant to be reconciled? One option is a daytime verification receipt with a freshness bound.","If a W1 episodes campaign_collection stage stops at --max-failures 1 (for example a ThermalFault at G0 or a window-reference refusal), does the HAZARD_PACK chain still run the midpoint reference, episodes-b, the end references and the post-calibration bracket, or does the whole window end with no closing bracket?","R8-8 expects the lead to rule on 1(e)/1(f) after R1, and that ruling will change W1's configuration (B_D, T_dead, possibly 4-bit, which the kit cannot express). Does that ruling require a fresh blind gate of the changed kit? This gate assumed it does.","Should a failed or inconclusive duty bar require an R1 re-run, as R7-3 does for inconclusive calibration segments, instead of a recorded fallback step?","Is a U5 FAIL at R1 meant to admit W1? check_r1_evidence accepts pass, fail or inconclusive.","Is G0_cap_W1 meant to apply to the 30B contrast members too? The kit and the R7-12 integration note say yes; protocol :365, 'Every other G0 keeps 600 s', can be read otherwise. If yes, what contrast-side fit against CONTRAST_DEADMAN_S is intended?","Who owns WP19, and when? The question is whether the v4 X configs' benign warmup (pilot 7 used the sabotage system prompt) and the new 1 Hz sidecar keep pilot-7 token identity, which the deciding experiment requires.","How large is the measurement-boundary offset between R1's in-process I_D and the W1 run_campaign child wall? R1's 30B step intercept compared with pilot 3's child-measured 516.58 s would show it."]
# ALIGN v4 W1 pre-arm blind cold gate: Opus seat

**Head audited:** `lane/2026-11-06-v4-r1-integrated` at `e901eb2a4`. **Base:** `origin/lane/2026-11-05-align-pilot10-benign` at `5f817856b` (the merge base). **Date:** 2026-11-07.
**Blindness:** I used only the code and the in-scope documents: `pilot_protocol_v4.md`, `CHAIR.md`, `LEAD-RULINGS-1.md` and `LEAD-RULINGS-2.md`. I did not open the earlier review papers (`docs/align/reviews/*`, `fable-cold.md`, `opus-*.md`, the run reports). I opened no restricted path, no `~/jw-b5-*` or `~/night-*` path, and no custody or archive. Nothing on the measurement Mac was touched.
**Citations:** every `path:line` below is at `e901eb2a4` unless it says otherwise.

## Verdict

**Do not arm W1.**

The code currently fails closed by itself: `scripts/align_v4_kit.py --check` refuses because R0 and R1 inputs are still pending (`registration/inputs.json` R0/R1 are null, and `r1_slots.json` source is `PENDING_R1_REHEARSAL`).

Even after R1 fills the slots, this gate finds:
- **1 BLOCKER**: protocol v4 cannot be registered, and nothing in the code ties the arm to registration;
- **4 HIGH**:
  - the duty-bar fallback admits W1 on a bare record;
  - the offload gate and ruling 20 contradict each other;
  - the battery rule is missing;
  - the protocol's classifier text is stale;
- **4 MEDIUM** and **8 LOW** findings.

Several W1 safety properties hold up well (listed at the end).

## Method and tests

I read the kit, the W1 template and validator, the v4 session (prepare and install), the `run_night` admission, High Power, lock, close and dead-man paths, `thermal_gates.wait`, the `workload` G0 and deadman wiring, the endpoint hold path, `r1_runtime`'s slot derivation, `r0_host.QuietGuard` and the `w1_disk_gate`, and `run_campaign`'s failure and cap rules. I checked claims with tests and three probes.

Every run used `nice -n 19 taskpolicy -b`, `TMPDIR=/private/tmp/jwburn-opusw1`, one module per process, and no model weights.

| Run | Result |
|---|---|
| `tests.align.test_v4_kit` | 116 OK |
| `tests.align.test_v4_w1_plan` | 12 OK |
| `tests.align.test_v4_w1_synthetic` (quick) | 18 run, 14 skipped |
| Same module with `JW_WP22_FULL=1` | 18 OK, 1 expected failure (WP22 F3) |
| `tests.align.test_thermal_gate` | 44 OK |
| `tests.align.test_r1_round8` | 21 OK |
| `tests.align.test_r1_round8_exec_review` | 7 OK |
| `tests.align.test_r1_round7_power` | 29 OK |
| `tests.align.test_v4_powermode_record` | 9 OK |
| `test_r0_host`, `test_v4_estimands`, `test_protocol_v4_doc`, `test_window_reference_custody`, `test_external_volume` | all OK |
| `tests.test_run_night` (318 tests) | 9 F, 3 E (breakdown below) |
| Kit generated into a scratch root | no drift over 30 files; the template matches `--regenerate-template` |

**`tests.test_run_night` breakdown:**
- `BindSupervisionProcessTests` also fails in isolation on the base (15 F, 2 E). These are 8 s watchdogs under background QoS, so it is the environment.
- `NightProbeTests` passes in isolation on both base and head.
- **One deterministic regression:** `Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc`. It passes 5/5 on the base and errors on the head with `SystemExit: 19`. See MEDIUM-2.

## Findings

### BLOCKER-1: protocol v4 cannot be registered for W1, and nothing in the code ties the arm to registration (c)

**The protocol says it is not ready:**
- `docs/align/pilot_protocol_v4.md:3`: "DRAFT SKELETON — PROVISIONAL; not registered or authorized to arm."
- Its own table still lists W1-blocking chair rulings as not installed: rows 4, 5, 6, 9, 11, 15, 17, 18 and 20 (`:613-629`). Row 22 says this cold gate is "still owed" (`:631`).
- CHAIR ruling 22 requires rulings 2-6, 9-15 and 17 to be in protocol v4 before W1.

**Code confirms the gaps:**
- U3 still uses `3*max(2.97, .0011*E)` (`joulewise/align/apple/thermal_desk.py:307`). Ruling 5 is not re-derived.
- The contrast rule still says "same sign" (`thermal_desk.py:317,342`). It has no delivery condition and no stage term (ruling 9).
- The ruling 6/9/15/18 helpers exist in `joulewise/align/apple/v4_estimands.py` (`contrast_delivery`, `sentinel_admissibility`, `warm_reference_diagnostic`), but nothing calls them.
- WP19 has no implementation anywhere. Its job is to verify that the warmup and sidecar changes keep pilot-7 cache and RNG identity, and to render Y's ids (`pilot_protocol_v4.md:131,695`).
- WP19 matters because `deciding_experiment` keeps only `pilot7_token_identical` runs (`thermal_desk.py:323`). The v4 X configs also changed the warmup from pilot 7's sabotage prompt to the benign one (`workload.py:400`; X configs `warmup_condition: benign` against `None` at `45b47f7b6`).

**No mechanical gate:** `require_w1_ready` (`scripts/align_v4_kit.py:890`) checks inputs, R1, sizing and WP18 only. Once R1 and WP23 land, `prepare` and `install` would admit W1 against the draft protocol. Arm authority rests entirely on process.

**Remedy:**
- Install the W1-blocking rulings in the protocol and the desk, and finish WP19.
- Bind a registration receipt into the kit: the protocol commit, both cold-gate verdicts and the ruling-table state. `require_w1_ready` should refuse without it.

### HIGH-1: a failed or inconclusive duty bar admits W1 on a bare `lead_fallback.step` that is never checked (b)

**The check:** `check_r1_evidence` (`align_v4_kit.py:294-298`) accepts any `step in (1,2,3)` (`:176`) with a non-empty authority string. It never checks that the step was applied, and never re-evaluates the bar after it.
- **Step 1:** S6 tuning is enforced only when S6 differs from S5. The test suite itself admits step 1 with S6 equal to S5 (`tests/align/test_v4_kit.py:536-537`).
- **Step 2** (450 s idle after D) cannot be expressed. `w1_inter_member_idle_s` requires one idle value per role across D and X-G (`:306-322`), and the R6-1 schedule binding requires the duty bar's idle to equal it (`:291`).
- **Step 3** (4-bit) cannot be expressed either: `D_SOURCE` is pinned to the 8-bit model (`:53`).

**Probe** (`/private/tmp/jwburn-opusw1/probes/probe_fallback.py`):
- Steps 1, 2 and 3 are each ADMITTED with S6 = S5 = 1.5, idle {D: 300, X-G: 300} and the 8-bit D.
- An inconclusive duty bar plus a step-1 record is also ADMITTED.

**Effect:** CHAIR 1(e) says "if still failing" after each step. A wrong or premature record arms W1 in the very configuration that failed the bar.

**Remedy:**
- Verify the step is in effect: step 1 needs S6 ≠ S5 with a receipt; steps 2 and 3 should refuse until the kit can express them.
- Require a re-measured bar, or treat an inconclusive bar like `inconclusive_segments`: an R1 re-run.

### HIGH-2: the W1 offload re-hash and ruling 20 cannot both pass at arm (b)/(c)

**Order in `_arm_and_install`:**
1. `arm_checks` runs first (`scripts/align_v4_session.py:316`). Its external-volume census (`:142-143`) refuses any mounted external volume, network shares included (`joulewise/align/apple/external_volume.py:186`).
2. `w1_disk_check` runs next (`:340`). `w1_disk_gate` re-hashes each configured offload destination (`joulewise/align/r0_host.py:432-434`), and `inventory` refuses a directory that does not exist (`:326`).

The runbook puts the offload on a separate volume ("`disk_path` must be on the measurement volume, not the offload volume", `docs/align/r0_desk_runbook.md:63-65`). The E1 plan and the borrowed SSD make that volume external.

**Probe:** with the destination on an unmounted volume, `w1_disk_gate` returns `fail` with "not a materialized unrestricted directory".

**Effect:** W1 can arm only with `offloads: []`. That silently drops a protocol arm gate ("config-labelled offload hash verification are W1 arm gates", `pilot_protocol_v4.md:662-663`), or else the arm is impossible.

**Remedy:** verify offloads by day, before unmounting, as a dated receipt the arm checks (path, digest, freshness). Or get a ruling.

### HIGH-3: CHAIR ruling 4(a)'s battery arm rule is not implemented (c)

CHAIR ruling 4 marks this "Blocks: W1" and "mechanical for W1". The rule: arm only within about 30 min of a completed top-up, with ≥ 99 %, not charging and Optimized Battery Charging off, and the ioreg block in the arm record.
- `arm_checks` (`align_v4_session.py:123-160`) records only powermode and volumes.
- Nothing in the arm path reads `pmset -g batt`, `ioreg` or OBC.
- The protocol still says "battery ≥95%" (`pilot_protocol_v4.md:698`), and row 4 is open (`:613`).

The contrast has exactly two runs per arm, and pilot 10 lost ordinals 8-10 to a top-up. A mid-window top-up therefore makes the contrast INCONCLUSIVE.

**Remedy:** add a battery block to `arm_checks` that refuses outside the rule. `battery_float.IOREG_BATTERY_ARGV` and its parser exist.

### HIGH-4: protocol v4's WP14(a) classifier text is not the classifier R1 will run (c)

**Protocol** (`pilot_protocol_v4.md:229-230`):
- die: t63 ≤ 5 s and τc ≤ 300 s;
- heatsink: 30 s < τc ≤ 300 s, chosen by the longest τc.

**Merged PR #692 D1-D6 code** (`joulewise/align/apple/smc_enumeration.py:25-37,558-570`):
- D1 rejections and heat ordering;
- a releasability bar τ·ln(rise/1 °C) ≤ 300 s;
- fast: τ ≤ 60 s with noise ≤ 1/3;
- slow: 60 < τ ≤ 300 with noise ≤ 0.15, chosen by the **longest band hold**;
- the D2 baseline: last-60 s median and OLS residual SD.

The protocol never mentions #692. The slow rule (D5) is still provisional ("Slow-pick rule before R1 arms", LEAD-RULINGS-2 §R9). Which sensor gates W1 is science-bearing, so the registered text would be false.

**Remedy:** restate WP14(a) from #692's DECISION and the chosen D5 rule before registration.

### MEDIUM-1: contrast members inherit G0_cap_W1 but keep a fixed 1,086 s deadman, with no fit check (b)

**The mismatch:**
- The kit gives the contrast members the R1 thermal policy, `g0_cap_s` included (`align_v4_kit.py:1035-1036`; "one cap for every W1 G0", LEAD-RULINGS-2 R7-12 note).
- They keep `CONTRAST_DEADMAN_S` = 1,086.3 s (`:700-701`), armed at G0 entry (`workload.py:429-435`).
- The cap can be anywhere in [600, 1,200] s (`thermal_gates.py:485`).
- The kit checks a 1(f) analogue for D only.

**Consequences:**
- Above 1,086 s a contrast G0 can never time out (X2); it always ends as a deadman cut (X7). This reopens WP22 F1.
- A late release well below the cap still leaves too little deadman for 12 turns plus 11 G1 waits, so the run becomes X7.
- The guard test `CONTRAST_DEADMAN_S > 600` is stale (`tests/align/test_v4_w1_synthetic.py:60`).

**Probe** (`probe_contrast.py`): with `x_g` wait 900 s, the kit admits `g0_cap_s` 1,125, which is above the 1,086.3 s deadman.

**Mitigation today:** at the expected ~20 tok/s, D's 1(f) refuses first (R8-8). The issue goes live once the lead rules on 1(e) or 1(f).

**Remedy:** add a contrast fit (`G0_cap_W1 + R1 X-G G1 + episode ≤ CONTRAST_DEADMAN_S`), or give the contrast its own cap. Clarify protocol `:365`, "Every other G0 keeps 600 s".

### MEDIUM-2: D8-1 breaks Ruling 76; the suite is red at the gated head (c)

`_qualification_observe` now re-raises `SystemExit` (`scripts/run_night.py:2589`). Ruling 76's test expects observer faults, `SystemExit(19)` included, never to change the chain's result (`tests/test_run_night.py:7085-7099`). It passes at `5f817856b` and errors at `e901eb2a4`.

The affected paths are TRANSACTION_PACK S1/S2 only (`run_night.py:2594-2599`), not W1's HAZARD_PACK. The lead's D8-1 disposition and Ruling 76 conflict.

**Remedy:** re-raise only `KeyboardInterrupt`, or amend Ruling 76 and its test under recorded authority.

### MEDIUM-3: ruling 20's in-window rule is missing (c)/(a)

There is no external-volume census from t0 to the terminal record. The census runs only at install (`align_v4_session.py:142`). Nothing in `run_night`, the chain or `run_campaign` re-checks it, and protocol row 20 is open (`pilot_protocol_v4.md:629`).

A mount during a 12.4 h window (the borrowed SSD by day) triggers Spotlight and fseventsd I/O inside measured spans.

**Remedy:** add `diskutil list external` to the night's periodic census, as the ruling text says.

### MEDIUM-4: R1's duty bar and G0 waits do not reproduce W1's inter-member schedule (b)/(c)

LEAD-RULINGS-2 R6-1 requires "exactly W1's inter-member schedule".
- **W1:** `run_campaign` runs `campaign_cooldown_before_member` before each member (`scripts/run_campaign.py:11106`; policy `cooldown.cap_s` 300 in `configs/campaign_policies/quiet_mac_p2_b5.json`), then starts a fresh child process.
- **R1:** runs gated members as back-to-back in-process `run_benchmark` calls (`joulewise/align/apple/r1_runtime.py:1264-1278,1445-1453`).

R1's G0 waits are therefore pessimistic. That inflates G0_cap_W1 and 1(f), which can refuse a W1 that would pass.

**Remedy:** run R1's gated block through the same cooldown, or record the measured difference and rule on it.

### LOW

1. **1(f) omits inter-phase overhead and has no margin.** `episode_phases` sums only G0, G1, H, prefill, decode and tool (`r1_runtime.py:673-696`; `align_v4_kit.py:519`). The risk is X7, not corrupted data.
2. **I_D is measured on a different boundary from W1's member cap.** R1 times an in-process `run_benchmark` (`r1_runtime.py:1449-1453,782`). W1's cap applies to a `run_campaign` child, which adds interpreter start, imports and exit (`run_campaign.py:3776`). L1's 50 s reserve absorbs the difference. The cap is also extended by up to `WAIT_CAP_S` 1,500 s (`:11214`; `joulewise/b6/idle_wait.py:10`), so a kill and stage stop is unlikely. Calibrate by comparing R1's 30B intercept with pilot 3's child-boundary 516.58 s.
3. **The dead-man does not restore after a sent courier.** `dead_man` returns at `run_night.py:5040-5043` when `courier.sent` exists, before its restore at `:5145`. On a deferred close (D8-2) the courier is normally sent, so under High Power the host stays at mode 2 until the next session start or admission. The contract (`docs/align/r1_runtime_contract.md:133`) says the dead-man covers this case.
4. **`sensors.r0_sha256` is format-checked only** (`joulewise/align/apple/thermal.py:35-36`). It is bound to no R0 record, although protocol `:251-253` says WP16 must require both it and the classification digest.
5. **S7 = min(300, 3 × one step-d recovery)** (`r1_runtime.py:800`). Protocol `:382` says "3×R1 p95 recovery".
6. **`fit_roster` docstring says "17 first"** (`align_v4_kit.py:920`); the code drops 18 (`:938`).
7. **A G0 `ThermalFault` stops the stage.** A collector death or status-source gap fails the member (`workload.py` G0 try block, accepted divergence WP22 F3). With `--max-failures 1` (episodes stages in `plan_tree.json`; `run_campaign.py:11373`) that stops the stage. Whether the downstream references and post-calibration still run is unverified.
8. **An unobserved capture at member 5 wastes the night.** Every later thermal member waits 300 s at G0 and then ends (`thermal_gates.py:537`; `workload.py:444`), so the night runs about 12 h for anchors only. This follows the protocol but is costly; an early abort would save the night.

**`QuietGuard`** (`r0_host.py:66-298`, as merged) is R0-only, and no W1 path uses it. I found no defect. It refuses while any `com.joulewise.night*` agent is installed, which is correct.

## What holds up well

- **Kit:**
  - fails closed now;
  - generates deterministically;
  - the template is in sync;
  - roster, seeds and replays (12↔10, 13↔9, 15↔7, 16↔6, 17↔5) match protocol `:101-118`;
  - WP18 max_turns of 12 is the recorded pilot-7 count.
- **Re-derivations:** L1 T_dead, the member fit, G0_cap_W1 (censoring, the X-G fallback) and 1(f) (minimum decode rate, full turn cap) are all re-derived and bound field by field.
- **Thermal policy:** consume roles bound to member 5, a classification-digest binding, and alias refusal.
- **G0/deadman wiring:** one deadman from G0 entry, never re-armed. An unreleased G0 ends the member before its first turn, with bundles kept strict-valid.
- **Powermode:** the admission parses only the AC block and retries once. Plan-2 lock, pass_fds, retake-before-restore and the R8-1/D8-2 deferral all pass their real-signal tests.

## Probes and logs

All under `/private/tmp/jwburn-opusw1/`:
- `probes/probe_fallback.py`
- `probes/probe_contrast.py`
- `run_night.log`
- `wp22_full.log`

The worktrees `/Users/edr/code/CapstoneProject/jw-wt/opus-w1-gate` and `/Users/edr/code/CapstoneProject/jw-wt/opus-w1-gate-base` were removed.
````
