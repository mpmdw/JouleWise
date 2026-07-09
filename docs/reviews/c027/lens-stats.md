# WHAT I READ

The premise needs one correction: `docs/specs/` explicitly contains draft, non-canonical planning material ([docs/specs/README.md:3](/Users/edr/code/JouleWise/docs/specs/README.md:3)). The binding statistical rules are primarily in:

- D-014, D-037/038, D-053/054, and D-057–059 in [docs/decision_log.md:653](/Users/edr/code/JouleWise/docs/decision_log.md:653).
- [measurement_methodology.md:187](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:187), [analysis_plans.md:15](/Users/edr/code/JouleWise/docs/contracts/analysis_plans.md:15), [claims_ladder.md:12](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:12), and [token_normalization.md:16](/Users/edr/code/JouleWise/docs/contracts/token_normalization.md:16).
- The P2-015 design in [detection_floor.md:25](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:25).
- Draft variance/checkpoint specs in [rq_energy_variance_design.md:42](/Users/edr/code/JouleWise/docs/specs/rq_energy_variance_design.md:42) and [checkpoint_metrics_spec.md:97](/Users/edr/code/JouleWise/docs/specs/suite_next/checkpoint_metrics_spec.md:97).

Implementation reviewed: `aggregate.py`, `reduce.py`, `schemas.py`, `controller.py`, the powermetrics contamination detector, and `generate_matrix.py`, `run_campaign.py`, and `claims_lint.py`.

Tests reviewed: `test_aggregate.py`, `test_uncertainty_p2029.py`, `test_reduce.py`, `test_experiment.py`, `test_generate_matrix.py`, `test_run_campaign.py`, `test_powermetrics.py`, `test_claims_lint.py`, and relevant schema tests.

There is no implemented P2-015 floor calculator, contrast-analysis module, or full claim-decision module. The closest objects are a marginal repetition aggregator, a window-evidence precheck named `claim_eligibility`, and structural claim-document linting.

# FINDINGS

1. **BLOCKER — The marginal 95% CI is computed correctly, but the D-053 claim-bearing contrast CI does not exist.**

   The end-to-end path is `run_experiment` → incremental experiment manifest → `aggregate_experiment` ([controller.py:1162](/Users/edr/code/JouleWise/joulewise/controller.py:1162), [controller.py:1180](/Users/edr/code/JouleWise/joulewise/controller.py:1180)). For each metric it uses the successful, finite, non-null point count as \(n\), sample standard deviation, \(df=n-1\), and
   \[
   \bar x \pm t_{.975,n-1}s/\sqrt n
   \]
   ([aggregate.py:201](/Users/edr/code/JouleWise/joulewise/aggregate.py:201), [aggregate.py:263](/Users/edr/code/JouleWise/joulewise/aggregate.py:263)). At the normal headline \(n=5\), it correctly uses \(df=4\), \(t=2.776\). For `[10,12,14,16,18]`, the result is \(14\pm3.93\), matching the independent hand test ([test_aggregate.py:66](/Users/edr/code/JouleWise/tests/test_aggregate.py:66)).

   But D-053 supersedes marginal-interval separation: claims must use a paired/block or named-model contrast, with leave-one-out and, when applicable, randomization and multiplicity handling ([decision_log.md:2602](/Users/edr/code/JouleWise/docs/decision_log.md:2602), [measurement_methodology.md:209](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:209)). None is implemented; the aggregator only sees one repeated condition.

   Counterexample: paired blocks
   `A=[100,200,300,400,500]`, `B=[101,201,301,401,501]`.
   Each marginal CI has half-width about 196 J and overlaps almost completely. Paired differences are `[1,1,1,1,1]`, whose CI is exactly `[1,1]`. Current code cannot produce the supported contrast.

   Fix shape: add an analysis artifact consuming the frozen `contrast_id`, executed block/order metadata, and bundle hashes; compute paired/block contrasts, LOO verdicts, design-respecting randomization checks, and Holm/BH adjustments there.

