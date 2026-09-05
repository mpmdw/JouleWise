```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"NOT LANDABLE: one inherited blocker, four should-fix findings, one cut; prescribed tests pass.","workspace":{"base_requested":"850ea169","base_mode":"exact","head_start":"850ea16947150dd40fa403233fc4796ff121b1cc","head_end":"850ea16947150dd40fa403233fc4796ff121b1cc","upstream_end":null,"branch":null},"pathspec":["docs/process_traces/2026-09-04-paper-k/06-astra-peer-review.md"],"unowned_dirty":[],"verdict":{"result":"NOT LANDABLE","findings":[{"id":"F1","severity":"blocker"},{"id":"F2","severity":"should_fix"},{"id":"F3","severity":"should_fix"},{"id":"F4","severity":"should_fix"},{"id":"F5","severity":"should_fix"},{"id":"F6","severity":"nit"}]},"verification":[{"id":"V1","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 1.800s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 10 tests in .*s\\n\\nOK"}},{"id":"V2","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 4 tests in 1.378s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 4 tests in .*s\\n\\nOK"}},{"id":"V3","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_select_outcome_branches","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 0.485s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests in .*s\\n\\nOK"}}],"flags":[{"id":"R1","kind":"environment","level":"nonblocking","text":"Ruling 43 is absent locally; read its named path in /Users/edr/code/JouleWise-wt-dl-ratify.","needs":""}]}
```

## Findings

All draft lines refer to `docs/paper/draft-v2-skeleton.md` at 850ea169. Reviewed `git diff 4ea033ec...HEAD -- docs/paper tests`, traces 01-04, ruling 43, and 17 §B.

**F1 — blocker — Refusal conflates unavailable evidence with empirical non-admission.** Line **907**; also 41, 1187, 1422 and registry OR-01 (`docs/paper/results-fill-registry.md:925`). Inherited from J, but incompatible with ratified 43 Q-17-6 and 17 Q6/scope-freeze. Missing evidence selects fallback; independently verified, unaffected verdicts survive.

Old: “Before comparison, Refusal applies when a model-specific measurement window was excluded or an authenticated token-generation or prompt-processing verdict is absent.”

Proposed: “Before comparison, an empirical non-admission statement requires a verified failed production-window record bound to the affected model and window; missing or invalid source evidence selects the methods/diagnostics fallback. Independently authenticated, unaffected model-comparison verdicts remain reportable.”

Propagate this distinction through the three Refusal carriers and governing form/registry. Keep authenticated close-out arithmetic refusals, including zero denominators; missing ratio evidence must not erase a separately authenticated model verdict.

**F2 — should_fix — Abstract numerator and first-use construction.** Lines **29, 35, 41**, common third sentence. Code maximizes a complete residual/prediction bound (`detection_floor.py:861-915`), not the largest energy change. B's “every division” and “second value” have no constructed operands; Refusal also invokes an unexplained division. The allocation multiplication is likewise missing before its compound label.

Old: “JouleWise first used deliberately started graphics-processor work to measure how far the dividing time could be wrong, then recalculated the largest change in interval-overlap-assigned phase energy over the registered timing domain—the set of edge movements fixed before collection.”

Proposed for A/B: “Using a timing allowance from commanded graphics-processor pulses, JouleWise recalculated bounds on repeat scatter or same-condition differences over the registered timing domain—the edge movements fixed before collection—and divided each largest bound by its recorded-time value.” For Refusal use “would recalculate” and “divide”: a before-comparison stop cannot assert completion.

Old, preceding sentence: “Moving that dividing time changes the energy assigned to each part without changing the request total.”

Proposed: “JouleWise assigns energy to each part as average power times overlap duration; moving the dividing time reallocates energy without changing the request total.”

Reconcile the phrase-based regressions and recheck the Abstract word caps.

**F3 — should_fix — permanent dominance survives its withdrawal.** Line **1171**, Discussion A. Both complete bounds depend on observed energies and sample size; passage at one sample size does not prove the twofold relationship persists with additional repeats. Ratified D-078 withdraws permanent-dominance assertions.

