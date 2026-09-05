```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Qualify Q3, correct Q4 rationale, restore early readiness cutoff.","workspace":{"base_requested":"f1430906","base_mode":"exact","head_start":"f14309066f762f7f70569af3d9732544b39c81d8","head_end":"f14309066f762f7f70569af3d9732544b39c81d8","upstream_end":null,"branch":"feat/2026-09-04-astra-peer"},"pathspec":["docs/process_traces/2026-09-04-peer-audit/16-astra-final-position.md"],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"should_fix","title":"Qualify Q3's max formula."},{"id":"F2","severity":"should_fix","title":"Comparative understatement is unproved."},{"id":"F3","severity":"should_fix","title":"Restore the early readiness cutoff."}]},"verification":[{"id":"V1","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nfrom joulewise.analysis_engine.claims import evaluate_claim as C\nfor x,h,want in [(6,.1,'direction_supported'),(10,7,'not_resolvable')]:\n r=C(estimate=x,metrology_aware_ci95={'lower':x-h,'upper':x+h},decision_interval={'lower':x-h-4,'upper':x+h+4},floor_gate_j=5,adjusted_rejected=True,hypothesized_direction='positive')\n assert r['outcome']==want\n print('estimate=%g F+B=9 max(F,h+B)=%g %s'%(x,max(5,h+4),r['outcome']))\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["estimate=6 F+B=9 max(F,h+B)=5 direction_supported","estimate=10 F+B=9 max(F,h+B)=11 not_resolvable"]},"expected":{"exit_code":0,"tail_regex":"max\\(F,h\\+B\\)=11 not_resolvable"}},{"id":"V2","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nimport json\nr=json.load(open('docs/paper/round7/excursion-decomposition.json'))['per_pulse']\na=sum(x['onset_best_fit_lag_ms']>0 for x in r);b=sum(x['offset_best_fit_lag_ms']<0 for x in r)\nassert len(r)==59 and (a,b)==(59,49)\nprint('DERIVED JSON pulses=59 late_onsets=59 early_offsets=49; no raw replay')\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DERIVED JSON pulses=59 late_onsets=59 early_offsets=49; no raw replay"]},"expected":{"exit_code":0,"tail_regex":"early_offsets=49; no raw replay"}}],"flags":[{"id":"R1","kind":"lead_ruling","level":"nonblocking","text":"Advice only; no ruling installed.","needs":"Correct 17; cold-gate exact addenda."}]}
```

## Findings

Clean exact head; 14/15 read fully; `14:n`/`15:n` cite them.

- **F1 — should_fix:** 15:25 omits symmetry: max(F,h+B) assumes metrology interval estimate±h and symmetric widening B. Actual endpoints/eligibility govern (`joulewise/analysis_engine/claims.py:363`, `:381`); V1 refutes F+B necessity and sufficiency.
- **F2 — should_fix:** 15:10's comparative understatement is unproved: additive same-prompt means cancel in null ABBA; noise/edge-response dependence remains unknown. Reproduced 14's R_abs=3.000000/1.073827 proves no comparative bias direction (`joulewise/detection_floor.py:925`, `:952`).
- **F3 — should_fix:** 15:41–42's content-freeze readiness deadline conflicts with 14:64's 24–48-hour cut: require readiness **6 September**, select content 9 September.

### Q1–Q7

| Question | Final position / agreed text |
|---|---|
| Q1 | **SETTLED:** Relabel the conditional estimand; pinned desk enclosure → appendix/DERIVE row, authenticated inputs, supported nonnegative domains, each record once. |
| Q2 | **SETTLED:** Relabel shared energy-sign sensitivity under .v2; preserve arithmetic/thresholds/v1 history, withdraw physical-common-time robustness, stop this submission's rebuild. |
| Q3 | **STILL DISAGREE:** Qualify the invariant (F1; `joulewise/analysis_engine/claims.py:363`; V1); keep both roles, gating:false and version-aware migration. |
| Q4 | **SETTLED:** Prompt-0 contrast; floor packs/G2-a prefill unchanged; prospectively supersede affected contrast artifacts, disclaim prompt generality; correct F2. |
| Q5 | **SETTLED:** TR-01 → LIMITATION; “Transfer of the pulse-derived timing allowance to inference was not tested”; update selectors, stop late transfer. |
| Q6 | **SETTLED:** Use 15:37's exact non-admission sentence only from verified failed production evidence bound to model/window/basis/membership/governing row; amend OR-01/DS-32/PG-08, map affected arms, preserve unaffected verdicts, require 15:39–41's CLI cases. |
| Q7 | **SETTLED:** Every active producer/profile omits legacy results or emits VOIDED with no joule observations, result table, “primary” or “manual review”; status alone is insufficient. |

### Final moves

1. **SETTLED:** Complete methods/diagnostic base now; acquisition cut 8 September night, freeze 9 September; advance for earlier authoritative dates.
2. **STILL DISAGREE on timing (F3):** By 6 September prove CLI outcomes, fixture labels/source maps or select fallback; retain clearance, cut unbuilt means/sizing. **Accept edit 1:** #285's stated fixture dependency justifies existing scope, subject to final-head gates (`docs/orchestration.md:77`), not “nearly done.”
3. **SETTLED:** By 6 September prove unattended budget: watchdog rehearsal/stand-down → G2-a → desk pin/packs/clone proof → G2-b/transaction/nightly G3 → both floors AND gamma → extraction/mint/close-out; otherwise fallback.
4. **SETTLED:** Days 1–3 finish paper-K, enclosure, empirical figures, References/Availability and statistical qualifications; stop optional expansion.
5. **SETTLED:** Freeze completed evidence; retain attempts/refusals; replay published floors' census/primary widths, including absolute operands; no historical/fixture substitution.
6. **SETTLED:** Final 48 hours: final-head proof, package rebuild, PDF/HTML/source-map inspection, reproduction limits. **Accept edit 2:** LINEAGE affirmation recorded, unmerged.

