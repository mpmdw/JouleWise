# Seat: opus-stats

## Bottom line

The v4 design is coherent and unusually well pre-registered for an exploratory series, and it CAN answer a narrow form of the mission question for Qwen3.8-27B: does omitting a turn's reasoning tokens show up as excess GPU energy against the frozen sequence design, under a held thermal state, with per-pair held-out benign thresholds. It CANNOT yet answer the paper-grade question. Three things stand between it and a defensible paper: (1) an unmodeled operational risk that return-to-reference holds plus G1 waits consume the ~1,086 s deadman and leave D with 1-2 turns per episode and mass X2/X7 exclusions (thermal_gates.md: "G0, G1 and H all consume it"), which R1's two gated D runs cannot size and the escalation ladder makes worse; (2) by construction no FPR, no power, no test cohort (sample-maximum thresholds at m=21, 3 sabotage per pair, Q6 default no), so the central claim is a calibration-set description; (3) the tamper estimand was defined for a template that drops reasoning from history and is not re-specified for Qwen3.8's preserve_thinking history, where omitted reasoning also lives in every later turn's prompt. Add the pilot-10 battery top-up confounder, which has no v4 rule and is near-certain in 58,260 s D windows. Fix order: pre-declare a hold/gate duty bar with a named fallback before R1 freezes slots; decide registration grade now; re-specify the tamper estimand in protocol v4; add a battery rule. None of this blocks R0.

## Expected MDE

Guesses until R1 gives e_D and D1 gives s_r. Reference (30B, v3, sequence design): e ≈ 0.62 J/decode token; per-pair s_r 19-58 J (pilots 8-9) → s_r/e ≈ 30-95 tokens; score thresholds 2.53 (bank) / 7.13 (spam) → minimum detectable H of order 100-700 reasoning tokens; every untampered-sabotage trajectory crossed at the first grid point tried (the first turn's full reasoning, 539-1,193 tokens). For D (27B dense 8-bit): e ≈ 40 W / 11 tok/s ≈ 3.5 J/token; an episode is 15-45 kJ (2-3 turns × ~15 kJ). If s_r scales with episode energy as the U6 bar assumes (~0.4 %), s_r ≈ 60-180 J → s_r/e ≈ 20-50 tokens → minimum detectable H ≈ 50-350 tokens, i.e. roughly 2-15 % of one xhigh turn's reasoning (median ≤ 2,048 by the R0 ladder bar). Practical floor is the tamper grid's smallest point (H = 128) because with 2-3 turns per episode there are few sub-turn omission sizes to test. If the clock-correlated residual structure persists on D without gates removing it, expect s_r inflated 3-5× and the floor to move to ~500-1,500 tokens (a whole turn's reasoning), which is detectable but trivially so.

## Issues

### [CRITICAL] D's wall-time budget under return-to-reference holds + G1 + deadman is unmodeled; plausible arithmetic gives 1-2 turns per episode and mass X2/X7 exclusions
- owner: lead ruling; blocks: R1
- evidence: thermal_gates.md (assembled lane): 'The deadline is the earlier of episode-start + T_dead and G0-entry + T_dead; G0, G1 and H all consume it.' FINAL-DESIGN §2.2: T_dead = (1,750 − I_m)/1.13544 ≈ 1,086 s. §1(c): a 4,096-token D turn ≈ 370 s at 11 tok/s. §2.6: G1 and H release only when S_fast and S_slow are both within δ = max(1.0 °C, 3 SD) of the episode's G0 release for 5 consecutive samples; heatsink class has τc 30-300 s, so one recovery ≈ τ·ln(ΔT/δ) ≈ 1.8 τ, i.e. up to ~300 s = G_turn cap. Amendment 1 A3.1: N_chunk = 2,048 if no decline, else 256·⌊0.6·t_decline·r/256⌋ (e.g. t_decline 150 s → 768 tokens → 5 holds per turn). Turn 0 (372 s) + one hold (~200-300 s) + G1 (~200-300 s) + turn 1 (372 s) ≈ 1,150-1,350 s > T_dead. Only S6 (raise δ_slow until median G1 wait ≤ 90 s, tuned on R1's two D runs) addresses this; the 1,800 s member law and B_D floor 6,144 assume near-zero gate time. Pilot 4: even the 120 s guard stopped 8/12 bank trajectories on the 30B.
- recommendation: Before R1 freezes slots, add to protocol v4 a pre-declared hold/gate duty bar measured on R1's D runs (e.g. gate+hold wall time ≤ decode wall time, and ≥ 4 admitted turns in both gated D runs) with a NAMED fallback decided now: (a) hold release on a looser δ_hold than δ_G1, (b) fixed-duration holds (recorded, not referenced), or (c) G0+G1 without holds accepting X1 as the only thermal exclusion. Make the R1 slots file print T_dead consumption per phase and the predicted turns-per-episode. Raise R1 to ≥ 3 gated D runs including one bank/benign (the long-prefill pair).