2. **BLOCKER — There is no executable full claim gate; current “eligible/publishable” outputs can admit statistically unsupported evidence.**

   The binding gate requires \(n\), contrast CI/direction, floor row, interpolation/effect comparison, AP/family/multiplicity fields, and the three-way verdict ([detection_floor.md:357](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:357), [decision_log.md:2606](/Users/edr/code/JouleWise/docs/decision_log.md:2606)). `reduce._window_claim_eligibility` accepts no floor, effect, contrast, \(n\), or AP inputs. It checks only sample count, cadence, clock, and whether bounds are present—not whether they are small enough ([reduce.py:523](/Users/edr/code/JouleWise/joulewise/reduce.py:523)).

   `run_campaign` then calls a single successful, strict-valid bundle “publishable” regardless of repetitions, CI, floor, or `claim_eligibility` ([run_campaign.py:1209](/Users/edr/code/JouleWise/scripts/run_campaign.py:1209)); that behavior is explicitly tested with one bundle ([test_run_campaign.py:827](/Users/edr/code/JouleWise/tests/test_run_campaign.py:827)). `claims_lint` only checks that prose names a pending or concrete floor reference ([claims_lint.py:300](/Users/edr/code/JouleWise/scripts/claims_lint.py:300)).

   Numeric failure: a 4 s phase sampled at 1 Hz at constant 8 W has adequate sample count and cadence, and code records a 4 J interpolation bound. If the floor is 1 J and the claimed effect 2 J, the allowed bound is below `min(1, 1)=1 J`; the claim must fail. Current code returns eligible because `4 J` merely exists.

   Fix shape: rename the current object `window_evidence_precheck`, and implement a separate fail-closed claim evaluator returning `not_estimable`, `not_resolvable`, `unresolved`, `direction_supported`, or `equivalent`.

3. **BLOCKER — Propagated uncertainty is attached as metadata but is not used in CIs, including mJ/token CIs.**

   The spec requires gross repetition variance, idle-baseline mean variance, and deterministic bounds to remain distinct ([detection_floor.md:326](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:326)). Code first computes `lower`/`upper` solely from the observed metric points, then separately attaches propagated terms ([aggregate.py:228](/Users/edr/code/JouleWise/joulewise/aggregate.py:228), [aggregate.py:322](/Users/edr/code/JouleWise/joulewise/aggregate.py:322)). Those terms never affect the interval or gate. Token metrics are pointwise divisions followed by the same ordinary t interval ([reduce.py:908](/Users/edr/code/JouleWise/joulewise/reduce.py:908)).

   Counterexample: five runs each report 10 J over exactly 100 observed output tokens, so all ratios are 100 mJ/token. Suppose each run also carries idle-mean energy variance \(1\ \mathrm J^2\). Code reports a zero-width ratio CI `[100,100] mJ/token`. Even the minimal independent-variance calculation gives
   \[
   SE=\sqrt{(1/5)}/100=0.004472\ \mathrm{J/token}
   \]
   and a \(t_4\) half-width of \(0.01241\ \mathrm{J/token}\), or about `100 ± 12.41 mJ/token`.

   Fix shape: distinguish “repeat-point t interval” from a metrology-aware interval. For exact token counts, scale the propagated numerator variance by \(1/T^2\); for varying denominators, predeclare whether the estimand is mean request ratio or ratio of totals and retain numerator/denominator covariance.

