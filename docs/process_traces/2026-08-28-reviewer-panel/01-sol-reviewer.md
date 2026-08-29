# Sol reviewer seat (gpt-5.6-sol, xhigh, read-only) — blind, 2026-08-28
Thread id: 01a04b27-b2ef-7c43-881e-319899ccc33f

## 1. Summary of contribution

This paper presents JouleWise, a phase-energy measurement methodology for LLM inference on one Apple M3 Max system using MLX and `powermetrics`. Its central insight is that repeatable energy measurements may still misattribute energy between prefill and decode when their boundary is uncertain. The system therefore brackets each science window with commanded GPU pulse trains, uses a corrected rate-aware set-membership clock model to bound pulse-edge placement, propagates timing uncertainty through phase-energy integration, combines that result with same-condition repeatability and drift allowances into a cell-specific resolution bound, and permits a directional model comparison only when separate magnitude, interval-direction, and registered-inference gates pass. The prospective `_v4` campaign is deliberately capable of producing either an attribution-dominance finding or a null, while preserving explicit refusals and a diagnostic negative result for short-prefill resolvability.

## 2. Strengths

- The central question is falsifiable. The paper explicitly states what happens if dominance holds for both phases, one phase, or neither, rather than defining success as whatever the campaign produces.

- The distinction between repeatability and attribution error is physically important and unusually well explained. The observation that repetition cannot remove a shared boundary error is a strong contribution to experimental practice.

- The corrected clock-anchor method is specified at an exceptional level of detail. Appendix A gives the affine-clock assumptions, exact feasible-set construction, outward rounding rules, refusal cases, and a worked reconstruction from retained clock stamps.

- The calibration is bracketed around the science window, and the operative bound cannot silently shrink after the post-window calibration. Recomputing or refusing affected phase energies when the later bound widens is good metrology discipline.

- The paper separates deterministic bounded uncertainty from statistical variation instead of treating all uncertainty as independent random noise. This is conceptually preferable to gaining artificial precision through averaging.

- Admission and custody are fail-closed. Missing, malformed, duplicated, stale, or inconsistent evidence yields a named refusal, while failed attempts and replacements remain visible.

- The A/B/B/A design addresses first-order drift, retains actual midpoint times, and acknowledges that unequal runtimes, curvature, and whole-window drift remain.

- The paper distinguishes evidence refusal, magnitude failure, and direction failure. In particular, it repeatedly avoids interpreting “not resolvable” as equality or zero effect.

- Diagnostic-era evidence is clearly separated from prospective claim-bearing evidence. The draft does not promote retired-clock results into current findings.

- Scope is disciplined: one physical unit, one software stack, processor channels rather than whole-system energy, and no unsupported model-size scaling law.

- The artifact path is unusually auditable. The permitted supporting guide, `docs/paper/artifact-guide.md`, confirms that calibration replay derives the anchor and pulse fits from primary bytes rather than trusting stored summaries.

## 3. Weaknesses, RANKED by how much each lowers your score

1. **The central validity assumption is not tested in the claim-bearing campaign.**

   **Where:** `## 7. Discussion and limitations` — “Nothing in the frozen `_v4` campaign tests that transfer.”

   **What:** A timing bound measured with isolated commanded GPU pulses under a lighter CPU regime is transported to sustained mixed CPU/GPU/ANE inference.

   **Why it matters:** Before/after pulse agreement establishes stability of the calibration regime, not applicability to inference. Scheduler contention, telemetry production, runtime event emission, and mixed-rail behavior could alter the relation between runtime boundaries and reported sample intervals. Consequently, even a clean `_v4` attribution-dominance result remains conditional on the paper’s largest unvalidated premise.

   **Fixability:** Needs measurement for a direct validity claim. At the desk, the authors can only narrow every conclusion and title to “conditional on pulse-to-inference transfer.”

