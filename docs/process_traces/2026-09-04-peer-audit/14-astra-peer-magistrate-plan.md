```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Peer ruling: prompt-0 contrast, desk enclosure, narrower verified Refusal prose, and a complete dated fallback.","workspace":{"base_requested":"cfdb24ac","base_mode":"exact","head_start":"cfdb24acd3a709d95120cafdc81ea9e921f2c267","head_end":"cfdb24acd3a709d95120cafdc81ea9e921f2c267","upstream_end":"cfdb24acd3a709d95120cafdc81ea9e921f2c267","branch":"feat/2026-09-04-astra-peer"},"pathspec":["docs/process_traces/2026-09-04-peer-audit/14-astra-peer-magistrate-plan.md"],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker","title":"Q6 does not yet establish the proposed Refusal rendering."},{"id":"F2","severity":"should_fix","title":"Q4 rotation changes the absolute-floor question; prefer contrast on prompt 0."},{"id":"F3","severity":"should_fix","title":"Amend Q1/Q2/Q3/Q5 details; agree with Q7 retirement shape."},{"id":"F4","severity":"should_fix","title":"The week needs dated fallback cuts, complete acquisition dependencies, and final artifact verification."}]},"verification":[{"id":"V1","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nfrom joulewise.detection_floor import absolute_false_effect_floor as floor\nnoise=[-.1,.1]*5\nfor label,means in [('fixed',[0.]*10),('rotated',[float(i%8) for i in range(10)])]:\n values=[100+m+n for m,n in zip(means,noise)]\n p=floor(values,admissible_half_widths_j=[0.]*10).unguarded_floor_j\n b=floor(values,admissible_half_widths_j=[.2]*10).unguarded_floor_j\n print('%s point=%.6f widened=%.6f R=%.6f' % (label,p,b,b/p))\ndef null(m,n):\n return ((m+n)+(m+n)-(m-n)-(m-n))/2\nassert [null(100,n) for n in noise]==[null(100+i%8,n) for i,n in enumerate(noise)]\nprint('null ABBA unchanged by prompt means: True')\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["fixed point=0.250074 widened=0.750221 R=3.000000","rotated point=6.022568 widened=6.467193 R=1.073827","null ABBA unchanged by prompt means: True"]},"expected":{"exit_code":0,"tail_regex":"null ABBA unchanged by prompt means: True"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_analysis_claims","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}}],"flags":[{"id":"R1","kind":"lead_ruling","level":"nonblocking","text":"Peer advice only; magistrate owns ratification and final verification.","needs":"Resolve Q4/Q6 before implementation."},{"id":"R2","kind":"verification_gap","level":"nonblocking","text":"Seam absent at this head; in-flight branches and live sources unverified.","needs":"Verify landed behavior and submission artifacts."}]}
```


## Findings

Peer magistrate, 2026-09-04, clean exact head cfdb24ac. Read 01/02/03, 04, 05, 10/11/12 and 13 fully; governing intake has no stop card. This assigned [AGENT] review writes only this report. Make a complete conditional methods/diagnostic paper the base deliverable; add prospective results only if the entire chain finishes. Costs below are estimates.

### F1 — blocker — Q6: AMEND; no receipt family, but prove the negative-outcome route

Against 13:58-77: **KEEP** the five-ref seam/renderer; **PARK** both receipt designs, AUTH, kernel expansion, skill-distill, LINEAGE and MODULARITY follow-ups. A named paper object is necessary, not sufficient: optional sentences do not create critical-path work.

**Yes:** a verified `whole_window_verdict` ref can support **“The registered window was not admitted for this submission's claim-bearing comparison.”** Bind its affected model/window. Failed production admission is evidence, not permission to publish its numerical results.

**Not demonstrated here:** the seam and its contract are absent at this head (prospective D-173, `docs/decision_log.md:10914`). Existing admission validation calls nonempty core conditions provenance-invalid (`joulewise/whole_window.py:4172-4174`) and rejects non-passed rows (`:5292-5293,5475`). Distinguish **source-valid failed admission** from **authentication failure** by reproducing the negative disposition for exact policy, production role, basis, membership and governing/superseding row. Ignoring validator errors is insufficient; D-173 forbids printing nested validator codes (`decision_log.md:10922-10927`).

OR-01 requires stage/reason/precedence; DS-32/PG-08 require their verdict or evidence of prevented evaluation (`results-fill-registry.md:885,894,921`, under `docs/paper/`). Failed admission alone proves neither that comparison never ran nor both verdicts' absence. Amend the rows to non-admission, map affected arms through dependencies and preserve unaffected issued verdicts. “Before comparison,” if kept, must name an admission stage, not execution history.

Accept only after the actual CLI renders a source-valid failed production row while missing, corrupt, diagnostic-only, conflicting and wrong-window inputs render no empirical refusal. These are D-161 evidence/mistake checks. If the seam cannot do this promptly, choose the methods fallback.

