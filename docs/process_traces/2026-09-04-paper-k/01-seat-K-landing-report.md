```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Paper seat K landed the provisional ruling-17 pedagogy and fact corrections, retained the outcome structure, and passed all three authorized tests.",
  "workspace": {
    "base_requested": "30b5bc1f",
    "base_mode": "exact",
    "head_start": "30b5bc1f0406aa447ab81b4f9ba4efdb14bc3118",
    "head_end": "30b5bc1f0406aa447ab81b4f9ba4efdb14bc3118",
    "upstream_end": null,
    "branch": "feat/2026-09-04-paper-k"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/results-fill-registry.md",
    "docs/paper/fill-rehearsal/select_outcome_branches.py",
    "tests/test_paper_first_use_ledger.py",
    "tests/test_paper_terms_lint.py",
    "tests/test_select_outcome_branches.py",
    "docs/process_traces/2026-09-04-paper-k/01-seat-K-landing-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["..........", "----------------------------------------------------------------------", "Ran 10 tests in 1.747s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["....", "----------------------------------------------------------------------", "Ran 4 tests in 0.984s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_select_outcome_branches",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["...", "----------------------------------------------------------------------", "Ran 3 tests in 0.142s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in .*\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Final ruling 17 is still provisional pending the cold gate; every substantive cure below is recorded as a reversible sentence-unit replacement.",
      "needs": "If the cold gate amends the ruling, re-brief this seat against the cure ledger."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The requested selector test module did not exist at the exact base and its preflight import failed; the authorized tests/test_select_outcome_branches.py was added and the final run passes.",
      "needs": ""
    }
  ]
}
```

## Change

Implemented the eight ordered cure groups without changing the three outcome-group structures. The raw fill-marker census moved from 140 to 131 solely because the nine TR-01 markers became fixed limitation prose. Each selected outcome retains three transfer-limitation sentences. The first-use ledger ends with `Terms inventoried: 261; FAILS: 0.`

### Reversible cure ledger

1. **17-Q1 / 03-F1 / 02-F1 → line 17.** Old: “JouleWise — Measuring Phase Energy in Large-Language-Model (LLM) Inference on Apple Silicon.” New: “JouleWise — Measuring Interval-Overlap-Allocated Energy for Large-Language-Model (LLM) Inference Phases on Apple Silicon.”

2. **17-Q1 / 03-F1 / 02-F1 → lines 29, 35, 41.** Old: “JouleWise first used deliberately started graphics-processor work to measure how far the dividing time could be wrong, then recalculated the largest false difference after every allowed movement.” New: “JouleWise first used deliberately started graphics-processor work to measure how far the dividing time could be wrong, then recalculated the largest change in interval-overlap-assigned phase energy over the registered timing domain. This timing sensitivity is conditional on holding each record at its reported average; it is not a bound on physical phase energy under arbitrary within-record allocations.”

3. **17-Q1 / 03-F1 / 02-F1 → lines 60–70.** Old: “JouleWise assigns the record by multiplying that average by the time on each side of the phase boundary. ... Moving the edge within the same record transfers a slice of that energy from one phase to the other ... it cannot remove a displacement shared by every repeat.” New: “The measurand is energy assigned to each phase by interval-overlap allocation of the sampler's interval-average records. ... The timing envelope describes movement of that allocation over the registered timing domain, conditional on holding each record at its reported average. It bounds neither physical phase energy under arbitrary within-record allocations nor inference transfer nor future-error coverage. ... Repeating the request can narrow ordinary run-to-run scatter; it does not remove this allocation sensitivity.”

4. **17-Q1 / 02-F1 enclosure diagnostic → lines 72–76.** Old: no enclosure sentence. New: “In a synthetic enclosure diagnostic, a 0.9-s window crossing ten 100-ms records that each report 10 W is assigned 9 J. Its ±10-ms two-edge timing envelope is [8.8, 9.2] J, while the nonnegative partial-record enclosure is [8, 10] J. The latter is a diagnostic of allocation ambiguity at the registered window; it is reported, never composed into any bound.”

5. **17-Q1 / 03-F1 title-adjacent and claim-spine cures → lines 81, 500–504, 897, 1375, 1387, 1410, 1416, 1422.** Old: “The resulting bounds do not transfer”; “This 0.30-J movement is the change the timing uncertainty is allowed to make”; “JouleWise makes a false phase-energy difference measurable”; “carries uncertain phase-edge placement into the bound”; “treats worst-case phase-edge placement as bounded systematic uncertainty.” New, respectively: “allocation sensitivities do not transfer”; “This 0.30-J movement is the allocation sensitivity calculated under the held-average reconstruction; it is not a physical enclosure for arbitrary within-record power allocations”; outcome text measures interval-overlap-assigned phase energy conditional on the held-average reconstruction; “carries registered phase-edge perturbations into the allocation-sensitivity calculation”; “treats movement over the registered phase-edge domain as deterministic allocation sensitivity.”

