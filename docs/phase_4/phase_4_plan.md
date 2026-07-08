# Phase 4 Plan: Core Characterization And Analysis

Status: tracked in `docs/phase_4/phase_4_exit_checklist.md` (per-item
status authority, per D-023). Gated by the Phase 4 readiness section of
`docs/phase_3/phase_3_exit_checklist.md` — except Stage 4.6, which is
ungated desk work and may start any time.

Companion docs:

- Exit gates: `docs/phase_4/phase_4_exit_checklist.md`
- Statistical protocol: D-014 in `docs/decision_log.md` and the
  methodology doc's Statistical Protocol section
- Boundary table: D-018 / methodology Measurement Boundaries section

## Goal

Turn the accumulated run bundles into defensible findings: every claim in
the final report traces to a figure, every figure regenerates from a script
over validated bundles, and uncertainty is quantified rather than implied.

The threat model for this phase is the capstone defense: assume every
number will be challenged with "how do you know?" and build the artifact
chain that answers it.

## Stages

### Stage 4.0: Statistical Protocol Ratification

Objective: confirm or amend D-014 against the variance actually observed in
Phase 2/3 data, *before* computing headline results.

Actions: compute per-condition coefficient of variation across the baseline
dataset; check normality plausibility at n=5 (normal-quantile plots on a
sample of conditions); run the planned bootstrap-vs-t sensitivity
comparison; compute a per-target / per-backend / per-metric measurement
floor for the headline metrics (the smallest energy, power, or time
difference the instrument can resolve, derived from sampling rate, idle
variance, and quantization); pin a minimum-sample rule for phase attribution
before any phase-level claims are made. A ~9 Hz sampler (the observed
8.8-8.9 Hz powermetrics rate) cannot resolve a ~94 ms prefill window as a
standalone claim because fewer than ~1 sample lands in the window; phase
attribution below the minimum sample count is reported as not-resolvable,
not as a number. Decide whether any element of D-014 changes (e.g., if CV is
large, more reps for headline conditions); update D-014's status and the
methodology section with findings.

Evidence: a short analysis note (`docs/phase_4/protocol_ratification.md`)
with the numbers, the measurement-floor table, the minimum-sample rule, and
the decision.

Acceptance: D-014 status updated with observed-variance justification; any
amendment applied before Stage 4.2 figures are produced (auditable order:
the ratification note is dated before the figure scripts' first results
commit); measurement floors are recorded before headline claims are drafted.

Fallback: if data volume is too thin to ratify (heavy descoping happened),
record that the protocol stands on its a-priori reasoning and flag wider
intervals prominently.

### Stage 4.1: Aggregation Layer

Objective: one validated analysis dataset from all bundles.

Design notes:

- `python3 -m joulewise aggregate runs/ --output analysis/dataset.csv`
  (pandas via `[analysis]`; CSV chosen over parquet for stdlib readability
  and diff-ability of a small dataset - revisit if size argues otherwise;
  if it does, the escalation path is stdlib `sqlite3` as a local cache
  before any DuckDB dependency, preserving D-009).
- The aggregate verb reads bundles through the shared `BundleReader`
  (D-025, built in Slice 2N) - it must not become a fourth independent
  bundle parser.
- Row = one run bundle: identity (run_id, experiment_id, config hash,
  schema_version), dimensions (target, model, quantization, workload
  profile, run_kind, link label, prompt/output tokens), all summary
  metrics (incl. per-phase energy), quality fields, bundle path.
- Inclusion rule: bundles must pass `validate-bundle --strict` (D-030:
  succeeded bundles must be reducer-consumable and their summary must
  match a fresh re-reduction); failures are listed, not skipped silently.
- Exclusion log: `analysis/exclusions.md` - every excluded bundle with
  reason (incomplete, superseded by re-run, quality-flagged with cause per
  D-014). The aggregate command writes candidates; a human/agent confirms
  with reasons. No silent exclusions anywhere in the pipeline.

Actions: implement aggregate verb + tests (synthetic bundle set => exact
expected rows; exclusion listing).

Evidence: tests; `analysis/dataset.csv` generated from the real corpus with
row count reconciled against bundle count + exclusion log.

Acceptance: dataset rows + exclusions = bundles on disk, exactly.

Fallback: none needed.

### Stage 4.2: Figure Pipeline