### F2 — should_fix — Q4: DISAGREE; contrast on prompt 0

Against 13:37-48, retain both floor packs' same-condition repeats/nulls; use their prompt for decode contrast. Prospectively amend D-166 and regenerate affected contrast configs, identities, manifests/projections and custody pins with supersession. Preserve G2-a prefill; never mutate frozen packs in place.

Opus is right about shape: my inspection found eight 42-token renderings; contrast enforces shape and forced-512 output (`configs/campaigns/d117_contrast_v5/generate_configs.py:975-981,1539`), cycling once per block (`:1380-1381,1731-1738`). Floors pin prompt 0 (`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:1030-1034`). Equal shape does not prove equal energy/timing response.

**Understatement is a risk, not an established direction.** Absolute floors center energies on one mean (`joulewise/detection_floor.py:925-928`); rotation includes prompt means. Same-prompt null ABBA cancels that additive mean; comparative floors use those deltas (`:952-964`). Prompt-dependent noise/edge response remain unknown. True model-by-prompt effects are not automatically measurement noise.

V1 holds run noise and all 0.2-J timing widths fixed:

| Synthetic population | Point floor J | Widened J | R_abs |
|---|---:|---:|---:|
| Fixed prompt | 0.250074 | 0.750221 | 3.000000 |
| Rotated prompt means | 6.022568 | 6.467193 | 1.073827 |

Those means leave constructed null ABBA deltas unchanged. This is no Qwen3 forecast. It supports blind Fable: labeling does not preserve the timing-versus-repeatability question when the denominator's population changes.

Prefer the narrower fixed-prompt question this week; disclaim prompt generality. If Ed requires an ensemble question, accept prospective rotation in both arms with that explicit interpretation. Print the 10-over-8 weights even then: matching them does not erase imbalance (contra 11:128-129).

### F3 — should_fix — Other rulings

**Q1 — AMEND: relabel; desk enclosure this week.** Agree with 13:7-17 on the estimand. My P1 rerun: point 9.000 J, interpolation 0.000, timing [8.800,9.200], nonnegative allocations [8,10]. Overlap allocation is already the contract's estimand (`docs/contracts/run_bundle_layout.md:805`).

Opus wins placement: `reduce.py:99-109`, the explicit version/frozen-output roster (`run_bundle_layout.md:759-786`), `joulewise/schemas.py:37-46` and strict comparison (`joulewise/cli.py:468-478,626`) show numeric invariance alone does not settle schema/identity/pin churn. Re-reduction checks consistency, not independent physics; coverage is not free.

Use one pinned appendix script, authenticated records/windows, existing read/rail semantics, input hashes and a DERIVE row. Full/cut/outside records contribute Q/[0,Q]/0; union windows and count each record once. Refuse invalid/negative/unsupported domains. Name counter-record allocation, not wall accuracy. Label fixed-window scope or explicitly union allowed timing windows; never mechanically add this width to frozen bounds. Check P1 and a window inside one record. Cost: half to one desk day. An exact compatibility exhibit could reverse placement.

**Q2 — AMEND: relabel, withdraw physical-common-time robustness, defer.** 13:19-27 works for registered shared-sign sensitivity only: magnitudes receive a shared sign (`joulewise/dominance_closeout.py:687-700`), without time coordinates (`:56-66`). Joule offsets cancel; time shifts need not (`:51-55`). Bench 04:15 and consult 12:40-50 establish disagreement, including a reported reverse-direction case. Do not call it conservative or treat random-trial frequency as empirical incidence. Keep numeric threshold/census/arithmetic unless prospectively amended; preserve historical meanings under old IDs. **STOP the optional shared-edge rebuild this week.** Withdraw an indispensable physical-common-time headline rather than change the model after seeing ratios.

**Q3 — AMEND: correct the sum; preserve both required roles.** Agree with 13:29-35's versioned consumer/fixture migration and D-078/D-083 amendments. Disagree with `both_terms_required: false`: two roles remain mandatory, although their thresholds do not add. Specify that invariant and “sizing sum is not an acceptance gate”; preserve exact v1 bytes. Sources: `joulewise/detection_floor.py:348-362`, `docs/contracts/adapter_contracts.md:621-642`.

My rerun accepts 6 J at F=5, B=4. Code tests floor and interval exclusion separately (`joulewise/analysis_engine/claims.py:336-375`): for symmetric half-CI h, numerical direction requires |estimate| > max(F,h+B), plus multiplicity. F+B is neither that threshold nor sufficient design sizing. Call it heuristic planning; never invent its missing supplier from `deterministic_bounds.total`. Expressly supersede D-083's “correct description” (`decision_log.md:5315-5327`); migrate new exact-object consumers together.