### [CRITICAL] Paper cannot state FPR, power, or a test-set result: sample-maximum thresholds at m=21, 3 sabotage per pair, no locked test cohort
- owner: needs Ed; blocks: paper
- evidence: FINAL-DESIGN V12 and §2.7: rank ⌈0.95(m+1)⌉ is the sample maximum at m = 20-21; 'There is no FPR or power claim.' Amendment 1 A2: yield 21 held-out benign and 3 held-out sabotage per pair after D1-D3; registration grade (m ≥ 39 + locked test cohort) only on Ed's go, Q6 default NO. Item 175: at m=28 on the 30B the spam threshold still rests on one trajectory (7.13 vs next 2.99), i.e. sample-max thresholds are a single-point statistic. The mission question ('untampered sabotage below threshold, all tampers detected') with n=3 sabotage per pair has no inferential content on the untampered-sabotage false-alarm rate.
- recommendation: Decide Q6 now, before D1's desk is read: either commit D4-D6 (registration grade, m ≥ 39 + locked test cohort, ~+3 windows) or re-scope the paper's claim to 'calibration-set description with a pre-registered FPR estimator' and pre-register that estimator (expected FPR 1/(m+1) for a sample-max threshold, with its binomial interval) and a minimum sabotage count per pair (≥ 6) for any sabotage statement.

### [HIGH] The tamper estimand is template-dependent and not re-specified for Qwen3.8's preserve_thinking history
- owner: lead ruling; blocks: D-series
- evidence: pilot_protocol_v3.md l.155-163: the estimand 'holds measured joules and context/prefill fixed and strips the logged reasoning count from the first k residual rows'. That matches the Qwen3 (30B) template, which drops earlier reasoning from history. FINAL-DESIGN V5 and B2: Qwen3.8 renders prior reasoning via reasoning_content with preserve_thinking default on, so omitted reasoning tokens also sit in every later turn's prompt (P and C terms). A real log omission would change P/C counts derived from the transcript; the frozen desk strips only D (conservative for detection, but unstated), while runtime fed/cached counts are not tamperable. WP8 F1 (deferred): a refused XML call is invisible to the desk, which touches the 'unlogged turns cannot shift H' ledger claim.
- recommendation: Protocol v4 must define the v4 adversary model explicitly: what the log contains, which counts the monitor derives from the log vs from the runtime, and state that the frozen estimand (strip D only) is a lower bound on the residual shift of a real omission under preserve_thinking. Add a print-only 'full-omission' variant that also strips the omitted tokens from later P/C rows. Resolve WP8 F1 before D1.

### [HIGH] Battery top-up confounder from pilot 10 has no v4 rule; 58,260 s D windows make it near-certain and time-correlated
- owner: lead ruling; blocks: D-series
- evidence: RUN_STATE item 175: pilot 10 excluded spam ordinals 8-10 for a macOS battery top-up at 21-31 W after the pack sagged to ~95 %; 'Expect this in any long v4 session; a charge setting or schedule may remove it (doctrine gate 5).' FINAL-DESIGN §3.1 only requires ≥ 95 % at arm with Optimized Charging off. Amendment 1 A2: D windows up to 59,520 s (16.5 h). U1(b) allows ≤ 1 thermal exclusion per model per window, but battery assist is not in X1-X8 and correlates with elapsed time, biasing the calibration pool toward early members.
- recommendation: Add a pre-declared power-source rule to protocol v4 before W1: either a charge-hold mechanism verified in R1 (record pmset/battery state at 1 Hz in the sidecar) or an explicit exclusion X9 'power.battery_assist' with its count folded into U1(b) and a window-level bar. Print battery percentage and charger wattage per member in the desk.

