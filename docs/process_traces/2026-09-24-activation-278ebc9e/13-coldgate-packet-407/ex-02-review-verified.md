# Record 02 — A fresh Opus 5.5 whole-repo review (Ed pasted it ≈04:50 PDT 09-24), with Fable's bench verification of its load-bearing claims

Provenance: Ed ran an independent Opus 5.5 review of `main` @ `cdc05e9` (five parallel read-only lenses: measurement physics, statistics, process, research agenda, code) and pasted the result into the interactive session. The full text is in §3. Fable checked the claims below at the bench at `1afbd77d` before giving Ed a verdict.

## 1. Verified at the bench

| Claim | Result | Evidence |
|---|---|---|
| powermetrics boundary is CPU + GPU + ANE only; DRAM/fabric power excluded | TRUE | `joulewise/adapters/powermetrics.py` `RAIL_MANIFEST = ["cpu_power","gpu_power","ane_power"]`; boundary string "Apple SoC CPU + GPU + ANE package power" |
| Workload events stamped with `time.time()` | TRUE, with monotonic recorded beside it | `joulewise/clock.py` `now()` returns `time.time()`; `stamp()` records epoch and monotonic before/after |
| The 09-22 02:17 refusals came from wall-clock adjustments | TRUE, and already cured | A267 clock-anchor v3.1 + network-time attestation (PR #380); the 09-23 07:00 pilot retained 11/12 |
| Equivalence-night rule has ~50 % false-alarm rate under no change | TRUE (my simulation: pass rate 0.37–0.76 depending on old-corpus size and m; 0.54 at n_old = 12, m = 7) | bench Monte Carlo, 20,000 trials per cell |
| Zero claim-bearing numbers after ~107 days | TRUE | README table row B "preserved, not claim-bearing"; every 2026-09 night was an idle pilot |
| Governance docs ≈ 3 MB; `arm_readiness.py` 12.9k lines > controller + reducer | TRUE | `wc`: 3,056,485 bytes; 12,896 vs 3,327 + 4,003 lines |
| `CLAIMS_STATUS.md` / `WINDOW_STATUS.md` stale since August | TRUE in substance | last content commits 08-24 and 09-12 (link repair only) |
| No deadline recorded | TRUE in the repo | `docs/milestones.md` row "Not yet recorded"; Ed's end-of-November deadline exists only in email |

## 2. Wrong or stale

- **"No wall-meter check; purchase still open (D-092)."** STALE. The POWER-Z KM003C has been connected and reading live since 09-23 (lane E214 unblocked). B1 is runnable now.
- **"The claim gate is neither a minimum-effect test nor TOST."** NOT CONFIRMED. The gate at the cited location already carries a `tost_v1` equivalence branch and an `effect_not_above_floor` reason; whether the √n scale error exists needs a targeted read, not a headline.
- **"Switching to monotonic stamps removes the need to switch off network time."** Directionally right, but the current cure already works (11/12); this is hygiene, one small PR.

## 3. Unverified but plausible, cheap to act on

- Dominance test (D-165) mostly measures its own bound: plausible; a simulation of the repo's floor code would settle it in an hour.
- ABBA block order never randomized (small model always first): not checked at the cited line; counterbalancing the start arm per block is a one-line change in the generator and costs nothing.
- SE(log R) ≈ 0.25 at n = 64, Level 5: matches our own 4-decisions email (95 % interval ×/÷ 1.59). The consequence stands: a crossover at R ≈ 1 cannot be resolved near the crossover level by this design; AP-5M's "not resolved" outcome admits it, the reviewer's "make the thinking budget the independent variable" (A2) is the better design.

## 4. Fable's verdict, given to Ed

Substantial merit. The most important sentence is "energy data only adds information where energy ≠ tokens × a constant": if J/token per model is flat, the MATH headline is token arithmetic with a power meter attached. A3 (J/token along a 32k trace, one night) decides that. B1 (wall/powermetrics ratio by phase and bit-width) is the most citable single result available and the meter is on hand. The process numbers are accurate and Ed has already said the same thing (D-183). Under D-184 this goes to the four-model council as design input, not as a decision by this session.

## 5. The review, verbatim

(Pasted by Ed; author: a fresh Opus 5.5 session outside the loop; reviewed `main` @ `cdc05e9`.)

# JouleWise review, and scientific questions it could answer

I did this review with five parallel read-only reviews (measurement physics, statistics, process, research agenda/paper, code quality), then checked the load-bearing claims myself. Nothing in the repo was changed. File references are to `main` @ `cdc05e9`.

## Summary

- **The engineering is careful and honest.** Run bundles are never rewritten. Pre-registration is real, with hashed frozen packs, a fixed sample size and fixed multiplicity families. A refusal to issue a result counts as a result. The team found and voided its own biggest defect: D-078, a timestamp alignment error of 0.5–1 s.
- **After about 107 days (first run 2026-06-09) there are zero claim-bearing numbers.** At least five windows (overnight collection sessions) passed and were later reclassified as non-claim-bearing. 748 stored bundles were voided because the timing estimator behind them was shown wrong. The headline question has changed four times, most recently on 09-23.
- **The central problem is that effort went into precision the questions don't need, while accuracy is unchecked.** A great deal of machinery pushes timing-attribution error down to about 1 J, and a 5 J difference is the smallest the project accepts as real. But the interesting effects here are hundreds to thousands of joules. Meanwhile the questions a reviewer asks first are unanswered: does `powermetrics` agree with a wall meter, and what about memory power?

## Review

### 1. Measurement core

**How it works**
- `powermetrics` samples at 10 Hz. Each record is an average over roughly 100 ms (observed ~113 ms) of **CPU + GPU + ANE power only** (`adapters/powermetrics.py:57`).
- Energy for a phase is the sum of each record's power times its overlap with the phase window (`reduce.py:167-181`).
- The time anchor (anchor-v3) fits the whole-second wall timestamps in the `powermetrics` output under a constant-clock-rate assumption. It is a clever set-membership fit (`uncertainty_evidence.py:878-1130`).
- A 59-pulse GPU calibration run bounds the lag between commanded and observed power changes (`powermetrics_fiducial.py`).

**The stated ~1 J attribution limit is physically consistent.** A ±31 ms timing envelope at about 33 W gives about 1 J. A full 100 ms record at 50 W would be 5 J.

**Issues, in order of importance:**
1. **Memory power is outside the boundary.** Decode is limited by memory bandwidth and prefill by compute. So the missing DRAM/fabric share probably differs by phase, which biases prefill-vs-decode shares, quantization comparisons and cross-model J/token. It is undocumented whether Apple folds any of it into `gpu_power`. This matters more than every sub-joule timing correction combined, and there is no wall-meter check (the purchase is still open in D-092).
2. **Workload events are stamped with `time.time()` (wall clock), not a monotonic clock** (`clock.py:56-57`). That makes the macOS time daemon's millisecond wall-clock adjustments into measurement error. It is the direct cause of the 5 ms refusals that discarded 10 of 12 captures on the 09-22 pilot night. Monotonic stamps are already recorded (`clock.py:59-72`). Switching to them removes the problem and the need to switch off network time.
3. **Power is assumed constant within each 100 ms record, and that error is priced at zero** (`reduce.py:519-520`). The worst-case split error is about 25 ms × ΔP. For large low-to-high steps it can exceed the envelope that is supposed to cover it.
4. **A systematic lag is bounded as if it were random, then charged twice**, once in the floor and once in the claim interval. The mean lag is not subtracted (`powermetrics_fiducial.py:278`). Repeatability is about 3× smaller than the envelope, which suggests most of the 24.9 ms bound is a consistent bias that cancels in paired designs.

### 2. Statistics

1. **The registered headline test mostly measures the instrument's own bound.** "Dominance" (D-165) asks whether the timing-aware floor is at least twice the naive floor, on all 12 components. Running the repo's own floor code in simulation, that ratio is about 2 exactly when the constructed worst-case half-width w roughly equals the repeatability SD σ. P(ratio ≥ 2) is 0.47 per component at w/σ = 1, and all 12 must pass. So the verdict depends mainly on how conservative the bound is and which window lengths were chosen, not on physics. No interval is reported on the ratio.
2. **The equivalence-night rule is badly calibrated.** I reproduced this independently. The rule passes if every retained value is at most the old corpus maximum and the new range is at most the old range. With no real change, P(PASS) is **0.48** at m=12 retained captures and **0.68** at m=6. Losing captures makes passing easier. The one night that got a verdict (m=7) FAILED, and that FAIL is quite plausibly a false alarm.
3. **The claim gate has the wrong scale.** `claims.py:344` compares a mean of n blocks against a prediction bound for one new block, which is about √n too conservative. It tests the point estimate, not a confidence bound, so it is neither a minimum-effect test nor TOST (two one-sided tests for equivalence). Its sample-maximum term grows with n.
4. **The block order is never randomized.** Every ABBA block starts with the small model (`generate_configs.py:2539`), so heat carried over from the large model is not balanced.
5. **The energy-per-correct design (MATH headline, draft branch) cannot resolve its own target.**
   - At Level 5 with n=64, SE(log R) ≈ 0.25, so only R < 0.5 or R > 1.9 would clear Holm. The crossover it is looking for sits at R ≈ 1.
   - The "crossover" is defined as the lowest Holm-significant level. That is not an estimator of where the crossover is.
   - The weaker model's J/correct is largely set by the token cap, which a 16-problem pilot chooses. The cap alone could produce a crossover.
   - Greedy decoding plus a bootstrap over problems gives a muddled estimand.
6. **J/correct may add nothing beyond token counts.** The project's own premise PC-4 (decode power roughly flat at 23–28 W) implies J/correct ≈ tokens × a per-model constant ÷ accuracy, which anyone can compute from token logs without a power meter. This is the most important scientific risk, and it shapes the questions below.

### 3. Process

- The four main governance files (`TASK_QUEUE.md`, `RUN_STATE.md`, `decision_log.md`, `council_log.md`) come to about 3 MB. With the 716 KB state kernel the total is about 3.7 MB, roughly 390k words. The paper is 17.5k words.
- `docs/` holds 177 MB in about 6k files, 79 MB of it process traces.
- About 35% of `joulewise/` is governance or custody code. `arm_readiness.py` alone is 12.9k lines, larger than the controller and reducer combined.
- In the last two days: about 21k lines of process traces were added against about 630 science-facing lines of package code. 101 of 170 commits were bookkeeping.
- Gates are strict far below what the science can resolve. Seven of twelve pilot captures were rejected over roughly 7 mJ of clock adjustment.
- A self-imposed 24-hour evidence expiry killed the `_v3` packs before they were ever collected.
- `CLAIMS_STATUS.md` and `WINDOW_STATUS.md` have been stale since August.
- Ed has already written the diagnosis himself (D-183): *"the process is meant to prevent bad science not work for 40h."*
- No deadline is recorded (`docs/milestones.md`; the ED-DATES-01 task).

### 4. Code

- **What works:** the mock pipeline (run → strict validate → reduce) runs end to end on Linux in 1.3 s. Core test modules pass (about 690 tests). The package is stdlib-only, `interfaces.py` has clean protocols, and bundle writes are atomic.
- **What doesn't:**
  - God-functions: `validate_claim_verdicts` is 2,502 lines (`analysis_engine/artifact.py:981`).
  - Import cycles: `cli` → `controller` → registry → `cli`.
  - Versioned sibling copies: analysis-manifest v1/v2/v3, and eight reducer wire versions in one file.
  - About 13k lines of orchestration live in `scripts/`, not the package.
  - No ruff or mypy.
  - **No local NVML or RAPL path at all.** The NVIDIA route has never touched real hardware.
  - Minor: `reduce` without `--output` writes into the current working directory (`cli.py:1901`).

### What to keep
Pre-registration, immutable bundles, refusal as a result, byte-identical replay, and the D-078 audit. These practices are rarer in energy-measurement papers than they should be.

## Proposed scientific questions

**The organizing idea: energy data only adds information where energy ≠ tokens × a constant.** On a unified-memory machine that happens in three places:
- **Context length:** reading the KV cache grows with position in the sequence.
- **Parallelism:** batching spreads the cost of reading the weights across requests.
- **Power states:** decode is memory-bound, so it may not need full clocks.

The best questions sit in those places. They also involve hundreds to thousands of joules, so the ~5 J smallest-accepted difference stops being the limit. I checked the bank: parallel sampling, thinking budgets, overthinking and power-state questions are **absent** (the bank explicitly bans pass@k).

### A. Test-time compute measured in joules (the natural replacement headline)

**A1. Is parallel test-time compute almost free in joules?**
- Test-time-scaling papers (Snell et al. 2024; Brown et al., *Large Language Monkeys*) count FLOPs or tokens. On memory-bound decode, k samples in one batch read the weights once, so energy(k) ≈ E₁·(1 + (k−1)ε) up to the point where B×KV bytes ≈ weight bytes.
- **Design:** Qwen3 1.7B/4B/8B; k ∈ {1,2,4,8,16}; batched vs sequential; majority vote on a MATH subset.
- **Output:** energy–accuracy frontiers per difficulty level, for example "1.7B × 8 votes vs 8B × 1".
- **Feasibility:** static batching at B=2/4 is already verified feasible in MLX (the AXI-SB verdict). This merges BATCH-KNEE and EPCA into one question nobody seems to have asked on this hardware.

**A2. What is the energy-optimal thinking budget per difficulty?**
- Force thinking caps of {0.5k, 1k, 2k, 4k, 8k, 16k} tokens, crossed with model and level. Report accuracy(budget) and J(budget), and find the cheapest (model, budget) pair per level.
- This makes the cap the independent variable, which removes the cap-dependence flaw, and replaces the fragile "crossover level" with a frontier.
- Together with A1 it gives a two-dimensional compute-allocation map: sequential vs parallel.

**A3. Does J/token rise along a long reasoning trace, and by how much?** This is the prerequisite for everything else in A.
- Force generation out to about 32k tokens and measure J/token in 1k-token bins. At 8B each bin is tens of joules, so it is easy to resolve.
- Fit E(n) = an + bn². If b ≈ 0, J/correct really is token arithmetic, and the MATH headline needs A1 or A2 to be about energy at all.
- Add one model with a different attention scheme (sliding-window or linear; the bank's MIXER-3B) as a contrast. This takes about one night.

**A4. What is the overthinking tax in joules?**
- What fraction of reasoning energy is spent after the trace first reaches its eventual final answer, or on attempts that end wrong, by level and model size?
- Add a counterfactual: an early-exit heuristic's joules saved against accuracy lost.
- This is almost pure reanalysis of A2's traces plus A3's energy-by-position profile.

### B. Is the instrument accurate, not just precise?

**B1. Is `powermetrics` biased by phase or by quantization?**
- Take the wall/`powermetrics` ratio (and an IOReport counter read, as Zeus does on Apple) for compute-bound prefill vs bandwidth-bound decode, across bit-widths.
- Hypothesis: the ratio is larger in decode because DRAM is excluded.
- If that holds, it affects essentially every Apple-silicon LLM energy paper, which makes it the most citable result available here.
- It needs roughly a $50–150 meter. A 1 Hz meter is fine for long steady-state decode.

**B2. Recast "dominance" as a usable rule: the minimum phase duration for 10 Hz interval-average telemetry.**
- Report the timing share of the uncertainty budget, u_B²/(u_A²+u_B²) with a CI, as a function of phase duration. Add a one-token prefill arm as a boundary-free falsifier.
- This turns a self-referential pass/fail into a practitioner rule that also carries over to NVML.

### C. Hardware knobs on unified memory

**C1. Race-to-idle, or run slow and steady?**
- Does Low Power Mode lower J/token for decode (memory-bound, so clocks may matter little) with small tok/s loss, while hurting prefill?
- Report the energy-delay product per phase. It is cheap, practical for laptop inference, and not in the bank.

**C2. The bytes-moved law, plus the watts × time decomposition of quantization.**
- This endorses the prospectus's top-ranked BYTES-LAW / COEFF-LAW, with one addition.
- Split E = P̄·t across 3/4/6/8-bit/bf16 of one model, to show whether quantization saves energy through time or through power.
- Then test a held-out prediction of J/token from bytes read per token, with MoE active bytes and the TOPK-KNOB manipulation as the clean intervention.
- Run it with B1's wall meter; otherwise the DRAM exclusion biases exactly the term being studied.

## Suggested order

1. **Fix the clock stamping** (monotonic event stamps) and **replace the equivalence rule** with TOST plus a variance-ratio test sized by simulation. Both are small, and they remove most current night refusals.
2. **Run A3 as the first science night.** One night decides whether the MATH headline is about energy at all.
3. **Buy the meter and run B1** alongside.
4. **Then A1 + A2** as the headline paper, with **A4** reanalysed from the same traces.
5. **Apply full gating only to claim-bearing code:** the reducer, estimators, admission predicates and registrations. Everything else gets one reviewer plus CI.