2. **The corner construction appears to ignore physically shared timing-error dependence, which can make attribution dominance an artifact of the envelope model.**

   **Where:** `## 4. The resolution bound and how it is composed` — “Enumerate all \(2^n\) joint *corners*”; `### Most probative diagnostic-era observations` — “every member in the session contains the same shared fiducial term plus a member-local term.”

   **What:** Every member interval may independently take its lower or upper endpoint even though the dominant fiducial term is shared within a session and possibly within an A/B/B/A block.

   **Why it matters:** Independent sign choices can construct combinations that the physical clock or sampler cannot produce. Such enumeration is conservative for a gate, but it does not necessarily support the stronger interpretation that boundary attribution physically “dominates” repeatability or that the resulting number is “the largest false difference this measurement system can manufacture.” It may instead be the largest difference allowed by an intentionally dependence-free relaxation. Since the headline result compares this corner maximum with the point-only guard, the dependence choice can determine the headline outcome.

   **Fixability:** Primarily desk work if the issued artifacts retain shared and member-local terms: report unconstrained, session-shared, and block-shared variants and make the claim conditional on the chosen dependence model. Establishing which model is physically correct needs measurement.

3. **The word “bound” carries stronger coverage semantics than the estimator presently justifies.**

   **Where:** `#### A.3.5 The pulse-fit (accepted-region) algorithm` — “\(\Lambda = Loss^* + \max(1.0, 0.05 \cdot Loss^*)\)”; `#### A.3.6 The calibration bound B_fiducial and validity` — “it is a ‘95/95’ bound”; `### A reproducible construction` — “\(g(n)=\max\!\left(1,\sqrt{9/(n-1)}\right)\).”

   **What:** The accepted-region tolerance, small-sample multiplier, and 95/95 interpretation are operationally fixed but not scientifically calibrated in the paper.

   **Why it matters:** The loss tolerance is not a confidence region; \(g(n)\) has no stated derivation; and the sample-maximum tolerance argument requires the 59 pulse excursions to be suitably independent and identically representative. The varied schedule and common trace make that assumption nontrivial. These choices may be defensibly conservative, but reproducibility of an algorithm is not the same as coverage of the true edge or a validated resolution limit.

   **Fixability:** Desk-fixable by stating the exact conditional semantics, supplying sensitivity analyses, and removing unsupported coverage language. Empirical calibration of coverage or dependence needs measurement. The discussion should also position this hybrid bounded/statistical construction against JCGM 100:2008, *Evaluation of measurement data—Guide to the expression of uncertainty in measurement* [VERIFY], and JCGM 101:2008, *Supplement 1 to the GUM—Propagation of distributions using a Monte Carlo method* [VERIFY].

4. **Several result fields lack frozen producing semantics, which is more serious than values merely being pending.**

   **Where:** `### Why 256 prompt tokens were selected` — “That bound’s supplier is not yet built”; Table 2 caption — “the results-fill registry records these suppliers as unknown.”

   **What:** The reported-mean member basis, composed mean intervals, per-token denominators, claim-side bound, and some verdict-rendering bindings remain undefined.

   **Why it matters:** A prospective result cannot be filled defensibly if the producing statistic and admitted population are chosen after results are visible. The permitted `docs/paper/results-fill-registry.md` confirms that the D-123 mean fields are `STOP_FILL / SUPPLIER_UNKNOWN`, DS-29 has no claim-side-bound supplier, and several Table 3 outcomes lack exact bindings. No numerical `_v4` outcome can repair an undefined estimand retrospectively. The artifact guide also states that the current gamma manifest is inadmissible until its two-member family is reissued.

   **Fixability:** Desk work, but it must be completed and frozen before collection or under a demonstrably results-blind reissue. Otherwise the affected columns should be removed.

