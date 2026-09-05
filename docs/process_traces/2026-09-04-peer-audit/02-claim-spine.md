```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Ten ranked claim-spine findings; physical-model and publication gaps matter more than additional custody machinery.","workspace":{"base_requested":"cc56a9a7","base_mode":"exact","head_start":"cc56a9a76c4d43f8dcf7fb9f4a6d424ae1dd9136","head_end":"cc56a9a76c4d43f8dcf7fb9f4a6d424ae1dd9136","upstream_end":"f4c812b40210fda148fc00968acae2723d3838b6","branch":null},"pathspec":["docs/process_traces/2026-09-04-peer-audit/02-claim-spine.md"],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker"},{"id":"F2","severity":"blocker"},{"id":"F3","severity":"blocker"},{"id":"F4","severity":"should_fix"},{"id":"F5","severity":"should_fix"},{"id":"F6","severity":"should_fix"},{"id":"F7","severity":"should_fix"},{"id":"F8","severity":"should_fix"},{"id":"F9","severity":"should_fix"},{"id":"F10","severity":"should_fix"}]},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 59 tests in 0.322s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=1\\))?"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_render_results_fills","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 27 tests in 1.385s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=1\\))?"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_detection_floor","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 159 tests in 2.547s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=1\\))?"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 47 tests in 11.144s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=1\\))?"}},{"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_whole_window.TwoScopeRefusalTests","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 7 tests in 0.025s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=1\\))?"}},{"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_claim_window_passes_and_embeds_never_zero_allowance_once tests.test_calibration_bracketing.CalibrationBracketingTests.test_missing_post_bracket_refuses_claim tests.test_calibration_bracketing.CalibrationBracketingTests.test_claim_bracket_refuses_v2_only_candidates_but_accepts_v3_pair","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 0.009s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=1\\))?"}}],"flags":[{"id":"R1","kind":"verification_gap","level":"nonblocking","text":"Desk audit only: 302 tests reported across six sequential module invocations, one skipped; arithmetic counterexamples are synthetic. No hardware acquisition, other measurement checkout, or full discovery suite was used.","needs":"Lead owns live evidence review and the separate full suite."},{"id":"R2","kind":"residual_risk","level":"nonblocking","text":"Targeted end-to-end inspection, not exhaustive review of every branch in the approximately 48,000 lines of named modules. No live floor-to-paper artifact chain was independently replayed.","needs":"Retain the existing evidence-release and floor-binding limitations until demonstrated on the actual submission artifacts."},{"id":"R3","kind":"baseline_drift","level":"nonblocking","text":"origin/main advanced to f4c812b40210fda148fc00968acae2723d3838b6 during inspection; detached HEAD stayed at the requested cc56a9a7.","needs":"Findings apply to the requested base; assess later changes separately."}]}
```

## Findings

Peer physics/evidence audit, 2026-09-04, detached `cc56a9a7`. Only this report is changed. Ranked by damage to the paper, then cheapest credible remedy. “Blocker” blocks the corresponding claim, not a narrowly worded methods paper. Recommendations do not authorize collection or changes to frozen evidence. Coverage limits: flags R1–R2; all executed demonstrations are synthetic.

The strongest near-term paper is about **conditional resolution of phase-assigned software-counter energy**. The main risks concern the meanings attached to quantities after custody checks pass. A large uncertainty envelope does not demonstrate a large realized physical error. Most remedies are narrower prose or a bounded replay, not another process framework.

Source shorthand: bare module citations are in `joulewise/` (analysis modules in `joulewise/analysis_engine/`); `draft-v1.md` means `docs/paper/draft-v1.md`.

### F1 — blocker — Partial-interval allocation leaves physical phase energy unidentified

**What is wrong.** `joulewise/reduce.py:167-180` computes sum of interval-average power times overlap duration. `reduce.py:519-520` and `554-555` set interpolation uncertainty to zero for these traces. The timing envelope then shifts the same piecewise-constant representation (`reduce.py:2148-2161,2219-2268`). An interval average determines its full-interval energy, not how that energy was distributed inside a boundary-straddling interval.

This is **not a coding deviation from the declared point estimand**: `docs/contracts/run_bundle_layout.md:805` explicitly defines overlap clipping as that estimand. The break is promoting its timing-only envelope to coverage of physical phase energy without another assumption or term. The paper's physical framing and “largest false difference” description make that distinction consequential (`docs/paper/draft-v1.md:11,19,298`).

