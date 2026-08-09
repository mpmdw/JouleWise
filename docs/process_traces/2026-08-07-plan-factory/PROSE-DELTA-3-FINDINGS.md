# Verdict: FAIL

**SAME-SIGNATURE QUESTION: YES.** Round 3 installs most prescribed mechanisms, but the class “unconditional assertions inside insufficiently discriminated conditional prose” survives outside those mechanisms. The shipped linter also accepts substantive violations of the binding contract.

## CONSULT-2 conformance

| Section | Result | Audit |
|---|---|---|
| §1 §7 selection | PASS | Seven predicates and definitions are present; visible guards render from parsed ASTs; D has four canonical cells, raising the total to 20; `CELL_NONPUBLICATION_SUMMARY` and the no-contrast/no-sizing ending are present. |
| §2 measurement licensing | **FAIL** | All 16 required renderers have exact present/absent and companion/no-companion forms; C1/C2 have the exact conditional tokenizer form in the right order. However, assertion-bearing measurement prose remains immediately outside the renderers—see Blocker 1. |
| §3 §6 B rows | PASS | Six `ROW_RENDER`s; all listed numeric tokens are inside their diagnostic-present branches; the drift-passed sentence is separately guarded by `outcome_drift_supported`. |
| §4 §6 C diagnostics | PASS | Fixed-order present-only renderer, partial-absence wording, and all-five-absent form are present. |
| §5 Variant 0 | PASS | Exact neutral heading `(DEFAULT)` and original predicate/lead-in behavior retained. |
| §6 E/X/A selector | **FAIL semantically** | The closed sets and ten steps are copied verbatim, but the algorithm is not total: step 3 can select N before step 4 detects a second, generically absent component. The exact-floor path also never explicitly assigns `E=true`. |
| §7 N renderer | PASS | Fixed four-value order, diagnostic-only sentences, and exact zero-diagnostic form are present. |
| §8 linter | **FAIL** | Most families exist and all ten named tests discriminate real mutations, but three contract-breaking mutations still pass the linter. |

## Blocking findings

### BLOCKER 1 — `MEASUREMENT_RENDER` boundaries still leak measurement existence

After a renderer is allowed to select its ABSENT branch, the template unconditionally emits:

> “Prompt processing remains floors-only, so these prefill values support no model-size direction claim.”

This occurs in A, B1, and B2 at [template:690](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:690), [template:1130](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:1130), and [template:1572](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:1572). C1/C2 use singular “this prefill value” at [template:2116](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:2116) and [template:2349](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:2349).

Those predicates license prompt-cell T/N and measurement-ABSENT states. The output can therefore say “No gross prompt-processing energy estimate is reported” and then refer to “this/these prefill value(s).” B1 additionally asserts that “the … intervals above are individual-arm intervals” even when one or more renderers emitted no interval.

This is the same-signature class and directly defeats CONSULT-2 §2’s stated purpose of protecting prompt-cell T/N outcomes.

### BLOCKER 2 — tokenizer identity remains an unguarded outcome

The fill key itself says:

> “both arms record the SAME tokenizer identity”

at [template:257](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:257), with no source atom or guard.

The same factual assertion remains outside companion renderers in A/B1/B2 and outside §6 row/diagnostic renderers. Most seriously, §6 C—selected solely by a refused whole-window verdict—states:

> “Both arms in each attempted per-token paired comparison record the SAME tokenizer identity…”

at [template:2588](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:2588).

None of the nearest predicates contains a tokenizer-identity atom. C1/C2 were correctly repaired to “When both arms record…,” but the same unsupported factual form survives elsewhere and in the fill key.

### BLOCKER 3 — the E/X/A selector can bypass `STOP_FILL`

The fill key says generic absence or nullness does not automatically enter N, but step 3 says:

> “If at least one [normalized exact-unavailable state] exists and terminal is empty => E=true, X=false; select N.”

Only afterward does step 4 reject an unclassified absent component ([template:127](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md:127)).

Counterstate:

- absolute component legitimately normalizes to exact-unavailable;
- comparative component is generically absent/null without the permitted normalized reason;
- terminal set is empty.

Step 3 selects N because “at least one” normalized state exists; step 4 is bypassed. N then describes the cell as otherwise eligible despite the unlicensed second absence. This leaves round-2 blocker 6 only partially closed.

A lesser fillability ambiguity remains: steps 2–3 assign `E`, but the exact-floor L/U path sets `X` and `A` without explicitly assigning `E=true`.

### BLOCKER 4 — the semantic linter accepts contract violations

The linter genuinely parses template predicates through its recursive-descent parser. The A→B1 mutation produced actual parsed-table errors:

- valid state 6: gap `[]`
- valid state 7: overlap `['7_A', '7_B1']`

However, three additional in-memory mutations all **passed**:

1. Removed the entire visible §6 B selection guard.
2. Appended `Unlicensed claim floor [F_claim_decode_armwise_max_J] J.` outside every §7 section.
3. Removed `contrast_signed_present` from A and regenerated its visible guard from the mutated AST, allowing A when the signed source is missing.

Causes:

- No retained “§6 guard immediately after each heading” check exists after the parsed §6 table at [linter:620](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py:620).
- Claim-token licensing scans only the bodies of the seven recognized §7 sections, not all claim-token occurrences, at [linter:763](/private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/prosefix/docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py:763).
- The §7 truth table enumerates only nine curated outcomes. It does not assert zero selected variants for missing-source/contradictory states, so weakening a required presence atom can pass.

## Assertion/guard census

Every assertion-bearing family was traced; repeated canonical instances are grouped below.