6. **17-Q2 / 03-F7 / 02-F2 abstract A → line 29.** Old: “the result remained at least twice as large when the same timing error moved together across each group of four comparison runs.” New: “the result remained at least twice as large under a second calculation retaining a shared sign for block-level energy allowances.”

7. **17-Q2 / 03-F7 / 02-F2 → lines 138–154 and 633–714.** Old: “A four-run comparison has an additional physical problem: one timing error can be common to all four runs”; “timing-error sign”; “shared-error ratio”; “This quotient is the comparative shared-error ratio.” New: A/B/B/A floor and science roles are separated; the replay uses an energy-allowance sign; and `R_cm` is a “shared-energy-sign/local-corner sensitivity diagnostic” that “does not globally replay one physical common-time shift and has no proven conservatism for common-time motion.” The method adds: “Retaining the same sign for the scalar q_j allowances does not preserve or replay one physical time shift; their extrema can arise at different timing coordinates.”

8. **17-Q2 / 03-F7 → lines 717–720 and first-use ledger lines 1877–1878.** Old: “An absolute R_cm is not_applicable, not missing: the absolute formula first subtracts the cell mean, so a uniform shared shift cancels from every residual”; ledger row repeated that cancellation. New: “Absolute R_cm remains not_applicable because the registered replay is comparative-only, not because absolute timing uncertainty vanishes.” The cancellation row was deleted and the successor diagnostic rows state that this is not a physical common-time replay.

9. **17-Q2 registry → registry lines 225–231, 238–266.** Old: `d165_shared_sign_local_corner_replay.v1`, common-mode conservatism, and deviations-from-mean cancellation rationales. New: `.v2`, “shared-energy-sign/local-corner sensitivity diagnostic, with no proven conservatism for common-time motion”; “A uniform additive energy offset cancels from absolute residuals; a common time shift need not”; and comparative-only absolute `not_applicable` rationales.

10. **17-Q3 / 03-F5 / 02-F10 → lines 872–878.** Old: no explicit relationship between the two mandatory gates and F+B. New: “The floor and decision interval remain separate mandatory gates. For a symmetric measurement interval with half-width h and symmetric nonnegative deterministic widening B, their numerical conjunction is |estimate|>max(F,h+B); asymmetric intervals use their actual endpoints. F+B is only a non-gating planning diagnostic, neither necessary nor sufficient for acceptance, and neither mandatory gate may be removed as double counting.”

11. **17-Q3 / 03-F5 / 02-F10 registry → registry lines 884 and 893.** Old: “sizing sum F+B and signed clearance.” New: “planning-only sizing diagnostic F+B and signed clearance,” with any issued F+B value explicitly non-gating and neither necessary nor sufficient.

12. **17-Q5 / 03-F2 → lines 29, 35, 41, 1171, 1179, 1187, 1410, 1416, 1422.** Old: nine `[FILL:TR-01]` carrier clauses (“A later check ...; it [FILL:TR-01]”, “the inserted-gap check ... [FILL:TR-01]”, or “post-campaign inserted-gap check [FILL:TR-01]”). New at all nine placements: “Transfer of the pulse-derived timing allowance to inference was not tested.”

13. **17-Q5 / 03-F2 conditional-transfer clause → lines 1171 and 1195–1202.** Old: “This result supports the headline ... only if the post-campaign inserted-gap check supports applying the pulse-derived limit to inference. If that check supports the transfer ...”; “The concrete closing check is the inserted-gap experiment ... an exceedance would withdraw transfer.” New: “This registered allocation-sensitivity result does not establish physical common-time robustness or transfer the pulse-derived timing allowance to inference”; “The paper therefore does not apply it as an inference-error bound or make a later inserted-gap result a submission predicate.”

14. **17-Q5 registry and selector → registry line 923; selector lines 21–26, 100–103, 158–181.** Old: TR-01 `STOP_FILL` with an unissued transfer-fiducial supplier; selector counted a transfer-result marker and printed `transfer_slots=3`. New: TR-01 is `LIMITATION`, with dated `WITHDRAWN 2026-09-04` status and no evidence predicate; selector validates the fixed sentence and prints `transfer_limitations=3`.

15. **03-F4 interpolation → lines 854–860.** Old: “The calculation assigns power there from the straight line joining those samples, moves the start and end through their allowed neighboring-sample gaps, and retains the largest resulting energy change.” New: “For native interval-average records, the reducer integrates constant reported power over the overlap duration; its interpolation-bound term is zero. Timing uncertainty enters through separately recomputed boundary envelopes.” Point-sample interpolation is retained only as a named fallback.