Diagnostic P1 constructs a 0.9 s window crossing ten 100 ms records, each averaging 10 W. The point is 9 J and the ±10 ms two-edge envelope is [8.8, 9.2] J. The same record totals permit 8 or 10 J in that window: use 20 W in one half and 0 W in the other half of each of the two cut records. All complete interior records are unchanged. This is an information-loss counterexample, not a claim that a measured campaign has those waveforms. More overlapping records and an exact clock do not determine the two missing partial integrals.

**What I would do differently.** Cheapest: name the estimand “energy assigned to the phase by interval-overlap allocation” and condition any physical interpretation on within-record behavior. If physical containment is central, add or independently display the nonnegative partial-record enclosure: a cut record with total Q contributes somewhere in [0,Q], with optional tighter limits only from justified power-shape information. Do not silently redefine frozen results.

**Minimum paper evidence.** The overlap equation; one boundary-straddling raw record; its full energy, overlap-assigned energy, and admissible partial energy; both phase endpoints; the timing-only and combined enclosures. State which enclosure controls the claim. Acceptance: P1 is contained by the claimed physical enclosure, or the paper explicitly restricts itself to the allocation estimand. **Cost:** hours for disclosure and desk sensitivity; higher if a new physical model must be validated. **D-078/D-161:** timing arithmetic is guarded; this missing physical information is not a refusal condition.

### F2 — blocker — D-165 confuses a shared timing shift with a shared energy shift

**What is wrong.** Extraction evaluates onset/offset energy sweeps (`joulewise/floor_extraction.py:318-372`). `dominance_closeout.py:313-333` reduces each sweep to a nonnegative width. Replay then applies one common **energy sign** to these widths across blocks (`dominance_closeout.py:683-700`). That loses which timing displacement produced each energy displacement. A common time shift can increase one block's energy and decrease another's, depending on its edge powers. Common extrema can also occur at different timing coordinates.

P2 passes the replay's scalar preconditions with ten blocks having delta=1 J and alternating +0.5/−0.5 J responses to the same normalized onset displacement. Exact replay of that common timing parameter yields R=2.250368; the implemented common-energy-sign replay yields R=1.500000 and the opposite >=2 verdict. This demonstrates a semantic mismatch; it does not demonstrate a forged production sidecar or a live false-positive claim.

The absolute cancellation ruling makes the same substitution: `dominance_closeout.py:51-55` and `configs/campaigns/d117_contrast_v5/generate_configs.py:514-519` say a uniform shared fiducial shift cancels in deviations from the mean. A uniform **additive energy offset** cancels. A shared **timing** offset gives, locally, dE_i/dt = P_i(end) − P_i(start); it is not generally the same offset for every run. I disagree with the physical justification of that ruling even though the code implements its registered rule.

Separately, R is a ratio of worst-case floor constructions (`dominance_closeout.py:233-254`), not an estimate of realized attribution error. R>=2 supports “the registered uncertainty model dominates this operational bound,” not by itself “edge placement actually contributed more error than scatter.”

**What I would do differently.** Preserve the timing coordinates and replay a single shared onset and a single shared offset across all blocks, with the local residual terms handled separately. Until that exists, call the existing R_cm a registered shared-sign sensitivity calculation; withdraw the physical-common-mode interpretation and the asserted absolute cancellation. Report R and the D-078 label as different objects.

**Minimum paper evidence.** Per-block response curves against the **same time axes**, the maximizing common timing coordinates, point and widened floor operands, all eight independent ratios and four comparative ratios, and the precise headline predicate. Acceptance: same-slope and opposite-slope cases both agree with direct timing replay, including P2; no unconditional absolute cancellation sentence survives. **Cost:** a bounded desk derivation/replay, roughly a day; very low for narrower prose. **D-161:** source hashing and replay consistency cannot repair a wrong physical model.

### F3 — blocker — The current renderer does not enforce issued-source publication

**What is wrong.** The live registry requires authenticated suppliers and current model/workload identities (`docs/paper/results-fill-registry.md:21-36,43-53,138-162`). But `scripts/render_results_fills.py:268-285` loads JSON and checks schema identity, without authenticating it as an issued artifact. `756-783,967-970` still construct 1.5B/7B prompt/decode tokens. The manifest's `fixture_label` is allowed but unused in output (`945-999`), and the same path has no D-165 close-out input.

