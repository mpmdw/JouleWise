```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "All accepted round-2 cures implemented; 19 prescribed tests pass; Abstracts A/B/Refusal are 243/244/218 words.",
  "workspace": {
    "base_requested": "e057ce89",
    "base_mode": "exact",
    "head_start": "e057ce89a89f40f7612dbb4457cfebd654a53ca7",
    "head_end": "e057ce89a89f40f7612dbb4457cfebd654a53ca7",
    "upstream_end": "e057ce89a89f40f7612dbb4457cfebd654a53ca7",
    "branch": "feat/2026-09-04-paper-k"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/figures/fig3_decision_gates.svg",
    "docs/paper/results-fill-registry.md",
    "tests/test_paper_first_use_ledger.py",
    "tests/test_paper_terms_lint.py",
    "tests/test_select_outcome_branches.py",
    "docs/process_traces/2026-09-04-paper-k/07-fix-round-2-report.md"
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
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 11 tests in 1.892s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 1.229s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_select_outcome_branches",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 0.354s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in .*s\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The D-165 producer still emits replay.v1. All four comparative registry rows and the D165 note now disclose SUPPLIER_PENDING; the separately owned producer relabel remains an integration dependency.",
      "needs": "Lead verifies the producer relabel before production filling."
    }
  ]
}
```

## Change

All accepted Opus BL-1–BL-3, SF-1–SF-4, N-1–N-4, and Astra F1–F5 are cured. F6 is limited to deleting the redundant screen-renderings sentence. The identity fingerprints and binary64 walkthrough remain in place. No selector implementation change was needed; its existing structure and count guards pass the revised branches.

The three selected Abstracts contain **A: 243 words; B: 244 words; Refusal: 218 words**, leaving 7, 6, and 32 words under the 250-word cap. Refusal started at 250; cuts to its opening, repeated stop language, diagnostic sentence, and machine-scope sentence pay for the evidence distinction and glosses. These are selector counts with registered fill markers still present; final filled copies remain subject to its existing `--check-rendered` guard.

The draft retains **131 fill markers**, the three Abstract/Discussion/Conclusion outcome groups, nine unselected fixed transfer limitations (three per selected draft), and **Terms inventoried: 264; FAILS: 0.** Figure 3 parses as XML; its three bottom text nodes agree with the adopted caption. The SVG geometry was not changed.

Recomputed with the repository's `two_sided_student_t_p_value`: repeat SE = 0.442718872424 J; t = 11.293848786316 on 9 df; two-sided p = 1.28854294285e-6, printed as **1.29e-6**. With the illustrative other raw p = 0.041, Holm-adjusted values are 2.57708588569e-6 and 0.041; both still pass. At the fixed 2.262 critical value the repeat-only interval is [3.998569911, 6.001430089] J; with a stipulated 4-J deterministic widening it is [-0.001430089, 10.001430089] J. The sheet's separate 0.2-J metrology example is explicitly distinguished rather than presented as this path's arithmetic. No remaining dependent 2.8e-6 number exists in the draft.

**Wording precedence and first-use exceptions.** Astra's F2 construction replaces Opus's suggested Abstract energy-change sentence. Its new phrase “commanded graphics-processor pulses” otherwise precedes its Introduction construction, so each Abstract adds “(work with time-stamped start and stop commands)” and the ledger home moves to Abstract. In the Refusal Abstract, “stating that a window failed requires” carries the empirical non-admission condition without introducing “admission” before its construction; “absent” also avoids moving the established “missing / malformed” first use. The exact F1 proposed sentence is adopted in Section 4 and both later Refusal carriers. Astra's F5 removes the premature alias; a sentence now defines total standard error at its actual later first use, and its ledger home is Further limitations. No Astra wording was displaced by Opus wording. OR-01 and its carriers identify unavailable source evidence when no issued reason exists, rather than inventing a reason.

**Cure ledger — exact baseline-to-final edits.** Old lines refer to e057ce89; new lines refer to the uncommitted final tree. Every changed hunk in the six implementation/test files is reproduced below; an empty side means insertion or deletion. The report itself is the seventh changed path.

**1. F2 / BL-3 / N-1 — Abstract A operands, allocation, pulse gloss, and budget** — `docs/paper/draft-v2-skeleton.md`, old line 29 → new line 29.

Old:

```text
> Software can report one average power value over a span that crosses the change from reading an input to generating output tokens. Moving that dividing time changes the energy assigned to each part without changing the request total. JouleWise first used deliberately started graphics-processor work to measure how far the dividing time could be wrong, then recalculated the largest change in interval-overlap-assigned phase energy over the registered timing domain—the set of edge movements fixed before collection. This timing sensitivity is conditional on holding each record at its reported average; it is not a bound on physical phase energy under arbitrary within-record allocations. For every required calculation, that limit was at least twice the limit obtained at the recorded dividing time; the result remained at least twice as large under a second calculation retaining a shared sign, meaning one direction applied to the nonnegative energy changes allowed in every group of four runs. Independently of those calculations, the fixed Qwen3-8B and Qwen3-1.7B comparison reported [FILL:DS-32] for generating later output tokens and [FILL:PG-08] for reading the input through its first output token. Earlier measurements of short requests found that [FILL:DG-067] of [FILL:DG-068] measured parts had fewer than three power readings crossing them, while [FILL:DG-069] had at least three. The result is limited to the tested Apple computer, software, workloads, and processor-power figures reported by macOS rather than power at the wall outlet. Transfer of the pulse-derived timing allowance to inference was not tested.
```

New:

```text
> Software can report one average power value over a span that crosses the change from reading an input to generating output tokens. JouleWise assigns energy to each part as average power times overlap duration; moving the dividing time reallocates energy without changing the request total. Using a timing allowance from commanded graphics-processor pulses (work with time-stamped start and stop commands), JouleWise recalculated bounds on repeat scatter or same-condition differences over the registered timing domain—the edge movements fixed before collection—and divided each largest bound by its recorded-time value. This timing sensitivity is conditional on holding each record at its reported average; it is not a bound on physical phase energy under arbitrary within-record allocations. For every required calculation, the largest bound was at least twice its recorded-time value; the result remained at least twice as large under a second calculation retaining a shared sign, meaning one direction applied to the nonnegative energy changes allowed in every group of four runs. Independently of those calculations, the fixed Qwen3-8B and Qwen3-1.7B comparison reported [FILL:DS-32] for generating later output tokens and [FILL:PG-08] for reading the input through its first output token. Earlier short requests had [FILL:DG-067] of [FILL:DG-068] measured parts crossed by fewer than three power readings; [FILL:DG-069] had at least three. The result is limited to the tested Apple computer, software, workloads, and processor-power figures reported by macOS rather than power at the wall outlet. Transfer of the pulse-derived timing allowance to inference was not tested.
```

**2. F2 / BL-3 / N-1 — Abstract B operands, allocation, pulse gloss, and budget** — `docs/paper/draft-v2-skeleton.md`, old line 35 → new line 35.