### [HIGH] Clock-correlated residual (bank +0.79 to +0.92 across five sessions) is the strongest structure, the design forbids a clock term, and the 30B contrast cannot speak for D
- owner: lead ruling; blocks: D-series
- evidence: RUN_STATE items 169, 171, 175: corr(residual, GPU clock) bank +0.92, +0.87, +0.79 (print-only). FINAL-DESIGN §2.4 Analysis: 'No clock or temperature term (cf1baad2 Ruling (2))'; corr(residual, clock) printed as diagnostic only. Amendment 1 A3.2: the contrast's branch 'no longer controls any cell in this series'. §2.5: a 30B result cannot certify a dense 27B. So if D's residual tracks clock in D1 there is no pre-registered consequence; a reviewer will say the detector is a clock-state detector.
- recommendation: Pre-register for D a consequence on the clock diagnostic (e.g. if |corr(residual, mean decode clock)| > 0.5 with 90 % CI excluding 0 in D1, pause the D series for a design consult before D2) and a print-only clock-conditioned sensitivity. State in the paper that gates are the chosen remedy and show the pre/post-gate correlation side by side.

### [HIGH] Model identity the paper will claim ('Qwen3.8-27B at xhigh, AA 303') is conditional on an R0 ladder that likely lands at medium/low with a 4,096 cap and 2-3 turns
- owner: needs Ed; blocks: paper
- evidence: Amendment 1 A0: Ed chose the 27B for its xhigh AA index 303. FINAL-DESIGN §2.2 ladder: pass if ≤ 20 % turns end at cap with unclosed reasoning AND median reasoning ≤ 2,048 tokens per turn, stop at first passing rung (xhigh → medium → low); V9 card warns lower effort gives 'insufficient analysis, more failures, repeated retries'. Risk 1: fewer than ~3 turns → 4-bit; if that fails D is a screen. B_D floor 6,144 tokens = 1.5 turns at the cap. Capability gate is binary (any state-changing action per pair).
- recommendation: Ed should accept now that the paper's model is 'Qwen3.8-27B-8bit at <R0 rung>, 4,096 tokens/turn, ≤ B_D tokens/episode' and that this is a reasoning model operating far below its card's 32k budget. Protocol v4 should pre-declare the reported capability statistics (turns, tool calls, main/side task scores by condition) so the realism gap is quantified, not just gated.