P3 invokes the actual CLI on its tracked synthetic fixture: exit 0, old model names, “operative floor is published,” and no synthetic/fixture label. No raw bundle, issued v5 floor or D-165 close-out was supplied. This is a concrete accidental-publication route, not a malicious-forgery threat.

The 27 passing tests do not establish live-registry readiness: `tests/test_render_results_fills.py:1-8` explicitly calls them interim, `150-152` replaces the renderer's registry sets, and `167-177` routes CLI tests through that modified module. The old successful rendering paths coexist with deliberate supplier stops for claim-bearing results (`render_results_fills.py:975-988`). This is known unfinished implementation, not proof of a current completed paper pipeline.

**What I would do differently.** Put a small publication entry point in front of the renderer: require the finalized manifest, exact floor/claim/close-out hashes, current identities and an explicit production role; invoke their existing validators; refuse the entire output on missing suppliers. Keep synthetic examples visibly labeled. Replace the interim vocabulary only once the G2-a selection and actual v5 identities issue.

**Minimum paper evidence.** One result table generated from the actual frozen manifest and custodied artifacts; a source map from each printed value and branch to artifact path/hash/field; a deliberate wrong-generation and missing-close-out refusal. Acceptance: P3 can emit only a conspicuous example or refuses; a real v5 result and its refusal alternative are rendered without test monkeypatches. **Cost:** about a day for the narrow production adapter; do not count template tests as completion.

### F4 — should_fix — Floor consumption incompletely binds uncertainty operands

**What is wrong.** The analysis loader calls `bind_floor_artifact_evidence` (`analysis_engine/inputs.py:3175-3184`). Its binding loop validates bundles, complete hashes, config/order/stack identities and point metric equality (`1866-1901,1933-1989`), but does not rederive and compare member/block uncertainty widths. The floor validator recomputes widened floors from widths supplied **by the floor record** (`detection_floor.py:3123-3163`).

The mint is stronger: `floor_mint_estimator.py:683-717` recomputes common-mode widths from authenticated sources and checks exact equality. That path is called by `scripts/mint_floor_artifact_generalized.py:4127`, not the above analysis binder. A coherently generated wrong-width floor is therefore not independently caught at every consumption boundary. Finalized-manifest byte seals do catch subsequent substitution (`analysis_engine/inputs.py:842-866,883-897`); this is not a one-field-edit bypass. The paper already acknowledges incomplete floor binding (`draft-v1.md:398,672`).

**What I would do differently.** Reuse the mint's authenticated recomputation on the exact submission floors. Share that path with the consumer if needed; do not create another estimator or custody service.

**Minimum paper evidence.** Source members, actual widths, bracket/basis, estimator identity and reconstructed/published floor comparison. Acceptance: correct points with coherently wrong widths cannot count as source-reproduced; actual submission floors independently match. **Cost:** half to one day with sources available. **D-161:** a relevant generator/operator mistake class; mint protection exceeds generic consumption protection.

### F5 — should_fix — Pulse-to-inference and GPU-to-summed-rail transfer remain assumptions

**What is wrong.** The fitted primary rail is GPU power (`powermetrics_fiducial.py:69-70,1257`); the measured trace sums CPU/GPU/ANE (`adapters/powermetrics.py:57,1793-1806`; `reduce.py:1873-1877`). A 4096-square GPU matmul pulse protocol (`powermetrics_fiducial.py:61-70,1554-1585`) does not directly establish emission behavior for CPU/mixed-load phase boundaries. Before/after bounds constrain the same calibration experiment at two times, not this cross-workload/cross-rail transfer.

This limitation is **already honestly disclosed** in `docs/paper/draft-v1.md:53,294` and `docs/contracts/powermetrics_fiducial.md:86-91`. The wrong step would be treating the bracket's `passed` as experimental validation of that transfer. There is no executable T3 validation in the bracket's pass predicate (`calibration_bracketing.py:1952-1989`).

**What I would do differently.** Keep the paper conditional, and spend the next suitable lead-controlled diagnostic window on the existing inserted-gap falsification rather than another desk custody check. Fit with the unchanged estimator. A small successful check supports applicability; it does not establish a new 95/95 tolerance claim.

**Minimum paper evidence.** A compact applicability table naming fitted rail, claimed rail sum, calibration load, inference load, timing bounds, and whether each transfer was measured or assumed. If available, show the gap-edge residuals for the named inference workload against the session's pulse bound, including failed detections. Acceptance: no narrative promotes bracket consistency into load-transfer validation; any measured transfer result has real primary artifacts. **Cost:** minutes for explicit disclosure, one quiet diagnostic session for useful new evidence; no collection was performed by this audit.

