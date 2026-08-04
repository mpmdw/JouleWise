# Capstone Scope And Headline Contract

Status: binding scope contract for the capstone headline from 2026-07-09
onward, amended 2026-07-30 by D-091. It narrows reader-facing claims under
`docs/contracts/claims_ladder.md` and composes with the cut ladder in
`docs/risk_register.md` R-012.

Evidence inputs: `docs/reviews/2026-07-09-scientific-rigor-review.md`
B4 and Appendix D Part C rows 1, 2, 3, and 10; `PROJECT_STATUS.md`
D-091 metrology-centric framing and Q1-Q6; `docs/contracts/claims_ladder.md`;
`docs/risk_register.md`; `docs/milestones.md`.

## D-091 Amendment — 2026-07-30

D-091 supersedes the original model-contrast-first ordering and every statement
below that calls a filled benchmark matrix the capstone's end goal or primary
scientific artifact. The binding scope is now a trustworthy measurement
instrument plus demonstration studies: the instrument is the product, and the
paper leads with its linearity, additivity, detection-limit, and drift-control
evidence. Model contrasts, workload matrices, and split-inference experiments
are vehicles for demonstrating what the instrument can and cannot resolve;
they are not the capstone's completion criterion.

The 2026-07-09 contribution-ladder text is retained below as history. Its
matrix-as-end-goal and matrix-as-primary-artifact sentences are visibly marked
superseded and carry no current scope authority.

## Frozen Headline Claim

**Headline claim:** JouleWise provides auditable, boundary-labeled local LLM
energy characterization on named hardware/runtime/model/workload stacks.

This headline is an umbrella scope statement, not a global L2/L3 ceiling.
Per-result ceilings: instrument cells may reach L1 when the L1 evidence rule is met (n >= 3 strict-valid bundles, or single runs explicitly labeled smoke/capability), otherwise L0 capability language; qualifying same-boundary
contrasts may reach L2; fitted fixed/marginal matrix claims may reach L3
only when the full L3 evidence rule is met; generalized claims require L4
replication and calibration evidence.

Split inference remains a stretch extension gated on a named live-replay,
synthetic-transfer, or analytical-composition method and the claims ladder;
cross-boundary quantitative winners additionally require a named calibration
bundle.

This headline is intentionally stack-bound. It does not claim that one
hardware class is more efficient than another, that a runtime effect belongs
to the hardware, or that local inference beats a datacenter scenario.

Fallback claims, in cut order:

| Claim | Allowed level | When to use |
|---|---|---|
| JouleWise produces strict-valid, boundary-labeled instrument results for local LLM inference on named stacks, including request energy, latency, token provenance, and measurement-quality fields. | L0-L1 per the ladder evidence rules, with L2 only for same-boundary contrasts that meet n, order, uncertainty, and detection-floor gates. | Use when the corpus is too small or too single-target to support a filled comparative matrix. |
| JouleWise is an auditable local-inference energy measurement instrument whose split-inference path is reported as feasibility evidence or analytical scenario analysis, not as a measured crossover result. | L0-L1 for split capability or feasibility; L1-L2 for the local measurement cells that satisfy their own gates. | Use if live split replay, target access, interconnect control, or calibration does not clear before the capstone cut line. |

## Contribution Ladder

The contribution should be argued as a ladder, not as a single all-or-nothing
claim.

**Rung 1: instrument and methodology contribution.** This rung is available
when strict bundles, raw-to-derived validation, boundary labels, floor rules,
and claim ceilings remain intact. It is defensible today as a capstone
contribution because it turns local LLM energy measurement from an ad hoc
reading into an auditable evidence pipeline. Its natural claim language is
L0-L1, with L2 only after the comparison protocol is satisfied. Strict
validation is artifact consistency, not physical validation.

**Rung 2: scoped empirical coverage contribution — ORIGINAL 2026-07-09;
MATRIX-AS-END-GOAL LANGUAGE SUPERSEDED BY D-091.** I agree with Ed's
2026-07-09 position in substance: once the workload suite expands along
difficulty axes, the model set spans quantization and size axes, and the
hardware targets span meaningful local stacks, the filled matrix itself is
the end goal. It should not be presented as "just a demonstration of
auditability." If the related-work review, including JouleSort, MLPerf Power,
ML.ENERGY, and Zeus, confirms no prior dataset covers this specific
combination of local LLM workloads, named local stacks, explicit
measurement-boundary labels, and re-reducible bundles, the filled matrix may
be presented as a scoped empirical coverage contribution. Ladder levels
attach to claims drawn from it: instrument cells may reach L1 when their
ladder evidence rule is met, qualifying same-boundary
contrasts are L2, and fitted fixed/marginal models with holdouts may be L3.