Objective: every report figure regenerates deterministically from the
dataset by script.

Design notes:

- `scripts/make_figures.py --dataset analysis/dataset.csv --output figures/`
  - one function per figure, a registry table mapping figure ID -> function
  -> dataset filter -> output file; deterministic (sorted inputs, fixed
  style, no randomness without fixed seed).
- Notebooks may explore; only the script produces report figures. A figure
  that exists only in a notebook does not exist.

Figure registry (initial; extend by editing the table and script together):

| ID | Figure | Primary question |
|---|---|---|
| F1 | Energy/token and energy/request by target × model (homogeneous), with 95% CIs and raw points | baseline characterization |
| F2 | Exemplar power-trace timelines with lifecycle/phase shading, one per target | measurement validity |
| F3 | Prefill vs decode: per-phase power and per-phase energy shares by target | motivates disaggregation |
| F4 | Split decomposition stacked bars: prefill/transfer/deserialize/decode energy per pairing × link | Q1 |
| F5 | Crossover curves: total energy vs prompt length, split vs both monolithic references, per link speed | Q1, Q2 |
| F6 | Energy-latency Pareto: energy/token vs TTFT (and vs throughput), points = configurations, frontier marked | Q3 |
| F7 | Interconnect: transfer energy/GiB and effective throughput vs payload size per link (synthetic sweep) | Q2 |
| F8 | Measurement quality summary: observed vs requested sampling rate, idle stddev, thermal drift, cooldown-cap hits | honesty/limitations |

Pareto definition (pinned now): a configuration is on the frontier if no
other configuration in the same comparison set has both lower energy/token
and lower latency metric; frontier computed per model, latency metric
stated on the figure (TTFT for interactive framing, throughput-inverse for
batch framing - both variants generated).

Crossover definition: per pairing × link × model, the minimum prompt length
where median split total energy < median of the better monolithic
reference; absence of crossover within measured range is reported as such
with the gap quantified.

Actions: implement registry + functions; tests on synthetic dataset rows
(figures render, files exist, no exceptions; numeric spot checks of the
aggregation feeding F5).

Evidence: `figures/` regenerated from scratch in CI-like conditions
(documented single command), byte-stable except embedded timestamps.

Acceptance: all registry figures render from the real dataset; each Q has
its figures; regeneration command documented and tested.

Fallback: figures degrade with the dataset (R-012 ladder): F4/F5 shrink to
available pairings; F7 stands on synthetic data alone if needed.

### Stage 4.3: Claims-To-Evidence Index

Objective: the audit spine of the report.

Design: `docs/phase_4/claims_index.md` - a table: claim ID, claim text
(one sentence), supporting figure(s), script function, dataset filter,
bundle/manifest IDs, status (`supported` / `weak` / `refuted` /
`out-of-data`). Rule: no quantitative claim appears in the report or slides
without a row here; a claim whose status is not `supported` appears only
with its caveat. Routing rule: every quantitative claim must first pass the
Stage 4.0 / 4.5 detection-floor gate before it can enter this index as
`supported`; below-floor claims enter only as caveated `weak` /
`out-of-data` findings with "not resolvable" language.

Actions: create with the first claims as figures land; review pass at the
end of the stage walking every report-draft claim back to a row.

Evidence: the index itself; spot-check three claims end-to-end (claim ->
figure -> script -> bundles on disk).

Acceptance: 100% of quantitative claims in the results draft have rows;
spot-checks pass.

Fallback: none - this is cheap bookkeeping with outsized defense value.

### Stage 4.4: Results And Limitations Draft

Objective: written findings for Q1/Q2/Q3 plus an honest limitations
section.

Required content:

- Where splitting wins, loses, and *why* (mechanistic story tied to F3-F7:
  bandwidth vs compute time, idle floor of the second node, transfer
  energy share).
- Effect-size honesty (Stage 4.5 feeds this): differences are claimed only
  where CIs separate and the effect clears the measurement floor. "No
  measurable difference" is a stated result category only when the effect is
  above the floor but inside the confidence interval; when the effect is
  below the floor, the result is "not resolvable", never "no difference".
- Limitations inherited by construction (each pre-seeded from earlier
  decisions): measurement-boundary differences across targets (D-018
  table); consumer-hardware sample of one per target; controller
  co-residency residual (D-013); modeled-vs-measured composition where
  fallbacks were exercised (R-004/R-005); network conditions (R-011).