| Assertion family | Multiplicity / nearest guard | Result |
|---|---|---|
| T terminal nonpublication/refusal/diagnostic-only sentences | 20 cell blocks × T guard | Licensed |
| N no-exact-floor and diagnostic-only sentences | 20 × N guard plus N diagnostic renderer | Licensed, subject to selector Blocker 3 |
| L components/max/not-summed/labelled publication | 20 × L guard | Licensed |
| U components/max/not-summed/unlabelled publication | 20 × U guard | Licensed |
| Gross measurement present/absent | 16 matching `MEASUREMENT_RENDER`s | Licensed |
| Per-token companion/no-companion | 16 companion guards | Licensed |
| A/B1/B2 window, contrast, gate, claim-bound, sizing and direction sentences | Corresponding parsed §7 predicates | Licensed |
| A/B1/B2 prompt-value and B1 “intervals above” references | Outside renderers; §7 predicates do not imply prompt measurement presence | **Unlicensed** |
| A/B1/B2 same-tokenizer factual assertions | Outside companion guards; no predicate atom | **Unlicensed** |
| D nonpublication summary and no-contrast/no-sizing ending | D predicate plus selected T/N summary | Licensed; no later contradiction found |
| C1/C2 refused-window and termination prose | C1/C2 predicates | Licensed |
| C1/C2 conditional tokenizer licence | Exact conditional sentence; scope sentence precedes it | Licensed |
| C1/C2 “this prefill value” | Outside measurement renderer | **Unlicensed** |
| C3 no-floor/no-contrast/no-ranking termination | C3 predicate | Licensed |
| §6 Variant 0 | 0 predicate | Licensed |
| §6 A characterization vector | all-six-supported predicate | Licensed if `SUPPORTED` entails the authenticated diagnostics; that implication should be made explicit |
| §6 B row outcomes | Row fill plus B predicate | Licensed |
| §6 B numeric clauses | Corresponding `diagnostic_*_present` branch | Licensed |
| §6 B drift-passed sentence | `outcome_drift_supported` | Licensed |
| §6 C refusal/diagnostics/absence sentences | C predicate plus present-only renderer | Licensed |
| §6 A/B/C same-tokenizer factual assertions | Only section predicates | **Unlicensed** |
| Fill-key derivation and diagnostic-render rules | Mechanical source/selector conditions | Licensed |
| Fill-key affirmative tokenizer identity | No guard or source input | **Unlicensed** |

## Round-2 six-blocker closure

| Round-2 blocker | Closed? | Round-3 mechanism |
|---|---:|---|
| A/B1/B2 claim-floor prose reachable with decode T/N | YES | Both decode-publication atoms plus `claim_floor_defined`; D owns the complementary T/N state. |
| §6 B numeric vector under an any-row-mixed guard | YES | Six independent `ROW_RENDER`s with per-row diagnostic-present branches. |
| §6 C five diagnostics despite missing stages | YES | Ordered `PRESENT_DIAGNOSTICS_RENDER`, absent-row list, and all-absent form. |
| C1/C2 assert tokenizer identity about refused arm | YES | Exact conditional tokenizer sentence, preceded by the required prompt/BOS scope sentence. |
| Variant 0 “unfunded” heading exceeds predicate | YES | Neutral “not yet result-bearing” heading. |
| Nondeterministic E/X/A selection | **NO** | Closed code sets and `STOP_FILL` greatly narrow it, but the step-3 mixed-absence bypass remains. |

## Prior-design-unchanged

| Item | Result |
|---|---|
| Canonical T/N/L/U order, guards, prose | PASS; all 20 normalize to the canonical hash |
| Max rule and seven derivations | PASS |
| L labelled and U exact-unlabelled publication | PASS |
| T terminal and N exact-unavailable meanings | PASS textually |
| C1/C2 model split and C3 termination | PASS |
| §6 0/A/B/C meanings | PASS |
| B1 magnitude-only plus four arm intervals | PASS |
| Exact two-half sizing denial | PASS; exactly A/B1/B2 |
| Runtime denominator and prompt/BOS scope | PASS textually |
| Same-tokenizer licence/prohibition | Preserved, but mechanically unguarded outside C1/C2 |
| ≥3-session rule, D-119 wording, 105+9 addendum | PASS; addendum remains unchanged |

## Revised must-not-change

All nine textual requirements remain intact: `(DEFAULT)`; exact non-summed-threshold sentence; B1 magnitude-only; no point diagnostic published as a floor; no synthesized floor from missing evidence; gross-request primacy/different-tokenizer prohibition; C3 termination; untouched 105+9 addendum; and no detected change to governing measurement semantics. The tokenizer rule’s preservation does not cure Blocker 2’s missing guard.

## Ten discrimination mutations

All ten tests are substantive and were refused: U→absolute publication; T positive publication; U labelled publication; moved ≥3 rule; lowercase enum; concrete derived source; A/B1 predicate overlap with both textual copies updated; claim paragraph moved into C3; C measurement token outside its renderer; and B absent-diagnostic leakage. The test file ran 11 tests including the real-template positive case, all green. The parsed-overlap test is genuine, not a string-inequality test.

## Fillability

The common all-present path is practically fillable, and D, row rendering, diagnostic omission, and N’s zero-diagnostic case are clear. It is **not fillable for every state the template itself admits**:

- absent prompt measurements leave unavoidable “this/these prefill value(s)” prose;
- tokenizer identity lacks a selector input or conditional rendering outside C1/C2;
- the mixed normalized/generic absence cell state has contradictory N-versus-`STOP_FILL` instructions;
- exact-floor L/U selection leaves `E=true` implicit rather than assigned.

Checks performed: `git status --short --branch`; template linter PASS (20 blocks, seven parsed predicates, 768+9 enumerated states); focused tests `Ran 11 tests — OK`; `git diff --check` clean; three read-only in-memory adversarial mutations unexpectedly PASS. No files were edited.