**Rung 3: specific scientific findings from the matrix.** Crossovers,
scaling structure, workload-category effects, quantization effects, and
split-vs-monolithic tradeoffs are contingent on the data. They are not the
headline promise. Each finding must earn its own claims-ladder level:
same-boundary effects may reach L2, fitted fixed/marginal structure may
reach L3 only with a designed matrix, holdout cells, strict-valid source
bundles, runtime-observed denominators, residual and sensitivity analysis,
detection-floor audits for fitted effects, and stated boundaries/workload
policies, and generalized claims require L4 replication and calibration
evidence. If nature is boring or the floor absorbs the effects, the honest
result is a matrix with `not resolvable` cells and a better measurement
limit, not a failed capstone.

**ORIGINAL 2026-07-09 ORDERING — SUPERSEDED BY D-091:** I do not disagree
with Ed's core novelty argument. The only correction is ordering: the filled
matrix is the primary scientific artifact only after Rung 1 makes the cells
interpretable. Auditability is not a substitute for novel empirical coverage;
it is the warrant that lets the coverage count.

## Minimum-Viable-Capstone Contract

This contract adds scope stop-lines and cut triggers. It does not replace
the R-012 descope ladder in `docs/risk_register.md`; when a cut is needed,
use that ladder as the ordered fallback path.

Hard stop-lines:

- Do not use split inference in the headline unless a named live-replay,
  synthetic-transfer, or analytical-composition method has cleared its
  feasibility gates and the claim follows the claims ladder.
- Do not publish cross-boundary winners without a named calibration bundle;
  otherwise, report boundary-labeled descriptive cells.
- Do not publish L2 comparative claims without strict-valid bundles, n/order
  evidence, uncertainty reporting, and detection-floor clearance.
- Do not publish hardware-class, vendor-class, or architecture-wide claims
  from one physical unit per target. Single-unit data characterize named
  stacks only.
- Do not convert `not resolvable` into "no effect," "equivalent," or a win.
- Do not let the matrix grow by sacrificing the audit path: raw evidence,
  provenance, stack identity, and claim-level review are protected scope.

Minimum deliverables:

Minimum deliverables are defined by R-012. This contract adds reporting
stop-lines to that floor: all reader-facing results must include boundary
labels, raw points, uncertainty, floor status, stack identity, and
limitations; split work that is not live-valid must be labeled as
synthetic-transfer, analytical-composition, feasibility, or unavailable
evidence.

Cut triggers:

- If supervisor approval, final report date, colloquium date, or hardware
  access compresses the calendar, protect the Mac local-characterization
  corpus and analysis rigor first; cut stretch matrix width and split scope
  per R-012.
- If a target cannot produce strict-valid bundles before its campaign start,
  demote it to capability, feasibility, or telemetry-unavailable evidence.
- If calibration hardware is unavailable, keep within-boundary claims as
  primary and demote cross-boundary quantitative comparisons to descriptive
  or scenario analysis.
- If split replay portability fails, move to synthetic transfer plus
  analytical composition, with the failure itself reported as a feasibility
  finding.
- Use the three-way floor rule for cut decisions: below-floor contrasts are
  `not resolvable`; above-floor contrasts whose confidence interval does not
  support direction are `unresolved` with no directional claim; equivalence or
  "no difference" language is allowed only through a predeclared equivalence
  gate whose margin exceeds the floor and whose contrast confidence interval
  lies entirely within that margin. Preserve the matrix cell as measured
  evidence.

## Single-Unit Limitation Language

Stack-identity fields for captions and result tables follow
`docs/contracts/token_normalization.md` (2026-07-09).

2026-07-09 pointer: this caption template composes with the full
`docs/contracts/token_normalization.md` stack-identity field table; do not
treat the bracketed slots below as a shorter replacement for that table.

Use this language, adapted with the concrete stack fields, in final-report
figure captions and result tables:

> Measurements in this figure characterize one physical unit of
> [target hardware] running [OS/version], [runtime/library], [model artifact],
> [quantization], [tokenizer], [sampler/output policy], and [measurement
> boundary]. They support stack-specific claims under the stated boundary and
> do not establish hardware-class, vendor-class, or unit-general results
> without independent replication or calibration evidence.

For cross-boundary figures without a calibration bridge, add:

> Boundary labels differ across cells, so absolute energy values are
> descriptive rather than a calibrated cross-target ranking.

## Benchmark Consumer And Decision

JouleWise should name the consumer and the decision it supports.

| Consumer | Decision JouleWise can support | Decision it must not imply without more evidence |
|---|---|---|
| Local deployer | Whether a named local stack, model, quantization, runtime, and workload shape has a measurably different energy/latency profile under a named boundary. | That a hardware class or vendor is universally more efficient. |
| Researcher | Whether an energy result can be audited, re-reduced, replicated on a named stack, or compared under a same-boundary or calibrated boundary, with a declared analysis plan and claim level. | That strict validation is physical calibration or external validity. |
| Advisor/reviewer | Whether the capstone claim is supported at the stated ladder level, whether cuts preserved a complete artifact, and whether limitations are explicit. | That stretch split-inference goals are required for a defensible capstone. |
