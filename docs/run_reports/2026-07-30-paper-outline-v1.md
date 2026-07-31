# Paper outline v1 — metrology-centric (post-Rivoire-ratification, 2026-07-30)

*Provenance: verbatim copy of `paper-outline-v1.md` from the 2026-07-30 magistrate session scratchpad
(`/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/`), committed to the repository 2026-07-31.*

Working title (Rivoire to adjudicate; recommendation #1):
**"JouleWise: Detection Floors for LLM Inference Energy Measurement on
Consumer Silicon"**
Alt: "How Many Joules Can a MacBook See?" (workshop register) /
"Joules per Token, With Error Bars" (findings register).

Target shape: 6-page workshop (EuroMLSys ~Feb '27 / HotCarbon ~May '27)
expandable to ICPE full track. Artifact-evaluation-ready by construction.

## 1. Introduction (~0.75 pp)
- Hook: LLM energy numbers are everywhere (leaderboards, policy debates,
  per-query estimates spanning 10×); error bars are nowhere. The field's
  most-used free instrument on consumer hardware (Apple powermetrics) has
  never been validated; its own docs call its outputs estimates.
- Thesis: treat the software power counter as a scientific instrument —
  calibrate it in-session, derive detection floors, refuse claims beneath
  them.
- Contributions (numbered): (C-i) an in-window calibration method that
  measures timing-attribution error for phase-resolved energy integration;
  (C-ii) detection floors composed from measured repeatability,
  worst-case attribution, and measured drift — published with every
  result; (C-iii) a fail-closed collection protocol (admission gates,
  ABBA ordering, custody chains, pre-registration) with its refusal log
  as evidence; (C-iv) full instrument characterization: linearity, null
  response across magnitudes, empirical floor verification, phase-
  attribution causal consistency, drift/settle; (C-v) demonstration
  measurements: phase-resolved J/token for two model sizes with a
  pre-registered contrast [+ quantization ladder if window budget
  allows]; (C-vi) open tool + hash-bound reproducible artifacts.

## 2. Background and the gap (~0.5 pp)
- Three lineages: energy benchmarking rules (SPEC/MLPerf Power — per-run
  uncertainty accounting, but datacenter instruments); software-counter
  validation (RAPL in Action, CCGRID '23 — error bars vs wall power, no
  detection-limit concept, no Apple silicon); LLM energy studies
  (TokenPowerBench, ML.ENERGY, Silicon Showdown, Intelligence-per-Watt —
  breadth without instrument characterization).
- The gap sentence: no published work combines phase-resolved LLM energy
  + consumer silicon + per-measurement error budgets + any validation of
  powermetrics. (Verified sweep 2026-07-30; nearest-neighbor table in §8.)

## 3. The instrument (~1 pp)
- Measurement principle: power sampling integrated between phase-boundary
  events emitted by the runtime adapter (we drive the workload; phases
  are known from code, not inferred from traces). Single-request
  sequential scope AS A DESIGN DECISION: it is what makes phase
  attribution well-posed (contrast: TokenPowerBench's unspecified
  tagging under batching).
- Threat model, 5 threats × defense × evidence-it-fired:
  (1) contamination → admission gates (evidence: XProtect + Time Machine
  catches, quarantine/supersession records); (2) slow drift → ABBA
  cancellation (arithmetic) + measured whole-window allowance from
  dedicated reference runs; (3) attribution/clock → bracketing pulse-train
  calibration (§4); (4) custody/tampering → hash-bound bundles,
  re-derive-never-trust, exclusive writes (evidence: the mint refusing
  its own inputs); (5) analysis flexibility → pre-registration with
  hard literals, fail-closed gates (evidence: refusal-then-repair
  history on the record).
- Protocol figure: window timeline (pre-cal → bound corpus → references →
  members → references → post-cal).

## 4. Error model and detection floors (~1 pp)
- The three measured terms: repeatability (max of worst observed dev and
  Student-t bound, n=10); attribution (measured boundary-placement bound
  × boundary power, worst-case corner composition across ABBA members);
  drift allowance (derived per-window from NEG-8 references).
- Composition: max(statistical, attribution) + allowance; single-count
  discipline; why RSS would be anti-conservative for the worst-case term.
- MDE formalism: powered minimum-detectable-effect δ* = 2.80·σ_D/√m and
  the workload-sizing inversion; prior-ratchet pre-registration.
- Floor values with full decomposition table (1.5B: 7.38 J; 7B: 14.00 J)
  and the finding that floors scale with device power (not model-
  independent).

## 5. Instrument characterization (~1.25 pp — THE core results)
The property/test-signal/result/claim table, one row per campaign:
- Linearity: ramp 128→2048 output tokens; response linear, fitted
  per-token cost = energy standard for later tests.  [CLAIM C1]
- Zero: null (A==A) ladder across magnitudes; unbiased, scatter tracks
  the error model's envelope.                        [CLAIM C2]
- Detection threshold: micro-delta probes walking known effects across
  the floor (0.5×/1×/1.5×/3×); floor operationally verified both
  directions.                                        [CLAIM C3]
- Attribution: additivity (phases sum to whole) + causal invariance
  (prefill energy independent of output length; slope 0 ± ε).
                                                     [CLAIM C4]
- Temporal: long holds → drift curvature within allowance; measured
  thermal settle time vs the 180 s convention.       [CLAIM C5]
- Stability: calibrations/nulls/floors repeated across ≥3 sessions/days.
                                                     [CLAIM C6]
- Internal cross-validation: channel-sum vs package reconciliation
  [+ battery/SMC drain check if feasible].           [CLAIM C7]
- [CONDITIONAL, pending wall-meter decision: external validation —
  regression wall = f(powermetrics) per SPEC/Khan/CCGRID design;
  validates totals only, phase splits remain pulse-train-validated.
                                                     CLAIM C8]

## 6. Demonstration measurements (~0.75 pp)
- Phase-resolved J/token, both models, per-phase denominators,
  context-binned.
- The pre-registered model-size contrast (1.5B vs 7B decode, same-window
  ABBA): effect, CI, effect/floor ratio, "operationally meaningful"
  column. Sublinear scaling observation (4.7× params → 3.8× energy;
  power AND time decomposition).
- [If budget: quantization ladder 4/8/16-bit with per-stack floors.]
- Every number: value ± floor-decomposed uncertainty, effect/floor
  multiple.

## 7. Limitations, scope, and threats to validity (~0.5 pp)
- Internal-to-powermetrics scale (unless C8 lands): gain error would
  bias absolute J uniformly; ratios and detections survive.
- Pulse-to-inference transfer assumption for the attribution bound
  (mitigated by C3).
- One machine, one runtime (MLX), single-request scope; floors are
  per-stack properties (demonstrated, not assumed — the 7 vs 14 J
  result).
- Conservative composition (~3× potential tightening identified, queued).

## 8. Related work (~0.5 pp)
Nearest-neighbor table (from the 2026-07-30 sweep): work × hardware ×
phase-resolved? × error budgets? × pre-registered? × consumer silicon?
Explicit differentiation vs TokenPowerBench (phase energy, no
uncertainty), Illusion-of-Power-Capping (mechanism energy, no error
composition), Silicon Showdown / IPW (Apple silicon, unvalidated
counter), Jay/Khan (validation lineage, no floors, no LLM phases).

## 9. Availability (~0.25 pp)
Tool (pip), hash-bound artifacts, refusal logs, pre-registration
records; artifact-evaluation packaging (ICPE badge target).

## Campaign → claim dependency map (execution order)
1. Contrast window (READY, runs first): feeds §6 + stresses cross-stack.
2. Metrology window A: linearity ramp + additivity shapes + null(mid) +
   holds in tails → C1, C4, C5 (+slope for C3 design).
3. Metrology window B: null ladder ends + micro-deltas (k from ramp
   slope) + stability repeat #2 → C2, C3, C6 partial.
4. Window C (any night): stability repeat #3 + spillover → C6.
5. Desk throughout: C7 reconciliation; MDE machinery; counter-mechanics
   audit (paper §3/§7 support); wall meter iff ratified+hardware [C8].
Total: ~3-4 quiet windows beyond tonight's contrast. September target
comfortable.