4. **BLOCKER — P2-015 is a design and nullable schema seam, not implemented floor mathematics.**

   D-054 adopts the false-effect guard:
   \[
   \max\left(\max|r_i|,\ t_{.975,n-1}s_r\sqrt{1+1/n}\right)
   \]
   and the analogous mean-shifted comparative rule ([decision_log.md:2636](/Users/edr/code/JouleWise/docs/decision_log.md:2636), [detection_floor.md:63](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:63)). The repository contains only nullable suite fields and a hardcoded `none_pending_P2-015` source ([reduce.py:990](/Users/edr/code/JouleWise/joulewise/reduce.py:990)); no calculator, artifact validator, ABBA delta implementation, or formula tests exist.

   The design also leaves the required \(5\le n<10\) guard factor unspecified ([detection_floor.md:78](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:78)). For energies `[10,10,10,10,20]`, residuals are `[-2,-2,-2,-2,8]`, \(s_r=\sqrt{20}\), and the unguarded floor is about `13.60 J`. A guard of 1.0 yields 13.60 J; 1.5 yields 20.40 J. That choice cannot remain operator-discretionary after observing data.

   Method judgment: at \(n=10\), the t prediction bound is a defensible operational one-new-observation guard under approximate iid normality. It is not a population detection limit, nonparametric tolerance bound, MDE, or family-wide guarantee—the document correctly says so. Freeze the factor numerically, define the ABBA block delta, version the artifact schema, and add hand-calculated fixtures before P2-015 execution.

5. **SHOULD-FIX — The precheck wrongly requires idle-drift evidence for gross request energy.**

   Gross request energy explicitly does not inherit idle-subtraction terms; idle drift applies to idle-subtracted request energy ([detection_floor.md:288](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:288)). Code has one generic `request` gate and always sets `require_drift=True` ([reduce.py:424](/Users/edr/code/JouleWise/joulewise/reduce.py:424)).

   Thus a valid 100 J gross request with adequate cadence, zero clock bound, a small interpolation bound, and no idle model is rejected solely as `drift_term_unknown`. This is the requested supported-claim-fails direction, assuming its gross floor and contrast otherwise clear.

   Fix shape: metric-specific gates such as `gross_request` and `idle_subtracted_request`; only the latter requires idle SE/drift evidence.

6. **SHOULD-FIX — The interpolation “bound” is only a one-edge sensitivity and can understate joint edge error by 2×.**

   The spec calls for perturbing window edges and recomputing a deterministic bound ([detection_floor.md:271](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:271)). Code perturbs start or end individually and takes the maximum ([reduce.py:393](/Users/edr/code/JouleWise/joulewise/reduce.py:393)).

   For constant 8 W, 1 s gaps, and a 4 s window, shifting either edge by 0.5 s changes energy by 4 J, which code reports and tests bless ([test_uncertainty_p2029.py:363](/Users/edr/code/JouleWise/tests/test_uncertainty_p2029.py:363)). But shifting both outward changes duration by 1 s and energy by 8 J. Under a Cartesian worst-case interpretation, 4 J is not a bound.

   Fix shape: evaluate joint start/end sign combinations or sum per-edge absolute bounds, and document any assumed correlation between edge errors.

7. **SHOULD-FIX — Total-token normalization violates later binding D-058 by preferring configured prompt counts.**

   D-058 requires runtime-observed denominators for governed token metrics ([decision_log.md:2735](/Users/edr/code/JouleWise/docs/decision_log.md:2735), [token_normalization.md:39](/Users/edr/code/JouleWise/docs/contracts/token_normalization.md:39)). `_total_tokens` instead lets configured prompt tokens plus runtime output events override an available runtime-observed total ([reduce.py:278](/Users/edr/code/JouleWise/joulewise/reduce.py:278)). A test explicitly locks in this older behavior ([test_reduce.py:577](/Users/edr/code/JouleWise/tests/test_reduce.py:577)).

   Counterexample: 25 J, configured prompt count 32, four output events, but runtime-observed total 999. Code reports \(25/36=0.6944\) J/token; the binding denominator gives \(25/999=0.0250\) J/token.

   Fix shape: runtime-observed total wins. If unavailable, null the governed total-token metric or mark it L0-only. The output-token-only path already correctly refuses config fallback.