### F6 — should_fix — 59 pulses do not yield a deterministic all-claims guarantee

**What is wrong.** `powermetrics_fiducial.py:1021-1043` takes the largest fitted edge-region excursion plus capture anchor uncertainty. Count/detection/hash/binding checks (`1417-1444`) and deterministic pulse gaps (`370-397`) do not establish independent draws from one residual distribution.

The paper correctly disclaims a deterministic out-of-sample guarantee (`draft-v1.md:652`), but 1−0.95^59 needs a sampling assumption. The contract goes further: `docs/contracts/powermetrics_fiducial.md:73-91` says T1–T3 make the bound deterministic for a claim. Matching identities, recency and distributional transfer cannot eliminate the residual tail. Dependence also matters: perfectly correlated pulse draws give confidence 0.05 instead of 1−0.95^59. This is a counterexample to the inference, not a diagnosis of live pulse dependence.

The deterministic branch-and-bound promise (`powermetrics_fiducial.py:1475-1481`) encloses an accepted **loss region**; it does not establish that region's coverage of the true edge.

**What I would do differently.** Explicitly assume independent/stationary pulse maxima and condition claim propagation on the residual lying in the transferred set. Reserve “deterministic” for propagation within that set. Holm does not repair calibration-tail risk.

**Minimum paper evidence.** Pulse-max residuals in acquisition order, n=59 pulse units rather than 118 independent edges, a dependence/stationarity diagnostic, and separate interpretations of numerical containment, 95/95 tolerance and simultaneous campaign coverage. Acceptance: no sentence says T1–T3 alone remove the tail; every 95% level names its probability target. **Cost:** a few hours for analysis/editing.

### F7 — should_fix — The floor is an operational guard, not a maximum possible false effect

**What is wrong.** Absolute values are centered at their sample mean (`detection_floor.py:919-928`); comparative deltas retain their mean (`952-964`). The recipe is max(observed maximum, Student-t prediction term), times g(n)=max(1,sqrt(9/(n−1))) for n>=5 (`666-708`). The code says g(n) is **not** a tolerance, confidence, coverage or power guarantee (`104-110`). Exact corners maximize over the chosen finite box (`861-916`), not all future effects.

“The largest false difference this measurement system can manufacture” (`draft-v1.md:11,19,298`) overstates that object. Uniform fixed energy bias leaves the absolute residual floor unchanged, so this is not absolute accuracy calibration. It is not an MDE with specified type-I/type-II errors either.

**What I would do differently.** Use “registered operational resolution guard,” or define detection floor with those limits. Preserve the paper's existing boundary/external-cross-check caveats (`draft-v1.md:25,330`).

**Minimum paper evidence.** Each component's n, observed maximum, s, t, prediction term, g(n), corner widening, drift allowance and final cell maximum. Distinguish one null replicate's prediction from uncertainty of a contrast mean. Acceptance: the equations reproduce the number without implying confidence, power or absolute-accuracy certification. **Cost:** hours, chiefly wording/table work.

### F8 — should_fix — NEG-8 checks sparse reference excursions, not an envelope over arbitrary phase drift

**What is wrong.** `whole_window.py:1776-1817` computes the range of start/midpoint/end reference means and uses max(observed range, derived repeatability bound). It explicitly records `duration_scaling="not_applied_no_governed_time_law"`. The production reference shape is three start, one midpoint and three end observations (`1889-1900`). Phase metrics map to the gross-energy family (`1756-1763`), whose allowance is then consumed in phase contrast bounds (`analysis_engine/inputs.py:3818-3856`).

This is a real, nonzero reference-derived allowance; the bug is not dropping it. But a transient between sampled reference times is unconstrained without a time law, and unchanged total reference energy does not bound redistribution between prefill and decode. A common sensor gain drift also produces different energy changes on differently sized workloads. “Curvature ... remains covered” in the schematic explanation (`docs/paper/draft-v1.md:57,61`) needs a transfer/smoothness qualification. Authenticating every reference cannot supply that missing physical relation.

**What I would do differently.** State what this diagnostic samples and its workload-transfer assumption. Use existing timestamps/reference values to show the actual spacing and sensitivity to the allowance. Do not invent duration scaling retrospectively. If the paper needs stronger containment, it needs justified phase-specific or load-scaled evidence, not more hashes.