Old: “Additional repeats can narrow the point-only value, but they cannot remove the larger contribution from allowed boundary movement under the specified perturbation set; the fixed Qwen3-8B-versus-Qwen3-1.7B pair demonstrates that decision behavior, not a model-size scaling law.”

Proposed: “At the observed sample sizes, the registered perturbation calculations at least doubled every required component's point-only bound; this result does not establish how additional repeats would change those ratios.”

**F4 — should_fix — withdrawn floor definition remains visible.** Line **922**, final sentence; `docs/paper/figures/fig3_decision_gates.svg:89-91`. Inherited but still displayed. A sample maximum/model-based prediction amount is not an unrestricted largest effect. The planning sum is F+B, not a floor plus an interval.

Old: “The three bottom notes define the cell floor as the largest apparent effect produced when nothing changed, after the safeguards of Section 4, state that the floor and interval are separate gates, and state that their sum is a planning disclosure rather than an acceptance threshold.”

Proposed: “The bottom notes define the cell floor as the registered operational resolution guard for assigned-energy differences, retain the separate floor and interval gates, and identify F+B—floor plus deterministic widening—as a non-gating planning diagnostic, neither necessary nor sufficient for acceptance.”

Align the SVG notes with that sentence.

**F5 — should_fix — orphaned alias after the stochastic rewrite.** Lines **851-854**. K removed the construction of “total standard error”; its explicit equality now appears at 1253/1265-1268, despite ledger line 1887 claiming first-use construction.

Old: “The direction check requires two named complete uncertainty intervals: the measurement interval, formed from the total standard error, and the decision interval, formed by extending both ends of that measurement interval by the sum of the recorded deterministic bounds.”

Proposed: “The direction check requires the measurement interval, formed from the repeat standard error already defined for this gross phase-energy path, and the decision interval, formed by extending both ends by the sum of the recorded deterministic bounds.”

The green test checks defining phrases anywhere in the first-use paragraph (`tests/test_paper_first_use_ledger.py:373-376`), not the sentence unit, and its selected phrase list omits this alias. F2/F5 fail the manual first-use read. The new order/sign glosses pass.

**F6 — nit — what I would cut.** Lines **484-486**.

Old: “The same screen is rendered elsewhere as 0.009724 s, as a 9.724-ms reference, and again as 9.724 ms; these are unit or prose renderings of that one screen, not separate sensitivity results.”

Proposed: delete; the preceding sentence already gives 9.724 ms. Also move the identity fingerprints (174-191) and binary64 padding walkthrough (665-687) to Appendix A, retaining definitions and evidence pointers in the body.

**Code check and verdict: NOT LANDABLE.** The five required checks support the main corrections:

- `reduce.py:167-184,515-560`: overlap integration and zero native interpolation term.
- `analysis_engine/inputs.py:3668-3676`: no additional stochastic variance on the gross phase path.
- `aggregate.py:42-46`: fixed t-table values 12.706 and 2.776.
- `analysis_engine/claims.py:336-400`: strict floor comparison, both interval checks, multiplicity, and registered-direction eligibility.
- `dominance_closeout.py:278-337,585-711`: shared scalar energy sign plus independent local signs; maximum complete bound, not global common-time replay.

No affirmative physical common-time robustness or transfer-result claim survived the textual sweep. All nine fixed transfer limitations remain. The main-text F+B disclaimer and strict max(F,h+B) conjunction are correct. F3/F4 are surviving overclaims.

A and B remain distinct alternatives: all twelve ratios pass versus all evaluable with at least one below two; both retain independent model verdicts. Refusal is structurally selectable but scientifically incomplete (F1). In-memory selection yields Abstract word counts A=241, B=240, Refusal=250 and three visible transfer limitations per selected draft. All 17 prescribed tests passed sequentially.

Next: lead adjudicates F1-F5, applies cures, and repeats the modules and sentence read.

## Residual risk

Desk evidence only; no live validation or independent corpus replay. No discovery suite, measurement, generator, model launcher, commit, or out-of-scope edit ran. Proposed sentences are untested. This head still emits replay rule v1 (`dominance_closeout.py:50`), while the registry requests v2; the separately ordered v2 relabel and prompt-0 artifact supersession require lead integration verification before production use.

