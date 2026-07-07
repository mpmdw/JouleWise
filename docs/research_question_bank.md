# Research Question Bank

Candidate research questions the instrument can answer, beyond the named
set in `PROJECT_STATUS.md`. Populated from council sessions C-003/C-004
(2026-07-07; see `docs/council_log.md` for positions and votes). Promotion
out of the bank requires: a named RQ slot in `PROJECT_STATUS.md`, a data
plan that does not displace queue ranks above it, and (post P1-001) scope
fit. Killed ideas stay recorded with their cause of death.

## Promoted 2026-07-07 (now Q4-Q6 in PROJECT_STATUS)

- **Q4 Fixed-vs-marginal energy model** — fit
  `E = fixed + prefill(prompt_tokens) + decode(output_tokens)` per
  target/model/quantization; predicts which workloads flatter which
  devices and enables compositional split-energy prediction (predict
  split-run energy from monolithic coefficients + transfer measurements,
  validate on a subset) — the method that makes Q1 answerable at scale.
  Subsumes the prefill-scaling-exponent question.
- **Q5 Ranking stability** — do device rankings survive workload changes
  (prompt/output/quantization regimes), or where do they flip? Uses the 2M
  matrix directly.
- **Q6 Boundary sensitivity** — do conclusions change when measured at
  platform rails vs AC wall power? (Gated on the wall meter, P1-003/R-007;
  reframes calibration as a research result.)

## Methodology centerpiece (deliberately NOT a numbered RQ — C-003 vote)

- **Detection floor / noise floor**: the smallest idle-subtracted energy
  difference each target/telemetry backend can honestly resolve. Observed
  motivation: idle baseline stddev (5.4 W) exceeded its mean (3.5 W) in
  the first real capture. Pairs with the reducer feature all council
  members converged on: **phase/item identifiability flags** (windows with
  fewer than N samples report a flag, not a bare joule value).

## Banked (viable, not yet promoted)

- **Dark silicon / rail utilization**: what fraction of a SoC's rails does
  a runtime energize? (Measured: ANE at 0.0 W through 512 tokens of MLX
  decode — the most quotable standalone finding to date.)
- **CPU:GPU energy division by phase**: does the rail mix shift between
  compute-bound prefill and memory-bound decode? Upstream of split
  economics.
- **KV-growth decode drift**: does per-token energy rise with sequence
  position? Valid only in CHUNKED form — token cadence (~4 ms) far
  outruns the power sampler (~113 ms); no per-token joule claims.
- **Cooldown recovery as thermal characterization**: recovery time vs
  preceding run intensity; cap-hit rates (observed: one 305 s cap-hit vs a
  117 s recovery in the first flagship experiment).
- **Failure frontier**: structured `unsupported` bundles as data — which
  model/quant/context combinations fit, fail, or throttle. Competitors
  discard their failures.
- **Cold-start / keep-warm energy**: model-load joules and the reload-vs-
  resident breakeven. Needs sampling outside the current measured window
  (harness extension).
- **Energy-per-correct-answer vs difficulty** (C-004): instrumented by the
  `affine_mod_ladder_v1` scored workload profile (see below). Claim shape
  pinned by the council: "energy per correct answer rises as accuracy
  falls under a controlled per-attempt energy envelope" — difficulty is
  DESIGNED to hold token budget approximately constant, and observed
  token/stop-reason distributions must be reported to verify residual
  EOS/output-length effects are negligible (wrong-answers-terminate-early
  would bias the curve's magnitude). NOT "difficulty causes energy."
- **Speculative-decoding energy**: joules per accepted token with/without
  a draft model. Needs runtime support + quality-equivalence controls.
- **Power-mode Pareto**: energy-latency tradeoff across OS power modes;
  wait until power mode is a first-class config/environment field.
- **Deferred (C-003/C-004 unanimous): general joules-per-solved-task /
  intelligence-per-joule** — drags in accuracy-evaluation policy before
  the measurement dataset matures, and sits in Intelligence per Watt's
  lane where JouleWise is least differentiated. The quarantined ladder
  profile above is the minimal version that survives.

## Instrument expansions adopted by C-004 (queue P2-009 / P2-010)

- **P2-009 rich telemetry (land FIRST — zero capture cost):** parse the
  already-captured-but-discarded plist fields — per-cluster E/P-core DVFS
  residency histograms, per-core frequencies/idle/parking, GPU
  freq/dvfm_states/idle_ratio/sw-requested-vs-achieved state, vendor
  combined_power as a cross-check — plus per-bundle environment snapshots
  (battery/charger state, Low Power Mode, memory pressure, load, display
  state; all sudo-free). Evidence this matters: decode pins the GPU at
  1380 MHz / idle_ratio 0.0 / ~22 W, and the contaminated idle window was
  mechanically visible in `gpu.idle_ratio` (first half at 13 W / 1363 MHz
  before true idle) — parsing it turns our contamination anecdote into an
  automated idle-quality gate. Opt-in `rich_telemetry` tier later: the
  `tasks` sampler (per-process attribution — the direct answer to
  background contamination), disk/network samplers.
- **P2-010 scored workload suite v1:** `affine_mod_ladder_v1` per the
  C-004 design (seed-deterministic SHA-256-derived modular recurrences;
  difficulty = iteration count with prompt shape and answer length fixed;
  exact-integer scoring; levels 1..64 powers-of-two, 16 items/level;
  suite-per-bundle with item/level marker events; level-window energy
  primary; per-item flagged unidentifiable below minimum samples;
  correctness lives in stdlib `joulewise/workloads.py`, scored by the
  reducer so summaries stay re-reducible). Quarantine rules (C-004):
  one optional workload profile, correctness as annotation, no
  "difficulty causes energy" claims.