**Minimum paper evidence.** Reference energy versus actual wall time, seven individual observations and endpoint means, longest unsampled interval, derived bound and operative allowance, and its exact contribution to each phase contrast. Acceptance: the paper does not infer arbitrary between-reference or phase-specific drift containment from three reference epochs. **Cost:** a few hours for the plot/disclosure; stronger physical validation costs a new design.

### F9 — should_fix — ABBA cancels a slot-linear trend only if the relevant time averages match

**What is wrong.** The estimator is (B1+B2−A1−A2)/2 (`detection_floor.py:1269-1273`; `analysis_engine/__init__.py:699-706`). It uses no observation times. The paper's ABBA diagram asserts a shared mean time and cancellation of steady linear drift (`docs/paper/draft-v1.md:57-61`). Equal slot spacing gives that result, but model reloads, unequal runtimes and cooldowns need not.

For a drift term k*t, the remaining contrast is k*(t_B1+t_B2−t_A1−t_A2)/2. For times [0,1,2,10] s in ABBA order and k=1 J/s, the false contrast is −3.5 J. This follows directly from the implemented equation; no actual campaign timestamps were assumed. The code appropriately avoids inferred ABBA cancellation when composing deterministic bounds (`analysis_engine/__init__.py:646-663`), so the overstatement is primarily the explanatory physics.

**What I would do differently.** Say ABBA balances order and suppresses a linear trend under the specified timing symmetry. Quantify the symmetry using actual member times instead of inferring it from labels. Keep the registered estimator unchanged unless a prospective replacement is necessary.

**Minimum paper evidence.** Member timing/duration plot and each block's B-minus-A mean-time imbalance; explanation of how any residual is covered or remains an assumption. Acceptance: the diagram is explicitly equal-spacing schematic, and cancellation claims use measured time balance. **Cost:** very low; a small table or plot plus wording.

### F10 — should_fix — The issued “effective clearable effect” formula disagrees with the actual gates

**What is wrong.** `detection_floor.py:348-362` emits `effective_clearable_effect_formula="floor_j + claim_side_bound_j"` and says both terms are required. But `analysis_engine/claims.py:336-375` independently tests |estimate|>floor and exclusion of zero by intervals. `analysis_engine/estimators.py:479-486` widens the CI by the deterministic total. Two conjunctions do not require their thresholds' sum.

P1 also supplies a minimal counterexample: estimate=6 J, floor=5 J, CI=[5.9,6.1], decision interval=[1.9,10.1] after a 4 J deterministic allowance; the claim evaluator returns direction_supported and claim_ready=True, although 6<5+4. This is a unit-level gate example, not a fully admitted production claim or an issued value for the registry's separately unbuilt claim-side supplier.

D-083 explicitly chose the two-gate semantics while retaining “effective bar = floor + claim-side” as their supposed joint description (`docs/decision_log.md:5315-5327`). I disagree with that mathematical description. The draft is more careful: it calls F+B a **planning** disclosure and specifies separate gates (`draft-v1.md:272,285`). That editorial distinction should also be in the emitted metadata.

**What I would do differently.** Keep the existing prospective decision rule, but rename F+B as a planning/sizing diagnostic and remove the claim that it is the implemented threshold. Do not retroactively impose an additive gate. Do not substitute the deterministic total for the unissued separate supplier; the registry expressly blocks that inference.

**Minimum paper evidence.** Display F, both intervals, the actual gate outcomes and Holm decision; distinguish any issued sizing B from the bound used to widen the interval. Acceptance: P1's accepted example is describable without contradiction and a missing sizing supplier remains absent/refused. **Cost:** hours, unless the lead chooses a new future acceptance rule.

### End-to-end quantity, assumption and pin map