**Q5 — AMEND: withdraw TR-01; stop the late-window shortcut.** Agree with 13:50-54's registry amendment, fixed untested-transfer prose and selector update. The max-residual predicate at 13:55-56 cannot substitute for actuator/stamp, eligible/missed-edge and sign/baseline definitions (`docs/paper/draft-v2-skeleton.md:1298-1326`; `joulewise/adapters/mlx_runtime.py:768-819`). Gap success would support that test, not all unmodified inference edges. Future work; no extra night.

**Q7 — AGREE with 13:79-82's producer-owned VOIDED demonstration: zero joule values, no result table or “primary”/“manual review.”** Still unverified here: `scripts/build_capstone.py:34` and its generated page retain the old label. Lead verifies regeneration and assembled includes after landing; raw/history stay.

### F4 — should_fix — Ranked final moves

Proposed internal cuts, not academic dates. Move earlier if required; reserve the last 48 hours for replay, assembly and reading.

1. **Today:** ratify the amended ruling and start a complete methods/diagnostic fallback using historical excursion/record-support evidence with exact standing and labeled P1 illustration. No v5 collection is not an observed Refusal. Set last useful acquisition to **8 September night**, content freeze **9 September**; failures do not license selective retries.
2. **First 24–48 hours:** land legacy L1/reviewed paper work after final-content checks; keep wave-2 only for its unattended dependency. Finish seam plus actual-CLI success/below-threshold/failed-admission rendering, fixture labels and source maps. Keep clearance |estimate|−floor; cut unbuilt means/sizing columns and unused characterization. Missing readiness selects fallback, not another receipt design.
3. **Concurrent acquisition preparation:** demonstrate a feasible slot/duration budget within two days or commit to fallback. Chain: **watchdog rehearsal/stand-down → G2-a → desk pin, pack updates and throwaway-clone proof → G2-b/transaction, nightly G3 → both floor windows AND gamma → extraction/mint/close-out**. 13:89 omits gamma/intermediate dependencies. Only the unattended watchdog collects, without sudo, local Ed intervention, new hardware or overlapping agents. This peer touches no host state.
4. **Desk days 1–3:** paper-K, enclosure and empirical figures. Add Q1/Q2/Q3/Q5, null-versus-model blocks, actual phase stochastic terms, interval integration, t convention and the risk qualifications below. Promote `fig4_edge_excursions.svg` with historical-current-method caption. Complete References/Availability; cut unused alternatives, author ledger and unperformed characterization. All this survives failed nights.
5. **By 9 September:** choose content from completed evidence; preserve all attempts/refusals. Replay each published floor's census/widths from authenticated sources, reusing `joulewise/floor_mint_estimator.py:683-717`; check absolute operands too, beyond that comparative helper. This finite check need not become a service. Keep ratios, directions and admission distinct. Missing sources restrict claims; historical floors/fixtures never fill v5.
6. **Final 48 hours:** one explicit source, selected branches, citations, source manifest/replay command. Lead runs publication-critical proof at the final head, recording skips, and rebuilds the intended shareable package in fresh permitted scratch. Inspect final PDF/HTML: every number/figure/refusal, no placeholders/stale models. If existing privacy authority prevents raw release, state exact reproduction limits and supply permitted derived outputs; infer no new release permission.

**STOP beyond 13:** reducer churn for appendix-only diagnostics; rotating absolute repeats; late transfer; optional shared-edge replay; tasks justified solely by optional FILLs; treating in-flight progress as proven integration.

**ADD:** complete no-v5 fallback now; dated cuts; gamma/G2-b/G3 budget; finite primary-width/census replay; package rehearsal and two days for final reading.

### Risks the magistrate underweights

- Relabeling can leave “largest possible false effect,” 95/95, deterministic or Holm guarantees elsewhere. Distinguish probability targets/assumptions; ABBA slot balance is not elapsed-time balance; sparse references do not bound arbitrary phase drift. Include 02:71-111 and 03:92-102 in paper-K.
- A refusal rehearsal is not acquisition success. Missed nights consume the buffer; missing data cannot become empirical refusal.
- Custody consistency is not operand correctness. 13:62-63 leaves 02-F4 as a question; apply existing recomputation to the finite published set.
- Mechanical schema/pin churn can cost another night. Matching weights does not preserve populations. Decide scope before outcomes.

### Questions that would change my position

1. Actual due date and minimum empirical requirements: is methods/historical fallback acceptable?
2. Is the question same-condition timing sensitivity or weighted prompt-ensemble variability? A required ensemble changes Q4.
3. Can delta 4 replay failed production admission through the real seam, binding reason/basis/arms? What proves claimed execution history?
4. What evidence shows all unattended stages fit before the cut without Ed/sudo?
5. Does the enclosure diff prove isolated output, frozen compatibility, unchanged campaign identities and no collection delay? That could change Q1.

## Residual risk

Synthetic arithmetic and one 59-test module only. No discovery suite, agent/model launcher, protected host path, measurement checkout, hardware, live corpus, hosted CI or final publication build used. In-flight branches may address findings; their landed behavior needs magistrate verification. This completed review installs no ruling and claims no live validation.