5. **The contrast’s inferential unit and dependence treatment are under-specified.**

   **Where:** `### Demonstration fixed before collection` — “Each contrast will use ten independent A/B/B/A blocks”; “Each raw two-sided Student-*t* p-value will use the contrast estimate divided by its total standard error and its issued degrees of freedom.”

   **What:** The paper calls blocks independent without saying whether they span sessions, how temporal dependence is handled, how `total standard error` is constructed, or how degrees of freedom are obtained.

   **Why it matters:** Ten blocks from one long window can share calibration error, thermal trajectory, background conditions, and serially correlated sampler behavior. A deterministic drift allowance can widen an interval but does not automatically make Student-*t* sampling units independent. The two-gate decision is reproducible only if the estimator, covariance assumptions, degrees of freedom, missing-block behavior, and multiplicity inputs are fully specified.

   **Fixability:** Desk-fixable if the frozen design already establishes independence or a valid covariance estimator. Otherwise the campaign needs independent-session replication or a redesigned inferential analysis.

6. **The three-record resolvability rule is operationally clear but scientifically unvalidated.**

   **Where:** `### Printed negative result: short prompt processing is not resolvable` — “A phase is resolvable only when at least three records count.”

   **What:** Positive overlap by three records is treated as sufficient even when boundary records may be only partially inside the phase, while two overlaps are categorically insufficient.

   **Why it matters:** A count threshold does not by itself show acceptable phase-energy error. Depending on alignment, three overlaps could contain little more interior information than two. The named negative result also retains two non-`_v4` diagnostic `[PENDING]` quantities—the record width and spacing—whose suppliers are not yet declared. This is a design/result gap, not simply a prospective campaign placeholder.

   **Fixability:** Desk work can supply an identifiability or worst-case-overlap derivation and remove the unresolved diagnostic prose. Validating the threshold against known-duration or inserted-gap phases needs measurement.

7. **There is no independent gain check for the energy axis.**

   **Where:** `### Further limitations` — “The counter has no independent gain check against wall power.”

   **What:** The paper calibrates temporal attribution but does not validate whether `powermetrics` energy magnitude is linear and stable across the compared load regimes.

   **Why it matters:** A wall meter cannot partition prefill from decode, as the authors correctly note, but synchronized request-total checks can still reveal load-dependent gain error. Without them, the paper supports a counter-internal phase-attribution result more strongly than it supports energy differences in physical joules.

   **Fixability:** Needs measurement. Alternatively, consistently frame all findings as properties of the named `powermetrics` processor counter, not validated physical energy.

8. **Independent reproduction is not yet available, and the open floor-binding limitation affects the central gate.**

   **Where:** `## 9. Evidence and code availability` — “cannot independently recreate the claim-authorizing extraction-to-analysis link”; `## Appendix A. Reproducing this work` — “not presently open to independent re-reduction.”

   **What:** The paper supplies a detailed future reproduction route, but the archive locators are absent and FLOOR-BIND-01 prevents a third party from independently binding the floor to the complete governed extraction evidence.

   **Why it matters:** The cell floor is the central scientific object and claim gate. An artifact that cannot independently reconstruct its authorization chain falls short of the paper’s otherwise strong reproducibility standard.

   **Fixability:** Desk/engineering work: release the archive and manifest, close FLOOR-BIND-01, and execute the published replay on a clean checkout before publication.

9. **The bibliography still contains a claim mismatch and unresolved verification issues.**

   **Where:** `### LLM energy measurement` — “Broader efforts such as ML.ENERGY, Intelligence per Watt, and Apple-focused inference characterizations map energy across useful deployed configurations.”

   **What:** Reference [13] is attached to an energy-mapping claim even though the permitted `docs/paper/bibliography-audit-2026-08-27.md` reports that it characterizes performance without energy. The same audit marks [19] and [23] unverified and identifies ten uncited entries still present because renumbering was deferred.

   **Why it matters:** This does not threaten the method, but a metrology paper should apply the same traceability standard to related-work claims that it applies to evidence.

   **Fixability:** Desk work: correct [13], verify [19] and [23], remove or cite orphan entries, and renumber consistently.

## 4. Specific requested changes

1. **`## 7. Discussion and limitations` — “Nothing in the frozen `_v4` campaign tests that transfer.”** Add the inserted-gap fiducial to the evaluation before making an unconditional attribution-dominance claim. If it cannot be added, qualify the abstract, title, result labels, and conclusion explicitly as conditional on pulse-to-inference transfer.