Old:

```text
> Software can report one average power value over a span that crosses the change from reading an input to generating output tokens. Moving that dividing time changes the energy assigned to each part without changing the request total. JouleWise first used deliberately started graphics-processor work to measure how far the dividing time could be wrong, then recalculated the largest change in interval-overlap-assigned phase energy over the registered timing domain—the set of edge movements fixed before collection. This timing sensitivity is conditional on holding each record at its reported average; it is not a bound on physical phase energy under arbitrary within-record allocations. Every required value matched its named source record, and every division used a nonzero second value, but at least one result was less than 2. The cases below 2 were [FILL:OB-01], so the evidence did not show that allowed movement at least doubled the recorded-time limit in every case. Independently of those calculations, the fixed Qwen3-8B and Qwen3-1.7B comparison reported [FILL:DS-32] for generating later output tokens and [FILL:PG-08] for reading the input through its first output token. Earlier measurements of short requests found that [FILL:DG-067] of [FILL:DG-068] measured parts had fewer than three power readings crossing them, while [FILL:DG-069] had at least three. The result is limited to the tested Apple computer, software, workloads, and processor-power figures reported by macOS rather than power at the wall outlet. Transfer of the pulse-derived timing allowance to inference was not tested.
```

New:

```text
> Software can report one average power value over a span that crosses the change from reading an input to generating output tokens. JouleWise assigns energy to each part as average power times overlap duration; moving the dividing time reallocates energy without changing the request total. Using a timing allowance from commanded graphics-processor pulses (work with time-stamped start and stop commands), JouleWise recalculated bounds on repeat scatter or same-condition differences over the registered timing domain—the edge movements fixed before collection—and divided each largest bound by its recorded-time value. This timing sensitivity is conditional on holding each record at its reported average; it is not a bound on physical phase energy under arbitrary within-record allocations. Every required value matched its named source record, and every recorded-time value was nonzero, but at least one result was less than 2. The cases below 2 were [FILL:OB-01], so the evidence did not show that allowed movement at least doubled the recorded-time limit in every case. Independently of those calculations, the fixed Qwen3-8B and Qwen3-1.7B comparison reported [FILL:DS-32] for generating later output tokens and [FILL:PG-08] for reading the input through its first output token. Earlier short requests had [FILL:DG-067] of [FILL:DG-068] measured parts crossed by fewer than three power readings; [FILL:DG-069] had at least three. The result is limited to the tested Apple computer, software, workloads, and processor-power figures reported by macOS rather than power at the wall outlet. Transfer of the pulse-derived timing allowance to inference was not tested.
```

**3. F1 / F2 / BL-3 / N-1 — Refusal Abstract evidence distinction, conditional calculation, glosses, and budget** — `docs/paper/draft-v2-skeleton.md`, old line 41 → new line 41.

Old:

```text
> Software can report one average power value over a span that crosses the change from reading an input to generating output tokens. Moving that dividing time changes the energy assigned to each part without changing the request total. JouleWise first used deliberately started graphics-processor work to measure how far the dividing time could be wrong, then recalculated the largest change in interval-overlap-assigned phase energy over the registered timing domain—the set of edge movements fixed before collection. This timing sensitivity is conditional on holding each record at its reported average; it is not a bound on physical phase energy under arbitrary within-record allocations. JouleWise stopped at one of two points. Before comparison, it stopped if either model's planned measurement period was excluded or a required, source-checked result for reading the input or generating output tokens was absent. At close-out, it stopped if a required division lacked a value, could not be matched to its source record, or divided by zero. The issued stop and reason were [FILL:OR-01]. The stopped evidence supports neither a direction between Qwen3-8B and Qwen3-1.7B nor a statement about how much the dividing-time error increased the limit. Earlier measurements of short requests found that [FILL:DG-067] of [FILL:DG-068] measured parts had fewer than three power readings crossing them, while [FILL:DG-069] had at least three. The stop is limited to the tested Apple computer, software, workloads, and processor-power figures reported by macOS rather than power at the wall outlet. Transfer of the pulse-derived timing allowance to inference was not tested.
```

New:

```text
> Software can report average power over a span crossing the change from reading input to generating tokens. JouleWise assigns energy to each part as average power times overlap duration; moving the dividing time reallocates energy without changing the request total. Using a timing allowance from commanded graphics-processor pulses (work with time-stamped start and stop commands), JouleWise would recalculate bounds on repeat scatter or same-condition differences over the registered timing domain—the edge movements fixed before collection—and divide each largest bound by its recorded-time value. This holds each record at its reported average; it does not bound physical phase energy under arbitrary within-record allocations. Before comparison, stating that a window failed requires a verified failed production-window record bound to the affected model and window; absent or invalid source evidence selects the methods/diagnostics fallback. Independently authenticated, unaffected model-comparison verdicts remain reportable. At close-out, a required division stops on absent or unauthenticated values or a zero denominator. The stop and issued reason, or unavailable source evidence, were [FILL:OR-01]. Stopped evidence supports no ratio result or model direction. Earlier short requests had [FILL:DG-067] of [FILL:DG-068] measured parts crossed by fewer than three power readings; [FILL:DG-069] had at least three. The scope is one Apple computer, software configuration, workloads, and macOS processor-power records. Transfer of the pulse-derived timing allowance to inference was not tested.
```

**4. BL-3 — allocation, timing-envelope, and held-average constructions** — `docs/paper/draft-v2-skeleton.md`, old line 61 → new line 61.

Old:

```text
interval-overlap allocation of the sampler's interval-average records. The
record's integrated energy is the time integral \(\int P(t)\,dt\) over its full
span. The timing envelope describes movement of that allocation over the
registered timing domain, conditional on holding each record at its reported
average. It bounds neither physical phase energy under arbitrary within-record
allocations nor inference transfer nor future-error coverage. Moving the edge
```

New:

```text
**interval-overlap allocation**: each sampling record's energy is divided
between the two phases in proportion to the share of its interval falling on
each side of the phase boundary. The record's integrated energy is the time integral \(\int P(t)\,dt\) over its full
span. The **timing envelope** is the range of assigned energies over the
registered timing domain, conditional on the **held-average reconstruction**,
which holds each record at its reported average. It bounds neither physical
phase energy under arbitrary within-record allocations nor inference transfer nor future-error coverage. Moving the edge
```

**5. SF-4 — reconstructible partial-record enclosure** — `docs/paper/draft-v2-skeleton.md`, old line 74 → new line 75.

Old:

```text
envelope is [8.8, 9.2] J, while the nonnegative partial-record enclosure is
[8, 10] J. The latter is a diagnostic of allocation ambiguity at the registered
window; it is reported, never composed into any bound.
```

New:

```text
envelope is [8.8, 9.2] J, while allowing each record's energy to sit anywhere
inside its own interval gives the nonnegative partial-record enclosure
[8, 10] J: the eight records lying wholly inside contribute 8 J, and the two
records the window only partly covers contribute between 0 and 1 J each.
The latter is a diagnostic of allocation ambiguity at the registered window; it is reported, never composed into any bound.
```

