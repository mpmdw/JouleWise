# W1 budget fit (ruling 1(f)) and the ruling 1(e) fallback: synthesis of two seat audits

- **Date:** 2026-11-07.
- **Synthesizer:** Opus 5.5 (`claude-opus-5-5`).
- **Seats:**
  - seat 1 is the Fable 5.1 seat ("Fable seat audit");
  - seat 2 is the Opus 5.5 seat ("Opus seat"). Its tools are on `opus/burn-w1fit@43b305425`, under `docs/align/reviews/2026-11-07-w1-budget-fit-opus/`.
- **Code base:** `lane/2026-11-06-v4-r1-integrated@e901eb2a4` unless another ref is named. "FD" is `docs/align/council-2026-11-05/FINAL-DESIGN.md` and "A1" its Amendment 1, both on `origin/main@bd7a3efcd` (FD's last change is `219fb1515`; seat 2's FD line numbers at `6eb1ff5be` are the same lines). "CHAIR", "LR1" and "LR2" are `CHAIR.md`, `LEAD-RULINGS-1.md` and `LEAD-RULINGS-2.md` under `docs/align/council-2026-11-06-v4-review/`. "P4" is `docs/align/pilot_protocol_v4.md`. The R0 records are `origin/records/2026-11-07-align-r0-v4-rerun7@7bdfdae6e` and `...-rerun5@ea89c4d3f`.
- **What I checked myself:**
  - every disputed claim and every load-bearing citation, against the code and docs;
  - the arithmetic, which I recomputed independently from the kit's formulas (§5);
  - the R0 rate fields, from the rerun 5 and rerun 7 `report.json`;
  - Apple's M3 Max specs, at <https://support.apple.com/en-us/117737>.
- **Blinding:** I opened nothing under `jw-b5-*`, `night-*`, custody/archive or `restricted/`. Every number below is a timing, rate, count or configuration field, and nothing here depends on a Block-5 value. I ran no tests and loaded no weights.

---

## 1. Executive summary

1. **At 8-bit, ruling 1(f) cannot pass at any admissible B_D, whatever R1 measures, as long as R7-2's G0 term and R6-3's full last turn stand.** Both seats found this and it is verified.
   - The G0 term is G0_cap_W1, which is never below 600 s.
   - At the 6,144 floor the decode term is always 10,240 tokens.
   - Even the physically unreachable corner needs r ≥ 15.1 tok/s: I_D = 300 s, zero G1, hold, prefill and tool time, and the G0 term at 600 s. A realistic 35 s prefill raises that to 16.0 tok/s.
   - This Mac (Mac15,9 with 128 GB, so the 400 GB/s M3 Max) has a bandwidth ceiling of **14.0 tok/s** for D's 28.58 GB of 8-bit weights.
   - R0 measured **11.85-11.95 tok/s**, the same in reruns 5 and 7.
2. **The "about 20 tok/s" premise in LR2:363 (R7-2 builder note) and LR2:593 (R8-8) has no source.**
   - R5-4's builder note (LR2:61) and FD:145 use 11 tok/s.
   - Twenty tok/s is the 4-bit projection. 4-bit is unmeasured, with a ceiling of 24.8 tok/s and about 21 tok/s at 8-bit's 85 % bandwidth efficiency.
3. **None of 1(e)'s named steps rescues 8-bit, and no 1(e) ruling can reach the kit today.**
   - Step 1 (S6) shrinks only the holds term.
   - Step 2 (idle 450 s) costs 132 s of T_dead, pushes the contrast members' bound to 1,900 s, and forces ordinal 18 out.
   - Step 3 (4-bit) fits the current rule only in a corner.
   - Step 4 ends D.
   - `DUTY_FALLBACK_STEPS` is honoured only by the duty-bar check, while the 1(f) refusal is unconditional (`scripts/align_v4_kit.py:176, 294-298, 629-633`).
4. **Where the seats disagree on a remedy, I side with neither.**
   - Seat 1's W1-only expected-case waiver is incoherent. W1 must run in the final D configuration: ordinal 5 is the D_k sentinel original and the E_ref source, and 5/17 is W1's U3 pair (A1:112, A1:144, FD:386, FD:523, CHAIR 6). So a W1 X7 is not free, and the waiver only postpones the same refusal to D1.
   - Seat 2's plan-declared member cap (S1) is valid but costs Ed's Mac time, so it belongs at council, not first.
   - **The minimal deviation that keeps 1(f)'s worst-case guarantee is a budget-sized D G0 cap (seat 1's D-d, generalised).**
     - Arm D's W1 G0 cap at G0\* = T_dead − holds − prefill/tool − 10,240/r, with the 1(f) term equal to that armed cap.
     - Admit only when R7-2's own 1.25 × (max released gated D wait) fits under G0\*.
     - A long G0 then ends as a clean X2 before turn 1, never as an X7.
     - At 11.9 tok/s, G0\* is 76-268 s. So 8-bit survives only if R1's D-after-D waits are at most about 60-215 s.
     - At about 20 tok/s (4-bit), G0\* is 424-617 s.
5. **R1's G0 waits decide the branch.** The seats' physics predictions bracket them: 0-300 s if holds keep the slow sensor near the band (seat 1), 440-640 s or more from the unheld step test (seat 2). Neither is measured.
6. **New finding from the synthesis:** R1's gated runs are armed at step-d's B_D, not at the floor (`r1_runtime.py:794, 910-929, 1812`).
   - At 8-bit step-d's B_D is about 12,288-14,336, so the gated runs' own decode term exceeds T_dead.
   - X7 in the gated runs is therefore likely for budget reasons, not thermal ones.
   - That makes the duty bar's "no X7" likely to fail, and makes the recorded holds come from truncated runs.
   - Any admission path therefore needs a duty-bar 1(e) receipt as well as a 1(f) receipt.
7. **Build the kit lane before R1:**
   - a 1(f) receipt;
   - per-role G0 caps;
   - a D cap below 600 s under receipt;
   - holds projected per token.

   Also decide 4-bit staging and settle W1's final D configuration. Then the post-R1 ruling is mechanical (§6), and W1 does not lose a day.

---

## 2. Decisions needed from the lead

1. **Record the 8-bit verdict now, blind, before R1.** Under R7-2's G0 term and R6-3's full last turn, 8-bit D fails 1(f) at every admissible B_D for every possible R1 thermal outcome (§3 A1). Correct the record in LR2 R7-2/R8-8: 8-bit D runs at about 11.9 tok/s on this Mac, and about 20 tok/s is the unmeasured 4-bit projection.
2. **Pre-declare the post-R1 procedure (§6) before R1's numbers are read.** In particular, rule whether the budget-sized D G0 cap (D-d) may be used.
   - It lowers FD's and R7-2's 600 s G0-cap floor for D members only.
   - It keeps CHAIR 1(f)'s worst case intact and converts would-be X7 into X2-before-turn-1.
   - It needs the public deviation log.
   - The order I recommend:
     1. D-d at 8-bit;
     2. 4-bit, under the current rule or with D-d;
     3. council, with S1/S2 (member cap), a series-wide bounded-risk 1(f), final-turn truncation, or screen-only.
3. **Rule 1(e) step 2 out as a 1(f) lever, on the arithmetic, now.**
   - It costs 132 s of T_dead.
   - It puts the 30B contrast members at a 1,900 s bound against the 1,800 s member cap.
   - It forces ordinal 18 out of W1, and with it s93, ruling 15's alternate sentinel.

   It stays available only for the duty bar's G0 share.
4. **Commission the kit lane before R1, with failing-first tests and a cold review, so it can merge the day R1 lands.** It needs:
   - (a) a lead receipt `inputs.R1.ruling_1f` honoured by `ruling_1f_fit`;
   - (b) per-role G0 caps: D from the gated D waits, contrast from X-G. That matches R7-12's own wording, "W1's D-to-X G0 term" (LR2:451), and removes the path by which an inconclusive X-G sets D's term to 1,200 s;
   - (c) a D cap below 600 s under that receipt (`thermal_gates.validate_gate_policy`, `thermal_gates.py:102-105`);
   - (d) the holds term projected per decoded token to 10,240 tokens;
   - (e) the duty-bar `lead_fallback` receipt, recorded alongside the 1(f) receipt (§3 C1).
