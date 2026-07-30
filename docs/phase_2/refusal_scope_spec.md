# Refusal-scope specification v1 (the ONE home for reason-code scoping)

Ratified 2026-07-29 by the magistrate, implementing the cold-gate ruling
of the same date (cold Fable instance, approve-with-conditions on Q1/Q2;
paired Opus contract refuter: SAFE, five attack lines failed). This spec
must exist ratified BEFORE any scope change lands (Q2). Supersedes the
FIX-3 design-contract rationale line for `anchor_energy_envelope_unrecorded`
("stays global"), whose stated premise — that the classifier carries the
minted-envelope coverage promise — was falsified: that promise is
enforced by the allowlist-independent map-level guard (S3.3).

## S1 — Closed scope table

A refusal code is METRIC-LOCAL only when emitted by a governed child
evaluator and normalized to one recognized addressable precheck child.
Everything else is GLOBAL. Occurrence count never determines scope.

| Code | Scope | Emitter site | Rationale |
|---|---|---|---|
| nonpositive_window_duration | local | reduce.py child window evaluator (:974-1021) | property of one child window |
| insufficient_in_window_samples | local | same | per-window sampling density |
| cadence_ratio_unrecorded | local | same | per-window cadence evidence |
| cadence_ratio_below_threshold | local | same | per-window cadence quality |
| clock_bound_unrecorded | local | same | per-window clock evidence |
| clock_bound_exceeds_quarter_window | local | same | bound vs THAT window's duration |
| interpolation_bound_unrecorded | local | same | per-window interpolation evidence |
| drift_term_unknown | local | same | per-window drift term |
| idle_baseline_unrecorded | local | same | per-window baseline evidence |
| cooldown_cap_hit | local | reduce.py:1023-1024 in `_window_evidence_precheck_for_window` (:956), gated `require_cooldown` (request-level children only) | per-child cooldown state |
| anchor_energy_envelope_exceeds_quarter_metric | local | reduce.py envelope evaluator (:2316-2342) | quantified envelope vs THAT metric |
| anchor_energy_envelope_unrecorded (as precheck occurrence) | **local** (this spec; cold-gate 2026-07-29) | reduce.py:2315-2316 via `_anchor_envelope_gate_reasons`; stamped at mint time :2469-2487 on unmintable (sub-ms) windows BY DESIGN | describes THAT gate's metric only; the blanket carried zero evidence about sibling metrics and made the gate unsatisfiable on every reducer-0.5.2 corpus |
| anchor_energy_envelope_unrecorded (map-level add) | **global** | whole_window.py:577-611 direct `reasons.add` — never passes the classifier | missing/short-coverage minted envelope MAP = consumption promise broken |
| post_window_trace_tail_shorter_than_anchor_bound | global | reduce.py (session-level barrier) | evidence boundary of the whole capture |
| clock_anchor_unresolved | global | reduce.py | no usable time base for anything |
| instrument_calibration_* (all) | global | calibration_bracketing.py / whole_window.py | instrument state poisons every child |
| negative_power_sample | global | reduce.py universal barrier | physically invalid capture |
| whole_window_verdict_provenance_invalid | global | whole_window.py | custody/authentication failure |
| custody / verdict / membership / authentication / basis / bracket / structural / provenance failures (all) | global | various session-level sites | session integrity, not window property |

## S2 — Normative fail-global defaults

Unknown code → GLOBAL. Unknown or unrecognized path (normalization
returns None) → GLOBAL. Malformed reason container → GLOBAL
(`whole_window_verdict_provenance_invalid`). These defaults are part of
the contract, not implementation detail.

## S3 — Named owners of the D-078 gate-1 guarantee

(anchor-shift envelopes REQUIRED for claim-bearing extraction, per
consumed wire — D-078 cl.2 scopes eligibility at METRIC level):
1. Member-level extracted-metric guard — floor_extraction.py:1129-1143.
2. Per-metric precheck routing — floor_extraction.py:1113-1121 with
   `_member_fatal_reasons` (:1235-1238); the requested child's own
   reasons are fatal to that member.
3. Map-level minted-coverage/domination guard — whole_window.py:577-611
   (allowlist-independent; out of scope for any allowlist change).
4. Mint target guard — scripts/mint_floor_artifact.py:381-384
   (metric-correct independently of classification).
Composition paths (block-delta) must refuse any CONSUMED pointer lacking
a complete envelope (regression-pinned).

## S4 — Change control

Any future scope move for ANY code in S1 is a MANDATORY cold-gate
trigger (fresh cold instance + cross-model contract refuter on a
mechanical packet). Not lieutenant discretion, not a bench patch.

## Record

Cold-gate conditions C1-C5 and refuter residuals R1-R3 bind the
implementing commit (see the 2026-07-29 session run report). Decision-log
amendment: D-083.