**6. SF-2 — inserted-gap check is future work, not performed** — `docs/paper/draft-v2-skeleton.md`, old line 102 → new line 105.

Old:

```text
model-work edges with the same error. Because pulses are not inference, a
later **inserted-gap check** creates about 500 ms of no work between prefill and
decode and compares the gap's independently time-stamped edges with the power
record.
```

New:

```text
model-work edges with the same error. Because pulses are not inference, an
**inserted-gap check**—commanding about 500 ms of no work between prefill and
decode and comparing the gap's independently time-stamped edges with the power
record—is registered as future diagnostic work; this paper did not run it.
```

**7. F6 — delete only the redundant screen-renderings sentence** — `docs/paper/draft-v2-skeleton.md`, old line 483 → new line 486.

Old:

```text
the calibration corpus—is 9.724 ms. <!-- DG-059 --> The same screen is rendered
elsewhere as 0.009724 s, as a 9.724-ms reference, and again as 9.724 ms; these
are unit or prose renderings of that one screen, not separate sensitivity
results. <!-- DG-060; DG-061; DG-062 --> The superseded calibration corpus
```

New:

```text
the calibration corpus—is 9.724 ms. <!-- DG-059 --> The superseded calibration corpus
```

**8. BL-1 — recomputed two-sided probability** — `docs/paper/draft-v2-skeleton.md`, old line 831 → new line 831.

Old:

```text
degrees of freedom. The separate dependence-sensitivity sheet,
```

New:

```text
degrees of freedom, with two-sided \(p=1.29\times10^{-6}\). The separate
dependence-sensitivity sheet,
```

**9. BL-1 — dependent Holm ordering** — `docs/paper/draft-v2-skeleton.md`, old line 838 → new line 839.

Old:

```text
0.025; only if it passes, compare the second with 0.05. Pairing an illustrative
\(2.8\times10^{-6}\) with a second illustrative raw probability of \(0.041\) for
the other comparison orders them as \(2.8\times10^{-6}<0.041\): the smaller
```

New:

```text
0.025; only if it passes, compare the second with 0.05. Pairing that
\(1.29\times10^{-6}\) with a second illustrative raw probability of \(0.041\) for
the other comparison orders them as \(1.29\times10^{-6}<0.041\): the smaller
```

**10. SF-1 / BL-1 — distinguish the sheet's nonzero-metrology example** — `docs/paper/draft-v2-skeleton.md`, old line 845 → new line 846.

Old:

```text
paragraph is the other, and the sheet's \(\nu=9\) row fails that direction gate
on these same deltas while both comparisons pass Holm.
```

New:

```text
paragraph is the other. The sheet's \(\nu=9\) row adds a stipulated
0.2-J stochastic metrology standard error to these same deltas; its different
raw probability also passes Holm, but its decision interval fails the
direction gate. That composition example is not a campaign input.
```

**11. F5 / BL-2 — adopted repeat-standard-error interval sentence** — `docs/paper/draft-v2-skeleton.md`, old line 851 → new line 854.

Old:

```text
The direction check requires two named complete uncertainty intervals: the
measurement interval, formed from the total standard error, and the decision
interval, formed by extending both ends of that measurement interval by the
sum of the recorded deterministic bounds. A deterministic bound is a
```

New:

```text
The direction check requires the measurement interval, formed from the repeat
standard error already defined for this gross phase-energy path, and the
decision interval, formed by extending both ends by the sum of the recorded
deterministic bounds. A deterministic bound is a
```

**12. F1 — governing Refusal form preserves unaffected verdicts** — `docs/paper/draft-v2-skeleton.md`, old line 907 → new line 910.

Old:

```text
> Before comparison, Refusal applies when a model-specific measurement window was excluded or an authenticated token-generation or prompt-processing verdict is absent. At close-out, it applies when a required ratio is missing, unauthenticated, or has a zero denominator. In either case, the paper names the stopped stage and prints its issued reason as [FILL:OR-01]; it selects neither outcome A nor outcome B and makes no boundary-doubling or directional model claim from the stopped evidence.
```

New:

```text
> Before comparison, an empirical non-admission statement requires a verified failed production-window record bound to the affected model and window; missing or invalid source evidence selects the methods/diagnostics fallback. Independently authenticated, unaffected model-comparison verdicts remain reportable. At close-out, it applies when a required ratio is missing, unauthenticated, or has a zero denominator. In either case, the paper names the stopped stage and prints its issued reason, or identifies the unavailable source evidence, as [FILL:OR-01]; it selects neither outcome A nor outcome B and makes no boundary-doubling or directional model claim from the stopped evidence.
```

**13. F4 — adopted figure-caption notes** — `docs/paper/draft-v2-skeleton.md`, old line 922 → new line 925.

Old:

```text
*Figure 3. Decision-gate schematic; no measured data or numeric threshold is encoded by its layout. On the white background, the title and subtitle identify two gates and four outcomes. In the upper lane, a dashed box lists an admission or custody failure and the six evidence defects that can cause it; a right-pointing arrow labelled as a side entry that reaches no gate leads to the bordered “refused” box, which says that the evidence produces no result. A pale horizontal rule separates that refusal lane from the lower decision lane. The lower lane starts with a gray measured-contrast box containing the point estimate and composed uncertainty interval. A right-pointing arrow leads to the first white rounded box, Gate 1, which asks whether the estimate's magnitude exceeds the cell floor. Its “yes” arrow leads to the second white rounded box, Gate 2, which asks whether the whole uncertainty interval points one way; the next “yes” arrow leads to the blue directional-claim box, which states that both gates passed in the direction registered before collection. Gate 1's downward “no” arrow leads to the “not resolvable” box, which says the effect is smaller than this instrument can resolve and does not mean zero, equality, or no difference. Gate 2's downward “no” arrow leads to the “direction unresolved” box, which says the floor cleared but the interval did not settle direction, so no claim is made. The three bottom notes define the cell floor as the largest apparent effect produced when nothing changed, after the safeguards of Section 4, state that the floor and interval are separate gates, and state that their sum is a planning disclosure rather than an acceptance threshold.*
```

New:

```text
*Figure 3. Decision-gate schematic; no measured data or numeric threshold is encoded by its layout. On the white background, the title and subtitle identify two gates and four outcomes. In the upper lane, a dashed box lists an admission or custody failure and the six evidence defects that can cause it; a right-pointing arrow labelled as a side entry that reaches no gate leads to the bordered “refused” box, which says that the evidence produces no result. A pale horizontal rule separates that refusal lane from the lower decision lane. The lower lane starts with a gray measured-contrast box containing the point estimate and composed uncertainty interval. A right-pointing arrow leads to the first white rounded box, Gate 1, which asks whether the estimate's magnitude exceeds the cell floor. Its “yes” arrow leads to the second white rounded box, Gate 2, which asks whether the whole uncertainty interval points one way; the next “yes” arrow leads to the blue directional-claim box, which states that both gates passed in the direction registered before collection. Gate 1's downward “no” arrow leads to the “not resolvable” box, which says the effect is smaller than this instrument can resolve and does not mean zero, equality, or no difference. Gate 2's downward “no” arrow leads to the “direction unresolved” box, which says the floor cleared but the interval did not settle direction, so no claim is made. The bottom notes define the cell floor as the registered operational resolution guard for assigned-energy differences, retain the separate floor and interval gates, and identify F+B—floor plus deterministic widening—as a non-gating planning diagnostic, neither necessary nor sufficient for acceptance.*
```