5. **4-bit staging for the R1 night (magistrate's call on night length).**
   - Authorise the 16.1 GB download, the pins and `d_4bit_source` (null today, `configs/align/v4/r1_runtime.json:12`), so the optional `d-4bit` step (`--include-4bit`) records r4 and I_D4.
   - It is a step test only. The kit's 1(f) reads gated rows, so any 4-bit W1 still needs an R1-4bit gated night.
   - It adds up to about 5,764 s to a no-redo worst case of 56,207 s (D8-3).
6. **W1's final D configuration.** Rule that quantization, B_D, T_dead and the per-turn cap are settled before W1 arms, and that ruling 17's post-W1 revisions are limited to the G0 cap, δ_slow, G_turn and N_chunk.
   - A post-W1 change of B_D, T_dead or quantization forfeits W1 ordinal 5 as the sentinel original and E_ref source, and W1 as a U3/U4 window for D. If the lead accepts that cost, rule it explicitly.
   - This supersedes seat 1's step 6, which re-sizes B_D or switches quantization after W1.
7. **The contrast members' G0 cap.** P4:365 says "Every other G0 keeps 600 s", but the kit arms G0_cap_W1 on every W1 member through the shared `thermal_policy` (`align_v4_kit.py:964-973, 1034`). Rule which is meant. With a long cap, the contrast's 1,086 s deadman is at real X7 risk (§3 D).
8. **Seat 1's two "unconditional accounting refinements."** I recommend:
   - **reject D-a as stated.** Replacing the 1(f) G0 term with the measured maximum while W1 still arms a cap of 600 s or more loosens the worst case; the consistent form is D-d.
   - **replace D-f's "saves 0-40 %" with the symmetric per-token projection.** At 8-bit it will probably *raise* the holds term (§3 B5).
9. **Questions for Ed now, so they do not block council later:**
   - whether the paper may name a 4-bit model (CHAIR (B) Q6);
   - whether, if council picks S1/S2, he grants Mac time for W1 above 44,640 s (up to the 59,520 s D-window size, A1:117, A1:227) and for 4-7 D_k windows instead of 3.

---

## 3. Findings

Severity: **CRITICAL** blocks W1 on the R1 numbers; **HIGH** changes the ruling or its cost; **MEDIUM** is a precondition or a risk the ruling must state; **LOW** is a record fix. Each finding says which seat raised it: both, seat 1 (S1-seat), seat 2 (S2-seat), or synthesis.

### A. Agreed by both seats and verified

**A1 (CRITICAL). The 8-bit 1(f) refusal is structural.**
- **The rule as coded:** `worst = G0_cap_W1 + max(G1+H) + max(prefill+tool) + (B_D + 4,096)/r_min ≤ T_dead` (`scripts/align_v4_kit.py:469-524`, terms at `:519`).
  - G0_cap_W1 = clamp(ceil(1.25 × max counted wait), 600, 1,200) (`:419-466`, value at `:465`).
  - A turn is admitted while `used < B_D` and keeps its full cap (`workload.py:501`; FD:263).
  - `validate_budget` refuses B_D below 6,144 (`align_v4_kit.py:914-916`).
  - T_dead = min((1,750 − I_D)/1.13544, (1,800 − I_D − tail − 10)/1.13544) (`:704-708`; LR1 L1). I_D includes the 300 s idle, load, warmup and teardown (`r1_runtime.py:782`).
- **The decode rate needed at the floor** is 10,240 / (T_dead − 600 − HG − PT). It is ≥ 15.1 tok/s even at I_D = 300 s with HG + PT = 0, and ≥ 24.0 tok/s at the transferred I_D of 516.6 s with HG + PT = 60 s (§5 Table 2).
- **Rate evidence:**
  - R0 rerun 7, `/checks/4/short/gross_turn_tokens_per_second` = 11.95;
  - `/checks/6/turns/1..11` = 11.85-11.90 (turn 0 is 9.04, a first-turn transient);
  - rerun 5: 11.95 and 11.85-11.90;
  - FD:145 ("about 370 s at 11 tok/s");
  - the R0 load-reference cold pass (`docs/align/reviews/2026-11-06-r0-load-reference-fable-cold-pass.md:29`, "the rerun's 11-12 tok/s").
- **The ceiling (§3 B2):** 14.0 tok/s.
- **So the R1 night cannot change the 8-bit verdict under the current rule.** What R1 can change is which deviation works (§3 C2).

**A2 (LOW). The 20 tok/s premise is unsourced.** The figure first appears in the R7-2 builder's open note (LR2:363) and is repeated by R8-8 (LR2:593). LR2:61 (R5-4) computed with FD:145's 11 tok/s.

**A3 (HIGH). No kit path exists for a 1(e) ruling to admit W1 under a 1(f) refusal.**
- `check_r1_evidence` calls `check_r1_budget_and_policy` (`align_v4_kit.py:282`), which raises on `not fit['fits']` with no receipt (`:629-633`).
- `DUTY_FALLBACK_STEPS = (1, 2, 3)` (`:176`) is read only by the duty-bar check (`:294-298`).
- R6-3 says "No code fallback" (LR2:199-207). So every fallback needs a kit change (a receipt) or an R1 re-run.
- The lane should be built and reviewed before R1, so the ruling does not cost a day of Mac idle.

**A4 (HIGH). 1(e)'s named steps do not cure 8-bit (CHAIR:33-37).**
- **Step 1 (S6 ≤ 2.0 °C).**
  - It lowers HG only. G0's slope criterion (P4:357-358) is untouched, and G0_cap_W1 never goes below 600 s.
  - The kit binds the recorded holds (`:519`). An `s6_tuning` receipt changes `delta_slow_c` but not that number (`:600-627`), so credit needs a re-run of the gated block at S6.
  - It costs U5: the left side |β_T|₉₀ × δ_slow (LR1 L2) grows in proportion to δ_slow, so it doubles if S5 = 1.0 °C.
- **Step 2 (idle 300 → 450 s after D predecessors).**
  - The idle sits inside I_D, so T_dead falls by 150/1.13544 = 132 s.
  - The kit's G0 term is R1's 300 s-idle measurement. The kit binds `duty_bar.schedule` to the configs' idle (`:285-293`), so a 450 s config refuses the 300 s R1 record.
  - Net effect on 1(f): −132 s to +55 s at best (seat 2).
  - The contrast members' bound becomes 516.6 + 150 + 1.13544 × 1,086.3 = 1,900 s, over the 1,800 s cap, unless their deadman is cut to 954 s (`align_v4_kit.py:700-701`).
  - Window effect: §3 E.
- **Step 3 (4-bit).** r rises by about 1.7-1.8 × (§3 B9). Under the current rule (floor of 600 s) it fits at the floor only if G0_cap_W1 = 600 (every counted wait ≤ 480 s), HG + PT ≲ 60-150 s and I_D ≲ 400-450 s (§5 Table 2, rows r ≈ 20-21).
- **Step 4.** Never admits (`:172-176`). W1 without D needs a re-cut plan, and `fit_roster` never cuts the 5/17 pair (`:919-945`).

**A5 (MEDIUM). FD's own 4-bit trigger does not fire.**
- FD:253-254 sizes B_D from the planning member alone. `r1_runtime.py:794` computes `((1,800 − I_D)/1.13544 − prefill_s) × r`, which gives 12,288-14,336 at 11.9 tok/s for I_D 300-516.6 (§5).
- That is above 6,144, so "B_D < 6,144 at 8-bit" is false.
- Reading the trigger through CHAIR 1(f) (seat 1), or through 1(e)'s "duty bar fails" extension (seat 2), are both lead rulings. Either makes 4-bit a pre-registered consequence rather than a new deviation.

**A6 (MEDIUM). Predecessors.**
- In W1, only ordinal 18 follows a D (after 17). D members 5, 8, 11, 14 and 17 follow 30B members (`align_v4_kit.py:63-82`; P4:96-121).
- R1 measures only the D-after-D wait (R6-1), and X-G (30B after D). D-after-30B is never measured.
- The D-after-D bound is presumably conservative for W1, since a 30B member is a lighter load, but that is unmeasured.
- The D-series is mostly D-after-D, which R1 does measure.

**A7 (HIGH). A G0_cap_W1 of 1,200 s makes 1(f) infeasible at every rate.**
- Any censored gated G0, or an inconclusive X-G (R7-12, integration note LR2:455), sets the whole cap to 1,200 s.
- T_dead is 1,013-1,277 s across I_D 300-600, so the D term alone exceeds T_dead at I_D ≥ 516.6, and leaves at most 77 s otherwise.
- An armed cap at or above T_dead also means X7 always fires before X2 (S2-seat F4; the R7-2 builder notes the same at LR2:364).
- This confirms the round-7 cold pass LOW-2(d) (`docs/align/reviews/2026-11-07-r1-round7-cold-pass.md:126`).
- A per-role cap (Decision 4b) removes the X-G route.

**A8 (MEDIUM). 4-bit needs more than the optional step.**
- `d_4bit_source` is null (`configs/align/v4/r1_runtime.json:12`), and `k_d_4bit` refuses while it is (`r1_runtime.py:1794-1797`).
- `--include-4bit` adds only a `d-4bit` step test (`scripts/align_r1_rehearsal.py:535-536`). The kit's 1(f) rate and holds come from the gated rows, so a 4-bit W1 needs:
  - a 4-bit R0 (load, NLL, memory);
  - pins;
  - kit identity changes (`D_REPO` and int8 are hard-coded, `align_v4_kit.py:50, 1021`);
  - an R1-4bit gated block plus X-G.
- FD:255 asks for the download before R1 "if R0's measured rates already predict that switch". Under the current 1(f) term, R0's 11.9 tok/s does predict a certain 8-bit refusal.

**A9 (MEDIUM). Window arithmetic.** See §3 E. Every fallback that keeps D members at or under 1,800 s leaves W1 at span 26,927 s and window 44,640 s, 13 s inside the span limit.

**A10 (MEDIUM). Blinding.**
- Every input to the decision is an R1 timing or count field, plus the R0 capability proxy (ruling 21).
- Nothing reads energies, U5, residuals or scores.
- W1's D members enter no pool (CHAIR 17).
- Both seats' rules are adopted in §6:
  - record the procedure before R1's numbers are read;
  - freeze before the D1 desk;
  - judge the duty bar as declared;
  - log each deviation publicly;
  - start a new cohort for any change of quantization or B_D.

### B. Disagreements, resolved

**B1 (LOW). The deep-context decode rate.**
- Seat 1 reads R0 rerun 7's memory check as "≤ 8.3 tok/s gross at deep context". Seat 2 reads it as about 11.3-12.1 tok/s.
- The record: `/checks/8` has `prompt_tokens` 34,816, `decode_tokens` 6,144, `seconds` 739.23 (`check_seconds` 739.87). It does not split prefill from decode.
- 8.3 tok/s is 6,144 / 739 with the 34,816-token prefill included, so it is not a decode rate. Seat 2's 11.3-12.1 subtracts an assumed prefill of about 180-230 s, which is an inference.
- **Resolution:** the check is consistent with about 11-12 tok/s decode at 35-41k context.
  - D is a hybrid model: three `ArraysCache` linear-attention layers to each `KVCache` layer (`/checks/8/cache_classes`). So decode should not slow much with context.
  - Rerun 5's figure, 731.2 s, agrees.
- Neither seat's specific number is measured. 11.9 tok/s at short context is.

**B2 (MEDIUM). The bandwidth ceiling.**
- Seat 1 put it near 11-13 tok/s from 29.5 GB of weights (fable-cold.md:113). Seat 2 put it at 14.0 tok/s from 400 GB/s.
- **Verified:**
  - R0's host-identity check records `hw_model` Mac15,9 and `hw_memsize` 137,438,953,472 (128 GiB).
  - Apple's spec page lists 128 GB only for the 16-core CPU / 40-core GPU M3 Max, at "400GB/s memory bandwidth". The 14-core part is 300 GB/s and offers at most 96 GB.
  - D's `active_bytes` at position 0 is 28,579,478,576 (`/checks/8/memory_samples/0`). D is dense (CHAIR 26), so each token reads all its weights.
- **Ceiling:** 400 / 28.58 = **14.0 tok/s**. The measured 11.9 tok/s is 85 % of it, and also rules out the 300 GB/s part, whose ceiling is 10.5 tok/s.
- I could not find the "16 CPUs" host field seat 2 cites in R0's host check, so I rely on the memory size instead.

**B3 (HIGH). Can R1 change the 8-bit outcome?**
- Seat 2 says no, so the lead can rule the 8-bit branch now. Seat 1 calls it "structurally infeasible", yet its §7 still sends 8-bit to a waiver.
- **Resolution:** both are right under R7-2's G0 term. But both treat the 600 s floor in that term as fixed.
- The floor comes from the *armed* cap (R7-2). CHAIR 1(f) itself says "the worst-case R1 G0" (CHAIR:39).
- If the lead lets D's armed W1 cap fall below 600 s, and keeps 1(f)'s term equal to the armed cap (D-d, §3 C2), the worst-case guarantee survives. 8-bit then fits at the floor whenever 1.25 × (max released gated D wait) ≤ G0\* ≈ 76-268 s (§5 Table 3).
- So R1's waits *can* change the 8-bit outcome, but only through that deviation.
- Decision 1 records the current-rule verdict now. Decision 2 decides whether D-d is available.

**B4 (HIGH). Seat 1's D-a ("factor 1.0 in the 1(f) term, rule in unconditionally").**
- `ruling_1f_fit` reading `max_g0_s` instead of `value_s` (`align_v4_kit.py:465, 519`) drops both the 1.25 factor and the 600 s floor from the term. So it can save up to 600 s, not "≤ 240 s" as seat 1 says.
- But W1 would still arm `g0_cap_s = value_s` (`:573` binding). A W1 member could then wait up to the armed cap and run into X7, so the 1(f) "worst case" would no longer be W1's worst case.
- That is a margin loosening of the worst-case guarantee, which R7-2 placed deliberately ("ruling 1(f) uses it in the max-G0 term").
- **Rejected as an unconditional refinement.** The consistent version sets the term equal to the armed cap and sizes the armed cap to fit. That is D-d (§3 C2).

**B5 (MEDIUM). Seat 1's D-f (per-token holds) versus seat 2's F5 (holds understated).**
- Seat 1 expects per-token scaling to *save* 0-40 %, assuming step-d sets B_D "near 16-20k". That is wrong.
  - `r1_runtime.py:794` gives at most about 15.9k tokens even at I_D = 300 s.
  - It gives 12,288-14,336 tokens at 11.9 tok/s for I_D 300-516.6 (§5).
- At 8-bit the gated runs will probably be deadman-cut before 10,240 tokens (§3 C1). So projecting per token to 10,240 tokens probably *raises* the term (seat 2).
- **Resolution:** use the symmetric projection HG_proj = max(HG, max over runs of (G1+H) / decode_tokens × 10,240) for every sizing in §6. Better still, have `r1_slots` carry the per-gate wait lists (seat 2 OPEN).
- Do not bank on a saving.

**B6 (HIGH). The recommended remedy: seat 1's W1-only waiver versus seat 2's S1 member cap.**
- **Seat 1's D-e** (W1-only expected-case 1(f) with a recorded X7 bound) is not coherent as a W1-only device, for three reasons.
  1. **W1 must run in D's final configuration** (seat 2 F9, verified):
     - D_k sentinels are "exact seed replays of its W1 spam/benign s1 original" (FD:523; A1:112);
     - U4 uses "E_ref the model's W1 original" (FD:386), and E_ref includes W1's 5/18 runs (CHAIR 6, 18 being 17 after the 1(g) swap);
     - "U3 is evaluated in W1 for D" on the 5↔17 pair (A1:144).
     - The cohort key includes `max_episode_decode_tokens` and `deadman_s` (CHAIR 10).
  2. **So an X7 in W1 is not free.** It hits the sentinel original or the U3 pair. Ruling 15 then falls back to s93, which is the member the fit rule drops first.
  3. **The D-series inherits the same infeasibility.** Seat 1 keeps worst-case 1(f) for held-out windows, so an 8-bit W1 under a waiver only moves the quantization decision past W1, which point 1 forbids.
  - D-e survives only as a council option: a *series-wide* bounded-risk 1(f). That is the X7 erosion of m ≥ 19 that CHAIR 1 exists to prevent.
- **Seat 2's S1/S2** (plan-declared D member cap above 1,800 s) is a valid council option that keeps the estimand. But it needs:
  - W1 above 44,640 s, which needs Ed;
  - 4-7 D_k windows instead of 3;
  - a change to `HAZARD_MEMBER_CAP_S` (`scripts/run_campaign.py:3776`), which R8-2 avoided touching.
- **Resolution:** neither goes first. D-d, and then 4-bit (with or without D-d), come before council (§6).

**B7 (LOW). Step 2's span.**
- Seat 1 adds 150 s × 5 followers (6, 9, 12, 15, 18), giving 27,676 s. Seat 2 adds 600 s, giving 27,527 s.
- The planning law prices D at its 1,800 s cap and contrast at 850/1,150 s (P4:646-648). So ordinal 18's extra idle comes out of T_dead, not the span, and seat 2's 27,527 s is the consistent figure.
- Either way the span exceeds 26,940 s, ordinal 18 is dropped, and W1 runs at span 25,727 s and window 43,440 s. Both seats agree on that result.

**B8 (LOW). 4-bit and the MDE.**
- Seat 1 says the MDE in tokens "doubles under energy-fraction misfit". Seat 2 says it is "unchanged under A and B, about doubles if the floor is fixed in joules".
- CHAIR §C defines MDE ≈ q · s_r / e_D, with (A) misfit fixed in tokens and (B) misfit proportional to E_D.
- Under (A) the token MDE is unchanged.
- Under (B) it scales with E_D/e_D. That ratio is unchanged only if prefill and fixed energy halve along with e_D, so expect 1× to under 2×.
- The joule-fixed instrument floor (about 10 tokens) doubles to about 20 tokens, still far below misfit.
- Seat 2 is right for (A) and for proportional (B). Seat 1's "doubles" is the upper bound.

**B9 (LOW). The 4-bit rate.**
- Seat 1 says about 19-20 tok/s. Seat 2 says 17.5-22, default 1.70 × r8.
- 16.1 GB (FD:255) gives a ceiling of 24.8 tok/s, and about 21 tok/s at 8-bit's 85 % efficiency.
- All are projections. Use the measured `d-4bit` rate when it exists.

**B10 (LOW). Seat 2's "ruling 3's D5 cap holds only if C_D ≤ about 2,520 s".**
- Seat 2's own table gives 5 D_k windows at C_D = 2,700 s (12 D members, 10 held-out).
- Under A1's 2 sabotage per window (1 per pair), and before exclusions, I get about 2,590 s.
- The threshold therefore depends on the composition rule and the exclusion allowance. I treat it as roughly 2,500-2,800 s, not a firm 2,520 s.

### C. New findings from the synthesis checks

**C1 (HIGH). R1's gated runs are armed at step-d's B_D, so X7 there is likely for budget reasons, not thermal ones.**
- `k_gated_d` takes `t_dead, b_d = gated_budget(slots)` (`r1_runtime.py:1812, 910-929`), and that is step-d's B_D: about 12,288-14,336 at 8-bit.
- The gated runs' own decode bound, (B_D + 4,096)/11.9 ≈ 1,376-1,548 s, exceeds T_dead (1,086-1,189 s). So unless an episode ends naturally, a gated run ends X7.
- **Consequences:**
  - (a) The duty bar's "no X7" (`align_r1_rehearsal.py:83, 776`) will probably fail at 8-bit for a reason unrelated to the thermal duty it is meant to measure. A recorded 1(e) step 1-3 is then required for any W1 admission (`align_v4_kit.py:294-298`), on top of any 1(f) receipt.
  - (b) The recorded `max(G1+H)` comes from truncated runs (§3 B5).
  - (c) The duty bar must still be judged as declared (seat 2). The record should note the budget confound, and the duty bar must not be re-judged against a restated T_dead.

**C2 (HIGH). The budget-sized D G0 cap (D-d) is the only deviation found that admits 8-bit and keeps 1(f)'s worst case.**
- **Rule:**
  - G0\* = T_dead − HG_proj − PT − (6,144 + 4,096)/r_min.
  - Admit if no gated D G0 is censored and ceil(1.25 × W_D) ≤ G0\*, where W_D is the maximum released wait over D_bank, D_spam a and D_spam b.
  - Then arm D's W1 `g0_cap_s` = floor(G0\*). The 1(f) term is that cap, and B_D is the largest fitting value at or above 6,144.
- A G0 that has not released by the cap ends before turn 1 (`episode.g0_unreleased`, P4:375-379). That is X2, a clean exclusion, never an X7 mid-episode.
- **8-bit window** (§5 Table 3):
  - G0\* = 268, 228, 178 s at I_D = 400 s with HG + PT = 60, 100, 150 s;
  - 166, 126, 76 s at I_D = 516.6 s.
  - So W_D must be no more than about 61-214 s.
- **4-bit (about 20 tok/s):** G0\* = 424-617 s, so W_D ≤ about 339-494 s.
- **Costs:**
  - it changes FD's 600 s G0 cap for D (`thermal_gates.py:23, 102-105`);
  - it needs a per-role cap, because contrast members keep X-G's cap;
  - the X2 exposure for W1's five D-after-30B members is unmeasured until W1 itself.
- **Seat 1's own prediction** (D-after-D waits of 0-300 s) makes this live at 8-bit. Seat 1 called D-d "a non-starter at 8-bit", but the waits decide that, not the arithmetic.
- **D1:** a G0-cap change after W1 does not alter the episode, so ruling 17 can revise D's cap before D1 without forfeiting the sentinel (Decision 6).

**C3 (MEDIUM). Final-turn truncation (seat 1's D-c) removes 4,096/r seconds from the worst case.** That is 344 s at 11.9 tok/s and about 205 s at 20 tok/s.
- **At 8-bit with the 600 s floor** it leaves T_dead − 600 − 516 = 73 s for HG + PT at I_D = 400 s. In practice that does not fit.
- **With D-d,** G0\* rises to 420-613 s (§5 Table 3, right column). The waits needed then become comparable to 4-bit's.
- **Costs:**
  - it changes "4,096 tokens per turn" for last turns (CHAIR (B) Q6);
  - it raises the capped-turn fraction that FD's rung criterion reads;
  - it is a new cohort key value before D1 (CHAIR 10).
- Seat 2 rejected a lower per-turn cap but did not assess this narrower form. I keep it as a council option, not a first branch.

### D. Contrast and per-role caps (seat 2 F4, F7; PLAUSIBLE)

- The contrast deadman, 1,086.3 s (`align_v4_kit.py:700-701, 1034`), covers G0 and G1.
- The kit arms G0_cap_W1 for the contrast members too (shared `thermal_policy`, `:964-973`).
- With a D-to-X G0 of about 800 s or more, at most about 286 s remain for X-G, X-S, Y-G and Y-S at ordinals 6, 9, 12 and 15. Their planning costs are 850/1,150 s per member, that is about 333/633 s of episode after the 516.6 s intercept (P4:646-647).
- So contrast X7 is likely, and the T verdict risks INCONCLUSIVE.
- R1's X-G measures exactly this transition.
- This is arithmetic on planning values, not a measurement, so it stays PLAUSIBLE until R1. It motivates Decisions 4(b) and 7.

### E. Window length against `window_cap_s` = 44,640 s

The window maximum is 60·⌈(span + 17,700)/60⌉, the span limit is 26,940 s, and the base span is 26,927 s (P4:646-658; `align_v4_kit.py:56-58, 919-945`). Both seats' figures were re-derived.

| Variant | Span (s) | Window max (s) | ≤ 44,640? | Cost |
|---|---|---|---|---|
| Any fallback with D ≤ 1,800 s (steps 1 and 3, D-c, D-d) | 26,927 | 44,640 | yes (13 s slack) | none |
| Drop 18 only | 25,127 | 42,840 | yes | s93 (ruling 15's alternate sentinel) gets no W1 run |
| Step 2 (idle 450 after D) | 27,527 (seat 2) / 27,676 (seat 1) | 45,240 / 45,420 | no, so drop 18 | — |
| Step 2 + drop 18 | 25,727 | 43,440 | yes | loses s93; contrast bound 1,900 s (§3 A4) |
| S1: D member at 2,100 / 2,400 / 3,000 s | 28,727 / 30,527 / 34,127 | 46,440 / 48,240 / 51,840 | no (2,100 s fits only with 18 dropped: 44,340) | needs Ed (≤ 59,520); D_k 4 / 4 / 6 windows (seat 2 table, re-derived) |

Separately, the R1 night's no-redo worst case is 56,206.96 s (D8-3, LR2:632-658), and its plan `window_max_s` is still unset (LR2:301). This decides when the ruling can be applied.

### F. The fallback catalogue (merged)

| Option | Effect on 1(f) | Cures 8-bit? | Cures 4-bit? | Code / Mac time | Precision / power | Blinding / cohort |
|---|---|---|---|---|---|---|
| A1 fit rule (drop 18, lower B_D) | 1,024/r per step, then floor | no | no | none | fewer turns per session (s_r × 1.2-1.5, CHAIR §C) | none |
| 1(e) step 1, S6 ≤ 2.0 °C | lowers HG only | no | only combined | kit credit needs a gated re-run (about 2.5 h) | U5 harder (∝ δ_slow); print the energy band | none |
| 1(e) step 2, idle 450 s | −132 s T_dead; G0 credit only with an R1 re-run | no | no | kit binds 300 s; contrast 1,900 s | drops 18 | forks the D key or cuts T_dead for all D |
| 1(e) step 3, 4-bit | r × about 1.7-1.8 | n/a | corner under the current rule | 4-bit R0 + pins + kit identity + R1-4bit gated night | §3 B8 | new cohort; paper's model changes (Ed) |
| 1(e) step 4, screen-only | — | — | — | kit refuses as admission | no D claim | — |
| **D-d, budget-sized D G0 cap** | term = armed cap = G0\* | **if W_D ≲ 60-215 s** | **if W_D ≲ 340-490 s** | kit lane (receipt, per-role cap, cap < 600); no Mac time | X2 exposure instead of X7 | blind; cap revisable before D1 without forking the episode |
| D-c, final-turn truncation | −4,096/r | only with D-d | yes, wide | `workload.py` and kit cap check | capped last turns (rung criterion) | new cohort key value before D1 |
| D-e, bounded-risk 1(f) (series-wide only) | expected case plus X7 bound | likely, at a stated risk | yes | kit receipt | X7 erodes m ≥ 19 (what CHAIR 1 guards) | council |
| S1 / S2, member cap > 1,800 s | T_dead restated against C_D | yes | yes | `run_campaign.py:3776` (shared), kit L1, validator | 4-7 D_k windows; D5 at risk above about 2,500-2,800 s | Ed's Mac time; council |
| Rejected: B_D < 6,144, per-turn cap < 4,096, holds off, δ_slow > 2.0 °C, relaxing the G0 slope, precool outside the member, charging G0 to the idle-wait ledger | — | — | — | — | — | both seats' reasons stand (seat 2 §5b; seat 1 §4) |

---

## 4. What I dropped or downgraded, and why

- **Seat 1's claim that step-d sets B_D "near 16-20k" at 11-12 tok/s:** wrong. It is at most about 15.9k even at I_D = 300 s (`r1_runtime.py:794`).
- **Seat 1's claim that 8-bit "refuses at every B_D down to 1,024":** moot, because `validate_budget` floors at 6,144. It is also not exact: B_D = 1,024 fits at I_D = 400 s with a G0 term of 600 s and HG + PT = 60 s.
- **Seat 1's suggestion that R1's designed-state waits (R + 2 / R + 4 °C) bound the 30B → D transition:** unverified. The designed states are D planning turns from warm states, not 30B predecessors. Dropped.
- **Seat 1's claim that D-a saves "≤ 240 s":** understated, and in any case D-a is rejected (§3 B4).
- **The seats' G0-wait physics:** seat 1 predicts 0-300 s for D-after-D, seat 2 infers 440-640 s or more. Both are kept only as unmeasured predictions that bracket R1.
- **Seat 2's "R0 host record shows 16 CPUs":** not found in R0's host check. I replaced it with the 128 GB memory argument (§3 B2).
- **Seat 2's D5 threshold of about 2,520 s:** not reproduced (§3 B10).
- **Seat 2's 4-bit holds scaling, HG4 = HG × r8/r4:** a projection. It is kept only as a projection for branch selection, never as admission evidence.
- **Seat 2's S1/S2 C_D sizes (2,260-3,540 s) and its demo branches:** these are outputs of seat 2's tool (`opus/burn-w1fit@43b305425`). I did not re-run the tool. The window and D_k arithmetic behind them was re-derived (§3 E).
- **Seat 2's prefill rate of about 190 tok/s:** consistent with `/checks/4/generation` (109 tokens in 40.56 s after a SHADE prompt), but I did not re-check the prompt's token count.

---

## 5. Arithmetic (independent recomputation from the kit's formulas)

T_dead (L1, tail ≤ 40 s): I_D 300 → 1,277.0; 350 → 1,233.0; 400 → 1,189.0; 450 → 1,144.9; 516.6 → 1,086.3; 550 → 1,056.9; 600 → 1,012.8 s.

Step-d's B_D at 11.9 tok/s, with a 10k prefill at about 190 tok/s (`r1_runtime.py:794`): I_D 300 → 14,336; 400 → 13,312; 450 → 13,312; 516.6 → 12,288.

**Table 2. r (tok/s) needed at B_D = 6,144 under the current rule** (term = G0_cap_W1). Rows are I_D / HG+PT; columns are G0_cap_W1.

| I_D / HG+PT | 600 | 750 | 900 | 1,050 | 1,200 |
|---|---|---|---|---|---|
| 300 / 0 | 15.1 | 19.4 | 27.2 | 45.1 | 132.9 |
| 300 / 35 | 15.9 | 20.8 | 29.9 | 53.3 | 243.6 |
| 400 / 60 | 19.4 | 27.0 | 44.7 | 129.7 | ∞ |
| 400 / 150 | 23.3 | 35.4 | 73.7 | ∞ | ∞ |
| 450 / 100 | 23.0 | 34.7 | 70.7 | ∞ | ∞ |
| 516.6 / 60 | 24.0 | 37.1 | 81.1 | ∞ | ∞ |
| 516.6 / 150 | 30.5 | 55.0 | 282.3 | ∞ | ∞ |

This matches seat 1's Table B and seat 2's §4a, to 0.2 tok/s where they overlap.

**Table 3. G0\*, the largest G0 term (and armed D cap) that fits at B_D = 6,144.** Each cell is full last turn / truncated last turn (D-c).

| r (tok/s) | I_D 400, HG+PT 60 | 400, 100 | 400, 150 | 450, 100 | 516.6, 60 | 516.6, 100 | 516.6, 150 |
|---|---|---|---|---|---|---|---|
| 11.0 | 198 / 570 | 158 / 530 | 108 / 480 | 114 / 486 | 95 / 468 | 55 / 428 | 5 / 378 |
| 11.9 | 268 / 613 | 228 / 573 | 178 / 523 | 184 / 529 | 166 / 510 | 126 / 470 | 76 / 420 |
| 14.0 (8-bit ceiling) | 398 / 690 | 358 / 650 | 308 / 600 | 314 / 606 | 295 / 587 | 255 / 547 | 205 / 497 |
| 17.5 | 544 / 778 | 504 / 738 | 454 / 688 | 460 / 694 | 441 / 675 | 401 / 635 | 351 / 585 |
| 20.0 | 617 / 822 | 577 / 782 | 527 / 732 | 533 / 738 | 514 / 719 | 474 / 679 | 424 / 629 |
| 22.0 | 664 / 850 | 624 / 810 | 574 / 760 | 579 / 766 | 561 / 747 | 521 / 707 | 471 / 657 |

The current rule admits only where G0\* ≥ max(600, ceil(1.25 W_D)). D-d admits where G0\* ≥ ceil(1.25 W_D).

**Table 4. Largest fitting B_D with the G0 term = X** (D-d). Each cell lists I_D 400/HG+PT 60, 400/150, 516.6/60 and 516.6/150.
- r = 11.9:
  - X = 100 → 7,168, 6,144, 6,144, None;
  - X = 150 → 7,168, 6,144, 6,144, None;
  - X = 200 → 6,144, None, None, None;
  - X ≥ 300 → None.
- r = 20:
  - X = 300 → 12,288, 10,240, 10,240, 8,192;
  - X = 450 → 9,216, 7,168, 7,168, None;
  - X = 600 → 6,144, None, None, None.

**Ceilings:** 8-bit 400/28.58 = 14.0 tok/s (measured 11.9, 85 %); 4-bit 400/16.1 = 24.8 tok/s (about 21 at 85 %).

---

## 6. Mechanical decision procedure

### Now, before R1 arms (pre-declared, blind)

- **P1.** Record Decision 1 (the 8-bit verdict under the current rule) and this procedure in LR2 (a new round), with the deviation-log entry. Do this before any R1 number is read.
- **P2.** Read ruling 21's R0 capability proxy from the R0 dispositions: the fraction of ladder episodes with a state-changing tool call within the first 6,144 decode tokens, and the capped-turn fraction. If it is low, the 6,144 floor is a capability failure waiting to happen. The real choice is then rung against 4-bit (A1:155-157), not 1(f).
- **P3.** Build and cold-review the kit lane (Decision 4). The receipt fields are `{authority, branch, g0_term_rule, d_g0_cap_s, holds_term_rule, overshoot_rule, derivation}`. `--check` re-derives every number from `r1_slots`.
- **P4.** The magistrate decides 4-bit staging (Decision 5).
- **P5.** Settle Decision 6 (W1's final configuration) and Decision 7 (the contrast cap).
- **P6.** Ask Ed the questions in Decision 9.

### After R1: read only these `r1_slots` fields

- I_D and `max_r1_tail_s`, giving T_dead (L1);
- `deadman_budget[*].phases_s` (G0, G1, H, prefill, tool, decode), `decode_tokens`, `admitted_turns` and `g0_outcome`;
- `g0_cap_w1` (`waits_s`, `censored`, `x_g_fallback`);
- `budget_fit_inputs.r_decode_tok_per_s` (= r_min);
- `slots.B_D`;
- `inconclusive_segments`;
- `x_g.status` and `x_g.g0_wait_s`;
- `duty_bar.verdict` and `duty_bar.checks`;
- if it ran, the `d-4bit` step fields (r4, I_D4).

Nothing else is read: no energies, U5, β_T, residuals or W1 data.

### Compute

- HG_proj = max over runs of max(G1 + H, (G1 + H) / decode_tokens × 10,240).
- PT = max over runs of (prefill + tool).
- W_D = max released wait over D_bank, D_spam a and D_spam b. `censored_D` = any of those three not released.
- G0\*(r, T) = T − HG_proj − PT − 10,240/r.
- Then:
  - W(B) = G0_cap_W1 + HG + PT + (B + 4,096)/r_min, as the kit computes it;
  - gap = W(6,144) − T_dead.

### Steps

0. **`inconclusive_segments` non-empty, or step-d INCONCLUSIVE** → R1 re-run (R7-3, the magistrate's call). Stop.
1. **The kit fits** (`max_fitting_b_d` ≥ 6,144) → freeze B_D = that value (≤ `slots.B_D`) and run `fit_roster`. If the duty bar failed, record 1(e) step 1 as its `lead_fallback`. Stop. (This cannot happen at r < 15.1 tok/s.)
2. **Record 1(e) steps 1 and 2 as "still failing (arithmetic)"** whenever r_min < 10,240 / (T_dead − 600 − PT) (seat 2's best-case test). Step 2 is never applied for 1(f) (Decision 3).
3. **8-bit D-d.** If not `censored_D` and ceil(1.25 × W_D) ≤ G0\*(r_min, T_dead):
   - arm D's W1 `g0_cap_s` = floor(G0\*(r_min, T_dead));
   - B_D = the largest multiple of 1,024 ≥ 6,144 that fits with that term;
   - contrast members keep clamp(ceil(1.25 × X-G wait), 600, 1,200) per role.
   
   Record the X2 exposure: "a D member whose G0 exceeds G0\* = … s ends X2 before turn 1; R1's D waits were …".
   - Duty-bar receipt: 1(e) step 1, with S6 tuning only if R1's medians call for it.
   - W1 proceeds at 8-bit. Stop.
4. **3b, D-d with S6.** If step 3 fails only on HG, and passes with HG scaled to the S6 estimate (90 s divided by the larger recorded median G1 or H wait), branch to **S6 + gated re-run**. The magistrate re-runs the gated block and X-G at the tuned δ_slow (≤ 2.0 °C), then re-enters at step 0. Stop.
5. **4-bit.** Use r4 = the measured `d-4bit` rate, or 1.70 × r_min labelled as a projection. Use T4 from I_D4, or from I_D, and HG4 = HG_proj × r_min/r4 (projection).
   - If ceil(1.25 × W_D) ≤ G0\*(r4, T4), or the current rule already fits at r4, branch **STEP3-4BIT**: 4-bit R0, pins, kit identity, then an R1-4bit gated night. Re-enter at step 0 with 4-bit numbers. W1 waits; tell Ed (the named model changes).
   - If it fits only with the S6 scaling, branch **STEP1+3-4BIT-S6**: the R1-4bit gated block runs at the tuned S6.
   - Stop.
6. **STEP4-COUNCIL.** D is screen-only in this series unless council picks one of the following. The tool prints the sizing for each.
   - **S1:** an 8-bit member cap, C_D from T_dead′ = 1.25 W_D-based cap + HG_proj + PT + 10,240/r.
   - **S2:** 4-bit plus a cap.
   - **D-c with D-d.**
   - **Series-wide bounded-risk 1(f).**
   
   Seat 2's council rule: prefer the option with the fewest D_k windows among those with C_D ≤ 3,300 s and at most 5 windows, and prefer 8-bit on a tie. If none qualifies, the thermal regime itself is the problem (G0 slope criterion, hold intensity, High Power), and the question goes back to design.

**Before D1 (ruling 17, fixed now).** From W1's D members, read only the G0 waits (D-after-30B and D-after-D), admitted turns, decode tokens and X flags. D1's G0 cap may be revised by the same D-d or R7-2 rule. B_D, T_dead, quantization and max_tokens stay as W1 ran them (Decision 6). Every held-out window keeps the worst-case 1(f) assertion.

**Record.** Write the ruling text, all computed numbers (T_dead, r_min, HG, HG_proj, PT, W_D, G0\*, gap, the branch) and the deviation-log entry into LR2 before `align_v4_session.py install` runs. The kit receipt carries the same numbers.

**Expected outcome.** At the measured 11.9 tok/s, the branch is decided by W_D:
- W_D ≲ 60-215 s → step 3 (8-bit D-d);
- W_D ≲ 340-490 s → step 5 (4-bit);
- longer → step 6 (council).

Seat 2's R7-physics central case lands in council. Seat 1's held-episode physics lands in 8-bit D-d.

---

## Appendix A. Seat 1 report (Fable 5.1 seat), verbatim

````text
TOP: ["1(f) is structurally infeasible for 8-bit D on the M3 Max: the kit's G0 term can never be below 600 s and the floor's decode term is always 10,240 tokens, so the fit needs r_min >= 24 tok/s (I_D 516.6, 60 s holds+prefill) or >= 30 tok/s (150 s); the only recorded D rates are 11-12 tok/s (FD:145; r0-load-reference cold pass :29; R0 rerun-7 memory check 6,144 tokens in a 739.9 s check with a ~35k prefill). At 11-12 tok/s the gap at the floor is +410 to +545 s regardless of the measured G0 waits (break-even G0 cap 304-406 s, below the 600 s floor).","No kit path lets a 1(e) ruling admit W1 under a 1(f) refusal: DUTY_FALLBACK_STEPS (align_v4_kit.py:176) is honoured only by the duty-bar check (:294-298); the 1(f) refusal in check_r1_budget_and_policy (:628-633) is unconditional. Every fallback needs a kit change (a lead receipt with tests/reviews) or an R1 re-run; build that lane before R1.","The named 1(e) steps do not close the gap: step 1 (S6 tuning) changes only the holds term and not the recorded number the kit uses; step 2 (idle 450 s) shrinks T_dead by 132 s because idle is inside I_D, and breaks the 26,940 s span (27,676 s) unless ordinal 18 is dropped; step 3 (4-bit, ~19-20 tok/s) still misses the floor by +67 to +126 s with the 4,096 overshoot term and fits only in the corner G0_cap_W1 = 600, holds+prefill <= ~60 s, I_D <= ~450, or with final-turn truncation (B_D 7,168-8,192); step 4 ends D in W1.","The 20 tok/s premise in R7-2/R8-8 is unsourced; the R5-4 builder note (LEAD-RULINGS-2:61) used 11 tok/s. The brief's 15-30 tok/s grid is 4-bit territory; the 8-bit row is 11-12 tok/s and should be added to any lead table.","W1 has exactly one D-after-D transition (ordinal 18 after 17, after CHAIR 1(g)'s swap), the member the fit rule drops first; R6-1's D-after-D G0 measurement is right for the D-series and pessimistic for W1. A predecessor-appropriate G0 term for W1 (designed-state waits bound the 30B->D transition) is a legitimate blind refinement.","Recommended ruling shape: keep worst-case 1(f) for held-out windows; for W1 (development members, ruling 17 slot-filling pass) rule in the blind accounting refinements (G0 factor 1.0 in the term, per-token holds), then either a W1-only expected-case waiver with a recorded X7 bound (G0* = T_dead - holds - prefill - 10,240/r_min; at 8-bit only 46-194 s, so the waiver may itself fail) or the pre-registered 4-bit trigger (FD:254 read through CHAIR 1(f)) with final-turn truncation; decide by the mechanical procedure in section 7, reading only timing/count fields.","Window arithmetic: every fallback that keeps D members <= 1,800 s leaves W1 at span 26,927 s / window 44,640 s; idle 450 s after D predecessors needs ordinal 18 dropped (span 25,726 s, window 43,440 s) and costs the s93 development member (ruling 15's alternate sentinel); raising D members above 1,800 s is closed by the span limit even though run_campaign.py:11214 adds the unspent idle-wait budget to the 1,800 s kill.","Round-7 cold pass LOW-2(d) confirmed: an INCONCLUSIVE X-G sets the 1(f) G0 term to 1,200 s and needs r >= ~130 tok/s at the floor, so it is a W1 refusal in practice."]
OPEN: ["What decode rate did the R0 reruns actually record for D at short context (the ladder and long-decode did not run in rerun 7)? If a measured 8-bit rate above ~22 tok/s exists somewhere on the Mac, the whole analysis shifts one column; the repo only evidences 11-12 tok/s.","Does the lead read CHAIR 1(f) as superseding FD:253's B_D definition, so that `max_fitting_b_d = None` is FD:254's pre-registered 4-bit trigger? If yes, step 3 of 1(e) is a consequence, not a deviation, and the 16.1 GB 4-bit should be downloaded before R1 so `d-4bit` runs that night.","Should the 1(f) G0 term for W1 be the D-after-D wait (R6-1) when only ordinal 18 follows a D, and should it be predecessor-specific if the fit rule drops 18? Which `g0_waits` entries (designed states at R+2/R+4 degC) may bound the 30B->D transition?","Is final-turn truncation (`max_tokens_k = min(4096, B_D - used)`) acceptable as a cohort definition before D1, given the paper names '4,096 tokens per turn' (CHAIR B6) and capability scoring of cap-ended turns?","May a W1-only waiver of the worst-case 1(f) be recorded under the lead's prereg authority, and what X7 bound is acceptable for development members (suggested: no more than 1 of 4 counted R1 waits above G0*, expected-case fit <= T_dead)?","Will the lead accept the two blind accounting refinements (G0 factor 1.0 in the 1(f) term while the armed cap keeps 1.25x; per-token scaling of the holds term) as rulings before R1, so the kit lane can carry them?","R1 plan `window_max_s` is still unset against a 56,207 s no-redo worst case (D8-3); when is the R1 night, and can the kit lane for the 1(e) receipt be reviewed before it lands so W1 is not delayed a day?"]
# W1 budget-fit (ruling 1(f)) and the 1(e) fallback — Fable seat audit

Fable 5.1 seat, 2026-11-07. Sources read at `lane/2026-11-06-v4-r1-integrated@e901eb2a4` unless another ref is named: `docs/align/council-2026-11-06-v4-review/CHAIR.md`, `LEAD-RULINGS-1.md`, `LEAD-RULINGS-2.md`, `docs/align/pilot_protocol_v4.md`, `scripts/align_v4_kit.py`, `scripts/align_r1_rehearsal.py`, `joulewise/align/apple/{r1_runtime,workload,thermal_gates}.py`, `configs/campaigns/align_v4/night_plan.template.json`, `configs/align/v4/r1_runtime.json`, `docs/align/thermal_gates.md`, `docs/align/r1_runtime_contract.md`, the round-7 cold pass; FINAL-DESIGN (FD) and Amendment 1 (A1) on `origin/main`; the R0 rerun-7 record on `origin/records/2026-11-07-align-r0-v4-rerun7`. Nothing under `jw-b5-*`, `night-*`, custody/archive or `restricted/` was opened; no Block-5 value was inferred. No tests were run; no weights loaded; no commits, PRs or comments. Worktree `jw-wt/fable-w1audit` was created and removed.

## 0. Bottom line

1. **The refusal is structural, not a tuning outcome.** The kit's 1(f) term is `G0_cap_W1 + max(G1+H) + max(prefill+tool) + (B_D + 4,096)/r_min ≤ T_dead` (`scripts/align_v4_kit.py:469-524`). Two of its parts are fixed by design: the G0 term can never be below 600 s (`w1_g0_cap`, `:461-465`, floor `thermal_gates.G0_CAP_DEFAULT_S = 600`), and the decode term at the 6,144 floor is always 10,240 tokens (an admitted last turn keeps its full 4,096 cap, FD:263; `workload.py:501` admits while `used < B_D`). T_dead is at most 1,541 s and realistically 1,050-1,190 s (`l1_t_dead`, `:705-708`; I_D includes the 300 s idle). So at the floor 1(f) needs `r_min ≥ 10,240 / (T_dead − 600 − holds − prefill)`: **≥ 24 tok/s** at I_D = 516.6 s with 60 s of holds+prefill, **≥ 30 tok/s** with 150 s.
2. **The 20 tok/s premise is unsupported; the recorded D rate is 11-12 tok/s.** FD:145 plans D at ~11 tok/s; the R0-load cold pass records "the rerun's 11-12 tok/s" (`docs/align/reviews/2026-11-06-r0-load-reference-fable-cold-pass.md:29`); R0 rerun 7's memory check decoded 6,144 tokens at positions ≥ 34,817 inside a 739.9 s check that also held a ~35k-token prefill (`docs/align/r0/2026-11-07-rerun7/report.json:32918-32932` on the records branch), i.e. ≤ 8.3 tok/s gross at deep context. The Mac is a Mac15,9 M3 Max (`docs/align/v4/PREQUAL.md:4`); 29.5 GB of 8-bit weights per token (`fable-cold.md:113`) caps dense decode near 11-13 tok/s at that bandwidth. The brief's grid (15-30 tok/s) should be read as "4-bit territory"; the 8-bit row is 11-12.
3. **At 11-12 tok/s, 8-bit D cannot satisfy worst-case 1(f) at any B_D ≥ 1,024, for any measured G0, at any plausible I_D.** The gap at the floor is +410 to +545 s (Table B). Even with the 4,096 overshoot term removed it is still +67 to +172 s. 4-bit (~1.7× rate, ~19-20 tok/s) closes the gap only in the corner G0_cap_W1 = 600 ∧ holds+prefill ≤ ~60 s ∧ I_D ≤ ~450, or with the overshoot term removed (Table C).
4. **No kit path exists for any 1(e) ruling to admit W1 under a 1(f) refusal.** `DUTY_FALLBACK_STEPS` (`:176`) is honoured only by the duty-bar check (`:294-298`); the 1(f) refusal in `check_r1_budget_and_policy` (`:628-633`) is unconditional and runs before it. R6-3 ("no code fallback") therefore means every fallback the lead picks needs either a kit change (a lead receipt the kit honours, with tests and the usual reviews) or an R1 re-run under the changed slot. Of the four 1(e) steps, step 1 (S6 tuning) leaves the recorded holds term untouched, step 2 (idle 450 s) *shrinks* T_dead by 132 s and is at best a wash, step 3 (4-bit) needs its own R1 and still only fits in a corner, and step 4 ends D in W1.
5. **Recommended ruling shape (§7):** keep worst-case 1(f) for D1 onward (held-out members, the m ≥ 19 floor), but for W1 — whose D members are development members entering no pool (CHAIR 17) and whose own purpose is to fill B_D/T_dead (ruling 17) — replace the worst-case assertion with a bounded, recorded X7 risk computed from R1's numbers, arm at the floor, and let W1's realized G0 waits and turn counts size D1 (or trigger 4-bit). Decide it mechanically with the procedure in §7, blind to every energy and residual value.

## 1. What the kit asserts, exactly

- `ruling_1f_fit` (`align_v4_kit.py:469-524`): `worst = G0_s + holds_s + prefill_tool_s + decode_s` with `G0_s = w1_g0_cap(...)['value_s']`, `holds_s = max over the 3 gated runs of (G1 + H)`, `prefill_tool_s = max of (prefill + tool)`, `decode_s = (B_D + turn_cap)/r`, `r = min(step-d rate, every gated run's decode_tokens/phases_s.decode)` (R6-3). `fits = worst ≤ T_dead`.
- `w1_g0_cap` (`:419-466`): `value_s = clamp(ceil(1.25 × max counted wait), 600, 1200)`; an unreleased gated G0 counts at 1,200; an X-G not `measured` counts at 1,200 (R7-12). So **G0_s ≥ 600 always**, and ≥ 750 as soon as any counted wait exceeds 480 s.
- `max_fitting_b_d` (`:527-536`) scans multiples of 1,024 from `min(slots.B_D, 40960)` down to `BUDGET_FLOOR = 6144` (`:58`); `validate_budget` (`:914-916`) refuses anything below 6,144, so the kit cannot be talked into a smaller B_D.
- `check_r1_budget_and_policy` (`:539-634`) refuses on `not fit['fits']` with no receipt path; `check_r1_evidence` (`:179-298`) calls it (`:282`) before the duty-bar fallback check (`:294-298`).
- T_dead: `l1_t_dead` (`:705-708`) = min((1750 − I_D)/1.13544, (1800 − I_D − tail − 10)/1.13544). `derive_step_d_slots` measures I_D as member wall minus episode-from-G0 (`r1_runtime.py:779-781`), so the 300 s configured idle (`night_plan` member configs, `sampling.idle_seconds = 300`), model load, warmup and teardown are all inside I_D. The 30B intercept is 516.6 s (`align_v4_kit.py:700`); a 29.5 GB load makes D's I_D unlikely to be lower.
- The G0 wait lives inside T_dead by design ("Reserve no additional G0 allowance", `workload.py:426-430`; `docs/align/thermal_gates.md:115-121`). Any attempt to move G0 out is zero-sum against the 1,800 s member cap (`run_campaign.py:3776`).
- The duty bar (`align_r1_rehearsal.py:83, 771-781`): no X7, ≥ 3 admitted turns, G0+G1+H ≤ 0.40 × T_dead. Its `lead_fallback` receipt (`align_v4_kit.py:294-298`) is the only 1(e) hook in code.

## 2. Arithmetic grid

T_dead by I_D (L1 first term; tail ≤ 40 s): I_D 350 → 1,233 s; 400 → 1,189; 450 → 1,145; 516.6 → 1,086; 550 → 1,057; 600 → 1,013.

**Table A. Worst case at B_D = 6,144 (10,240 tokens), holds+prefill+tool (hp) = 100 s. `*` fits T_dead = 1,086 (I_D 516.6); `†` fits 1,145 (I_D 450).**

| r (tok/s) | G0 = 600 | 750 | 900 | 1,200 |
|---|---|---|---|---|
| 11 | 1,631 | 1,781 | 1,931 | 2,231 |
| 12 | 1,553 | 1,703 | 1,853 | 2,153 |
| 15 | 1,383 | 1,533 | 1,683 | 1,983 |
| 18 | 1,269 | 1,419 | 1,569 | 1,869 |
| 20 | 1,212 | 1,362 | 1,512 | 1,812 |
| 25 | 1,110 † | 1,260 | 1,410 | 1,710 |
| 30 | 1,041 *† | 1,191 | 1,341 | 1,641 |

**Table B. Required r_min at the floor** = 10,240 / (T_dead − G0 − hp):

| I_D / hp | G0 600 | 750 | 900 | 1,050 | 1,200 |
|---|---|---|---|---|---|
| 400 / 60 | 19.4 | 27.0 | 44.7 | 130 | ∞ |
| 400 / 150 | 23.3 | 35.4 | 73.7 | ∞ | ∞ |
| 516.6 / 60 | 24.0 | 37.1 | 81.1 | ∞ | ∞ |
| 516.6 / 150 | 30.5 | 55.0 | 282 | ∞ | ∞ |

**Table C. Largest fitting B_D** (None = refuse at the floor), hp = 100, I_D 516.6: r = 20 → None at every G0; r = 25 → 6,144 only at G0 = 600 and hp ≤ 60; r = 30 → 8,192 at G0 = 600, None at ≥ 750; r = 36 (4-bit optimistic) → 10,240 at G0 = 600, 7,168 at hp 150, None at ≥ 750; r = 45 → 14,336 / 8,192 (G0 600/750). At I_D 400 add roughly one 1,024 step and one G0 column.

**Table D. Gap at the floor (W − T_dead), G0 = 600, hp = 100; second figure with the 4,096 overshoot term removed (final-turn truncation, §4 D-c):**

| r | I_D 450 | I_D 516.6 |
|---|---|---|
| 11 | +486 / +114 | +545 / +172 |
| 12 | +408 / +67 | +467 / +126 |
| 15 | +238 / −35 | +296 / +23 |
| 18 | +124 / −104 | +183 / −45 |
| 20 | +67 / −138 | +126 / −79 |
| 25 | −35 / −199 | +23 / −141 |

**Table E. Break-even G0 cap at the floor** (hp 100): r = 11.5 → 304 s (I_D 516.6) / 406 s (I_D 400), both below the 600 s floor; r = 20 → 474 / 577, still below 600; r = 25 → 577 / 679; r = 30 → 645 / 748; r = 36 → 702 / 805. So **at any r ≤ ~22 tok/s the kit refuses regardless of what the gated G0 waits are**, and at 4-bit rates it refuses whenever any counted wait exceeds ~480-560 s.

**Table F. X7-free G0 wait, G0\* = T_dead − hp − 10,240/r** (the longest G0 a D member can wait and still be guaranteed no deadman at the floor): r 11.5 → 46-194 s; r 19.5 → 411-560 s. For a *typical* episode (6,144-8,192 tokens, not the worst case) at 11.5 tok/s the headroom for G0 is 274-452 s (I_D 516.6). The X7 risk at 8-bit is therefore not a tail event: a 300-450 s G0 plus an ordinary xhigh episode sits at T_dead.

Physics cross-check on G0 waits (R7-2 input): after the 900 s full-load step no key met 0.2 °C/min until 840-1,040 s, τ ≈ 430-510 s. The slope criterion |dS/dt| ≤ 0.2 °C/min with τ = 470 s is equivalent to "excess over the asymptote ≤ 1.57 °C"; the wait is τ·ln(A/1.57) for an initial excess A: A = 10 °C → ~870 s, 4 °C → ~440 s, 2 °C → ~115 s. A gated, held D episode ends within ~2·δ_slow of its G0 release (holds keep S_slow ≤ E + δ_slow), so after the 300 s idle the slope-limited D-after-D wait should be 0-300 s, not 900 s — unless the band part binds because the slow key never returns to the cold soak R + δ_slow late in the night (chassis warming). Expect G0_cap_W1 = 600 or 750 more often than 1,200, but Table E shows that does not rescue 8-bit.

## 3. What each named 1(e) step does to 1(f)

| Step (CHAIR 1(e)) | Effect on the 1(f) gap | Kit/code | Mac time | Window/span | Notes |
|---|---|---|---|---|---|
| 1. S6 tuning: δ_slow ≤ 2.0 °C jointly for G1 and holds (median ≤ 90 s) | Reduces only `holds_s`; typically 50-250 s. G1/H have no slope term, so widening the band shortens them directly; G0's slope criterion is untouched, so `G0_s` is unchanged. The kit's `holds_s` is the *recorded* R1 total; a tuning receipt (`s6_tuning`, `:619-627`) changes `delta_slow_c` but not that number. | Kit must accept a re-derived holds term (recompute each recorded G1/H wait as time-to-5-samples ≤ E + 2.0 °C from the 1 Hz journal) or R1 is re-run at S6. | 0 (journal recomputation) or ~15.6 h (re-run) | none | Never closes a +400-545 s 8-bit gap alone. |
| 2. Idle 300 → 450 s after D predecessors | Negative for the deadman: I_D + 150 → T_dead − 132 s (idle is inside the member, `run_benchmark` idle_baseline, R6-1). Shortens the D-after-D G0 wait by ≤ 150 s, but the kit's G0 term is R1's 300 s-idle measurement, so no credit without an R1 re-run. Net ≈ 0 or worse. | Kit: `w1_inter_member_idle_s` binds `duty_bar.schedule` to the member configs' idle (`:289-293`), so changing configs to 450 refuses the 300 s R1 record. Single I_D/T_dead for all D members (`inputs.R1`), so a per-ordinal idle needs a kit change too. | R1 re-run | +150 s × 5 followers (6, 9, 12, 15, 18) = +750 s → span 27,676 > 26,940 → fit rule drops ordinal 18 → span 25,726, window 43,440 s. | Contrast-neutral: each arm has exactly one D predecessor (A1 table). Useful for the duty bar's G0 share, useless for 1(f). |
| 3. 4-bit at the same rung | r × ~1.6-1.8 (16.1 GB vs 29.5 GB weights; FD:255). At ~19.5 tok/s the floor still misses by +67 to +126 s with the overshoot term (Table D) and fits only at G0 = 600 ∧ hp ≤ ~60 ∧ I_D ≤ ~450; with final-turn truncation it fits at B_D 7,168-8,192 for G0 = 600 (Table C). | `r1_runtime.json` `d_4bit_source` is null; needs the download, the W1 disk gate (≥ 80 GB free), and a 4-bit R1 (step-d-4bit + 3 gated runs + X-G, ≥ 4-5 h best case; the kit's rate/holds come from gated rows, so a step-test alone cannot feed 1(f)). | ≥ 0.3-1 night | none | Halves e_D: MDE in tokens doubles under energy-fraction misfit (CHAIR C), unchanged under token-model misfit. New cell; capability is "selection data again" (A3.7); the paper's named model changes (CHAIR B6). FD:254's own trigger ("B_D < 6,144 at 8-bit → 4-bit") is literally what `max_fitting_b_d = None` means if the lead rules that CHAIR 1(f) is the operative B_D sizing. |
| 4. D screen-only, return to council | — | Never admits (`DUTY_FALLBACK_STEPS = (1,2,3)`, `:172-176`). | 0 | W1 without D needs a re-cut plan; `fit_roster` forbids cutting the 5/17 pair (`:919-945`). | Loses W1's D yield entirely (U1-U3 for D, capability gate, rates, 5/17 U3 pair). |

Other protocol-allowed instruments: the A1 fit rule (drop 18, then lower B_D, then lead; `fit_roster`, `:919-945`; protocol v4:654-658) governs span, not T_dead; ruling 17 makes W1 a second slot-filling pass that may revise δ_slow, G_turn, N_chunk, B_D and T_dead before D1 (CHAIR:194-196; protocol v4:626) — this is the hook the recommendation uses; the U1-U3 escalation ladder (FD:400-405, ruling 14 direction-conditional) is the registered response if W1's D fails U1 on timeouts.

## 4. Minimal deviations that preserve the pre-registered estimand

The estimand (per-pair conformal threshold on residual scores, H\*, benign-carrier curve) does not depend on how 1(f) is accounted; 1(f) only controls X7/X2 loss. All of these are blind (they read only R1 timing fields) and must be recorded in LEAD-RULINGS before W1 arms, with the public deviation log entry.

- **D-a. G0 term = max counted wait, factor 1.0 (or 1.25 kept for the *cap* `g0_cap_s` but not for the 1(f) term).** Saves 0.25 × max wait, ≤ 240 s, only when max wait < 960 s. Kit: `ruling_1f_fit` reads `g0_cap['max_g0_s']` instead of `value_s`. Risk: none to blinding; the cap W1 arms stays generous.
- **D-b. Predecessor-appropriate G0 term for W1.** After CHAIR 1(g), only ordinal 18 (development s93) follows a D in W1; 5, 8, 11, 14, 17 follow 30B members (A1 roster; template roles). R1's gated waits (D-after-D, R6-1) are the right bound for D-series windows, a pessimistic one for W1. If the fit rule drops 18, every W1 D G0 follows a 30B member, and the R1 record's designed-state waits (`r1_slots.g0_waits`, R + 2 / R + 4 °C states) bound that transition. Kit change; needs the lead to name which waits count.
- **D-c. Final-turn truncation: `max_tokens_k = min(4,096, B_D − used)`.** Removes the 4,096 overshoot term (saves 4,096/r: 356 s at 11.5 tok/s, 210 s at 19.5). Changes `workload.py` admission/cap semantics and the kit's `turn_cap_tokens` check (`:515-517`, which reads anchor 1's `max_tokens`); a new cohort key value before D1 is allowed (ruling 10). Cost: the last turn can be cap-ended with unclosed reasoning (capability scoring); X2/X7 semantics unchanged. Note that "budget-reserving admission" (admit only if used + 4,096 ≤ B_D) is *not* a lever: it equals the current rule with B_D shifted by 4,095.
- **D-d. G0 cap sized to the budget (X7 → X2 conversion).** Set W1's `g0_cap_s = G0*` (Table F): a member whose G0 does not release by G0\* ends before turn 1 (`episode.g0_unreleased`, round-4 decision) instead of risking a deadman mid-episode. Same member lost either way for calibration; X2-at-G0 spends no T_dead, keeps the window short and leaves a clean bundle. Needs `thermal_gates.validate_gate_policy` to accept a cap below 600 (`thermal_gates.py:102-105`) and a kit rule `G0_term = g0_cap_s`. Only useful if R1's released waits are mostly below G0\*; at 8-bit G0\* ≈ 50-200 s, so most members would be X2 — a non-starter at 8-bit, viable at 4-bit (G0\* ≈ 410-560 s).
- **D-e. W1-only expected-case waiver.** Replace the worst-case assertion for window 1 by: `median released gated G0 wait + holds_s + prefill_tool_s + (B_D + 4,096)/r_min ≤ T_dead`, plus a recorded X7 bound (fraction of R1's counted waits above G0\*, and the per-member risk statement). Kit: an `inputs.R1.ruling_1f_waiver {authority, window: 1, terms, derivation}` honoured only when the plan's `window == 1`; D1's freeze re-asserts the worst case. At 8-bit and 11.5 tok/s even this may fail (Table F): typical-episode headroom for G0 is 274-452 s.
- **D-f. Per-token scaling of the holds term** (`holds_s × (B_D + 4,096)/decode_tokens_of_that_run`, plus one maximal G1 wait). More accurate when the gated runs decoded far more than 10,240 tokens at `slots.B_D` (which step-d will set near 16-20k at 11-12 tok/s: `r1_runtime.py:794-796`). Saves 0-40 % of holds. Reinterpretation of "worst-case R1 holds"; lead's call.
- **Rejected or closed levers.** Lower per-turn cap (2,048): changes the named model ("4,096 tokens per turn", CHAIR B6) and the R0 rung evidence; shorter idle: redefines R capture (ruling 18 rejects); G0 outside T_dead: zero-sum under the 1,800 s member kill; raising the member cap: `run_campaign.py:11214` adds the remaining idle-wait budget (≤ 1,500 s, `idle_wait.py:10-11`) to the 1,800 s kill, but that budget is the idle-admission pool and the W1 span is already at 26,927 of 26,940 s with D at 1,800, so any larger D member breaks the span (Table G); T_dead above L1: `require_ready` enforces L1 (`:667-671`).

## 5. Window length vs `window_cap_s` 44,640 s

Window max = 60·⌈(span + 3,300 + 7,200 + 7,200)/60⌉ (`b6/plan_inputs.py:56-59`); span limit 26,940 (`SPAN_LIMIT_S`, `:56`); base span 26,927 (A1, `sizing_preview.json`).

| Variant | Span (s) | Window max (s) | Fits 44,640? |
|---|---|---|---|
| Any fallback keeping D members ≤ 1,800 s (steps 1, 3, D-a..D-f) | 26,927 | 44,640 | yes (13 s slack) |
| Idle 450 s after D predecessors | 27,676 | 45,420 | no → drop 18 |
| Idle 450 + drop 18 | 25,726 | 43,440 | yes; loses the s93 development member (ruling 15's pre-named alternate sentinel gets no W1 run) |
| D members 2,000 s (member cap raised) | 28,126 | 45,840 | no; with 18 dropped 26,126 → 43,860 |
| Screen-only (no D) | plan re-cut | — | fit_roster refuses; council |

Separately, the R1 night's no-redo worst case is 56,207 s (D8-3) and its plan `window_max_s` is still unset (R6-8 deviation); not a W1 item but it decides when the 1(e) ruling can be applied.

## 6. Blinding and prereg fidelity

- Every input of the decision is a timing or count field of `r1_slots` (I_D, tails, `phases_s`, `g0_waits`, `decode_tokens`, rates, `admitted_turns`, `slots.B_D`) and the R0 capability proxy (ruling 21). None is outcome-bearing for any registered claim; R1 is a rehearsal and W1's D members enter no pool. The procedure must not read `energy_j`, U5/β_T, residuals, or anything from W1 before W1 runs; the D1 re-sizing after W1 reads only W1's G0 waits, turn counts and X flags, never its energies (fix that now, §7 step 6, so B_D cannot be chosen on residual appearance).
- Block 5 is untouched: no path under `jw-b5-*`/`night-*`/restricted was read, and nothing here depends on a Block-5 value.
- Prereg fidelity: CHAIR 1(f) is an engineering guard (it exists to keep X7 from eroding m ≥ 19, CHAIR:10, 27); loosening it for W1 only, blind and logged, is within "proportionate care" and the lead's prereg authority; loosening a U-bar margin is not (FD:407) and none of §4 does that. A change of B_D, T_dead, max_tokens or max_turns before D1 is a cohort definition, not a deviation (ruling 10, CHAIR D7).

## 7. Decision procedure (apply mechanically the morning after R1)

**Prepare now (before R1):** (P1) read ruling 21's R0 proxy from the R0 dispositions — the fraction of ladder episodes with a state-changing tool call within the first 6,144 decode tokens; if it is low, B_D at the floor is a capability failure in waiting and the real choice is rung-vs-4-bit (A3.7), not 1(f). (P2) open the kit lane that adds (a) a lead receipt `inputs.R1.ruling_1f` with fields `{authority, window, g0_term_rule, holds_term_rule, overshoot_rule, accepted_x7_bound}` honoured by `ruling_1f_fit`, (b) D-a/D-b/D-f as selectable rules, (c) the W1-only waiver with D1 re-assertion, each with failing-first tests; have it reviewed cold so it can merge the day R1 lands. (P3) decide whether the 16.1 GB 4-bit download and `d_4bit_source` go in before R1 so the optional `d-4bit` step runs that night (FD:255 says yes if R0's rates predict the switch — at 11-12 tok/s they do).

**Read from `r1_slots`:** I_D, `max_r1_tail_s` → T_dead (L1); `g0_cap_w1` (value_s, waits_s, censored); `deadman_budget[*].phases_s`, `decode_tokens`, `admitted_turns`; `budget_fit_inputs.r_decode_tok_per_s` (= r_min); `slots.B_D`; `duty_bar.verdict`; `inconclusive_segments`; `x_g.status`.

**Compute:** `H = max(G1+H)`, `P = max(prefill+tool)`, `W(B) = G0_s + H + P + (B + 4,096)/r_min`, `gap = W(6,144) − T_dead`, `G0* = T_dead − H − P − 10,240/r_min`, `n_over = number of counted released waits > G0*`, `W_exp = median released wait + H + P + (6,144 + 4,096)/r_min`.

1. **Any `inconclusive_segments` or step-d INCONCLUSIVE** → R1 re-run, magistrate's call (R7-3). Stop.
2. **gap ≤ 0** → no ruling; the kit freezes `B_D = min(max_fitting, slots.B_D)`. Stop. (Does not happen below ~22 tok/s.)
3. **Rule in the accounting refinements unconditionally** (blind, more accurate, not margin-loosening): D-a (factor 1.0 in the 1(f) term, cap unchanged) and D-f (per-token holds). Recompute `gap'`. If `gap' ≤ 0` → freeze and stop.
4. **If `r_min ≤ 14 tok/s` (8-bit at this Mac):** worst-case 1(f) is infeasible at every B_D (Table D). Choose by the R0 proxy and `G0*`:
   - 4a. If `W_exp ≤ T_dead` and `n_over ≤ 1 of 4` and the R0 proxy shows actions within 6,144 tokens → **W1-only waiver (D-e)** at B_D = 6,144, T_dead per L1, `g0_cap_s = G0_cap_W1`; record the X7 bound ("a D member whose G0 wait exceeds G0\* = … s can end X7; R1 saw n_over/4 such waits"); W1 proceeds; U1 for D decides the ladder before D1 (FD:401, ruling 14).
   - 4b. Otherwise → **4-bit (step 3) is the pre-registered consequence** (FD:254 trigger read through CHAIR 1(f)); schedule the 4-bit R1 (step-d-4bit + gated block + X-G) and re-enter this procedure with its numbers; W1 waits. Record that 8-bit D at the R0 rung is "screen-only unless 4-bit fits" (step 4 only if 4-bit also fails).
5. **If `r_min > 14 tok/s` (4-bit, or an unexpectedly fast 8-bit):** if `gap' ≤ 4,096/r_min` → **D-c final-turn truncation** closes it; freeze B_D = largest fitting under D-c (Table C: 7,168-8,192 at G0 = 600). Else if `G0* ≥ 400 s` and `n_over = 0` → **D-d** (cap the W1 G0 at G0\*, X7 → X2) with B_D at the largest fitting value. Else → 4a's waiver test; else step 3/4 of 1(e).
6. **Before D1 (ruling 17), fixed now:** from W1's D members read only `g0_wait_s`, `admitted_turns`, decode tokens and X flags; set D1's `g0_cap_s = clamp(ceil(1.25 × max W1 D-after-30B and D-after-D released wait), 600, 1200)`, `B_D` = the largest value for which worst-case 1(f) (with D-a/D-f) fits against the W1 rates; if none ≥ 6,144 → 4-bit for the D-series. Every held-out window keeps the worst-case assertion.
7. **Record:** the ruling text, the computed numbers (T_dead, G0_s, H, P, r_min, gap, gap', G0\*, n_over, W_exp), the chosen branch, and the deviation-log entry, in LEAD-RULINGS-3 before `align_v4_session.py install` runs; the kit receipt carries the same numbers so `--check` re-derives them.

**Table G (for step 6).** Expected D1 consequence by branch: waiver → D1 sized from W1 data, 8-bit kept if W1 X7 count ≤ 1 of 6 and U1 passes; 4-bit → e_D ≈ 1.8 J/token, MDE central 300-500 → up to 600-1,000 tokens under misfit-as-energy-fraction, unchanged under token-model misfit; truncation → shorter final turns in every trajectory (cohort definition), no MDE change; screen-only → no D-series.

## 8. Findings against the brief's premises

- "Refuse at every B_D down to the floor": confirmed, and stronger — at the recorded 11-12 tok/s it refuses at every B_D the runtime accepts (down to 1,024) for any G0 and any I_D ≥ ~500, and the 1(e) named order cannot fix it (§3).
- "Decode around 20 tok/s": not evidenced anywhere in the repo; the three recorded figures are 11, 11-12 and ≤ 8.3 (deep context). The builder's R5-4 note (LEAD-RULINGS-2:61) already computed with 11 tok/s; R7-2/R8-8 shifted to "about 20" without a source.
- "1(e) must be ruled after R1 on its numbers": true, but the ruling is not expressible to the kit without a code change (§0.4); the lane should be built and reviewed before R1 so the ruling does not cost a day of Mac idle.
- R6-1's D-after-D duty bar measures the D-series' typical transition; in W1 it describes one member (18), the one the fit rule drops first (§4 D-b).
- The round-7 cold pass LOW-2(d) is confirmed: an INCONCLUSIVE X-G is a W1 refusal in practice (G0_s = 1,200 needs r ≥ 130 tok/s at hp 60).
````

## Appendix B. Seat 2 report (Opus 5.5 seat), verbatim

````text
TOP: ["At 8-bit, ruling 1(f) cannot pass at B_D 6,144 for any R1 thermal outcome. Even with zero G1 and hold time, G0_cap_W1 at its 600 s floor, I_D = 300-350 s and PT = 35-40 s, the floor needs r >= 16-17.3 tok/s. The Mac15,9's 8-bit limit is 400 GB/s / 28.58 GB = 14.0 tok/s, and R0 measured 11.85-11.95 tok/s. The R1 night cannot change the 8-bit verdict, so the lead can pre-rule that branch now.","The brief's ~20 tok/s premise does not match the repo. R0 re-runs 5 and 7 (@ea89c4d3f, @7bdfdae6e, report.json /checks/4, /checks/6) record about 11.9 tok/s for 8-bit D, and FD:145 uses 11 tok/s. LEAD-RULINGS-2:363 and :593 carry the 20 tok/s figure, which is the 4-bit regime (limit 24.8 tok/s).","1(e) steps 1 and 2 cannot cure an 8-bit failure. Step 2's extra idle sits inside I_D: it costs 132 s of T_dead against at most 187.5 s off G0_cap_W1, a net of -132 to +55 s. Applied 'after D predecessors' as written, it pushes the 30B contrast members to a 1,900 s bound (over 1,800 s) and forks the D cohort key. In W1 it forces the fit rule to drop ordinal 18, the only D-after-D member.","1(e) step 3 (4-bit) fits only in a corner: r4 >= ~20-22 tok/s, G0_cap_W1 = 600 s (every counted gated G0 within 480 s) and HG + PT <= ~80-150 s. The R7 physics input (G0 settles 840-1,040 s after load; G1 at 279 s) makes this unlikely, so the expected end state is 1(e) step 4 and council.","What binds is the 1,800 s member cap against G0 + G1 + holds, not B_D. The fix that keeps the estimand is a plan-declared D member cap (S1; about 2,260-3,540 s at 8-bit) or 4-bit plus a smaller cap (S2; about 1,980-2,820 s). Both put W1 at Ed's 59,520 s D-window maximum (46,440-55,080 s needed) and need 4-7 D_k windows instead of 3. Ruling 3's D5 cap holds only if C_D <= ~2,520 s.","G0_cap_W1 = 1,200 s, set by any censored gated G0 or one inconclusive X-G under R7-12, makes 1(f) infeasible at every decode rate, because T_dead (about 1,083-1,233 s) is below 1,200 s. An armed G0 cap at or above T_dead also means X7 always fires before X2. R7-12's own wording ('D-to-X G0 term') supports one cap per role, which would remove the path by which an X-G deadman forces the D refusal.","1(f)'s holds term understates when R1's gated runs are cut by the deadman, which is likely for all three at 8-bit: max(G1+H) comes from truncated runs while the decode term assumes the full B_D + 4,096. Any S1 or S2 sizing should project holds per decoded token to 10,240 tokens, or commit the per-gate waits into r1_slots.","Contrast risk independent of D: G0_cap_W1 is also armed on the contrast members, whose 1,086.3 s deadman covers G0. At G0 >= 800 s after a D predecessor, <= 286 s remain for a 12-turn pilot-7 episode plus 11 G1 gates, so X7 is likely and the T verdict goes INCONCLUSIVE. R1's X-G decides this. Protocol v4:365 ('every other G0 keeps 600 s') is ambiguous on whether contrast members are exempt.","Before R1 arms: d_4bit_source is null (configs/align/v4/r1_runtime.json:12), so this R1 night gives no numbers for step 3. FD 2.2:255 says the 4-bit is downloaded and step-tested in R1 when R0's rates predict the switch, and under 1(e)'s extended trigger they do. Separately, W1 must run in the final D configuration, because ordinal 5 is the D_k sentinel original and feeds ruling 6's E_ref."]
OPEN: ["Where does the lead's ~20 tok/s expectation for 8-bit D come from? On-repo evidence (R0 re-runs 5 and 7, FD:145) and the M3 Max 400 GB/s bandwidth limit put it at about 11-12.5 tok/s.","Should the magistrate stage the optional 4-bit step on this R1 night (download, pins, d_4bit_source, --include-4bit), given that the R1 no-redo worst case is already 56,207 s? Or should the procedure plan a separate R1-4bit night?","Does protocol v4:365's 'Every other G0 keeps 600 s' exempt the 30B contrast members from G0_cap_W1? The R7-12 integration note and the kit arm one cap for every W1 G0, and with a long cap the contrast's 1,086 s deadman is at real X7 risk.","Ed: will he approve W1 at the 59,520 s D-window maximum and 1-4 extra D_k windows if S1 or S2 is chosen? Will he accept a 4-bit model named in the paper (CHAIR (B) Q6) if step 3 or S2 is ruled?","Is a per-plan D member cap in run_campaign's hazard path acceptable under 'frozen is not sacred'? R8-2 declined a change to shared Block-5 code. Or must S1 stay inside the runner's existing 1,800 s + unspent idle-wait envelope?","Should 1(f)'s G0 term use one cap per role (D members from the D gated waits, contrast members from X-G), as R7-12's 'D-to-X G0 term' wording suggests, rather than the single cap the integration implemented?","How will the contrast and anchor member_s values in w1_plan.json be filled from R1, when X-G (D-to-X, worst case) is the only contrast member R1 measures?","D-after-30B G0 covers 5 of W1's 6 D members and R1 never measures it. Is the D-after-D upper bound acceptable for the armed cap, or should W1 (ruling 17) supply it before D1?","Will the lead confirm that the pre-declared duty bar is judged as declared on R1's record (and fails), and is never re-judged against a T_dead restated under S1 or S2?","Should r1_slots carry the per-gate G1/H wait lists, so that a sizing under S1 or S2 can project the gate count directly instead of scaling holds per decoded token?"]
# W1 budget fit (ruling 1(f)) and the ruling 1(e) fallback: Opus seat

**Track:** "W1 budget-fit (ruling 1(f)) and the 1(e) fallback", 2026-11-07.
**Base:** `lane/2026-11-06-v4-r1-integrated@e901eb2a4`. All repo citations are at that commit unless another one is named.
**Tools:** I wrote two audit tools and pushed them to `opus/burn-w1fit@43b305425`, under `docs/align/reviews/2026-11-07-w1-budget-fit-opus/`:
- `w1fit_grid.py` does the arithmetic. It agrees with the kit's own `ruling_1f_fit`, `max_fitting_b_d` and `w1_g0_cap` at all 1,512 grid points.
- `w1_fallback_decision.py` takes an `r1_slots.json` and prints the 1(e) branch.

**What was not touched:** no model weights, no measurement Mac, no restricted or Block-5 path. I did not read the other seat's worktree. Nothing was merged and no PR was opened.

---

## 1. Bottom line

1. **At 8-bit, the R1 night cannot change the 1(f) verdict. W1 will be refused at every B_D.**
   - To fit B_D = 6,144, the decode rate must satisfy r ≥ 10,240 / (T_dead − G0_cap_W1 − HG − PT).
   - Take the most favourable thermal outcome that is physically possible: zero G1 and hold time (HG = 0), G0_cap_W1 at its 600 s floor, I_D = 300 s (the idle alone), and prefill plus tool time PT = 35 s. That still needs **r ≥ 16.0 tok/s**. With I_D = 350 s and PT = 40 s it needs 17.3 tok/s.
   - The 8-bit decode limit set by memory bandwidth on the Mac15,9 is about **14.0 tok/s**: 400 GB/s divided by 28.58 GB of weights read per token.
   - R0 measured **11.85-11.95 tok/s** gross for D.
   - So the lead can rule the 8-bit branch now. It turns only on r, and R0 already bounds r.
2. **The brief's "about 20 tok/s" is not the 8-bit rate.** Every on-repo source puts 8-bit D at about 11-12 tok/s (§3). Twenty tok/s is what 4-bit should reach.
3. **1(e) steps 1 and 2 cannot cure an 8-bit 1(f) failure.**
   - Step 2 is roughly neutral or harmful for 1(f): the extra idle sits inside I_D.
   - As written, step 2 also breaks the 30B contrast members' fit under the 1,800 s member cap.
4. **Step 3 (4-bit) fits only in a corner.** It needs all three of:
   - r4 ≥ about 20-22 tok/s;
   - G0_cap_W1 = 600 s, which means every counted gated G0 releases within 480 s;
   - HG + PT ≲ 80-150 s.

   The R7 physics input (G0 settles 840-1,040 s after load end; G1 released at 279 s) makes that unlikely.
5. **The most likely end of the mechanical procedure is 1(e) step 4:** D screen-only, return to council.
6. **What actually binds is the 1,800 s member cap against G0 plus G1 plus holds, not B_D.**
   - The fix that preserves the estimand is a plan-declared D member cap (option S1). With 4-bit plus a smaller cap (S2) as the alternative.
   - At the sizes these imply, both need Ed's Mac time: W1 at the 59,520 s D-window maximum, and 4-7 D_k windows instead of 3.
7. **One thing should be decided before R1 arms:**
   - Should the optional 4-bit step run on the R1 night? `d_4bit_source` is null today (`configs/align/v4/r1_runtime.json:12`).
   - FD 2.2 says that when R0's rates predict the switch, the 4-bit is downloaded and step-tested in R1 (`FINAL-DESIGN.md:255@6eb1ff5be`). Under 1(e)'s extended trigger, R0's rates already predict it.

---

## 2. The rule as coded

- **Ruling 1(f), kit form.** Source: `scripts/align_v4_kit.py:469-524` (`ruling_1f_fit`), per LEAD-RULINGS-2 R5-4, R6-3, R7-2 and R7-12.

      worst = G0_cap_W1 + max_runs(G1+H) + max_runs(prefill+tool) + (B_D + 4096) / r_decode  ≤  T_dead

  - r_decode is the minimum of step-d's rate and every gated run's observed rate (R6-3, `LEAD-RULINGS-2.md:199-207`).
  - The last turn is counted at the full 4,096-token cap (R6-3).
  - `max_fitting_b_d` searches multiples of 1,024 from step-d's B_D down to 6,144 (`align_v4_kit.py:527-536`).
  - The refusal names the largest fitting B_D (`:628-633`).
- **G0_cap_W1** = clamp(ceil(1.25 × the largest counted wait over D_bank, D_spam a, D_spam b and X-G), 600, 1,200) (`align_v4_kit.py:419-466`).
  - A G0 that did not release counts at 1,200 s.
  - An INCONCLUSIVE X-G sets the **whole** cap to 1,200 s (R7-12 integration note, `LEAD-RULINGS-2.md:455`).
  - The same cap is armed for D **and** for the contrast members, through the shared `thermal_policy` (`align_v4_kit.py:1024-1036`).
- **T_dead (L1)** = min((1,750 − I_D)/1.13544, (1,800 − I_D − tail − 10)/1.13544) (`align_v4_kit.py:704-716`; `LEAD-RULINGS-1.md:11`).
  - I_D includes the 300 s configured idle, load, warmup and teardown (`FINAL-DESIGN.md:270@6eb1ff5be`).
  - With a tail of 40 s or less, the first term governs.
- **Step-d's B_D** = 1024·floor(((1,800 − I_D)/1.13544 − prefill_s)·r / 1,024) (`joulewise/align/apple/r1_runtime.py:794`).
  - It includes no gates. That is why FD's original "B_D < 6,144 at 8-bit" trigger does not fire: at 12 tok/s step-d gives about 13,312.
- **The G0 release condition:** 10 consecutive samples that are within the band, with the slow-sensor slope |dS/dt| ≤ 0.2 °C/min, OS level 0, and Nominal powermetrics (`joulewise/align/apple/thermal_gates.py:521-530`).
  - S6 widens only the band part, never the slope part.
- **The deadman is anchored at G0 entry,** and G0, G1 and holds all consume it (`docs/align/thermal_gates.md:115-121`).
  - A G0 that does not release ends the member before its first turn (`docs/align/pilot_protocol_v4.md:375-379`).

## 3. Input ranges and evidence

| Input | Range used | Evidence |
|---|---|---|
| r_decode, 8-bit | 10.5-12.5 tok/s; central 11.5 | R0 re-run 7 (`origin/records/2026-11-07-align-r0-v4-rerun7@7bdfdae6e`, `docs/align/r0/2026-11-07-rerun7/report.json`): `/checks/6/turns/1..11/gross_turn_tokens_per_second` 11.85-11.90; `/checks/4/short` 11.95. Re-run 5 (`@ea89c4d3f`) is the same to 0.02. `/checks/8` (memory) decoded 34,816 prompt + 6,144 tokens in 739.2 s, which implies about 11.3-12.1 tok/s at 35-41k context (inference). FD:145@6eb1ff5be says 11 tok/s. LEAD-RULINGS-2:61 uses 11. |
| 8-bit bandwidth limit | 14.0 tok/s | Mac15,9 is the M3 Max with a 16-core CPU and 40-core GPU, at 400 GB/s ([Apple tech specs](https://support.apple.com/en-tm/117737); [EveryMac](https://everymac.com/systems/apple/macbook_pro/specs/macbook-pro-m3-max-16-core-cpu-40-core-gpu-16-late-2023-specs.html)). The R0 host record shows 16 CPUs. D's `active_bytes` at position 0 is 28,579,478,576 (`/checks/8/memory_samples/0`). |
| r_decode, 4-bit | 17.5-22 tok/s; default 1.70 × r8 | 16.1 GB of weights (`FINAL-DESIGN.md:255`) gives a bandwidth limit of 24.8 tok/s. Projection only. |
| Prefill rate | about 190 tok/s (8-bit) | `/checks/4/generation/attempts/0`: a 6,115-token SHADE prompt plus 109 tokens took 40.56 s. That puts the first-turn PT at about 32-36 s. Rebuilds (checkpoints are off) can add 40-80 s per turn. |
| PT | 35-150 s | as above |
| I_D | 300-520 s; T_dead 1,277-1,083 s | 300 s idle plus load, warmup and teardown. FD's transferred intercept of 517 s gives 1,086 s (`FINAL-DESIGN.md:270`). |
| G0_cap_W1 | 600-1,200 s | Physics input: no key reaches 0.2 °C/min until 840-1,040 s after load end (`LEAD-RULINGS-2.md:317-319`). In W1 a D-after-D G0 entry comes about 400 s after the previous load ends, so the inferred waits are about 440-640 s or more, and the cap about 600-800 s or more. Any censored wait, or a wait above 960 s, gives 1,200 s. |
| HG = max(G1+H) | 0-600 s measured; up to about 800+ s projected | Replayed G1 release at 279 s against the 300 s cap (`LEAD-RULINGS-2.md:319`). |

## 4. Grid results (exact kit arithmetic)

### 4a. Decode rate needed to fit B_D = 6,144

I_D = 400 s, so T_dead = 1,189 s. Rows are G0_cap_W1 (s); columns are HG + PT (s); cells are tok/s.

| G0c \ HG+PT | 40 | 100 | 200 | 300 | 450 | 600 |
|---|---|---|---|---|---|---|
| 600 | 18.7 | 20.9 | 26.3 | 35.4 | 73.7 | ∞ |
| 700 | 22.8 | 26.3 | 35.4 | 54.2 | 262.8 | ∞ |
| 800 | 29.3 | 35.4 | 54.2 | 115.1 | ∞ | ∞ |
| 900 | 41.1 | 54.2 | 115.1 | ∞ | ∞ | ∞ |
| 1,000 | 68.7 | 115.1 | ∞ | ∞ | ∞ | ∞ |
| 1,100 | 209.1 | ∞ | ∞ | ∞ | ∞ | ∞ |
| 1,200 | ∞ | ∞ | ∞ | ∞ | ∞ | ∞ |

- At I_D = 350 s (T_dead 1,233 s), the best cell is 17.3 tok/s.
- At I_D = 520 s (T_dead 1,083 s), it is 23.1 tok/s.
- With G0_cap_W1 = 1,200 s, nothing fits at any rate, because T_dead is always below 1,200 s.

### 4b. Largest fitting B_D (kit `max_fitting_b_d`)

I_D = 400 s. "—" means the kit refuses W1.

| r \ G0c | 600 | 700 | ≥ 800 |
|---|---|---|---|
| HG+PT = 60 s: r ≤ 17.5 | — | — | — |
| HG+PT = 60 s: r 20 / 22.5 / 25 / 27.5 / 30 | 6,144 / 7,168 / 8,192 / 10,240 / 11,264 | — / — / 6,144 / 7,168 / 8,192 | — |
| HG+PT = 150 s: r 25 / 27.5 / 30 | 6,144 / 7,168 / 8,192 | — | — |
| HG+PT ≥ 300 s: any r ≤ 30 | — | — | — |

Over the brief's own grid (r 15-30, G0c 600-1,200, B_D from 6,144 up), W1 is admitted only in the triangle r ≥ 20, G0c ≤ 700 and HG + PT ≲ 150 s. At 8-bit rates W1 is never admitted.

### 4c. Slack at the floor

T_dead − worst at B_D = 6,144, with I_D = 400 s and HG + PT = 150 s.

| r | G0c 600 | 700 | 800 | 1,000 | 1,200 |
|---|---|---|---|---|---|
| 11 | −492 | −592 | −692 | −892 | −1,092 |
| 12 | −414 | −514 | −614 | −814 | −1,014 |
| 15 | −244 | −344 | −444 | −644 | −844 |
| 20 | −73 | −173 | −273 | −473 | −673 |
| 25 | +29 | −71 | −171 | −371 | −571 |
| 30 | +98 | −2 | −102 | −302 | −502 |

## 5. Every fallback, with its consequences

### 5a. Fallbacks the protocol allows

**Lower B_D, then drop ordinal 18** (A1 fit rule; `pilot_protocol_v4.md:655-658`; `align_v4_kit.py:919-945`)
- Effect on 1(f): each 1,024 step removes 1,024/r s, and the floor is reached before any fit. Dropping 18 changes the span only.
- Cures 8-bit: no. Cures 4-bit: no.
- W1 window: 44,640 s; 42,840 s with 18 dropped.
- Power and precision: fewer turns, so the per-session fits have fewer rows (CHAIR §C puts the s_r inflation at 1.2-1.5×).
- Blinding and cohort: none.

**1(e) step 1: S6 joint tuning for G1 and holds, δ_slow ≤ 2.0 °C** (`CHAIR.md:34`; `FINAL-DESIGN.md:481`)
- Effect on 1(f): lowers HG. It shortens only the band part of G0, never the slope part, and never takes G0_cap below 600 s.
- Cures 8-bit: **no**. Even with HG = 0, the 8-bit floor needs r ≥ 16-18.7 tok/s (§4a).
- Cures 4-bit: only together with step 3, and only in a corner.
- W1 window: unchanged.
- Power and precision:
  - U5's left side, |β_T|₉₀·δ_slow, doubles at 2.0 °C, so U5 becomes harder to pass.
  - The energy band it implies must be printed.
- Blinding and cohort: none. The kit binds measured gated rows, so the gated block must be re-run at the tuned band.

**1(e) step 2: idle 300 → 450 s after D predecessors** (`CHAIR.md:35`)
- Effect on 1(f): the idle sits inside I_D.
  - T_dead falls by 132.1 s for each member that carries it.
  - G0_cap can fall by at most 187.5 s, and only if the counted waits were uncensored and the cap was above the 600 s floor.
  - The net headroom change is −132 to +55 s.
- Cures 8-bit: **no**. Cures 4-bit: no.
- W1 window:
  - In W1 it applies to ordinals 6, 9, 12, 15 (contrast) and 18.
  - The span grows by 600 s to 27,527, so the fit rule drops 18, which is the only D-after-D member.
  - The window is then 43,440 s.
- Power and precision: the 30B contrast members' bound becomes 516.6 + 150 + 1.13544 × 1,086.3 = **1,900 s, above 1,800 s**, unless their deadman is cut to 954 s.
- Blinding and cohort: it forks the D configuration key, or else T_dead must fall for every D member (ruling 10).

**1(e) step 3: 4-bit at the same rung** (`FINAL-DESIGN.md:253-255`; `pilot_protocol_v4.md:186-191`)
- Effect on 1(f):
  - r rises by about 1.7-1.78×.
  - Hold seconds scale with decode seconds, so HG falls by about 0.59×.
  - I_D falls slightly.
- Cures 8-bit: n/a.
- Cures 4-bit: **only if** G0c = 600, HG + PT ≲ 80-150 s and r4 ≳ 20-22.
- W1 window: unchanged (D still at most 1,800 s).
- Power and precision:
  - e_D roughly halves, so the MDE in joules halves.
  - The MDE in tokens is unchanged if the misfit scales with tokens or with energy (CHAIR models A and B), and about doubles if the noise floor is fixed in joules.
  - The instrument floor rises to about 20 tokens at 1σ, still far below the misfit.
- Blinding and cohort:
  - It is a new cohort and is never pooled with 8-bit.
  - The paper's named model changes (CHAIR (B) Q6, so Ed must answer).
  - It needs a 4-bit R0 (load, NLL, memory), pins, and an R1-4bit night. `d_4bit_source` is null today.

**1(e) step 4: D screen-only, return to council** (`CHAIR.md:37`)
- Effect on 1(f): n/a.
- W1 window: 44,640 s, if council lets W1 run as a screen.
- Power and precision: no D detection claim at all.
- Blinding and cohort: the kit refuses step 4 as a W1 admission (R5-10, `LEAD-RULINGS-2.md:125`).

**Ruling 17: W1 as a second slot-filling pass for δ_slow, G_turn, N_chunk, B_D and T_dead** (`CHAIR.md:194-196`)
- Effect on 1(f): it cannot lift T_dead past the L1 cap.
- Cures: no.
- Power and precision: if B_D is revised after W1, the D_k sentinels no longer replay W1 ordinal 5 as a whole episode (it stops at a different turn), which undermines U4 and ruling 6's E_ref.
- Blinding and cohort: none, as long as everything is frozen before the D1 desk.

**A3.7: a lower effort rung** (`FINAL-DESIGN-AMENDMENT-1.md:155`)
- Effect on 1(f): none. The worst-case terms are B_D plus the full last turn.
- Cures: no.

### 5b. Minimal deviations that keep the registered estimand

The estimand is the same throughout: turn-owned GPU energy at the reference state, 8-bit, 4,096-token turns, B_D floor 6,144, all gates and holds.

**S1 (recommended if step 4 is reached): a plan-declared D member cap C_D > 1,800 s.**
- Restate L1 against C_D. Keep 1(f)'s form, with HG projected to the full floor budget (§7, F5).
- Sizing from the tool's scenarios: C_D ≈ 2,260-2,520 s optimistic, about 3,000 s central after S6, and 3,360-3,540 s central or pessimistic without S6.
- W1 needs 46,440-55,080 s, so it must run at the D-window maximum of 59,520 s (A2 Q4, Ed).
- D_k windows hold 9-13 D members instead of 18, so 5-7 windows are needed instead of 3. Ruling 3's D5 cap holds only if C_D ≤ about 2,520 s (§6).
- Engineering:
  - a per-plan member cap in the hazard path of `scripts/run_campaign.py` (constant at `:3776`, cap at `:11214`), which is shared Block-5 code; R8-2 avoided touching it;
  - the kit's `MEMBER_CAP_S`, L1, `fit_roster`, and the validator's ≤ 1,800 s checks;
  - `r1_runtime.py:794`.
- The runner already allows 1,800 s plus up to 1,500 s of unspent idle-admission wait when idle admission is enabled (`run_campaign.py:3807-3819`; `scripts/align_pilot_kit.py:179-181`), but that is not guaranteed.

**S2: 4-bit plus a cap.**
- C_D ≈ 1,980-2,820 s, so D_k needs 4-6 windows.
- It carries both step 3's costs and S1's code change.

**Rejected deviations:**
- **B_D below 6,144.** The floor ties to capability (ruling 21's proxy is defined at 6,144). Below it, FD's own consequence is 4-bit. It also does not fit: at 8-bit even B_D = 0 leaves the full last turn, about 345 s.
- **A turn cap below 4,096.** It changes the paper's scope and the R0 ladder's capped-turn fraction.
- **Holds off, or an N_chunk override.** CHAIR rejected unreferenced holds, and D is heavy by protocol.
- **δ_slow above 2.0 °C.** That exceeds the 1(e) cap.
- **Relaxing the G0 slope criterion.** It changes the thermal-control design. It could be argued from R1's β_T and U5, but that is a design revision, not a fallback.
- **A precool stage outside the member.** At 8-bit it still fails: 1,189 − 853 − 60 leaves only 276 s for G0 plus holds. It also adds the same wall time to the window and needs a new plan-tree stage.
- **Charging G0 to the idle-admission wait ledger.** Shared b6 code; at D_k scale (18 × about 700 s) it overruns the 7,200 s session budget.

## 6. Window arithmetic

The A1 law: span = ceil(4,995 + Σ member_s), and window = 60·ceil((span + 17,700)/60). The caps are span 26,940 s and window 44,640 s (`scripts/validate_align_v4_w1_plan.py:34-35, 210`). Anchors and contrast members use A1's planning values.

| D member_s (s) | 18 members: span / window | Drop 18: span / window | ≤ 44,640? | ≤ 59,520? | D_k at 59,520: D members / held-out / windows for 48 |
|---|---|---|---|---|---|
| 1,800 | 26,927 / 44,640 | 25,127 / 42,840 | yes | yes | 18 / 16 / 3 |
| 2,100 | 28,727 / 46,440 | 26,627 / 44,340 | only with 18 dropped | yes | 16 / 14 / 4 |
| 2,400 | 30,527 / 48,240 | 28,127 / 45,840 | no | yes | 14 / 12 / 4 |
| 2,700 | 32,327 / 50,040 | 29,627 / 47,340 | no | yes | 12 / 10 / 5 |
| 3,000 | 34,127 / 51,840 | 31,127 / 48,840 | no | yes | 11 / 9 / 6 |
| 3,300 | 35,927 / 53,640 | 32,627 / 50,340 | no | yes | 10 / 8 / 6 |

- "48" is 42 benign plus 6 sabotage, i.e. at least 21 benign and at least 3 sabotage per pair, before exclusions.
- The W1 window is also exposed to the contrast members (F7). Their member_s grows toward the 1,750 s bound if their G0 waits are long. With all eight contrast members at 1,750 s, the fit rule ends in "return to lead" even with D at 1,800 s.

## 7. Further findings

- **F4: a G0_cap_W1 of 1,200 s is self-defeating.**
  - Any censored gated G0, or one inconclusive X-G, sets it (R7-12). Then 1(f) cannot fit at any decode rate.
  - An armed G0 cap at or above T_dead also means the deadman (X7) always fires before the G0 timeout (X2).
  - R7-12's own ruling text speaks of "W1's **D-to-X** G0 term". A cap per role (D members from the D gated waits, contrast members from X-G) would match that wording and remove the path by which an X-G deadman forces the D refusal.
- **F5: 1(f)'s holds term understates when the gated runs are cut by the deadman.**
  - At 8-bit all three probably will be.
  - max(G1+H) then comes from runs that decoded far fewer than B_D + 4,096 tokens, while the decode term assumes the full budget.
  - For any sizing under S1 or S2, project the holds: HG_proj = max(HG, max over runs of (G1+H)/decode_tokens × 10,240). Better still, commit the per-gate lists (`gate_waits_s`) into r1_slots.
- **F7: contrast viability.**
  - The contrast deadman of 1,086.3 s covers G0 (`align_v4_kit.py:701, 1034`).
  - With G0 ≥ 800 s after a D predecessor (X-G 6, X-S 9, Y-G 12, Y-S 15), at most 286 s remain for the pilot-7 episode. That episode is 12 turns and 5,506 (X) or 4,006 (Y) decode tokens per the WP18 fixtures, and the G arm adds 11 G1 gates.
  - The result is an X7 risk, and with it a T verdict of INCONCLUSIVE (fewer than 2 eligible runs per arm and template).
  - R1's X-G measures exactly this transition.
  - Protocol v4's "Every other G0 keeps 600 s" (`pilot_protocol_v4.md:365`) is ambiguous against the integration note's "one cap for every W1 G0".
- **F8: predecessors.**
  - In W1 only ordinal 18 is D-after-D. D members 5, 8, 11, 14 and 17 follow 30B members (A1 table).
  - R1 measures D-after-D (R6-1), so G0_cap_W1 is a conservative bound for most W1 D members. D-after-30B is never measured.
- **F9: W1 must run in the final D configuration.**
  - W1 ordinal 5 is the sentinel original for every D_k window, and ruling 6's E_ref uses W1 ordinals 5 and 18.
  - So quantization and the member cap must be settled **before** W1 arms. Do not use ruling 17 to settle them.

## 8. Blinding

- **Every input the procedure reads is an R1 engineering field:** rates, G0/G1/H/prefill/tool seconds, I_D, tail, decode tokens, admitted turns, X7, the duty-bar verdict, and the S6 median waits. R1 has no held-out seeds. W1's D members are development data and enter no pool. The tool's docstring whitelists these fields; it never reads `u5`, `planning_temperature`, `projected_mde`, energies, residuals or scores.
- **Rules to keep:**
  - Record the procedure before R1's numbers are read.
  - Freeze every resulting slot or cohort change before the D1 desk (rulings 10 and 17).
  - Choose between S1 and S2 on timing fields only, never on W1's D residuals.
  - Leave the pre-declared duty bar as declared (it will fail on R1's record). Do not re-judge it against a restated T_dead.
  - Log the deviation publicly: protocol v4 plus LEAD-RULINGS-2 Round 10.
  - Start a new cohort for any change of quantization or cap.

## 9. Mechanical decision procedure

**Now, before R1 arms:**
- **P-1.** The lead records this procedure as the pre-declared way 1(e) is applied (LEAD-RULINGS-2 Round 10).
- **P-2.** The magistrate decides whether to stage the 4-bit step on the R1 night (`--include-4bit`, `d_4bit_source`, 16.1 GB download by day, pins). Otherwise, plan an R1-4bit night later.
- **P-3.** Questions for Ed in advance:
  - W1 at the 59,520 s maximum, with 1-4 extra D_k windows, if S1 or S2 is chosen;
  - whether the paper may name the 4-bit model.

**After R1, run** `python3 -B w1_fallback_decision.py --root . --r1-slots configs/campaigns/align_v4/registration/r1_slots.json [--r4 X --i-d4 Y]`. It reuses the kit's functions, so it cannot disagree with the kit's refusal.

- **0. R1-RERUN.** If `inconclusive_segments` is non-empty, the remedy is an R1 re-run (R7-3, magistrate). Stop.
- **1. A-ADMIT-8BIT.** If `max_fitting_b_d` is at least 6,144, set B_D to that value and run `fit_roster`. A failed duty bar still needs a recorded 1(e) step.
- **2. Test steps 1 and 2 at their best case.**
  - Best case means HG → 0, G0c → 600, plus step 2's −132 s of T_dead. Compute r*_bc = 10,240 / (T_dead − 600 − PT).
  - If r < r*_bc, record steps 1 and 2 as "still failing (arithmetic)" and go to 3. No Mac time is spent.
  - Otherwise the branch is STEP1-S6-RERUN-GATED-BLOCK: tune S6 by replaying the gate journals, then have the magistrate re-run the gated block at S6. Step 2 is applied only if it closes the gap and touches no contrast member.
- **3. Test step 3 (cumulative with step 1).**
  - Use r4 measured, or 1.70 × r labelled as a projection. Use T_dead4. Keep G0c the same (the predecessor heat is similar). Set HG4 = HG·r/r4.
  - If it fits on the measured seconds, the branch is **STEP3-4BIT**: a 4-bit R0, pins, and an R1-4bit night before W1, with Ed told.
  - If it fits only once HG is scaled by the S6 estimate (90 s divided by the larger recorded median), the branch is **STEP1+3-4BIT-S6**: an R1-4bit night with the gated block at tuned S6.
- **4. STEP4-COUNCIL.** D is screen-only and the question returns to council. The tool prints the S1 and S2 sizing.
  - Council rule: take the option with the fewest D_k windows among those with C_D ≤ 3,300 s and at most 5 windows. Prefer 8-bit S1 when it ties.
  - If neither qualifies, the thermal regime itself (the G0 slope criterion, the hold intensity, High Power) has to be redesigned.

**The tool's demo (asserted) on synthetic R1 outcomes:**

| Synthetic outcome | Branch |
|---|---|
| 8-bit, optimistic | STEP1+3-4BIT-S6. 4-bit misses by 17 s on measured holds and fits on the S6 estimate. |
| 8-bit, central | STEP4-COUNCIL. S1 C_D = 3,540 s (about 3,000 s with S6); S2 = 2,760 s. |
| 8-bit, censored G0 | STEP4-COUNCIL. |
| Hypothetical 20 tok/s with G0 waits ≤ 480 s and HG ≈ 25 s | A-ADMIT at 6,144. |
| Hypothetical 25 tok/s, same conditions | A-ADMIT at 9,216. |

The brief's own premise of 20 tok/s fits only if every counted G0 releases within 480 s and holds are near zero.

## 10. Artifacts

- `opus/burn-w1fit@43b305425`, under `docs/align/reviews/2026-11-07-w1-budget-fit-opus/`:
  - `w1fit_grid.py`, with its output in `grid_output_e901eb2a4.md`;
  - `w1_fallback_decision.py`, with its output in `demo_output_e901eb2a4.txt`.
- The branch is not for merge. The worktree was removed afterwards.
````
