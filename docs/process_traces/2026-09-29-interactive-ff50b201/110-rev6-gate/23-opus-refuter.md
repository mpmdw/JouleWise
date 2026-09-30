REFUTER: CONCUR (the text has no defect that can make a number false; five should-fix edits below are text-only and should land before the seal; F2 must be done before C1 is armed)

Refuter: Opus 5.5, fresh and read-only, on main 0009b976. Sealable text read in full (22-*.md, 910 lines), plus the ruling and charge. Scratch: scratchpad/rev6ref/ (sim.py, sim.out, cb.py, ng.py, rn.py, issuer.py, tree/).
Executed:
- A pure-Python Monte Carlo (seed 20260930, 6,000 replications per row, t quantiles from main's distributions.py).
- The issuer's own build_quantile_proof for df 9 to 35: all pass.
- A JSON parse of the block, and preregistration_epoch_pins plus the chain-digest regex run on Rev 1..5 + sealable: 1 match each.
- shasum of /usr/bin/powermetrics: b762e5bf…, which equals the pin.
- Reads: bracket evaluation cb.py:2540-2640 and :1230-1250; validator ceiling cb.py:398-500; doubling cb.py:2375/2438 (uses >=); night_gate class_table :616-640 and _check_machine :1468-1700; run_night :3080-3110; prewindow_check.sh (all); gen_derivation_night; t0 capture step; A1 R0-R11; E1 steps 12-13.

## 1. Q99_within: conservative. CONFIRMED, with one false sentence
- C only decides refusal: CONFIRMED in code. At cb.py:2613 drift > C returns instrument_calibration_mismatch. The bound is max(pre,post) + max(drift,S) (:2616-2617). C never enters the bound. The second use, at :1245, also only returns None.
- C_rev6 = max(C_rev5, Q99_within) >= C_rev5 on every campaign. Ratio Q99_within/Q99: the simulated maximum equals the algebraic bound exactly, i.e. 1.0702 (n12 K2), 1.0266 (n24 K2), 1.1568 (n12 K3), 1.0555 (n24 K3), 1.0334 (n36 K3).
- Chance that a fresh same-window pair differs by more than C. Target 1%. Rev5 → Rev6:
  - no dependence: about 1.0% → 0.72-0.96%
  - window ICC 0.3: 0.51-0.65% → 0.42-0.62%
  - window ICC 0.6: 0.22-0.42% → 0.19-0.40%
  - A real window effect makes C larger. It never makes it smaller.
- The chance goes above 1% only in two cases:
  - neighbours alternate (serial φ = −0.5): 3.36% → 3.09%
  - the claim bracket runs in a window twice as noisy as the others: 6.36% → 5.85%
  - In both cases the excess means more healthy brackets are refused (lost yield). It never admits a bracket with a bound that is too small. Rev6 is lower than Rev5 in every scenario.
- "Can a window effect make C too small so a drifted capture is admitted?" No. Admission needs C too large. The max raises C by at most 15.7% (n12 K3), and every admitted bracket still carries its drift inside its reported bound.
- **F1 should-fix, §9 lines 789-791.** The text says "It exceeds Q99 only when the windows are more alike than chance would make them." This is false. Q99_within is the larger whenever F = MSB/MSW is below 1.454 (n12 K2), 1.188 (n24 K2), 1.122 (n36 K3) or 1.522 (n12 K3). With no window effect at all, that happens in 67-75% of simulated campaigns. Replacement: "It is the larger when the between-window mean square is below about 1.1-1.5 times the within-window one; with no window effect this happens in about 70% of campaigns, and raises C by at most the factor above." "A few percent at most" should say "at most 15.7% (n = 12, K = 3), 2-6% at n >= 24".
- The worked examples all recompute: 0.01902/0.01854; 0.015408/0.011596/0.015848; 2.9%.

## 2. Count rule and JSON block: unambiguous except for two gaps
Checked and sound:
- clause order;
- the second adverse window is caught by clause 1;
- the adverse window is replaced in place and faces futility afresh;
- at most 3 counting + 1 replacement, which agrees with R9 and with E1 step 12/13 ("both third-window triggers" gives T-members its authority);
- CLOSE after C2 needs all 24 slots counted;
- K = 1 degenerates safely (Q99_within = Q99);
- n − K >= 9 and the proofs pass;
- A-R5b makes the issuer compute adverse itself from raw bytes.

- **F3 should-fix, §4 and §7 stop_lines.** R9's fifth clause ("every median frame reported") has no stop line and no count-rule outcome. Take a capture whose raw bytes are missing: A1 R0(d) lists it without a need. The count rule can reach CLOSE_AND_DERIVE while the issuer refuses ("every clause of R9 passes"). The result is neither void nor shortfall, which is an undefined state. Add STOP-R9-FRAME (review; say explicitly whether the campaign is void), or say it is read as a shortfall.
- **F4 should-fix, JSON sessions.windows_of_this_registration.** A derivation session opened and then aborted before any finalized slot (a chain fault after reservation) counts as a window. A-R5b puts no obligation on unreached slots, so the window is a counting window with 0 counted and 0 valid. As the first counting window it fires STOP-FUTILITY. Later, it silently uses up one of the three counting windows. D-182 treats zero-capture t0 refusals as not-a-window. State which reading applies here (no number is at risk; this is a death-loop and yield issue).

## 3. Start conditions
- **F2 should-fix, with a hard precondition for arming C1. §6.2(g) is not on the derivation arm path today.**
  - prewindow_check.sh runs only as the D-134 T-0 step (capture_t0_step.py:415-417, arm_readiness_evidence_t0.py:910-940), behind night-gate row C2.
  - For DIAGNOSTIC_NO_PACK, the derivation receipt class, C2 is NOT_APPLICABLE (night_gate.py:624-630).
  - run_night.py, gen_derivation_night.py and the derivation chain never call it.
  - So the judge's §8.2 worry is real. The text also gives the issuer no check for the (a)-(g) evidence, so running without the dwell would pass silently.
  - Fix: add to §7's issuer checks "each window's start-condition evidence (a)-(g) is present in custody", and wire the dwell into the derivation driver before C1, or strike (g).
  - Wiring hazard: script check 8 (`grep -E "codex|claude|t3|mcp-server|run_campaign|window-chain"` over `ps aux`) blocks whenever any agent is alive. Its line-wide matching must be tested against the derivation driver's own argv.
- **F5 should-fix, §6.2(g) wording.** "All three of these hold … these are the constants of prewindow_check.sh" misstates the pinned script. It blocks on five conditions: the named daemons, load, AC, at least 20 GB free disk, and no process matching that check-8 pattern. It also has a 45-minute --wait timeout. This is the same class of defect as the judge's own finding 7#1. List all of them, or say "the script's checks, including …".
- **F6 nit, §6.2(g).** "The night gate repeats the load-average limit of 2.0 at t0" is true only on the legacy evaluate_night path. A quiet-admission (v4) derivation plan goes through bind_until_quiet/evaluate_dynamic_hard with legacy_load=False (night_gate.py:1558, :1840; run_night.py:3095). gen_derivation_night supports v4 (:511, :940). Either pin the path or qualify the sentence.
- Nothing physical from W1/W2 is missing. Interactive launch context (§5), battery float (e), thermal (d, present on both gate paths), census (c) and the 600 s settle are all present. The 1,200 s rest claim holds even without (g): the 600 s settle alone is more than the 403 s between captures inside a window.

## 4. Other
- **F7 nit, §9 line 737.** The text says the bracket's captures are "a few minutes apart (§0)". §0 does not say that, and the ruling lists it as NOT ESTABLISHED. Drop it, or cite a source. The direction of any error is refusal, not a false number.
- **F8 nit, §9 lines 769-771 and §12.** Q99_within needs its own recorded rule string (df n − K). The sealed TWO_DRAW_PREDICTION_RULE literally says "t(p, n-1)". Say that a new string is recorded, so WI-13 does not reuse the old one.
- Verified OK: the powermetrics pin; the V5 single-match parse; the JSON parse (19 slot occurrences); doubling uses >= 2n, so the 31/60/29 and 43/17 examples are right; quantile proofs pass at every df this rule can produce.