**14. F3 — observed-sample statement replaces permanent dominance** — `docs/paper/draft-v2-skeleton.md`, old line 1171 → new line 1174.

Old:

```text
> Every independent-edge ratio and every required comparative shared-energy-sign/local-corner ratio was at least 2. This registered allocation-sensitivity result does not establish physical common-time robustness or transfer the pulse-derived timing allowance to inference. Measurement practice should characterize the named workload boundary, construct a separate registered allocation-sensitivity calculation for each configuration cell, and size the comparison before collection against that planning information. Additional repeats can narrow the point-only value, but they cannot remove the larger contribution from allowed boundary movement under the specified perturbation set; the fixed Qwen3-8B-versus-Qwen3-1.7B pair demonstrates that decision behavior, not a model-size scaling law. Independently of the ratio disposition, its authenticated token-generation verdict is [FILL:DS-32] and its authenticated prompt-processing verdict is [FILL:PG-08]. Earlier non-claim measurements produced prompt-processing, token-generation, and short-prompt ratios of [FILL:DG-099], [FILL:DG-100], and [FILL:DG-101], respectively; these historical examples neither supplied nor selected the campaign result. Transfer of the pulse-derived timing allowance to inference was not tested.
```

New:

```text
> Every independent-edge ratio and every required comparative shared-energy-sign/local-corner ratio was at least 2. This registered allocation-sensitivity result does not establish physical common-time robustness or transfer the pulse-derived timing allowance to inference. Measurement practice should characterize the named workload boundary, construct a separate registered allocation-sensitivity calculation for each configuration cell, and size the comparison before collection against that planning information. At the observed sample sizes, the registered perturbation calculations at least doubled every required component's point-only bound; this result does not establish how additional repeats would change those ratios. Independently of the ratio disposition, its authenticated token-generation verdict is [FILL:DS-32] and its authenticated prompt-processing verdict is [FILL:PG-08]. Earlier non-claim measurements produced prompt-processing, token-generation, and short-prompt ratios of [FILL:DG-099], [FILL:DG-100], and [FILL:DG-101], respectively; these historical examples neither supplied nor selected the campaign result. Transfer of the pulse-derived timing allowance to inference was not tested.
```

**15. F1 — Discussion Refusal carrier** — `docs/paper/draft-v2-skeleton.md`, old line 1187 → new line 1190.

Old:

```text
> The result stopped at one of two points. Before comparison, it stopped if a model-specific measurement window was excluded or if an authenticated token-generation or prompt-processing verdict was absent. At close-out, it stopped if a required ratio was missing, unauthenticated, or had a zero denominator. The applicable stop and its issued reason were [FILL:OR-01]. The stopped evidence supports neither the all-pass statement nor a below-two result, neither a directional model result nor a boundary-movement quotient, and no model-size scaling law. Earlier non-claim measurements produced prompt-processing, token-generation, and short-prompt ratios of [FILL:DG-099], [FILL:DG-100], and [FILL:DG-101], respectively; these historical examples do not replace the unavailable campaign result. Transfer of the pulse-derived timing allowance to inference was not tested.
```

New:

```text
> The result stopped at one of two points. Before comparison, an empirical non-admission statement requires a verified failed production-window record bound to the affected model and window; missing or invalid source evidence selects the methods/diagnostics fallback. Independently authenticated, unaffected model-comparison verdicts remain reportable. At close-out, it stopped if a required ratio was missing, unauthenticated, or had a zero denominator. The applicable stop and its issued reason, or the unavailable source evidence, were [FILL:OR-01]. The stopped evidence supports neither the all-pass statement nor a below-two result, neither a directional model result nor a boundary-movement quotient, and no model-size scaling law. Earlier non-claim measurements produced prompt-processing, token-generation, and short-prompt ratios of [FILL:DG-099], [FILL:DG-100], and [FILL:DG-101], respectively; these historical examples do not replace the unavailable campaign result. Transfer of the pulse-derived timing allowance to inference was not tested.
```

**16. BL-2 — total-standard-error definition at actual first use** — `docs/paper/draft-v2-skeleton.md`, old line 1243 → new line 1246.

Old:

```text
\(d_i=(B_{i1}+B_{i2}-A_{i1}-A_{i2})/2\). The sensitivity calculation is
```

New:

```text
\(d_i=(B_{i1}+B_{i2}-A_{i1}-A_{i2})/2\). For this path, the **total standard error** equals the modeled repeat
standard error, with no additional stochastic metrology variance. The
sensitivity calculation is
```

**17. SF-1 — zero metrology is path-specific; sheet is arithmetic only** — `docs/paper/draft-v2-skeleton.md`, old line 1265 → new line 1270.

Old:

```text
For these gross phase-energy contrasts, the current builder supplies no
additional stochastic metrology variance. Every dependence model therefore
sets the total stochastic standard error to its modeled repeat standard error;
timing and other deterministic allowances remain separate. <!-- Pre-registered design/model
```

New:

```text
For these gross phase-energy contrasts the current builder supplies no
additional stochastic metrology variance, so \(SE_{\mathrm{metrology}}=0\) on
this path and each model's total stochastic standard error reduces to its
modeled repeat standard error. The dependence-sensitivity sheet's worked
example stipulates a nonzero \(se_{\mathrm{metrology}}\) and is an arithmetic
check of the composition, not a campaign input. Timing and other deterministic
allowances remain separate. <!-- Pre-registered design/model
```

**18. BL-3 — Conclusion A estimand glosses** — `docs/paper/draft-v2-skeleton.md`, old line 1410 → new line 1418.

Old:

```text
> JouleWise measures how interval-overlap-assigned phase energy changes over the registered timing domain, conditional on the held-average reconstruction; it does not bound physical phase energy under arbitrary within-record allocations. Every independent-edge ratio was at least 2, and every comparative ratio remained at least 2 under a second calculation retaining a shared sign for block-level energy allowances, so the registered perturbation calculations at least doubled every component's point-only value. Independently of that ratio disposition, the fixed Qwen3-8B-versus-Qwen3-1.7B comparison's authenticated token-generation verdict is [FILL:DS-32] and its authenticated prompt-processing verdict is [FILL:PG-08]; the pair demonstrates the resulting decision behavior rather than a model-size scaling law. The retained **short-input diagnostic records** are the earlier measurements of requests with short prompt processing. They found that [FILL:DG-067] of [FILL:DG-068] measured phases failed the minimum overlap rule and [FILL:DG-069] passed it. The result applies to one Apple computer, one software and internal-counter configuration, and the tested workloads. Transfer of the pulse-derived timing allowance to inference was not tested.
```