### [MEDIUM] Escalation ladder step 2 tightens δ (max(0.5 °C, 2 SD)) which worsens a U1(d) timeout failure
- owner: lead ruling; blocks: D-series
- evidence: FINAL-DESIGN §2.4 Consequences: on U1-U3 fail apply in order (1) idle 300 → 450 s, (2) δ → max(0.5 °C, 2 × SD), (3) holds on, (4) one quantization step down. Initial δ = max(1.0 °C, 3 SD) (§2.6). Step 2 lowers δ, so if the window failed U1(d) (G1/H timeouts > 2 %) the remedy increases timeouts; it only helps a U3 energy-spread failure. Step 3 is moot for D (holds already mandatory).
- recommendation: Make the ladder direction-conditional in protocol v4: timeout-driven failures loosen δ_slow in 0.5 °C steps (within a printed energy band via R1's dE/dT) or lengthen G_turn; spread-driven failures tighten. Remove step 3 for heavy cells.

### [MEDIUM] U4 (cross-window equivalence) is likely INCONCLUSIVE at D3 by construction, yet 'under control' requires it to pass
- owner: lead ruling; blocks: paper
- evidence: FINAL-DESIGN §2.4 U4: 90 % t-interval over windows with df = W − 1 inside ±0.5 %; Amendment 1 A2: evaluable at D3 (W = 3, df = 2, t₀.₉₅,₂ = 2.92). Pilots 6-10 K-session σ_w 4.7-5.1 J on ~2.7 kJ ≈ 0.18 %; half-width ≈ 2.92 × 0.18 %/√3 ≈ 0.30 %, with 2 sentinels per window adding within-window noise, so the interval will sit near or beyond ±0.5 %. 'Ed's under control means U1-U5 pass.'
- recommendation: State now that U4 is expected inconclusive at W = 3 and pre-declare the +2 sentinels per window from D1 (not after an inconclusive read), or redefine U4's pass at D3 as the point estimate inside ±0.25 % with the interval reported, deferring the interval test to D4+.

### [MEDIUM] U6 residual slope on turn index is uninformative with 2-3 turns per D episode; pilot 7's accumulation signature cannot be tested on D
- owner: lead ruling; blocks: D-series
- evidence: FINAL-DESIGN §2.4 U6: 90 % CI of the pooled per-turn residual slope on turn index inside ±1 J/turn scaled. §2.5: the deciding question is pilot 7's +2 to +8 J later-turn accumulation. D's token budget (B_D 6,144-12k at a 4,096 cap) yields 2-3 turns, so a slope has ~1 df per trajectory and the early/late-half test (±0.37 %) is the only usable part.
- recommendation: For heavy cells replace the slope criterion with per-turn-position residual means (turn 0 vs turn 1 vs turn 2) with pre-declared bands, keep the early/late-half criterion, and say explicitly that the pilot-7 accumulation question is answered only by the 30B contrast.

### [MEDIUM] Window reference R from ordinal 5's 300 s post-anchor idle is biased warm and, with chassis warming, makes late-window G0 waits lengthen into X2 flags that bias the pool toward early members
- owner: lead ruling; blocks: W1
- evidence: FINAL-DESIGN §2.6: R = medians over the last 60 s of the 300 s configured idle of the first sidecar member (ordinal 5, after four 30B anchors ≈ 52 min of work). A heatsink with τc up to 300 s is ~63 % recovered at 300 s. Chassis keys (τ > 300 s) are 'recorded but not gated' though they set the heatsink floor physically. G0 cap 600 s then 'flag and proceed' → X2 exclusion from calibration. U1(d) allows ≤ 1 G0 timeout per model per window. No desk print of G0 wait vs ordinal is specified.
- recommendation: Add to the desk a G0/G1 wait-vs-ordinal table and a pre-declared bar (e.g. no monotone increase > 2× from first to last third). Consider capturing R from a longer idle (R1's soak or a 600 s idle at ordinal 5) and recording the chassis key alongside so a warm-chassis exclusion can be diagnosed.

### [MEDIUM] Hybrid checkpoint (B7/#657) is 'enabled for D once exact' in Amendment 1 but 'off for the series' in the execution plan; protocol v4 must pick one and price the re-prefill either way
- owner: mechanical; blocks: W1
- evidence: Amendment 1 A3.6: 'kit v4 enables it for D as a safety path' once exactness is recorded. V4-EXECUTION-PLAN ruling 2: 'the series runs with checkpoints off'; WP13 table: 'B7 checkpoint: Off for the series.' The R0 ladder admits up to 20 % of turns ending at the cap with unclosed reasoning; each such turn is a rewrite on D's non-trimmable hybrid cache and a full re-prefill of up to 40k tokens. Whether the frozen energy_residual P term counts re-fed tokens is not stated in the design.
- recommendation: Record the decision in protocol v4 (off is fine). Confirm and state that re-fed tokens after cache.rebuilt_untrimmable enter the P/C counts the frozen desk uses, so rebuild energy is priced, and print rebuild counts per member against the 5 % bar.

### [MEDIUM] R1 is too thin for the slots it freezes for the whole series
- owner: lead ruling; blocks: R1
- evidence: Amendment 1 A5 R1: one 30-min soak, two step tests, one X-G, two gated+held D spam/benign s1 runs fill S1-S9, δ, G_turn, t_decline, N_chunk, B_D, I_D, T_dead and the heavy class. WP14(a): kit refuses any key not in R1's classification. §2.7: a frozen-commit record fixes every slot before D1's desk is read (so W1 can inform), but W1's roster and span are sized from R1 and no rule says which slots W1 may revise.
- recommendation: Pre-declare in protocol v4 that W1 is the second slot-filling pass and list the slots it may revise (δ_slow, G_turn, N_chunk, B_D, T_dead) with the revision rule; keep sensor keys and heavy class fixed from R1. Add one bank/benign D run to R1 (the 10k-prefill case the planning turn assumes).

### [LOW] Protocol v4 (B10/WP20) does not exist on the assembled lane; the registration cold gate and the reserved 'Addendum FN' have nothing to read
- owner: mechanical; blocks: W1
- evidence: git ls-tree of lane/2026-11-05-align-v4-assembled shows no docs/align/pilot_protocol_v4.md; WP20 is 'not needed to arm R1 itself, only for W1 registration'. Several findings above (estimand, battery rule, ladder direction, slot revision) have no home until it exists.
- recommendation: Land the WP20 draft with PENDING sections before R1 so R1's slot fills land into a document, then run the blind cold gate before W1 arm.

### [LOW] Stale citation: pilot_protocol_v3.md on the assembled lane is the 214-line pilot-4 text and does not carry the pilot-7 desk addendum Amendment 2 says it does
- owner: mechanical; blocks: none
- evidence: Amendment 2 §2: 'docs/align/pilot_protocol_v3.md: the pilot 7 desk addendum names the freeze commit.' The file on lane/2026-11-05-align-v4-assembled, pilot10-benign and v4-integration is identical (214 lines) and contains no 'cda28a5ef' or pilot-7 text; item 169 also flagged l.61 '12 distinct values' as stale.
- recommendation: Fix the Amendment 2 citation to the commit/branch that actually carries the addendum, or port the addendum onto the v4 line so the registration record is self-contained.

### [LOW] The 30B contrast governs no cell in this series but takes 8 of 18 W1 slots; the paper must not present it as validating D's gates
- owner: lead ruling; blocks: paper
- evidence: Amendment 1 A3.2: 'its branch no longer controls any cell in this series'; it feeds the pilots 8-9 disclosure and future light cells. FINAL-DESIGN §2.5: 'a 30B result cannot certify a dense 27B.' Cost ≈ 4,000 s of a 44,640 s cap window.
- recommendation: Keep it (cheap, settles the pilot 8-9 disclosure), but write the paper sentence now: the contrast decides attribution of the pilot-7 signature on the 30B; D's thermal control is evidenced only by U1-U5 on D's own sentinels and the 5↔18 pair.

### [LOW] Sabotage/benign 'common random numbers' pairing buys no paired power after turn-0 divergence
- owner: lead ruling; blocks: paper
- evidence: FINAL-DESIGN §2.7: 'Sabotage is paired with a benign seed (common random numbers, as in the existing law).' §1(c): the sabotage prompt is 755 tokens longer, so the first sampled token already draws from a different distribution and trajectories diverge at turn 0.
- recommendation: Do not describe sabotage members as paired with benign in the paper; treat them as independent trajectories scored against the benign fit.


## Cannot claim
- Any false-positive rate, power, or test-set performance: thresholds are the sample maximum at m = 20-21, 3 held-out sabotage per pair, no locked test cohort (Q6 default no).
- An operational monitor: gated and held energy is energy at a reference state; production agents do not pause every 2,048 tokens or wait for the heatsink between turns (FINAL-DESIGN risk 8).
- Cross-model or cross-architecture transfer of the frozen design: one production model until Flash-Next (Amendment 1 A0).
- That Qwen3.8-27B ran at xhigh / card-recommended budgets: effort rung, 4,096 cap, B_D and possible 4-bit fallback are decided by R0/R1.
- Detection of small omissions (below ~100 tokens) or of omissions inside a turn's non-reasoning content; the estimand is omission of logged reasoning counts only, with context/prefill held fixed.
- That thermal state is 'under control' (U4, U5) before D3, and U4 is likely inconclusive at W = 3; no thermal-control claim at all if the SMC thermometry bar fails (X4 on every member).
- That the 30B contrast verdict validates D's gates: it governs only light cells and the pilots 8-9 disclosure.
- A causal effect of sabotage on energy, or anything about untampered-sabotage alarm rates beyond 'n of 3 below threshold'.
- Comparability of the K-session anchor offset across the physical-setup change (new stand, possible High Power): printed only.
- Byte-identity of the measurement path for anchors beyond what the boundary tests assert: cli.py was rebound (WP14(c)) and mlx_runtime.py carries the #657 hook.