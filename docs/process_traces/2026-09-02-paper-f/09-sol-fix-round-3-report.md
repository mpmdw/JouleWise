# Sol fix round 3 report

Date: 2026-09-03 PDT  
Branch: `feat/2026-09-02-paper-f`  
Starting HEAD: `b7abc4fe0f4229c8330c73254430601d97a00442`

## Change

Implemented R3-final-2 in Section 3. The characterization table again has all
four ruled questions and retains their method text. A new plain-language status
column distinguishes the inputs collected by the campaign packs from the four
characterization reports that this campaign does not issue:

| Question | Collected input and location | Issuance status |
|---|---|---|
| Workload response | The floor packs record phase energies for their planned prompt workloads and fixed-output workload. | This campaign does not issue the workload-response characterization report. |
| Identical-condition null | The floor packs record same-condition A/B/B/A blocks as comparator-floor calibration data. | This campaign does not issue the identical-condition null characterization report. |
| Phase accounting | The floor packs and contrast pack record prompt-processing and token-generation phase energies. | This campaign does not issue the phase-accounting characterization report. |
| Drift and recovery | The floor packs and contrast pack record reference probes at the window opening, interior, and close. | This campaign does not issue the drift-and-recovery characterization report. |

The former two-characterization “does not collect” paragraph now states that
the campaign records relevant inputs for all four questions but applies none of
the frozen characterization calculations and issues none of their reports. One
sentence states Outcome D directly: the floor packs' same-condition null blocks
are calibration data used to build comparator floors, not a separate
characterization campaign. No characterization result number was added.

The remaining generic identical-condition “result” sentence is now conditional
on issuance. The DS-02, DS-03, DS-05, and DS-06 registry-anchor sentences remain
verbatim in Section 3. The only new built terms, `floor packs` and `contrast
pack`, are glossed at first use and recorded in both first-use ledgers.

## Executed evidence

### Mechanical first-use check of every added, moved, or retensed sentence

Wrapped Markdown was read as joined sentences. For each changed sentence, the
scan below inventories every term or criterion doing technical work and locates
its earlier or same-sentence construction. Ordinary connective words are marked
as carrying no technical term.

| Draft line(s) | Changed sentence(s) checked | First use and build/gloss | Result |
|---|---|---|---|
| 250–252 | The campaign records inputs for all four characterization questions but does not apply the frozen calculations or issue a report. | `instrument characterization` and the four physical questions are built at 234–248; `frozen` is built in Section 2 before this use. | PASS |
| 252–253 | The methods remain for a later campaign to apply. | No new technical term. | PASS |
| 253–256 | The floor-pack null blocks are comparator-floor calibration data, not a separate characterization campaign. | `same-condition A/B/B/A` and `comparator` are built at 240–241; `floor packs` is glossed in the same sentence as campaign plans collecting comparator-floor calibration data; `floor` is built in Section 1. | PASS |
| 355 | Workload-response question. | The question itself glosses `workload response` as whether request and token-generation energy increase with realized output length. | PASS |
| 355 | Floor-pack workload-input status and unissued-report status. | `floor packs` is built at 253–256; `phase energies` is built at 242; `fixed-output workload` states its fixed property in the phrase itself; `workload response` is glossed earlier in the row. | PASS |
| 355 | Restored workload calculation and refusal sentences. | `workload level`, `timing half-width`, and `per-token conversion` are each glossed in the sentence of first use; `admitted bundle` is built at 247–248; `registered` and `cell floor` are built earlier. | PASS |
| 356 | Identical-condition-null question. | The question itself glosses the term as an A/B/B/A comparison whose two conditions are the same. | PASS |
| 356 | Floor-pack null-input status and unissued-report status. | `floor packs` is built at 253–256; `same-condition A/B/B/A`, `calibration data`, and `comparator floor` are constructed there and at 240–241 before this use. | PASS |
| 356 | Restored null calculation and refusal sentences. | `workload magnitude` is glossed at first use; `interval of allowed differences` is constructed at 265–277; `mean interval` and the comparator test are constructed at 278–290; `A/B/B/A block` is built in Section 1. | PASS |
| 357 | Phase-accounting question and collected-input status. | The phase-accounting residual and phase energies are constructed at 323–342; `contrast pack` is glossed in the same sentence as the campaign plan collecting model-comparison data; `floor packs` is already built. | PASS |
| 357 | Phase-accounting unissued-report status. | `phase accounting` is constructed at 323–342 and named earlier in the row; `characterization report` uses the report/issuance distinction established at 250–253. | PASS |
| 358 | Drift-and-recovery question and reference-probe input status. | `drift and recovery`, `reference roles`, and `passing cooldown exit` are constructed at 344–351; reference probes are introduced at 243–246; both pack terms are already built. | PASS |
| 358 | Drift-and-recovery unissued-report status. | The characterization is built earlier in the row and at 344–351; the report/issuance distinction is established at 250–253. | PASS |
| 400–403 | An issued identical-condition result would establish measured-block containment only and would not claim population coverage. | `identical-condition`, `containment`, and the measured-block/population distinction are built at 265–321; the sentence introduces no new technical term and is explicitly conditional. | PASS |
| 1692 | Draft first-use ledger row for floor/contrast packs. | This meta-ledger row repeats the in-text gloss at 253–256 and 357. | PASS |
| 1881 | First-use inventory count changes from 250 to 251. | Mechanical ledger bookkeeping, not reader-facing technical prose. | PASS |
| Built-terms lexicon 39 | Successor-ledger row for floor/contrast packs. | Mirrors the in-text first-use glosses. | PASS |

### Requested test

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
```

Final tail:

```text
.............
----------------------------------------------------------------------
Ran 13 tests in 2.737s

OK
```

During the edit, the first run correctly rejected the new bold `floor packs`
term before its draft-ledger row was added; the next run correctly rejected the
stale inventory count. Both were repaired before the final passing run.

## Scope verification

`git diff --check` passes. The diff contains only Section 3, its first-use
ledger row and count, the successor built-terms row, and this report. The
Abstract, Section 6, Section 7 “What the finding changes,” Section 10, and all
other paper prose are unchanged.