| Stage | Quantity and assumptions | Frozen authority, enforcement and minimum paper evidence |
|---|---|---|
| Capture | CPU/GPU/ANE mW converted to W; each record carries elapsed_ns averaging support. This is vendor-counter SoC energy, not calibrated whole-system energy (`adapters/powermetrics.py:3-6,57,73-82,1793-1806`). | Raw native stamps and per-rail energy survive. Internal power/energy consistency is not independent validation (`uncertainty_evidence.py:62-93`). Show rails, units and one complete raw record. |
| Clock anchor | Projected feasible interval for record-0's endpoint under affine wall/monotonic time; midpoint point estimate, later records advanced by elapsed counts (`reduce.py:1744-1811,1865-1878`). | Exact-rational/outward solver; 250 us model allowance, 50 ppm rate limit, 60 s baseline, two rollovers, 5 ms bound cap, 1 us numeric padding (`uncertainty_evidence.py:35-61,814-866`). Missing/infeasible evidence refuses. Show paired stamps, rate interval and bound decomposition; network-time-off is a control, not measurement of every clock excursion. |
| Fiducial | Joint onset/off accepted loss region for a GPU overlap-pulse model; maximum edge excursion plus capture anchor yields B seconds (`powermetrics_fiducial.py:737-828,1021-1043`). | Protocol-v3 SHA pin at `powermetrics_fiducial.py:50`; 59 one-second pulses, 100 ms cadence, 100 us projection resolution, 165,000-cell/120 s work ceilings (`61-103`). Exhaustion discards partial fits (`992-1010`). Show one fitted raw pulse and all residual maxima; confidence caveat F6. |
| Calibration/ledger | B=max(pre,post)+max(observed drift, screen), transferred to the window. | Active n17 r6 artifact ID/digest at `calibration_bracketing.py:121-173`; screen 0.009724 s, preflight 0.032898493715362 s, maximum drift 0.010164834757777545 s (`205-215`). Four source-file digests trigger staleness (`180-184,1734-1739`); exact session and 24 h causal bracket enforced (`1680-1715,1830-1866`); allowance embedded once (`1952-1989`). Ledger authenticates physical chain against committed head (`calibration_ledger.py:1973-2044`); `calibration_exits.py:1-6` types operational refusals, not new physics. Show both source hashes, receipt/basis, times and allowance operands. |
| Read/reduce | Event-window overlap-assigned gross J, optional idle subtraction/token normalization; timing corners give energy intervals. | Exact rail manifest (`bundle_read.py:25-31`), paired nonoverlapping phase events (`576-586`), raw/CSV equivalence (`reduce.py:1911-1958`), cadence/sample/quarter-window gates (`956-1011`), tail coverage (`1881-1897`), nonnegative-power corner domain (`2148-2181`) and quarter-metric gate (`2328-2361`). Show phase events, counts, point/envelope and denominator source. F1 is outside those timing guards. |
| Whole window | Reference repeatability and excursion allowance in J plus environment/adapter/member admission. | Hashed policy/member/source census (`whole_window.py:5100-5149`), rederived NEG-8 verdict/conflict checks (`5330-5388`). Show every admitted/excluded/replaced occurrence, seven references, allowance and basis. Physical transfer remains F8. |
| Floor | Residual/ABBA prediction guard, exact uncertainty-box maximum, g(n), drift allowance; cell=max(abs,cmp). | Extraction requires authenticated consumption and strict current evidence (`floor_extraction.py:1954-1984,2832-2879`); attribution-only license (`2330-2352,2789-2817`); n=16 corner cap (`detection_floor.py:889-893`); hashed common-mode parameters (`132-178`); source width equality at mint (`floor_mint_estimator.py:683-717`); final component maximum (`detection_floor.py:1622-1635`). Show spec/estimator pins and full operand table; no replacement inferred from prose. |
| Dominance | R=unguarded widened/point floor, threshold 2 inclusive; R_cm is the registered sensitivity replay. | Named constants/zero-denominator refusal (`dominance_closeout.py:36-54,233-254`), finalized source-byte hashes, 8+4 census and operand equality (`1742-1752,1796-1838,1870-1947`). Show all components including failures; F2 challenges the model, not hash checks. |
| Claims | Mean ABBA differences, repeat/metrology SE, t CI plus deterministic allowance, floor and fixed-family multiplicity. | Planned n retained (`analysis_engine/__init__.py:717-724`); Holm m retained for missing hypotheses (`multiplicity.py:49-77`); unknown reasons refuse and direction/ceiling enforced (`claims.py:219-225,318-410`). Show block deltas, uncertainty terms, both hypotheses and sensitivity. Actual ceiling is L2/L1; L3 needs held-out fit and L4 replication (`docs/contracts/claims_ladder.md:61-65`). |
| Paper | Copy issued fields or apply a registered derivation. | v5 identities frozen; prefill length remains unissued until G2-a (`results-fill-registry.md:138-162`); Outcome-B close-out/list supplier stopped (`919`); historical diagnostics separately labeled (`576-603`). Show exact path/hash/field for every value, generation/estimator agreement and release locators. F3 is the missing executable publication boundary. |

### D-078 and D-161 assessment