2. **`## 4. The resolution bound and how it is composed` — “Enumerate all \(2^n\) joint *corners*.”** Define the dependence model for every uncertainty term. Report at least the current unconstrained-corner result and a physically shared session/block-error result, including whether the attribution-dominance predicate changes.

3. **`#### A.3.6 The calibration bound B_fiducial and validity` — “it is a ‘95/95’ bound.”** State and defend the independence/exchangeability assumptions required for this tolerance claim, or remove “95/95” and describe the value only as the maximum over the observed protocol pulses.

4. **`#### A.3.5 The pulse-fit (accepted-region) algorithm` — “\(\Lambda = Loss^* + \max(1.0, 0.05 \cdot Loss^*)\).”** Justify or empirically calibrate this tolerance and provide sensitivity to the Huber threshold, loss tolerance, region resolution, and \(g(n)\). Add the relevant standard uncertainty references, marked [VERIFY] until checked.

5. **`### Why 256 prompt tokens were selected` — “That bound’s supplier is not yet built.”** Freeze the exact \(F\), \(B\), any required margin, and the reported-mean/per-token schemas before measurement. If those quantities cannot be defined prospectively, remove the sizing-sum and per-token columns rather than filling them post hoc.

6. **`### Demonstration fixed before collection` — “ten independent A/B/B/A blocks.”** Define the physical independent unit, session allocation, block scheduling, midpoint-balance diagnostics, covariance assumptions, total-standard-error formula, and degrees-of-freedom calculation. Explain how serial correlation and shared calibration uncertainty enter the inference.

7. **`### Printed negative result: short prompt processing is not resolvable` — “at least three records count.”** Supply a derivation or validation for the threshold of three, fill or remove the unresolved diagnostic width/spacing values, and state precisely what three overlaps guarantee about phase-energy error.

8. **`### Further limitations` — “The counter has no independent gain check against wall power.”** Add synchronized whole-request wall-meter comparisons across representative load levels if feasible; otherwise change joule-level language throughout to emphasize that the values are unvalidated `powermetrics` processor-counter quantities.

9. **`## 9. Evidence and code availability` — “cannot independently recreate the claim-authorizing extraction-to-analysis link.”** Close FLOOR-BIND-01, release the exact archive/manifests, and include a clean-room replay receipt covering calibration, floors, Holm family, gates, and refusals.

10. **`### LLM energy measurement` — “Apple-focused inference characterizations map energy.”** Correct the [13] cite-to-claim mismatch, verify [19] and [23], and resolve the uncited-reference list reported in `docs/paper/bibliography-audit-2026-08-27.md`.

## 5. Questions for the authors

1. What specific software and hardware path is common to a commanded GPU pulse edge and a runtime prefill/decode boundary, and which plausible load-dependent delays are excluded by construction?

2. When several runs share one bracketing fiducial bound, which timing-error variables are common, which are member-local, and why may their energy intervals independently select opposite corners?

3. Does the attribution-dominance predicate mean “the conservative envelope is attribution-dominated” or “the physical measurement error is attribution-dominated”? What evidence supports the latter wording?

4. What independence or exchangeability argument supports treating 59 pulse excursions as draws for the 95/95 statement?

5. How were the loss-limit tolerance and \(g(n)\) selected? Were alternative values examined before diagnostic results were available?

6. What is one “independent” A/B/B/A block physically: a block, a window, a calibration bracket, or a night? How are correlations among blocks represented in the Student-*t* analysis?

7. Will the D-123 reported-mean schema, claim-side-bound supplier, gamma two-contrast manifest, and Table 3 verdict bindings be frozen before `_v4` begins?

8. What scientific property does the threshold of three overlapping records guarantee that two do not?

9. If `_v4` rejects attribution dominance in both phases, which parts of Table 2 and Table 3 remain publishable findings, and which title will be used?