8. **SHOULD-FIX — MAD outlier handling has an obvious zero-MAD masking failure, and the mandatory small-\(n\) influence analysis is absent.**

   D-014 specifies modified z/MAD flagging without silent deletion; D-053 adds leave-one-out analysis for \(n\le10\) ([decision_log.md:676](/Users/edr/code/JouleWise/docs/decision_log.md:676), [decision_log.md:2610](/Users/edr/code/JouleWise/docs/decision_log.md:2610)). When MAD is zero, code returns no outliers ([aggregate.py:423](/Users/edr/code/JouleWise/joulewise/aggregate.py:423)).

   For `[5,5,5,5,100]`, median=5 and MAD=0, so 100 is not flagged; the mean becomes 24 J and the CI approximately `[-28.74, 76.74]`. The test suite explicitly expects the analogous `[5,5,5,100]` miss ([test_aggregate.py:239](/Users/edr/code/JouleWise/tests/test_aggregate.py:239)). There is also no documented-cause input or with/without interval output.

   At \(n=5\), modified z should be forensic only. Add a zero-MAD fallback that flags off-median values for review, plus the D-053 contrast-level LOO verdict table. Continue keeping unexplained points in the headline.

9. **SHOULD-FIX — Idle contamination is gated for one positive flag, but campaign usability ignores other statistical ineligibility.**

   The powermetrics rule is a hardcoded heuristic: at least 40% of idle samples below 0.80 GPU idle ratio, or mean reported GPU frequency above 800, marks suspect ([powermetrics.py:47](/Users/edr/code/JouleWise/joulewise/adapters/powermetrics.py:47), [powermetrics.py:714](/Users/edr/code/JouleWise/joulewise/adapters/powermetrics.py:714)). This is reasonable as a conservative detector tied to observed contamination, but five samples cannot characterize contamination statistically.

   `run_campaign` correctly rejects `idle_window_suspect=True`, but its quality extraction checks nothing else ([run_campaign.py:843](/Users/edr/code/JouleWise/scripts/run_campaign.py:843)). A bundle with `cooldown_cap_hit=True`, unknown idle evidence, or reducer `claim_eligibility.eligible=False` remains “usable” if strict-valid and succeeded ([run_campaign.py:154](/Users/edr/code/JouleWise/scripts/run_campaign.py:154)). This conflicts with the cap-hit and unknown-input rules in D-057 ([decision_log.md:2713](/Users/edr/code/JouleWise/docs/decision_log.md:2713)).

   Fix shape: keep collection usability distinct from claim eligibility. Rename the campaign verdict or add a second claim-readiness verdict that consumes the stable reducer reason codes and metric-specific quality rules.

10. **SHOULD-FIX — Matrix generation creates five isolated runs but no aggregate/contrast analysis identity.**

   The matrix intentionally emits each repetition as a unique config with `repetitions=1` ([generate_matrix.py:97](/Users/edr/code/JouleWise/scripts/generate_matrix.py:97), [generate_matrix.py:134](/Users/edr/code/JouleWise/scripts/generate_matrix.py:134)) so conditions can be interleaved. That is operationally sound. But the only aggregate path groups repetitions within one config/experiment, while the generated order manifest merely records ordering ([generate_matrix.py:269](/Users/edr/code/JouleWise/scripts/generate_matrix.py:269)).

   After all five `mid_mid` configs run, there is therefore no automatic five-point experiment aggregate, paired block contrast, sentinel drift calculation, or frozen `contrast_id` linkage. Matrix tests thoroughly verify order structure but not analysis grouping ([test_generate_matrix.py:264](/Users/edr/code/JouleWise/tests/test_generate_matrix.py:264)).

   Fix shape: preserve one-run configs, but emit a frozen analysis manifest that gives each entry `cell_id`, `block_id`, `condition_id`, sentinel linkage, and enumerated contrasts; run the contrast engine over that manifest after collection.