**D-078's attribution-limit exception is actually implemented.** It is not blanket permission to turn a refused cell into a claim. The code identifies dominance against the guarded point diagnostic (`detection_floor.py:808-843`), makes the point diagnostic explicitly non-publishable (`789-805`), permits the exact widened floor only for the sole attribution condition (`floor_extraction.py:2330-2352,2789-2809`), carries labels to the cell (`detection_floor.py:1649-1670`) and validates metadata at claim time (`analysis_engine/claims.py:286-316`). Other evidence barriers remain operative. D-165's R>=2 is a separate registered headline rule; it should not be equated to the older coded label. The F+B disclosure is emitted but does not implement an additive gate (F10).

**D-161's physics/evidence and operator-mistake goal is substantially, but not completely, realized.** The raw reconstruction, no-fallback gates, committed acceptance/source pins, session-bound bracket, source-linked whole-window verdict and known refusal vocabulary are meaningful checks. They do not establish model adequacy (F1/F2/F5–F9). The floor-width consumption gap and renderer route are actual mistake-class concerns (F4/F3), not deliberate operator attacks. Hashes prove byte identity at a named boundary; they do not prove that the quantity encoded by those bytes has the claimed interpretation. The ledger explicitly accepts a trusted writer (`calibration_ledger.py:1-14`), consistent with the D-161 distinction (`docs/decision_log.md:10392-10405`).

### Executed diagnostic evidence

Tests were run one module at a time with bytecode writes disabled. The six envelope entries report 302 tests, one skipped, no failures. These tests verify existing contracts; they cannot settle the physical-model findings. No discovery suite, model launcher, powermetrics process, measurement checkout, LaunchAgent or night-custody access was used.

**P1 — interval-allocation counterexample and two-gate arithmetic.** Exact command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
from joulewise.bundle_read import TracePoint, Window
from joulewise.reduce import _integrate, _interpolation_joint_edge_bound_j, _corner_composed_anchor_shift_envelope
from joulewise.analysis_engine.claims import evaluate_claim
curve = [TracePoint(t=i/10, power_w=10.0, support_start_s=(i-1)/10, support_end_s=i/10) for i in range(1, 21)]
w = Window(0.55, 1.45)
env = _corner_composed_anchor_shift_envelope([(curve, [w])], 0.0, 0.01)
print('interval_average_point_J=%.3f interpolation_bound_J=%.3f envelope_J=[%.3f, %.3f]' % (_integrate(curve,w.start_s,w.end_s), _interpolation_joint_edge_bound_j(curve,w),env['lower_j'],env['upper_j']))
print('same_record_totals_true_window_J=[8.000, 10.000]; 20 W/0 W boundary half-intervals suffice')
r = evaluate_claim(estimate=6.0,metrology_aware_ci95={'lower':5.9,'upper':6.1},decision_interval={'lower':1.9,'upper':10.1},floor_gate_j=5.0,adjusted_rejected=True,hypothesized_direction='positive')
print('two_gate_example outcome=%s claim_ready=%s estimate=6 floor=5 deterministic_bound=4 sum=9' % (r['outcome'],r['claim_ready_for_l2_l3']))
PY
```

Exit 0; complete tail:

```text
interval_average_point_J=9.000 interpolation_bound_J=0.000 envelope_J=[8.800, 9.200]
same_record_totals_true_window_J=[8.000, 10.000]; 20 W/0 W boundary half-intervals suffice
two_gate_example outcome=direction_supported claim_ready=True estimate=6 floor=5 deterministic_bound=4 sum=9
```

**P2 — common timing versus common energy sign.** The bracket below is synthetic input to a pure arithmetic function, not an authenticated production capture. The output label “issued_shared_energy_sign” refers to the code's registered formula; no result artifact was issued. Exact command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
from joulewise.dominance_closeout import replay_common_mode_dominance
from joulewise.detection_floor import comparative_false_effect_floor
bracket={'status':'passed','endpoint_max_b_fiducial_s':0.04,'calibration_drift_allowance_s':0.01,'b_fiducial_s':0.05,'acceptance':{'allowance':{'rule':'max(observed_drift_s,bracket_screen_s)','value_s':'0.01','embedding_count':1,'embedded_in':'b_fiducial_s'}}}
deltas=[1.0]*10
signed_slopes=[0.5,-0.5]*5
blocks=[{'delta_j':d,'onset_sweep_j':[d-s,d,d+s],'offset_sweep_j':[d],'zero_point_contrast_j':d,'bundle_residual_half_widths_j':[0.0]*4,'member_window_bounds_s':[[1.0,2.0]]*4,'member_envelope_integral_sum_j':100.0} for d,s in zip(deltas,signed_slopes)]
r=replay_common_mode_dominance(blocks,calibration_bracket=bracket,shared_edge_bound_s=0.05)
physical=max(comparative_false_effect_floor([d+q*s for d,s in zip(deltas,signed_slopes)],admissible_half_widths_j=[0.0]*10).unguarded_floor_j for q in [-1.0,1.0])
print('synthetic_common_time_shift_ratio=%.6f passes=%s' % (physical,physical>=2))
print('issued_shared_energy_sign_ratio=%.6f passes=%s' % (r['ratio'],r['passes']))
print('same shared time shift; opposite block edge sensitivities; all scalar replay preconditions pass')
PY
```