Actions: draft in `docs/phase_4/results_draft.md`; every quantitative
sentence gets a claims-index row as written.

Evidence: the draft + its index rows.

Acceptance: a reader can challenge any number and be routed to bundles;
limitations section covers every exercised fallback.

Fallback: none needed.

### Stage 4.5: Uncertainty And Sensitivity Audit

Objective: verify the headline effects survive their error bars and clear the
instrument's detection floor.

Actions: for each headline comparison (split vs monolithic per pairing;
link-speed deltas): compare effect size against CI widths and the Stage 4.0
measurement floor; produce an effect-size-vs-floor table for every headline
claim (effect size, CI width, measurement floor, verdict); run the bootstrap
sensitivity (4.0); audit thermal drift across reps in the underlying
experiments (manifest order vs metric trend - a correlation means
contamination); check clock-offset bounds vs shortest attributed windows in
split runs. Below-floor claims read "not resolvable", never "no difference"
or "no measurable difference".

Evidence: sensitivity appendix in `results_draft.md` with a
pass/concern/fail table per headline claim, including the
effect-size-vs-floor columns.

Acceptance: every headline claim is marked effect>CI or explicitly
downgraded in the claims index; every quantitative claim has passed through
the detection-floor gate before entering the claims-to-evidence index as
supported; no unexplained order-correlated trends.

Fallback: claims that fail are downgraded or dropped - that is the stage
working as designed, not a failure of the stage.

### Stage 4.6: Background And Related-Work Draft

Objective: the report's background chapter - previously unowned anywhere
in the plan - drafted from a focused survey, so Stage 5.5 assembles
rather than writes it.

This is ungated desk work: it may start any time (it needs no data) and
is good fill-in work while hardware gates are closed.

Scope (survey targets, extended as reading reveals more):

- Naming lineage and framing: JouleSort (energy-efficiency benchmarking),
  Splitwise (prefill/decode disaggregation - the direct motivator).
- Disaggregated LLM inference: DistServe, Mooncake, and successors;
  where JouleWise's energy focus differs from their latency/throughput
  focus.
- Energy measurement of ML systems: MLPerf Power, Zeus, and
  software-power-measurement literature (methodology comparisons:
  boundaries, sampling, idle subtraction - tie to D-018/D-013/D-014).
- Edge/heterogeneous LLM inference measurement studies (Apple Silicon,
  Jetson-class devices).
- Named starting set from the 2026-07-05 landscape search - these are the
  closest recent works and the related-work section must position against
  each: TokenPowerBench (AAAI, Dec 2025 - LLM power benchmarking with
  prefill/decode decomposition, GPU/datacenter-focused); the ML.ENERGY
  Benchmark (arXiv:2505.06371 - Zeus-based, NVIDIA-focused);
  "Intelligence per Watt" (arXiv:2511.07885 - local-AI tokens/joule
  study across Apple Silicon and consumer GPUs); Bench360
  (arXiv:2511.16682 - local LLM inference benchmarking); "Where Do the
  Joules Go?" (arXiv:2601.22076 - inference energy diagnosis).
  JouleWise's distinguishing claims against this set: boundary-honest
  cross-device methodology (D-018), auditable raw run bundles rather
  than leaderboard numbers, and split-inference energy on local
  interconnects (none of the above measure disaggregation energy).

Actions: draft `docs/phase_4/related_work_draft.md` - per source: one
paragraph of what it establishes, and one sentence of how JouleWise
relates (adopts, extends, differs, or measures what it left open).
Every JouleWise design choice that mirrors or departs from prior art
cites the source here.

Evidence: the draft; citations resolvable (DOI/arXiv/URL recorded).

Acceptance: the report's background chapter can be assembled from this
draft plus the methodology doc without new research; the "why energy,
why split, why now" story is sourced, not asserted.

Fallback: scope the survey to the direct-motivator set (JouleSort,
Splitwise, MLPerf Power, Zeus) if time compresses - breadth of the
periphery is the cuttable part, the motivator set is not.

## Exit

Governed by `docs/phase_4/phase_4_exit_checklist.md`. The phase's product
is: validated dataset + deterministic figures + claims index + ratified
uncertainty story + results/limitations draft + background/related-work
draft ready for Phase 5 packaging.