New:

```text
> JouleWise measures how interval-overlap-assigned phase energy—average power times overlap duration—changes over the registered timing domain, conditional on the held-average reconstruction, which holds each record at its reported average; it does not bound physical phase energy under arbitrary within-record allocations. Every independent-edge ratio was at least 2, and every comparative ratio remained at least 2 under a second calculation retaining a shared sign for block-level energy allowances, so the registered perturbation calculations at least doubled every component's point-only value. Independently of that ratio disposition, the fixed Qwen3-8B-versus-Qwen3-1.7B comparison's authenticated token-generation verdict is [FILL:DS-32] and its authenticated prompt-processing verdict is [FILL:PG-08]; the pair demonstrates the resulting decision behavior rather than a model-size scaling law. The retained **short-input diagnostic records** are the earlier measurements of requests with short prompt processing. They found that [FILL:DG-067] of [FILL:DG-068] measured phases failed the minimum overlap rule and [FILL:DG-069] passed it. The result applies to one Apple computer, one software and internal-counter configuration, and the tested workloads. Transfer of the pulse-derived timing allowance to inference was not tested.
```

**19. BL-3 — Conclusion B estimand glosses** — `docs/paper/draft-v2-skeleton.md`, old line 1416 → new line 1424.

Old:

```text
> JouleWise measures how interval-overlap-assigned phase energy changes over the registered timing domain, conditional on the held-average reconstruction; it does not bound physical phase energy under arbitrary within-record allocations. Every required ratio was authenticated and evaluable, but at least one independent-edge ratio or required comparative shared-energy-sign/local-corner ratio was below 2, so the paper does not claim that the registered perturbation set doubled every point-only value. The components with a below-two ratio were [FILL:OB-01]. Independently of that ratio disposition, the fixed Qwen3-8B-versus-Qwen3-1.7B comparison's authenticated token-generation verdict is [FILL:DS-32] and its authenticated prompt-processing verdict is [FILL:PG-08]; the pair demonstrates the resulting decision behavior rather than a model-size scaling law. The retained **short-input diagnostic records** are the earlier measurements of requests with short prompt processing. They found that [FILL:DG-067] of [FILL:DG-068] measured phases failed the minimum overlap rule and [FILL:DG-069] passed it. The result applies to one Apple computer, one software and internal-counter configuration, and the tested workloads. Transfer of the pulse-derived timing allowance to inference was not tested.
```

New:

```text
> JouleWise measures how interval-overlap-assigned phase energy—average power times overlap duration—changes over the registered timing domain, conditional on the held-average reconstruction, which holds each record at its reported average; it does not bound physical phase energy under arbitrary within-record allocations. Every required ratio was authenticated and evaluable, but at least one independent-edge ratio or required comparative shared-energy-sign/local-corner ratio was below 2, so the paper does not claim that the registered perturbation set doubled every point-only value. The components with a below-two ratio were [FILL:OB-01]. Independently of that ratio disposition, the fixed Qwen3-8B-versus-Qwen3-1.7B comparison's authenticated token-generation verdict is [FILL:DS-32] and its authenticated prompt-processing verdict is [FILL:PG-08]; the pair demonstrates the resulting decision behavior rather than a model-size scaling law. The retained **short-input diagnostic records** are the earlier measurements of requests with short prompt processing. They found that [FILL:DG-067] of [FILL:DG-068] measured phases failed the minimum overlap rule and [FILL:DG-069] passed it. The result applies to one Apple computer, one software and internal-counter configuration, and the tested workloads. Transfer of the pulse-derived timing allowance to inference was not tested.
```

**20. F1 / BL-3 — Conclusion Refusal distinction and estimand glosses** — `docs/paper/draft-v2-skeleton.md`, old line 1422 → new line 1430.

Old:

```text
> JouleWise fixes how interval-overlap-assigned phase energy would be tested over the registered timing domain, conditional on the held-average reconstruction; it does not bound physical phase energy under arbitrary within-record allocations. The result stopped at one of two points. Before comparison, it stopped if a model-specific measurement window was excluded or if an authenticated token-generation or prompt-processing verdict was absent. At close-out, it stopped if a required ratio was missing, unauthenticated, or had a zero denominator. The applicable stop and its issued reason were [FILL:OR-01]. The stopped evidence supports neither a boundary-doubling result nor a below-two result, and it supports no model direction or scaling law. The retained **short-input diagnostic records** are the earlier measurements of requests with short prompt processing. They found that [FILL:DG-067] of [FILL:DG-068] measured phases failed the minimum overlap rule and [FILL:DG-069] passed it. The stopped result is confined to one Apple computer, one software and internal-counter configuration, and the tested workloads. Transfer of the pulse-derived timing allowance to inference was not tested.
```

New:

```text
> JouleWise fixes how interval-overlap-assigned phase energy—average power times overlap duration—would be tested over the registered timing domain, conditional on the held-average reconstruction, which holds each record at its reported average; it does not bound physical phase energy under arbitrary within-record allocations. The result stopped at one of two points. Before comparison, an empirical non-admission statement requires a verified failed production-window record bound to the affected model and window; missing or invalid source evidence selects the methods/diagnostics fallback. Independently authenticated, unaffected model-comparison verdicts remain reportable. At close-out, it stopped if a required ratio was missing, unauthenticated, or had a zero denominator. The applicable stop and its issued reason, or the unavailable source evidence, were [FILL:OR-01]. The stopped evidence supports neither a boundary-doubling result nor a below-two result, and it supports no model direction or scaling law. The retained **short-input diagnostic records** are the earlier measurements of requests with short prompt processing. They found that [FILL:DG-067] of [FILL:DG-068] measured phases failed the minimum overlap rule and [FILL:DG-069] passed it. The stopped result is confined to one Apple computer, one software and internal-counter configuration, and the tested workloads. Transfer of the pulse-derived timing allowance to inference was not tested.
```

**21. F2 — pulse term ledger home moves to Abstract** — `docs/paper/draft-v2-skeleton.md`, old line 1757 → new line 1765.

Old:

```text
| commanded graphics-processor pulses | 1. Introduction | glossed-at-first-use | Fixed-duration graphics-processor work with time-stamped start and stop commands inside one uninterrupted measurement session. |
```

New:

```text
| commanded graphics-processor pulses | Abstract | glossed-at-first-use | Each branch defines work with time-stamped start and stop commands; the Introduction supplies the fixed duration and measurement session. |
```

**22. BL-3 — three estimand ledger rows** — `docs/paper/draft-v2-skeleton.md`, old line 1759 → new line 1767.

Old:

```text
(absent)
```

New:

```text
| interval-overlap allocation / interval-overlap-assigned phase energy | 1. Introduction | glossed-at-first-use | Split each record's energy in proportion to the interval on each side of the phase boundary; each Abstract and Conclusion branch states average power times overlap duration. |
| held-average reconstruction | 1. Introduction | glossed-at-first-use | Hold each record at its reported average; each Abstract states the mechanism and each Conclusion glosses the label. |
| timing envelope | 1. Introduction | glossed-at-first-use | Range of assigned energies over the registered timing domain, conditional on the stated reconstruction. |
```

**23. N-2 — floor-pack ledger definition aligned** — `docs/paper/draft-v2-skeleton.md`, old line 1836 → new line 1847.

Old:

```text
| floor packs / contrast pack | 3. Instrument characterization | glossed-at-first-use | The first use defines floor packs as campaign plans that collect null-calibration data; the contrast pack is the separate two-model science comparison. |
```

New:

```text
| floor packs / contrast pack | 3. Instrument characterization | glossed-at-first-use | The first use defines floor packs as campaign plans that collect calibration data used to build a comparator floor; the contrast pack is the separate two-model science comparison. |
```

**24. BL-2 — total-standard-error ledger home corrected** — `docs/paper/draft-v2-skeleton.md`, old line 1887 → new line 1898.

Old:

```text
| total standard error | Adding publication safeguards after the ratio | glossed-at-first-use | For the gross phase-energy path, this is the standard error of the block differences because the builder supplies no additional stochastic metrology variance. |
```

New:

```text
| total standard error | Further limitations | glossed-at-first-use | For the gross phase-energy path, this is the standard error of the block differences because the builder supplies no additional stochastic metrology variance. |
```

**25. BL-2 — interval ledger definition aligned** — `docs/paper/draft-v2-skeleton.md`, old line 1895 → new line 1906.

Old:

```text
| measurement interval / decision interval / deterministic bound | Adding publication safeguards after the ratio | glossed-at-first-use | Total-standard-error interval; that interval extended by authenticated non-random maximum displacements. |
```

New:

```text
| measurement interval / decision interval / deterministic bound | Adding publication safeguards after the ratio | glossed-at-first-use | Repeat-standard-error interval for this gross phase-energy path; that interval extended by authenticated non-random maximum displacements. |
```

**26. BL-3 — 264-row zero-FAIL footer** — `docs/paper/draft-v2-skeleton.md`, old line 2022 → new line 2033.

Old:

```text
a failure. Terms inventoried: 261; FAILS: 0.
```

New:

```text
a failure. Terms inventoried: 264; FAILS: 0.
```

**27. F4 — SVG floor, independent gates, and F+B notes aligned** — `docs/paper/figures/fig3_decision_gates.svg`, old line 89 → new line 89.

Old:

```text
    <text x="40" y="572">The cell floor is the largest apparent effect this instrument produces on this kind of measurement when nothing has actually changed, after the safeguards of Section 4.</text>
    <text x="40" y="592">The floor and the interval are checked as separate gates. Their sum is only a sizing disclosure — a planning disclosure — and is never</text>
    <text x="40" y="612">used as a single acceptance threshold; the uncertainty interval is never compared with that sum.</text>
```

New:

```text
    <text x="40" y="572">The cell floor is the registered operational resolution guard for assigned-energy differences.</text>
    <text x="40" y="592">The floor and interval remain separate gates. F+B is floor plus deterministic widening: a non-gating planning diagnostic,</text>
    <text x="40" y="612">neither necessary nor sufficient for acceptance; the uncertainty interval is never compared with that sum.</text>
```

**28. SF-3 — D165 note discloses pending supplier** — `docs/paper/results-fill-registry.md`, old line 226 → new line 226.

Old:

```text
block inputs. R_cm is a shared-energy-sign/local-corner sensitivity diagnostic,
```

New:

```text
block inputs. SUPPLIER_PENDING: the producer emits .v1 until the D-165
relabel lands. R_cm is a shared-energy-sign/local-corner sensitivity diagnostic,
```

**29. SF-3 — alpha prefill comparative supplier status** — `docs/paper/results-fill-registry.md`, old line 242 → new line 243.

Old:

