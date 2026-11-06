# Executing reviews: SSD qualification kit with corrected Q1 statistics (PR #689)

Date: 2026-11-06. Branch `lane/2026-11-06-ssd-qual-fix` into `lane/2026-11-05-align-pilot10-benign`.
Gate: gate_policy rule 3 (Q1 selects the drive's operating option): CI, regression tests with counterfactuals, and two executing reviews from different model families, Sol 6.1 xhigh (local, `service_tier=priority`) and Opus 5.5 (the lead lane). Fix rounds per rule 4 until a round found nothing above LOW.

## Opus 5.5 (lead lane) executing review

- Reproduced the triage: `plan --out` on the lane at 033f5bebd still printed `87 segments; planned 4.70 h` (CLI defaults A-D-A, 8 idle pairs) although `plan()` defaulted to A-D-A-D-A. Fixed in 292ef1106 (shared `DEFAULT_BLOCKS` / `DEFAULT_IDLE_PAIRS`); the new CLI test fails on the old defaults.
- Monte Carlo, 400 seeds, decode block shock SD 50 mW, segment SD 20 mW, drift 0.05 W/h, margin about 63 mW: base segment-level fit on A-D-A covered the truth 39.0 % (truth 0) and 40.5 % (truth 0.10 W) and PASSed a true 0.10 W effect 14.75 % of the time; the block-mean fit on A-D-A-D-A covered 90.7 % / 89.7 % and PASSed it 1.0 %. Base fit on A-D-A-D-A: 46.3 % coverage, 8.25 % false PASS. Block-mean fit on A-D-A: always INCONCLUSIVE (df 0).
- Power (truth 0, segment SD 20 mW, A-D-A-D-A): Q1 PASS 99.75 % at block SD 0, 98.5 % at 5 mW, 88 % at 10 mW, 51 % at 20 mW, 25 % at 30 mW, 7.5 % at 50 mW. Recorded in the study §6 as a planning note.
- Removed the study's sqrt(1.09) / 4.4 % MDE claim for Q3 (Q3 is a t interval on a mean) and the matching code comment; 'Q1-Q5' -> 'Q1-Q3, Q5'.
- Mutation checks on every Sol-round fix are listed in the dispositions below.

Sol's scratch probes lived in an untracked directory of a throwaway clone and were not kept; its raw event logs are on the MacBook Air at `~/code/CapstoneProject/jw-wt/ssd.r{1,2,3}.events.jsonl` and `ssd.events.jsonl` (round 4).

## Sol 6.1 xhigh, round 1: 292ef1106 (whole lane, focus 44b99b37d..292ef1106)

The correction works for complete, balanced blocks. The admission tool still needs fixes before use. Reviewed through `292ef1106`; no tracked files changed.

1. **HIGH — Missing segments can invalidate Q1’s interval and double the false-PASS rate.**  
   [Block averaging](joulewise/align/apple/ssd_qualification.py:359) retains ordinary homoskedastic OLS uncertainty even when blocks have different segment counts. Their variances become `block_variance + segment_variance / n`.

   With 400 seeds, 5 mW block shocks, 20 mW segment noise, linear drift, and retained counts `[6,1,6,1,6]` produced by extraction flags:
   ```
   coverage90: 0.8325
   false_PASS_at_margin: 0.10
   false_PASS_actual_margin: 0.10
   ```
   Require balanced retained counts or adopt and validate an uncertainty method that handles unequal variances.

2. **HIGH — Q5 passes despite missing thermal evidence.**  
   [summarize_ops()](joulewise/align/apple/ssd_qualification.py:517) silently discards missing S_slow values. Removing readings from two hot attached blocks changed:
   ```
   complete: FAIL
   after_missing: PASS
   missing_offset: 0.0
   ```
   This contradicts §6’s “missing evidence fails” rule and can permit B. Require thermal evidence across the required segments. This defect originates in the first commit.

3. **MEDIUM — Three-block INCONCLUSIVE results crash CLI serialization.**  
   [evaluate()](joulewise/align/apple/ssd_qualification.py:417) sets the unavailable Q1 margin to `NaN`; the CLI rejects it with `allow_nan=False`:
   ```
   three_block_evaluate: Q1_presence_decode = INCONCLUSIVE
   CLI_three_block_error:
   ValueError: Out of range float values are not JSON compliant: nan
   ```
   Missing or singular Q1 evidence has the same problem. Serialize unavailable margins as `null`. The new tests verify the module result but miss this CLI path.

4. **MEDIUM — A/A-lite remain mechanically permitted without a variability gate.**  
   [The option mapping](joulewise/align/apple/ssd_qualification.py:425) still returns A on four PASSES, although revised §6 explicitly says Q3 tests only the mean and a variability criterion is needed before licensing A/A-lite. This is an acknowledged, unresolved issue; B is unaffected. Cap the result at B until that criterion exists.

5. **MEDIUM — Amendment A8 contradicts the implemented B rule.**  
   [A8](docs/align/v4/DRAFT-AMENDMENT-external-log-volume.md:117) says “A FAIL anywhere leaves Option C.” The executable counterexample is:
   ```
   Q1 PASS, Q2 FAIL, Q3 PASS, Q5 PASS → option B
   ```
   That behavior matches §6 and the stated requirements for B. Amend A8 to refer to criteria required by the selected option.

6. **LOW — Mixed timestamp availability silently mixes incompatible time coordinates.**  
   [The per-row fallback](joulewise/align/apple/ssd_qualification.py:351) combines epoch hours with ordinal-relative hours. Removing one timestamp changed the fitted presence estimate from **2.83 mW to 63.92 mW**. Require a consistent time basis. Normal extraction always supplies timestamps, so this concerns partial or externally supplied rows.

The balanced Monte Carlo supports the intended correction. With **400 seeds**, Gaussian 50 mW block shocks, 20 mW segment noise, and 0.05 W/h linear drift:

| Result | Corrected five-block fit | Old three-block fit |
|---|---:|---:|
| 90% interval coverage | 90.75% | 39.25% |
| PASS with true +100 mW effect | 1.25% | 14.50% |

At the ±62.5 mW boundaries, corrected PASS rates were **3.00% and 3.25%**, consistent with a level-5% TOST. Independent TOST calculations disagreed with interval decisions **zero times**. The df=2 critical value matched its analytic value.

Section 6’s numbers are consistent: **125 segments, 6.8333 h, 18 attached pairs per load, df=2**; margins are **62.5, 4.051 and 24.307 mW**, and nominal pair half-widths are **1.230 and 11.481 mW**. Default block names are unique, the residual print is calculated correctly, and the CLI default regression passes.

Reproducible probes and outputs are under scratchpad/ssd-executing-review:

```sh
nice -n 15 python3 -B -u scratchpad/ssd-executing-review/probe.py
nice -n 15 python3 -B -u scratchpad/ssd-executing-review/edge.py
nice -n 15 python3 -B -u scratchpad/ssd-executing-review/run_focused.py
```

Focused test output: `Ran 50 tests ... OK`. An in-memory invalid-df mutation was caught by the three-block regression. The sandbox denied `nice`’s priority change. The broader hazard census was interrupted; no full-suite or hardware validation is claimed. Final Git checks showed only untracked scratch files.

VERDICT: ADMIT_WITH_FIXES

**Disposition (lead):** All six fixed in fb32d540c: Q1 fails closed when a block keeps fewer than half the quiet segments of the fullest block (lead simulation, 1,000 seeds per case: [6,3,6,3,6] keeps 90-92 % coverage, [6,1,6,1,6] drops to 83 %); a missing or non-finite S_slow reading fails Q5; an unavailable Q1 margin serializes as null; `strongest_option_allowed` capped at B (Q3 bounds only the mean write effect); amendment A8 wording; one time basis for the Q1 fit. Regression tests fail on the previous module (5 of 26).

## Sol 6.1 xhigh, round 2: fix diff 292ef1106..fb32d540c

- **MEDIUM — An entirely unusable block bypasses Q1’s balance guard.** [Count construction](joulewise/align/apple/ssd_qualification.py:365) omits blocks with zero usable segments. Flagging all six quiet decode rows in `2-detached` produces **Q1 PASS / B**; retaining one or two produces **INCONCLUSIVE / C**. This contradicts §6’s “any block” rule. Include zero counts before filtering and add this regression case.

- **LOW — New tests miss meaningful regressions.** Three mutations survive all 26 qualification tests: ignoring missing detached S_slow readings, removing S_slow finite-value validation, and fitting ordinal time while reporting “epoch.” The clock fixture uses affine epoch/ordinal timestamps, which cannot distinguish the fits. An irregular-clock scratch probe catches the mutation: a true −0.10 W effect changes from **FAIL/C** to **PASS/B**. Additional scratch tests catch all three survivors.

The other fixes behave correctly: missing S_slow evidence fails Q5, absent Q1 estimates serialize with a null margin, A/A-lite remain capped, and Q2/Q3 failures do not block B. §6 and A8 agree on option mapping.

Verification: **48 focused tests passed; 8/11 mutations were caught.** Across 500 seeds per simulation case, admissible five-block count patterns gave **87.0–93.6% coverage** for nominal 90% intervals. Balanced cases gave 89.6–90.8%; severe `[6,2,6,2,6]` imbalance always failed closed. This supports near-nominal coverage under the tested assumptions.

Tracked files remain unchanged. Full evidence and reproduction details.

VERDICT: ADMIT_WITH_FIXES

**Disposition (lead):** Both fixed in b5396db6b. The lead re-ran the mutations (all-flagged block, ordinal fit reported as epoch, dropped missing S_slow, no finite check, balance guard off); each now fails the suite.

## Sol 6.1 xhigh, round 3: fix diff fb32d540c..b5396db6b

Two findings remain:

- **MEDIUM — Blocks represented only in other loads still bypass Q1’s balance guard.** The census at [ssd_qualification.py:367](joulewise/align/apple/ssd_qualification.py:367) considers only the requested load. Remove every decode row from `2-detached`, preserving its idle rows: Q1 returns **PASS**, option **B**, df **1**. It should count that block as zero and return INCONCLUSIVE/C. Reproduced for each of the five blocks. This leaves the previous fix incomplete.

- **LOW — Otherwise skipped rows without `block` now crash evaluation.** Append `{"load":"decode","condition":"quiet","extract_flags":["bad"]}` to the default fixture. The new census raises `KeyError('block')`; the CLI exits **1** without writing a verdict. The base revision handles this input without crashing. Handle missing block identity explicitly.

Verification: **26/26 affected tests pass**, and **all four mutations were caught**: dropping zero-block accounting, ignoring missing detached S_slow, removing S_slow finiteness checks, and fitting ordinal while reporting epoch. The default five-block plan retains df **2**; all-flagged blocks correctly produce INCONCLUSIVE/C.

No BLOCKER/HIGH findings. No tracked files changed. Reproducers, logs, and next fixes are in the scratch review report.

VERDICT: ADMIT_WITH_FIXES

**Disposition (lead):** Both fixed in c96e499f5 with regression tests; the lead mutated each fix back (load-only census; skipping a usable block-less row) and both mutations fail the suite.

## Sol 6.1 xhigh, round 4: fix diff b5396db6b..c96e499f5

No BLOCKER/HIGH/MEDIUM/LOW findings in `b5396db6b..c96e499f5`. Both round-3 fixes are correct; no new defect found.

- Blocks present only under the other load now count as zero. Missing decode data produces Q1 INCONCLUSIVE and Option C.
- Skipped rows without `block` are ignored; usable rows without a block identity fail closed.
- The default five-block fit retains df=2. Missing idle data affects only the idle print-only estimate.
- Each independent fix reversion was caught by the [committed regression test](tests/align/test_ssd_qualification.py:184).

Verification: 48 focused tests passed; 615 scratch checks passed, including 360 unchanged-fit comparisons and seven real CLI plan/evaluate cases with strict JSON output. Probe evidence.

Tracked files remain unchanged. Evidence is synthetic; the canonical full suite was not run.

VERDICT: ADMIT

**Disposition (lead):** No findings. Fix rounds closed (gate_policy rule 4).