### Answers A and B

**A:** “In a current-method re-analysis of one historical GPU pulse capture, all 59 fitted onsets occur after their commands and 49 of 59 fitted offsets occur before them; transfer of its timing allowance to inference remains untested.”

**Figure:** `docs/paper/figures/fig4_edge_excursions.svg`, promoted to main Figure 2. V2 checks the retained derived signs. Caption: historical current-method re-derivation, one capture, dependent edges; distinguish fitted lags, allowed-region excursions and anchor allowance. P1 is a separate appendix illustration; neither establishes phase-energy dominance or future-error coverage.

**B:** **Yes, conditionally; churn is not disqualifying.** Also prove era-aware parsing/strict comparison, preserved old-output/refusal contracts, independent enclosure checks, and a prospective identity/pin transition meeting readiness without collection delay. No blanket ignore-key exceptions (`docs/contracts/run_bundle_layout.md:759`, `:781`; `joulewise/cli.py:478`). Check P1 and a window wholly inside one record; declare fixed-window scope or union allowed timing windows, never mechanically add widths. No exhibit supplied; desk default stands.

### Decision-log addenda — proposed exact text

#### D-078 — estimand and clause 11

For phase and request metrics formed from interval-average sampler records, the estimand is energy assigned by interval-overlap allocation. The timing envelope describes movement of that allocation over the registered timing domain, conditional on the held-average reconstruction; it does not bound physical energy under arbitrary within-record allocations or establish inference transfer or future-error coverage. Withdraw clause 11's unrestricted largest-false-effect and permanent-dominance assertions. Preserve the labelled widened-floor path and both mandatory roles: the published floor and the claim's separately widened decision interval. F+B is only a non-gating planning diagnostic, never an effective-clearable-effect guarantee; neither role may be removed as double counting. Historical bytes remain unchanged; new disclosures use a versioned rule.

#### D-083

Supersede D-083's endorsement of F+B as the correct joint clearable-effect description; preserve its rejection of an additive acceptance gate. Checks remain separate: |estimate|>F and exclusion of zero by both metrology and decision intervals, plus multiplicity and evidence/eligibility requirements. For a symmetric metrology interval estimate±h and symmetric nonnegative widening B, the numerical conjunction is |estimate|>max(F,h+B); asymmetric intervals use actual endpoints. Both roles remain mandatory. F+B is heuristic planning, neither necessary nor sufficient for acceptance; absent suppliers remain absent. New metadata retains both_terms_required:true, states gating:false, and uses a distinct rule version with version-aware consumers; legacy objects retain exact bytes and historical meaning.

#### D-165

Supersede the physical common-time interpretation and R-5's fiducial-shift cancellation rationale. A uniform additive energy offset cancels from absolute residuals; a common time shift need not. R_cm is a shared-energy-sign/local-corner sensitivity diagnostic, with no proven conservatism for common-time motion. Retain the eight independent and four comparative diagnostic ratios, thresholds, census, arithmetic and branch restrictions: any required R_cm<2 still withdraws the dominance sentence; passage licenses no physical-common-time robustness claim. Absolute R_cm remains not_applicable because the registered replay is comparative-only, not because absolute timing uncertainty vanishes. Relabel under d165_shared_sign_local_corner_replay.v2; preserve v1 meanings/bytes. Rebuild is stopped for this submission; later changes require prospective registration.

#### D-166

Prospectively amend the v5 decode demonstration to use prompt 0 of real_prompts_v1 for every block in both model arms, matching the floor packs' fixed-prompt repeats and null blocks. Floor packs remain unchanged; thinking off, greedy forced-512 decoding, tokenizer/token-ID pins and shape checks remain required. G2-a prefill selection and its pin are unchanged. Regenerate affected contrast configs, identities, projections and custody pins with explicit supersession before collection and rerun the required clone proof. The comparison supports this fixed prompt and makes no prompt-population generality claim. An ensemble alternative requires explicit prospective authorization and matching registrations before its data are collected.

#### Scope-freeze rule

Until submission, tasks must be necessary for a selected figure, table or refusal sentence, name it, and have bounded acceptance and a stop time; optional slots create no dependency. Keep the five-ref seam, renderer, paper corrections, enclosure and acquisition dependencies. Park receipts, AUTH, new kernel work, skill-distill, LINEAGE merges, MODULARITY follow-ups, transfer and common-time replay. Preserve final-head, integration and publication checks. Methods/diagnostics is the base deliverable. Establish desk readiness and feasible acquisition scheduling by 6 September; final useful acquisition is the night of 8 September, content freezes 9 September, reserving 48 hours for verification/reading. Missing evidence selects fallback, never empirical refusal. Authoritative earlier deadlines advance these cuts.

## Residual risk

15's enclosure exhibit, migration hold, seam CLI, refuter census/fix, #285 replay, LINEAGE affirmation and emails remain unverified here. Seam/contract absent; D-173 PROVISIONAL (`docs/decision_log.md:10903`). Current producer still emits “supported”/“primary basis” (`scripts/make_figures.py:581`, `:464`); no in-flight fix or exact legacy-values/lint-row replay. Citation correction: 15:26's equality check is `detection_floor.py:3345`, not :3353.

Synthetic/derived-data checks only; no raw/live validation, discovery suite, agent launcher, measurement checkout, host action, CI or publication build. Due date, fallback acceptability and acquisition feasibility remain lead/user gaps. Only this report changed; next: corrected 17 and cold gate.