```text
| `[R_cm_1p7B_prefill_p[PREFILL_LENGTH]_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the alpha prefill cell's authenticated custodied block inputs | alpha / prefill-p[PREFILL_LENGTH] comparative R_cm column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence | D165, V5GEN, G2A |
```

New:

```text
| `[R_cm_1p7B_prefill_p[PREFILL_LENGTH]_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the alpha prefill cell's authenticated custodied block inputs | alpha / prefill-p[PREFILL_LENGTH] comparative R_cm column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence; SUPPLIER_PENDING: producer emits .v1 until the D-165 relabel lands | D165, V5GEN, G2A |
```

**30. SF-3 — alpha decode comparative supplier status** — `docs/paper/results-fill-registry.md`, old line 250 → new line 251.

Old:

```text
| `[R_cm_1p7B_decode_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the alpha decode cell's authenticated custodied block inputs | alpha / decode comparative R_cm column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence | D165, V5GEN |
```

New:

```text
| `[R_cm_1p7B_decode_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the alpha decode cell's authenticated custodied block inputs | alpha / decode comparative R_cm column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence; SUPPLIER_PENDING: producer emits .v1 until the D-165 relabel lands | D165, V5GEN |
```

**31. SF-3 — beta prefill comparative supplier status** — `docs/paper/results-fill-registry.md`, old line 258 → new line 259.

Old:

```text
| `[R_cm_8B_prefill_p[PREFILL_LENGTH]_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the beta prefill cell's authenticated custodied block inputs | beta / prefill-p[PREFILL_LENGTH] comparative R_cm column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence | D165, V5GEN, G2A |
```

New:

```text
| `[R_cm_8B_prefill_p[PREFILL_LENGTH]_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the beta prefill cell's authenticated custodied block inputs | beta / prefill-p[PREFILL_LENGTH] comparative R_cm column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence; SUPPLIER_PENDING: producer emits .v1 until the D-165 relabel lands | D165, V5GEN, G2A |
```

**32. SF-3 — beta decode comparative supplier status** — `docs/paper/results-fill-registry.md`, old line 266 → new line 267.

Old:

```text
| `[R_cm_8B_decode_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the beta decode cell's authenticated custodied block inputs | beta / decode comparative R_cm column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence | D165, V5GEN |
```

New:

```text
| `[R_cm_8B_decode_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the beta decode cell's authenticated custodied block inputs | beta / decode comparative R_cm column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence; SUPPLIER_PENDING: producer emits .v1 until the D-165 relabel lands | D165, V5GEN |
```

**33. N-4 — DS-28 column anchor restored** — `docs/paper/results-fill-registry.md`, old line 885 → new line 886.

Old:

```text
| DS-28 — Table 3 planning-only sizing diagnostic F+B and signed clearance, line 289, col 5 | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `C_decode_floor_clearance_J` on passage or negative of `S_decode_floor_shortfall_J` on refusal; branch must be explicit; any separately issued F+B value is non-gating planning information, neither necessary nor sufficient for acceptance | gamma / decode contrast | DERIVE | DRAFT/TEMPLATE SHAPE MISMATCH; draft has one unconditional cell | DRAFT, TPL |
```

New:

```text
| DS-28 — Table 3 planning-only sizing diagnostic F+B and signed clearance, line 289, col 5 under `Sizing sum F+B; signed clearance` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `C_decode_floor_clearance_J` on passage or negative of `S_decode_floor_shortfall_J` on refusal; branch must be explicit; any separately issued F+B value is non-gating planning information, neither necessary nor sufficient for acceptance | gamma / decode contrast | DERIVE | DRAFT/TEMPLATE SHAPE MISMATCH; draft has one unconditional cell | DRAFT, TPL |
```

**34. N-4 — PG-04 column anchor restored** — `docs/paper/results-fill-registry.md`, old line 894 → new line 895.

Old:

```text
| PG-04 — Table 3 planning-only sizing diagnostic F+B and signed clearance, line 290, col 5 | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | Future branch-explicit clearance or shortfall derivation for the selected `_v5` prefill contrast; no exact token exists; any separately issued F+B value is non-gating planning information, neither necessary nor sufficient for acceptance | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING; shape contract required | DRAFT, TPL, CV, V5GEN, G2A |
```

New:

```text
| PG-04 — Table 3 planning-only sizing diagnostic F+B and signed clearance, line 290, col 5 under `Sizing sum F+B; signed clearance` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | Future branch-explicit clearance or shortfall derivation for the selected `_v5` prefill contrast; no exact token exists; any separately issued F+B value is non-gating planning information, neither necessary nor sufficient for acceptance | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING; shape contract required | DRAFT, TPL, CV, V5GEN, G2A |
```

**35. F1 — OR-01 governing supplier/fallback distinction** — `docs/paper/results-fill-registry.md`, old line 925 → new line 926.

Old:

```text
| OR-01 — Refusal stop stage and issued reason in the Section-4 form and the Abstract, Section 7, and Section 10 Refusal paragraphs | `[FILL:OR-01]` | Before comparison: the authenticated window-admission outcome for the affected model or the authenticated claim-evaluation outcome for the affected token-generation (`DS-32`) or prompt-processing (`PG-08`) verdict. At close-out: authenticated `joulewise.d165_dominance_closeout.v1`. At every placement, render exactly one stage label (`before comparison` or `at close-out`) plus the reason issued by that governing evidence; name each affected model or verdict; include a Qwen-pair verdict only when its absence is the stop reason; never infer a reason from ratio disposition | fixed Qwen3 pair / two-stage refusal | STOP_FILL | SUPPLIERS_NAMED / VALUE_UNISSUED; TOKEN_MISSING; refuse on absent, unauthenticated, conflicting, or multi-stage-without-precedence inputs | DRAFT, AUTH, D165 |
```

New:

```text
| OR-01 — Refusal stop stage and issued reason in the Section-4 form and the Abstract, Section 7, and Section 10 Refusal paragraphs | `[FILL:OR-01]` | Before comparison: an empirical non-admission statement requires a verified failed production-window record bound to the affected model and window; missing or invalid source evidence selects the methods/diagnostics fallback, with no empirical failure inferred. At close-out: authenticated `joulewise.d165_dominance_closeout.v1`, including issued zero-denominator refusals; missing or invalid ratio evidence selects the fallback without erasing separately authenticated verdicts. At every placement, render exactly one stage label (`before comparison` or `at close-out`) plus the reason issued by its governing evidence, or explicitly state that the source evidence is unavailable or invalid without inventing an issued reason; name each affected model, window, or verdict. Independently authenticated, unaffected model-comparison verdicts remain reportable through `DS-32` and `PG-08`; never infer a reason or model verdict from ratio disposition | fixed Qwen3 pair / two-stage refusal | STOP_FILL | SUPPLIERS_NAMED / VALUE_UNISSUED; TOKEN_MISSING; use methods/diagnostics fallback on absent or invalid sources; refuse conflicting or multi-stage-without-precedence inputs | DRAFT, AUTH, D165 |
```

**36. BL-2 / BL-3 / F2 — defining phrases covered** — `tests/test_paper_first_use_ledger.py`, old line 53 → new line 53.

Old:

```text
(absent)
```

New:

```text
    "interval-overlap allocation / interval-overlap-assigned phase energy": (
        "energy is divided between the two phases in proportion to the share of its interval",
    ),
    "held-average reconstruction": ("which holds each record at its reported average",),
    "timing envelope": ("is the range of assigned energies over the registered timing domain",),
    "total standard error": (
        "equals the modeled repeat standard error",
        "with no additional stochastic metrology variance",
    ),
    "commanded graphics-processor pulses": ("work with time-stamped start and stop commands",),
```

**37. F2 — registered-domain regression follows adopted wording** — `tests/test_paper_first_use_ledger.py`, old line 70 → new line 80.

Old:

```text
        "registered timing domain—the set of edge movements fixed before collection",
```

New:

```text
        "registered timing domain—the edge movements fixed before collection",
```

**38. BL-2 / BL-3 / F2 — sentence-scoped term set** — `tests/test_paper_first_use_ledger.py`, old line 141 → new line 151.

Old:

```text
(absent)
```

New:

```text

SENTENCE_GLOSS_TERMS = frozenset({
    "interval-overlap allocation / interval-overlap-assigned phase energy",
    "held-average reconstruction",
    "timing envelope",
    "total standard error",
    "commanded graphics-processor pulses",
})
```

**39. BL-2 / BL-3 / F2 — first-use sentence enforcement** — `tests/test_paper_first_use_ledger.py`, old line 373 → new line 391.

Old:

```text
        block = _plain_for_gloss_check(blocks[occurrence.block_index].text)
```

New:

```text
        raw_block = blocks[occurrence.block_index].text
        unit = "paragraph"
        if row_term in SENTENCE_GLOSS_TERMS:
            # A definition in the next sentence cannot cure these first uses,
            # even when Markdown places both sentences in one paragraph.
            boundaries = list(re.finditer(r"[.!?]\s+", raw_block))
            start = max(
                (match.end() for match in boundaries
                 if match.end() <= occurrence.character_index), default=0,
            )
            end = min(
                (match.end() for match in boundaries
                 if match.start() >= occurrence.character_index),
                default=len(raw_block),
            )
            raw_block = raw_block[start:end]
            unit = "sentence"
        block = _plain_for_gloss_check(raw_block)
```

**40. BL-2 / BL-3 / F2 — sentence-specific failure diagnostic** — `tests/test_paper_first_use_ledger.py`, old line 379 → new line 414.

Old:

```text
                f"{row_term}: first-use paragraph (line {occurrence.line_index + 1}) "
```

New:

```text
                f"{row_term}: first-use {unit} (line {occurrence.line_index + 1}) "
```

**41. BL-2 / BL-3 / F2 — delayed-definition negative controls** — `tests/test_paper_first_use_ledger.py`, old line 484 → new line 519.

Old:

```text
(absent)
```

New:

```text

    def test_new_glosses_cannot_arrive_in_a_later_sentence(self) -> None:
        for term in SENTENCE_GLOSS_TERMS:
            with self.subTest(term=term):
                label = _alternatives(term)[0]
                definition = " ".join(GLOSS_REQUIREMENTS[term])
                row = LedgerRow(term, "Example", "glossed-at-first-use", definition)
                timely = [f"The {label} {definition}."]
                late = [f"The {label} is used here. Later: {definition}."]
                self.assertNotIn(term, "\n".join(_gloss_failures([row], timely)))
                self.assertIn(term, "\n".join(_gloss_failures([row], late)))
```

**42. N-3 — remove exact fill-count coupling from terminology lint** — `tests/test_paper_terms_lint.py`, old line 163 → new line 163.

Old:

```text
        self.assertEqual(draft.count("[FILL:"), 131)
```

New:

```text
        self.assertGreaterEqual(draft.count("[FILL:"), 1)
```

**43. F2 — registered-domain regression follows adopted wording** — `tests/test_paper_terms_lint.py`, old line 188 → new line 188.

Old:

```text
            "registered timing domain—the set of edge movements fixed before collection",
```

New:

```text
            "registered timing domain—the edge movements fixed before collection",
```

**44. BL-3 — allocation regression follows constructed definition** — `tests/test_paper_terms_lint.py`, old line 192 → new line 192.

Old:

```text
            "interval-overlap allocation of the sampler's interval-average records.",
```

New:

```text
            "**interval-overlap allocation**: each sampling record's energy is divided",
```

**45. SF-4 — enclosure regression follows derivation** — `tests/test_paper_terms_lint.py`, old line 194 → new line 194.

Old:

```text
            "envelope is [8.8, 9.2] J, while the nonnegative partial-record enclosure is\n"
            "[8, 10] J.",
```

New:

```text
            "envelope is [8.8, 9.2] J, while allowing each record's energy to sit anywhere\n"
            "inside its own interval gives the nonnegative partial-record enclosure\n"
            "[8, 10] J: the eight records lying wholly inside contribute 8 J, and the two\n"
            "records the window only partly covers contribute between 0 and 1 J each.",
```

**46. F2 — three-branch wording regression aligned** — `tests/test_paper_terms_lint.py`, old line 221 → new line 223.

Old:

```text
                "registered timing domain—the set of edge movements fixed before collection"
```

New:

```text
                "registered timing domain—the edge movements fixed before collection"
```

**47. F1 / F2 / BL-3 — selected branches construct operands and retain unaffected verdicts** — `tests/test_select_outcome_branches.py`, old line 62 → new line 62.

Old:

```text
(absent)
```

New:

```text
    def test_selected_branches_construct_allocation_and_preserve_verdicts(self) -> None:
        source = SKELETON.read_text(encoding="utf-8")
        for outcome in SELECTOR.BRANCHES:
            with self.subTest(outcome=outcome):
                selected = source
                for group in SELECTOR.GROUPS:
                    selected = SELECTOR._select_group(selected, group, outcome)
                abstract = selected.split("## Abstract\n", 1)[1].split(
                    "\n## 1. Introduction", 1
                )[0]
                sentences = abstract.split(". ")
                allocation = next(s for s in sentences if "assigns energy" in s)
                self.assertIn("average power times overlap duration", allocation)
                calculation = next(s for s in sentences if "Using a timing allowance" in s)
                self.assertIn("work with time-stamped start and stop commands", calculation)
                self.assertIn("bounds on repeat scatter or same-condition differences", calculation)
                self.assertIn("each largest bound by its recorded-time value", calculation)
                self.assertIn("holds each record at its reported average" if outcome == "REFUSAL"
                              else "holding each record at its reported average", abstract)
                conclusion = selected.split("## 10. Conclusion\n", 1)[1].split(
                    "## 11. References", 1
                )[0]
                first_sentence = conclusion.strip().split(". ", 1)[0]
                self.assertIn("phase energy—average power times overlap duration", first_sentence)
                self.assertIn("held-average reconstruction, which holds each record", first_sentence)
                if outcome == "REFUSAL":
                    self.assertIn("would recalculate", calculation)
                    self.assertIn("and divide each", calculation)
                    for section in (abstract, conclusion, selected.split(
                        "## 7.", 1
                    )[-1].split("### Further limitations", 1)[0]):
                        self.assertIn("verified failed production-window record", section)
                        self.assertIn("methods/diagnostics fallback", section)
                        self.assertIn("unaffected model-comparison verdicts remain reportable", section)
                        self.assertIn("zero denominator", section)
                else:
                    self.assertIn("JouleWise recalculated", calculation)
                    self.assertIn("and divided each", calculation)

```

## Verification notes

The user-mandated preflight replaced M0's discovery command. Only the three named unittest modules ran, sequentially, with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise` and `PYTHONDONTWRITEBYTECODE=1`. No discovery suite, model launcher, measurement, commit, or out-of-scope repository write ran. Scope-owned reporting replaces the normal RUN_STATE/TASK_QUEUE/run-report updates. Final desk verification is the three clean results in the envelope; lead review and production integration remain lead-owned.

Exact earlier test tails (the commands are the same V1/V2/V3 commands in the envelope):

Preflight V1:

```text
Ran 10 tests in 1.789s

OK
```

Preflight V2:

```text
Ran 4 tests in 1.388s

OK
```

Preflight V3:

```text
Ran 3 tests in 0.497s

OK
```

First post-edit V1:

```text
Ran 10 tests in 1.885s

FAILED (failures=1)
```

First post-edit V2:

```text
Ran 4 tests in 1.251s

OK
```

First post-edit V3:

```text
Ran 3 tests in 0.354s

OK
```

The intermediate V1 failure was `test_first_occurrence_is_in_exact_home_section`, term `missing / malformed`: Abstract versus Bracketed pulse-train algorithm. Replacing the two Abstract uses of “missing” with “absent” cured it without changing the ledger's established home. The final test additions bring the total from 17 to 19 tests. The new negative controls verify that the five newly guarded glosses fail if moved to a later sentence within the same paragraph; the branch test checks the allocation multiplication, complete-bound division, conditional Refusal calculation, Conclusion glosses, zero-denominator refusal, and survival of unaffected verdicts.

`git diff --check` passed. XML and text-node inspection verified the SVG edits; no visual render was performed. Workspace began clean at the requested exact head; HEAD and upstream remain unchanged. No unowned dirty files were observed.

## Residual risk

The D-165 producer still emits `d165_shared_sign_local_corner_replay.v1` at `joulewise/dominance_closeout.py:50`; the separately assigned relabel must land before v2-bound production filling. All four comparative rows and the D165 note now disclose that dependency. This round neither edits the producer nor claims live-hardware validation.

Next exact step: lead reviews this seven-path diff and integrates the separately owned D-165 relabel, checking its supplier identity before production filling. No commit was made.

