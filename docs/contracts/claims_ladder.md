# Claims Ladder

Status: binding for reader-facing claims from Slice 2M onward. Decision
D-037 records adoption. Per-claim IDs and mechanical enforcement arrive with
the Phase 4 claims index; until then, authors apply this ladder during review.

This contract governs wording in reports, slides, README/status prose, figure
captions, and tables that a reader could treat as a result. Dated run reports,
stream logs, council logs, and decision logs may preserve historical wording,
but later reader-facing summaries must use the current level.

## Global Rules

- Strict validation is the entry ticket for evidence. A run bundle that cannot
  pass the applicable strict checks does not support a result claim.
- Measurement boundaries follow D-018. Claims must name the boundary label
  where it matters, for example `M3 Max / MLX / powermetrics SoC rails`,
  `RTX / vLLM / nvidia-smi board power`, or `wall_meter AC`.
- Cross-boundary comparisons are descriptive only unless a named calibration
  bundle exists for the compared boundaries. Calibration bundles include wall
  meter or USB-C PD evidence that explicitly bridges the boundary.
- Comparative claims from 2M use the experiment manifest order. Interleaved
  order is required where model reload and operational constraints permit; if
  block order is forced, the claim must say so and remain below L2 unless the
  Phase 4 drift audit clears it.
- Detection-floor gates follow Phase 4 Stage 4.0 and Stage 4.5. Effects below
  the floor are reported as `not resolvable`, not as wins, losses, or no
  difference.
- Energy-per-output-token claims require runtime-observed output token counts,
  the runtime stop reason, and the output policy label. If the denominator
  comes from config fallback rather than runtime observation, the claim
  downgrades to L0 capability language.
- (2026-07-09) Token-denominated metrics and cross-tokenizer comparison
  language follow `docs/contracts/token_normalization.md`, including its
  stack-identity table for reader-facing figures.

## Ladder

| Level | Allowed Claim Shape | Required Evidence | Forbidden Language |
|---|---|---|---|
| L0 - Capability | The harness can execute this path and preserve auditable evidence. | One complete bundle; applicable strict validation; raw artifacts present; boundary label recorded. Config-fallback token denominators may appear only here. | faster, cheaper, more efficient, scales, crossover, ranking, law, proves |
| L1 - Instrument Result | On this exact stack, boundary, workload, and output policy, this measured quantity was observed. | n >= 3 strict-valid bundles, or a single run only if explicitly labeled smoke/capability; runtime-observed token counts for per-token claims; stop reason and output policy label; no suspect quality flags unless waived in text. | general device ranking, model-family law, cross-target winner, active-parameter scaling result |
| L2 - Comparative Result | Condition A differed from condition B within the same measurement boundary under a named workload and policy. | n >= 5 per condition; strict-valid bundles; 2M experiment manifest order recorded and interleaved where permitted; confidence intervals reported; effect clears the Phase 4 detection floor; same boundary label, or a named calibration bundle if boundaries differ. | cross-boundary winner without calibration, universal, architecture-wide conclusion, extrapolated crossover |
| L3 - Model Fit | A fitted fixed/marginal model predicts held-out cells within stated error for the tested matrix. | Designed matrix with holdout cells; strict-valid source bundles; runtime-observed token denominators; residual and sensitivity analysis; detection-floor audit for every fitted effect; boundaries and workload policies stated. | law, universal scaling, architecture-wide result, causal language beyond the fitted variables |
| L4 - Generalized Finding | The finding holds across named stacks, units, or calibrated boundaries under stated limits. | Independent replication across a second target or second unit; strict-valid bundles; n and order rules satisfied per condition; named calibration bundles for cross-boundary quantitative comparison; replicated runbook; sensitivity audit survives boundary and version changes. | unqualified claims outside tested hardware, workloads, runtime versions, policies, or calibration scope |

## Downgrade Examples

- Two strict-valid Mac/MLX/powermetrics points that differ in model size,
  architecture, and quantization are hypothesis-generating for Q4. They are
  not an active-parameter scaling result.
- A same-boundary energy/token difference with runtime-observed token counts
  but fewer than five interleaved repetitions is L1 until the comparative
  protocol is satisfied.
- A per-token result using configured output length because runtime token
  counts were unavailable is L0 capability language, even if the bundle is
  otherwise strict-valid.
