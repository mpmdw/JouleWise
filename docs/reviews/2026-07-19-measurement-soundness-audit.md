# 2026-07-19 — Measurement-soundness audit: UNSOUND for claim-bearing use as recorded (trace-time-anchor defect)

Ed-directed ("go over thoroughly all the existing measurements and systems to
make sure all the measurements are sound and make sense"). Auditor: one Sol
xhigh read-only session over all measurement corpora
(runs_recal3/4/5/6_20260719 = 288 bundles, plus runs_recal_20260718,
runs_recal2_20260719, runs/p2_015_floors_window_a) and the measurement-system
layer (methodology contract, detection-floor spec, reducer, D-077
admission/cooldown, analysis engine). Every P0 finding below was then
INDEPENDENTLY REPRODUCED BY THE LEAD from primary evidence before this record
was written. Verdict adopted by the lead: **UNSOUND for claim-bearing floors/
MDEs as recorded; sealed raw evidence is arithmetically coherent and retains
calibration/instrument value.**

## P0.1 — Power traces are causally misaligned with runtime events (CONFIRMED)

The powermetrics trace clock is anchored to the host event clock via the
midpoint of a pre-spawn/first-parse bracket (`joulewise/uncertainty_evidence.py`),
leaving ~±0.5 s anchor-only uncertainty and observed shifts >0.6 s. Lead
reproduction on `runs_recal5_20260719/p2015-df-rq-short-abs-r01`:

- Runtime tokenize→decode span: 0.371 s starting at `sampling_started`
  (1784491122.808).
- Power trace span begins 0.621 s BEFORE `sampling_started`; the GPU rail
  integrates to **6.682 J, 100% of it timestamped before the marker** and
  0.000 J after. CPU rail adds 1.571 J.
- Reported `gross_energy_j`: **0.274 J** — the reducer integrated the marker
  window over misaligned timestamps and captured only idle-tail samples.
  0.274 J over 0.371 s of active MLX inference (~0.7 W) is physically
  impossible; the true request energy is ~8 J.

Auditor's anchor-shift envelopes across classes (energy range as the anchor
moves within its own recorded bracket): short 0–6.5 J on a 0.257 J point;
mid-request 10.5–37.7 J on 24.07 J; long-prompt 14.2–57.6 J on 40.0 J; suite
135.2–157.9 J on 148.4 J. Even the suite's ±11–13 J sensitivity dwarfs the
~1.08 J D-054 suite comparative floor.

Scope: the anchoring mechanism is common to ALL powermetrics corpora,
including the 2026-07-17 published Window-A floor extraction. Short-window
point energies are unusable; long-window (~60 s) values are less relatively
damaged but carry multi-joule anchor sensitivity that no summary field bounds.

Disposition (adopted): no request/phase/item/idle-subtracted point energy from
these corpora supports L2/L3 claims or floor extraction as recorded. Any
salvage must produce a new artifact carrying a conservative anchor-shift
energy envelope; a post-hoc single "best shift" is not defensible.
Re-collection under a substantially tighter causal anchor is the expected
path.

## P0.2 — "Claim-eligible" conflated source provenance with metric eligibility (CONFIRMED)

`source_provenance.claim_eligible=true` (288/288) is a SOURCE-cleanliness
fact. The reducer's own `window_evidence_precheck` says: whole-request gross
eligible 50/288 (suite bundles only); ALL 238 non-suite request metrics
ineligible (dominant reason `clock_bound_exceeds_quarter_window`; short cells
also fail cadence/sample-count); phase windows eligible 0/…; suite item
windows 0/…. Lead reproduction: the short-cell precheck above shows
`eligible: false`, clock anchor bound 1.13 s, in-window samples 4, cadence
3.23 vs required 4.0.

The 2026-07-19 run-report headline ("266/266 claim-eligible") and RUN_STATE/
PROJECT_STATUS language repeated the conflation. Corrections are appended to
those documents this session. The precheck layer itself WORKED — the defect
is in the narrative language and in reading exploratory point values as
physical.

## P0.3 — Analysis engine cannot consume the new idle-variance wire (CONFIRMED)

All 288 summaries declare reducer `0.5.0` + idle method
`duration_weighted_newey_west_bartlett_10s_iid_floor_v2`;
`joulewise/analysis_engine/inputs.py` accepts only `0.4.x` +
`newey_west_bartlett_10s_iid_floor_v1` (lead-verified at the source). All
idle-subtracted claim extraction over this corpus fails closed until a
prospective consumer-compat change lands (do NOT rewrite stored summaries; do
not relax the check generically).

## P0.4 — Four cooldown cap hits are not reflected in bundle summaries (CONFIRMED)

Lead sweep of all recal campaign logs found exactly the auditor's four
`cap_hit` members — the run proceeded after the 300 s cap with rolling power
still above the release bound:

| member | waited_s | decision W | upper bound W |
|---|---:|---:|---:|
| recal4 `df-cmp-abba-su-b01-b1` | 306.7 | 0.0918 | 0.0770 |
| recal5 `df-ph-short-prefill-abs-r04` | 300.1 | 0.0820 | 0.0751 |
| recal5 `df-rq-long-prompt-abs-r03` | 306.9 | 0.1239 | 0.0797 |
| recal6 `df-cmp-abba-ph-prefill-b03-b1` | 300.7 | 0.0809 | 0.0722 |

Bundle summaries carry `measurement_quality.cooldown_cap_hit=null`, so
summary-only extraction would silently treat these cells as clean n. Per
`docs/phase_2/detection_floor.md` cap-hit members need a governed drift term
or same-slot exclusion (n=9 guard); extraction must JOIN campaign-log
cooldown evidence.

## P1 findings (extraction/adjudication obligations; auditor's numbers, lead spot-checked)

- **P1.1 idle-admission CPU hole:** 116/288 pre-run baselines have CPU
  samples >0.5 W (max 6.58 W); `idle_window_suspect` is GPU-based, so all
  pass. Deterministic idle-drift bounds: median 1.13 J, p95 5.29 J, max
  14.15 J. Once timing is fixed, gross stays primary; idle-subtracted claims
  consume the full drift bound; add processor/combined-power admission
  criteria + adapter-state continuity (a 140→70→140 W adapter discontinuity
  spans the recal3 brackets — recurrence of the earlier 140→100→140 pattern).
- **P1.2 NEG-8 brackets show real movement:** recal6 start→end +0.969 J
  (+4.18%) — 89% of the ~1.08 J suite comparative floor; chronological block
  trends up to −2.7%. "No window drift" must not be asserted; carry bracket
  sensitivity into adjudication; set a prospective acceptance threshold for
  future windows.
- **P1.3 suite position effect is real and suite-specific:** member means by
  within-run position (32.48, 31.69, 31.80, 31.83, 20.30 J); A holds
  positions 1/4, B 2/3 → 9/10 negative contrasts. The four W3 families show
  no universal direction (5/10, 6/10, 3/10, 5/10 negative). Keep D-054
  frozen — the formula's `abs(mean)` + max-|Δ| terms absorb the bias into the
  floor; label-swap/randomization inference is INAPPLICABLE (labels not
  exchangeable); future condition experiments must counterbalance
  condition-to-position.
- **P1.4 metric-selection trap:** the exploratory "prefill 40.18 vs decode
  42.89 J asymmetry" compared whole-request GROSS of different shapes; the
  target `phase_energy_j` values differ by only ~0.62%. Phase floors must
  extract `phase_energy_j.<target>`, never infer metric from cell name. Also
  `jw_sentinel` is FIVE items (512/256 each), not 48; and
  `throughput_tokens_s` is the legacy N/(t_last−t_first) convention (+1.59%
  at 64 tokens vs the governed N−1 form).

## What remains sound

- Arithmetic/rail identities: reintegrated gross matches summaries to
  ~1e-13 J across all 288; `gross − idle_sub = idle_mean × duration` exact;
  phase sums ≤ request gross; rich-telemetry/trace identities hold.
- Token accounting: all 288 match configured/observed counts
  (mid 1024/256, short 128/64, long-prompt 4096/64, long-decode 128/512,
  suite 5×512/256); `energy_output_token_j × tokens` reproduces idle-sub
  energy exactly. The 623 mJ/output-token long-prompt figure is the intended
  output-token denominator on prompt-heavy work.
- The D-077 environment guard, admission evidence, ABBA execution, order
  manifests, provenance sealing, quarantine custody, and backups all behaved
  as designed. The screensaver-contamination story (+30% on 07-17 suite
  cells) reproduces.

## Adopted verdict and gate

**UNSOUND for claim-bearing use as recorded.** No claim-bearing floor or MDE
may be published from any existing powermetrics corpus until: (1) the
trace-time-anchor defect is fixed prospectively (tight causal anchor +
anchor-shift energy envelope in the reduction); (2) extraction honors
`window_evidence_precheck` and campaign-log cooldown joins; (3) the analysis
consumer accepts the 0.5.0/v2 wire. The 2026-07-17 published floor table is
implicated (same instrument) and is caveated pending re-adjudication. The
288-bundle corpus is retained as instrument/calibration evidence — its
variance structure, guard behavior, and cross-window repeatability remain
informative; its absolute point energies do not.

Sol audit thread: 019f7dc2-80ce-70f2-bf2d-e299a8039d7e (xhigh, read-only).
Lead verification commands and outputs are recorded in the session transcript
and reproduced in the run-report correction.