10. Will the public artifact permit a third party to rederive the floor from raw bundles without a lead-controlled custody session?

## 6. Score, 1–5 (1 reject, 2 weak reject, 3 borderline, 4 accept, 5 strong accept) with a justification paragraph; also state the score you would give if `_v4` reproduces dominance and the score if it does not.

**Overall score: 3/5 — borderline.**

I do not penalize the deliberate `[PENDING]` result values. The paper identifies a real and underappreciated metrology problem, offers an unusually transparent calibration and refusal architecture, and precommits to a meaningful null. My score is held at borderline because the headline result depends on an untested pulse-to-inference transfer, the dominance predicate may be driven by an unconstrained dependence relaxation, several coverage claims are insufficiently justified, and some reported estimands still lack frozen suppliers. These are not cosmetic issues that favorable numbers can cure.

**If `_v4` reproduces attribution dominance: 3/5 — borderline.** The empirical story becomes stronger, but the transfer, dependence, and coverage issues still prevent an accept score. A successful inserted-gap validation plus desk closure of the supplier and inference contracts would move me toward 4.

**If `_v4` does not reproduce attribution dominance: 2/5 — weak reject.** The corrected clock model, prospective null, and refusal machinery remain valuable, but the submission’s principal empirical contribution becomes substantially narrower while the same validity and reproducibility gaps remain.

## 7. “What would make this paper IMPRESSIVE rather than merely sound”

### (a) Single most valuable addition achievable with DESK WORK only

Add one auditable **uncertainty-and-dependence ledger**, accompanied by a sensitivity table. For every term—clock-anchor feasible-set width, pulse-fit region, shared fiducial maximum, bracket drift, member-local edge term, repeatability guard, and whole-window joule allowance—the ledger should state its unit, whether it is deterministic or statistical, its claimed coverage, whether it is shared by session/block/member, the equation and gate it enters, and whether it has been validated under pulses or inference. Then report whether attribution dominance survives plausible shared-error models and reasonable settings of the operational tolerances.

This would do more than another page of prose: it would show whether the headline finding is physical, conditional, or an artifact of a conservative relaxation, while making the paper legible to readers who will not reconstruct the answer from artifact field names and Appendix A.

### (b) Single most valuable addition achievable with ONE MORE MEASUREMENT WEEK

Ranked by value per measurement night:

1. **Inserted-gap fiducial — top pick.** Command the approximately 500 ms gap between prefill end and decode start on roughly ten real-workload runs, fit both edges with the existing estimator, and compare residuals with the pulse-derived bound. This directly tests the paper’s primary validity threat using the actual runtime, mixed workload, telemetry path, and boundary events. Report every run, not only aggregate passage.

2. **Registered micro-delta challenge across independent sessions.** Exercise differences around 0.5, 1.0, 1.5, and 3.0 times an independently issued floor in both directions, with nights or calibration brackets as explicit independent units. This tests whether the operational floor and refusal boundary behave as claimed and supplies evidence about cross-session dependence.

3. **Synchronized external-meter request-total validation.** Cover several representative load levels and both models. It cannot partition phases, but it can test load-dependent `powermetrics` gain and establish whether reported joules track physical request energy.

4. **`_v5` model ladder.** Add more model sizes under the same protocol. This would improve generality and reveal whether the method yields coherent scaling behavior, but it should come after the transfer and floor-validity tests: more models amplify the reach of the instrument without first strengthening its validity.

The single top measurement-week choice is therefore the **inserted-gap fiducial**.

BRIDGE_REPORT_V1
{"status":"DONE","summary":"Completed the blind seven-section program-committee review of the frozen paper draft, including conditional scores and ranked desk/measurement additions.","pathspec":[],"verification":["Read docs/paper/draft-v1.md through its final heading, '### A.6 Release locators'.","Confirmed all seven required review section headings are present and in the specified order.","Consulted only the permitted bibliography audit, results-fill registry, artifact guide, and bridge protocol; did not read docs/process_traces/**.","Performed no writes or edits."],"flags":["no_edits"]}