11. **SHOULD-FIX — Several statistical tests would stay green against materially broken claim machinery.**

   The solid exception is the hand-computed t-interval test ([test_aggregate.py:66](/Users/edr/code/JouleWise/tests/test_aggregate.py:66)). Important blind spots are:

   - MAD-zero tests encode “obvious outlier, zero flags” as success ([test_aggregate.py:239](/Users/edr/code/JouleWise/tests/test_aggregate.py:239)).
   - Propagation tests verify the detached variance map but never require it to affect `lower`/`upper` or token metrics ([test_uncertainty_p2029.py:441](/Users/edr/code/JouleWise/tests/test_uncertainty_p2029.py:441)).
   - A gate test calls a request “eligible” with no floor/effect/contrast inputs ([test_uncertainty_p2029.py:247](/Users/edr/code/JouleWise/tests/test_uncertainty_p2029.py:247)).
   - Token tests preserve the pre-D-058 config-precedence rule.
   - Matrix tests verify `repetitions=1` without asserting a downstream five-repetition analysis grouping.
   - The “good AP” fixture passes with `pending-P2-015` and pending bundle links ([test_claims_lint.py:59](/Users/edr/code/JouleWise/tests/test_claims_lint.py:59)); that is valid for structural linting but vacuous as claim enforcement.

   Add mutation-style tests that delete floor comparison, replace paired differences with marginal means, ignore propagated variance, accept config token counts, omit LOO, and mark a one-run campaign claim-ready.

12. **NIT — Canonical decisions and prose are out of synchronization.**

   Named decisions win:

   - `measurement_methodology.md` still labels the D-053 amendments “pending ratification” ([measurement_methodology.md:189](/Users/edr/code/JouleWise/docs/contracts/measurement_methodology.md:189)), while D-053 says it ratifies those markers ([decision_log.md:2596](/Users/edr/code/JouleWise/docs/decision_log.md:2596)).
   - `detection_floor.md` says propagation is future work and neither module implements it ([detection_floor.md:302](/Users/edr/code/JouleWise/docs/phase_2/detection_floor.md:302)), while D-057 and the reducer/aggregator implement partial variance and bound fields.

   Update those passages to say “partially implemented; not yet consumed by contrast/floor claim tooling.”

# DESIGN JUDGMENT

The primary Student-t choice is right-sized for a descriptive mean at \(n=5\): it is better than a normal-z interval, and percentile bootstrap is not reliably better with five points. The implementation of that narrow calculation is correct. Its assumptions—iid, approximate normality, no informative missingness—are fragile in a thermally drifting, block-ordered benchmark, so it should not be promoted into the claim engine.

For comparative claims, the right unit is the predeclared paired/block contrast. I would retain \(n=5\) for large descriptive effects, but require at least six blocks when randomization inference is promised and top up toward ten for near-floor, equivalence, or influential-point cases. At \(n=5\), LOO sensitivity is more informative than a bootstrap histogram.

The P2-015 false-effect prediction-bound design is sensible as an operational calibration guard at \(n\approx10\), provided it remains explicitly distinct from an MDE, metrological accuracy statement, or population tolerance limit. The small-\(n\) factor must be frozen numerically before data, and the whole calculation must become a versioned artifact with exact bundle provenance.

The largest design gap is not a better CI formula; it is the absence of one integrated analysis artifact:

`strict-valid bundles → metric-specific evidence gates → paired/model contrast → propagated stochastic uncertainty + separate deterministic bounds → floor/three-way verdict → multiplicity adjustment → token/stack provenance → claim level`

Until that exists, the repository has careful contracts and useful low-level evidence, but not executable statistical claim discipline.

**CHECKS PERFORMED —** Static read only; no suite or project code was run and no files were changed. Re-derived the one-sample and paired Student-t intervals, \(df=n-1\), sample variance, modified-z/MAD rule, idle-baseline term \(D^2s_P^2/n_P\), exact-denominator ratio scaling \(\operatorname{Var}(E/T)=\operatorname{Var}(E)/T^2\), joint edge-perturbation bound, P2-015 one-new-observation prediction bound, \(1-0.95^n\) tolerance-bound arithmetic including \(n=59\), and the unpaired \(n=5\) MDE factor.