16. **03-F4 stochastic dispatch → lines 811–833 and 1265–1268.** Old: phase metrology variances and A/B covariance were combined with repeat scatter, and the example stipulated `se_metrology=0.2 J`. New: “For the gross phase-energy contrasts used here, the current builder supplies no additional stochastic metrology variance, so the repeat standard error is the standard error of the block differences. Timing and other deterministic allowances are propagated separately.” The example now has `se_repeat=0.442719`, `t=11.2938`; dependence alternatives are sensitivity scenarios.

17. **03-F4 Student-t convention → lines 577–587.** Old: `t=.975,4=2.776445`, prediction `4.808944 J`, comparative value `6.808944 J`. New: “Using the code's fixed three-decimal lookup-table convention, t=.975,4=2.776,” prediction `4.808173 J`, comparative value `6.808173 J`.

18. **01-F5 / 03-F3 → lines 111–126.** Old: “A four-run model comparison produces a difference ... its two runs of one model ... its two runs of the other model.” New: the three-row source-to-estimand table maps “Same-model repeats → Absolute floor,” “Same-model null A/B/B/A blocks, with A = B → Comparative floor,” and “Two-model A/B/B/A blocks → Science contrast.”

19. **17-Q4 / 01-F5 / 03-F3 → lines 174–192; registry lines 148 and 151.** Old: the token-generation workload was the ordered eight-prompt set. New: “Its token-generation contrast uses prompt 0 ... for every block in both model arms”; “The comparison supports this fixed prompt and makes no prompt-population generality claim.” Registry V5-WL-001/004 carries the same prospective prompt-0 rule and leaves floor packs unchanged.

20. **02-F6 / 02-F7 / 03-F7 → lines 152–154, 559–561, 780–782, 1689.** Old: ratios asked whether timing uncertainty was as large as ordinary variation; the prediction and drift statements were unqualified; “not a ‘95/95’ population-coverage bound.” New: “Both ratios measure enlargement under specified perturbation sets; they do not estimate how often or how strongly those errors occur”; the prediction is conditional on the independent-normal model; the drift allowance covers sampled registered epochs only; and 95/95 is expanded as “a bound covering 95% of future edge errors with 95% confidence.”

21. **03-F7 Holm → lines 805–809.** Old: Holm “keeps the chance of any false direction claim across the pair at 0.05.” New: “We apply Holm at nominal family-wise level 0.05 to two model-based tests; error control depends on their distributional and dependence assumptions.”

22. **02-F9 / 03-F7 A/B/B/A timing → lines 231–248, 525–529, 775–778, 1275–1278.** Old: “Matching the average run time ... cancels steady linear drift”; Figure 2 was “drift-cancelling.” New: “The order balances conditions and suppresses a linear trend only when the sums of the A and B run midpoints match; unequal runtimes or cooldowns can break that symmetry.” Figure 2 is “time-balanced,” and later occurrences repeat the midpoint-sum condition.

23. **03-F10 diagnostic capture → line 266.** Old: “Every value in this worked example is diagnostic instrument evidence; none of it supports a claim.” New: “These values support only the diagnostic reconstruction of this retained calibration capture; they do not supply the prospective Qwen3 comparison.”

24. **03-F10 historical record support → lines 1103–1105.** Old: “These data are non-claim-bearing, meaning no paper claim rests on them.” New: “These historical data support only the descriptive record-support result for this population and do not supply the prospective Qwen3 comparison.”

The first-use ledger was updated only for changed or deleted vocabulary: allocation estimand, same-model floor sources, energy-allowance sign, `R_cm`, operational resolution guard, qualified Holm, actual stochastic dispatch, interval-average integration, and planning roles. Rows for the removed power-sample interpolation gloss, shared-error/absolute-cancellation rationale, and nonexistent stochastic metrology terms were deleted. Tests now enforce those successors, the 131/9 fill census, `.v2` registry version, LIMITATION withdrawal, and all three selector outcomes.

## Verification notes

Preflight ran in the required order. The first-use and terms-lint modules passed. The requested selector module failed preflight import because `tests/test_select_outcome_branches.py` did not exist at the exact base; the authorized file was then added. Final verification reran all three modules, one at a time, with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`; the exact tails are in V1–V3. No discovery suite, quiet-machine measurement, Claude/Codex subprocess or agent launch, commit, or out-of-scope write was performed.

## Residual risk

The language reflects provisional final ruling 17. A cold-gate amendment may require reversing the listed sentence units; no empirical result or hardware validation was introduced.