Exit 0; complete tail:

```text
synthetic_common_time_shift_ratio=2.250368 passes=True
issued_shared_energy_sign_ratio=1.500000 passes=False
same shared time shift; opposite block edge sensitivities; all scalar replay preconditions pass
```

**P3 — actual renderer CLI with its tracked synthetic fixture.** Exact command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import os, subprocess, sys
cmd=[sys.executable,'scripts/render_results_fills.py','tests/fixtures/results_prose_render/synthetic_d_and_0_manifest.json']
r=subprocess.run(cmd,capture_output=True,text=True,env=os.environ)
print('renderer_exit_code=%d' % r.returncode)
print(r.stdout.splitlines()[0])
print('contains_fixture_label=%s' % ('synthetic' in r.stdout.lower() or 'fixture' in r.stdout.lower()))
print('contains_old_models=%s' % ('1.5B' in r.stdout and '7B' in r.stdout))
print('published_language=%s' % ('operative floor is published' in r.stdout))
PY
```

Exit 0; complete tail:

```text
renderer_exit_code=0
## §7 Variant D — a token-generation cell publishes no floor
contains_fixture_label=False
contains_old_models=True
published_language=True
```

### Five actions I would take first as lead tomorrow morning

1. **Choose and state the paper's exact physical claim before collecting more data.** Adopt conditional phase-assigned SoC-counter energy unless the missing physical enclosure is supplied. Fix “largest false difference,” 95/95/deterministic wording, ABBA timing and F+B language together (F1/F5–F10). **Acceptance test:** the abstract, equations, tables and limitations describe the same estimand; each bound names its assumptions and probability target; no passage claims an unconditional physical error maximum.

2. **Resolve the two information-loss derivations at the desk.** Use P1 to specify partial-record energy treatment and P2 to compare actual shared-time replay with the shared-sign surrogate; reconsider absolute common-mode cancellation (F1/F2). **Acceptance test:** simple opposite-slope and same-slope traces agree with the claimed replay, and all admissible partial-record energies are enclosed or explicitly outside the named estimand. Preserve the existing frozen outputs as historical if semantics change.

3. **Close one real source-to-result chain for the exact submission artifacts.** Reuse the mint's primary-evidence reconstruction for all floor operands; retain a compact table of member values, widths, references, bracket and final floor/claim/ratio outputs (F4). **Acceptance test:** independent reconstruction matches every published operand; wrong widths with correct point values refuse or are detected; all exclusions/refusals remain visible. If the sources are unavailable, retain the stated reproducibility limitation and do not imply this check passed.

4. **Make publication depend on that chain.** Complete the smallest v5 rendering adapter, including D-165 close-out and the issued G2-a identity; label fixtures and generate the real-table and refused-result alternatives (F3). **Acceptance test:** the real CLI rejects old-generation, missing-parent and mismatched-hash inputs without successful Results prose; synthetic input is unmistakably labeled; every printed number resolves to a hash-bound field or registered derivation without patched test vocabulary.

5. **Spend the next suitable quiet window on a discriminating physical check, then finish the paper.** Have the lead collect the already contemplated inference-gap diagnostic with the unchanged estimator and compare residuals with the same-session pulse bound; use actual member/reference times to assess the transfer and drift assumptions (F5/F8/F9). Keep diagnostics separate from claim inputs and do not retry refusals into success. **Acceptance test:** real raw/events/bindings and every first outcome are retained, the gap result is reported conditionally rather than promoted to 95/95 certification, and the submission ends with either authenticated prospective results or an explicit methods/refusal result. This audit session performs none of that quiet-machine collection.
