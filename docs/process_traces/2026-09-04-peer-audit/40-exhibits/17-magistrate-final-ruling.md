# Magistrate FINAL ruling on the peer audits — 2026-09-04 (for the cold Fable gate)

Lineage: audits 01/02/03 (gpt-6-astra) → bench 04 → questions 05 → seats 10 (Sol physics) / 11 (Opus contract) /
12 (blind Fable) → draft 13 → astra peer plan 14 → reply 15 → astra final 16. Ed's instruction: "have it mirror
your tasks and you two discuss final moves". Two rounds held. Cold gate judges THIS file and the addendum texts
in §B; nothing below is ratified until it rules. Rule 11: claim-bearing relabels + one process rule ⇒ mandatory.

## A. Rulings

Q1 ESTIMAND — RULED. The measurand is energy assigned by interval-overlap allocation of the sampler's
interval-average records; the timing envelope is that allocation's sensitivity over the registered timing domain,
conditional on the held-average reconstruction; it bounds neither physical phase energy under arbitrary
within-record allocations nor inference transfer nor future-error coverage. Enclosure diagnostic: the exhibit
astra asked for now exists (branch feat/2026-09-04-estimand-enclosure, 30-estimand-enclosure-seat-report.md):
additive field on the current 0.5.2/0.6.2 wires, existing_fields_changed=0 on the d078_r01 replay, two goldens
changed additively only, strict validation and floor extraction green (tests.test_cli_run + test_floor_extraction,
298 OK at the bench). Ruling: the REDUCER FIELD is accepted CONDITIONALLY on astra's B conditions as acceptance
tests, else the desk script: (i) an oracle for a window wholly inside one record; (ii) fixed-window scope declared
in the contract, never mechanically added to frozen bounds; (iii) no ignore-key exception anywhere (cli.py:478,
run_bundle_layout.md:759/781 unchanged in kind); (iv) the per-version roster in run_bundle_layout.md names the
field for the current versions only; (v) delta re-audit of the branch. D-078 addendum text in §B.

Q2 D-165 — RULED as 16: relabel under d165_shared_sign_local_corner_replay.v2; absolute-cancellation rationale
superseded; thresholds, census, arithmetic, branch restrictions unchanged; rebuild STOPPED for this submission.

Q3 F+B — RULED as 16 (astra's F1 accepted): keep both roles mandatory (both_terms_required true), gating false,
planning_sizing_formula, invariant stated with symmetry qualified and actual endpoints governing
(claims.py:363, :381); SINGLE_COUNT_DISCIPLINE_ID .v2 with version-aware consumers (the seven exact-equality
sites, first at detection_floor.py:3345; adapter_contracts.md:618-637; 14 rehearsal JSONs regenerated). The
FB-PLANNING-METADATA-01 landing (wt-fb-metadata) is HELD and re-briefed to this shape after the gate.

Q4 PROMPTS — RULED: contrast on prompt 0 in both model arms; floor packs and the G2-a prefill pin untouched;
prospective supersession of affected contrast artifacts; one-sentence generality disclaimer. Correction accepted
from 16-F2: comparative-arm understatement is NOT established (same-prompt means cancel in null ABBA; noise and
edge-response dependence unknown); 15 overstated it. Ed offered the ensemble alternative by email; absent his
answer this stands.

Q5 TRANSFER — RULED: TR-01 → LIMITATION; fixed sentence "Transfer of the pulse-derived timing allowance to
inference was not tested"; selector census unchanged at three; no late-window predicate.

Q6 REFUSAL BRANCH + SCOPE — RULED: sentence "The registered window was not admitted for this submission's
claim-bearing comparison" rendered only from verified failed production evidence bound to model, window, basis,
membership and governing row through the seam's whole_window_verdict ref; OR-01/DS-32/PG-08 amended to
non-admission; affected arms mapped, unaffected verdicts preserved; acceptance = actual CLI renders the failed
production row AND missing, corrupt, diagnostic-only, conflicting and wrong-window inputs render no empirical
refusal. Scope-freeze rule and dispositions per §B; astra's timing (readiness proven by 6 September or fallback
selected) accepted over 15.

Q7 LEGACY L1 — RULED and executed: rounds 1–3 on feat/2026-09-04-legacy-l1 (route census: every full-route
artifact is a void placeholder, claims row status voided under a first-class lint dialect, census regression +
supported-flip kill; v1 trees byte-identical). Delta re-audit running; PR after. D-161 one-line addendum.

Final moves — astra's list adopted with its F3 timing: base deliverable = methods/diagnostic paper; readiness
(CLI outcomes, fixture labels, source maps, unattended chain budget) proven by 6 September or fallback selected;
last useful acquisition night 8 September; content freeze 9 September; 48 h reserved for final-head proof,
package rebuild and reading. Headline sentence and Figure 2 per 16 §A (fig4_edge_excursions.svg promoted).

Wave-2 (#285) replay disposition (docs/process_traces/2026-09-04-fanout/30): node-worker localhost test =
environmental, pre-existing, identical bytes, production budget 900 s (ledger wording in 30); real-boot ARM test =
test defect unblocked by FIXTURE-MODERNIZATION-01 (fixture R0 uses a fictional 2e18 ns offset against a real
author anchor; 5 ms ceiling is a production invariant and stays). Cure seat launched on the wave-2 tree
(test-only); row 9 fills with the re-run tail.

## B. Decision-log addendum texts (astra's 16 §texts, adopted verbatim except where marked [M])
D-078 (estimand + clause 11): For phase and request metrics formed from interval-average sampler records, the
estimand is energy assigned by interval-overlap allocation. The timing envelope describes movement of that
allocation over the registered timing domain, conditional on the held-average reconstruction; it does not bound
physical energy under arbitrary within-record allocations or establish inference transfer or future-error
coverage. Withdraw clause 11's unrestricted largest-false-effect and permanent-dominance assertions. Preserve the
labelled widened-floor path and both mandatory roles: the published floor and the claim's separately widened
decision interval. F+B is only a non-gating planning diagnostic, never an effective-clearable-effect guarantee;
neither role may be removed as double counting. Historical bytes remain unchanged; new disclosures use a
versioned rule. [M] The nonnegative partial-record enclosure is a diagnostic of allocation ambiguity at the
registered window; it is reported, never composed into any bound.
D-083: Supersede D-083's endorsement of F+B as the correct joint clearable-effect description; preserve its
rejection of an additive acceptance gate. Checks remain separate: |estimate|>F and exclusion of zero by both
metrology and decision intervals, plus multiplicity and evidence/eligibility requirements. For a symmetric
metrology interval estimate±h and symmetric nonnegative widening B, the numerical conjunction is
|estimate|>max(F,h+B); asymmetric intervals use actual endpoints. Both roles remain mandatory. F+B is heuristic
planning, neither necessary nor sufficient for acceptance; absent suppliers remain absent. New metadata retains
both_terms_required:true, states gating:false, and uses a distinct rule version with version-aware consumers;
legacy objects retain exact bytes and historical meaning.
D-165: Supersede the physical common-time interpretation and R-5's fiducial-shift cancellation rationale. A
uniform additive energy offset cancels from absolute residuals; a common time shift need not. R_cm is a
shared-energy-sign/local-corner sensitivity diagnostic, with no proven conservatism for common-time motion.
Retain the eight independent and four comparative diagnostic ratios, thresholds, census, arithmetic and branch
restrictions: any required R_cm<2 still withdraws the dominance sentence; passage licenses no
physical-common-time robustness claim. Absolute R_cm remains not_applicable because the registered replay is
comparative-only, not because absolute timing uncertainty vanishes. Relabel under
d165_shared_sign_local_corner_replay.v2; preserve v1 meanings/bytes. Rebuild is stopped for this submission;
later changes require prospective registration.
D-166: Prospectively amend the v5 decode demonstration to use prompt 0 of real_prompts_v1 for every block in
both model arms, matching the floor packs' fixed-prompt repeats and null blocks. Floor packs remain unchanged;
thinking off, greedy forced-512 decoding, tokenizer/token-ID pins and shape checks remain required. G2-a prefill
selection and its pin are unchanged. Regenerate affected contrast configs, identities, projections and custody
pins with explicit supersession before collection and rerun the required clone proof. The comparison supports
this fixed prompt and makes no prompt-population generality claim. An ensemble alternative requires explicit
prospective authorization and matching registrations before its data are collected.
Scope-freeze rule (new decision number, process): Until submission, tasks must be necessary for a selected figure,
table or refusal sentence, name it, and have bounded acceptance and a stop time; optional slots create no
dependency. Keep the five-ref seam, renderer, paper corrections, enclosure and acquisition dependencies. Park
receipts, AUTH, new kernel work, skill-distill, LINEAGE merges, MODULARITY follow-ups, transfer and common-time
replay. Preserve final-head, integration and publication checks. Methods/diagnostics is the base deliverable.
Establish desk readiness and feasible acquisition scheduling by 6 September; final useful acquisition is the night
of 8 September, content freezes 9 September, reserving 48 hours for verification/reading. Missing evidence selects
fallback, never empirical refusal. Authoritative earlier deadlines advance these cuts.
D-161 (one line): the rpt001 capstone profile is a closed publication route for legacy energy values; every
producer under it emits void placeholders; regeneration cannot reopen it.

## C. Dissent recorded
None from the magistrate on 16. Opus (11) preferred mirroring the rotation into the floor packs and keeping the
receipt lanes; overruled on the R_abs arithmetic (14 V1) and on the absence of a non-integrity producer (03 of the
non-issuance design). Sol (10) preferred retiring the rpt001 profile outright; the void-placeholder shape meets
its acceptance (no build can assemble the numbers).
