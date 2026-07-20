# Splitwise replication roadmap (Mac-first) — 2026-07-19

Ed's directive: recreate Splitwise (Patel et al., ISCA'24) findings first,
pick ONE model class for the Splitwise analysis, then begin the harder
measurements; map what a quiet Mac must measure for a big chunk of analysis.

Inputs: Sol xhigh design consult (thread 019f7dc0-05e0, adopted with lead
adjudication recorded below) and the same-day measurement-soundness audit
(`docs/reviews/2026-07-19-measurement-soundness-audit.md`), whose verdict
reordered this roadmap: **instrument repair now precedes everything.**

## Adopted decisions (lead adjudication of the design consult)

1. **Model class: Qwen2.5 dense Instruct, MLX 4-bit — starting as the
   1.5B/7B pair** (not a five-size ladder). Rationale: continuity with the
   entire existing evidence base (1.5B is the pinned instrument model); the
   split-suite pack's registered Q1 selection is exactly `{1.5B}` or
   `{1.5B, 7B}`; D-016 prefers a same-family small/mid pair; D-073 sets the
   binding cross-target cap at 12 GiB (3080 Ti) — 7B INT4 fits, 14B is
   risky. The five-size ladder is a later extension. A switch to Llama for
   lineage-matching is rejected: no artifact/evidence chain, and the
   characterization claims concern phase behavior, not ancestry.
   (Consult dissent adopted over the lead's ladder draft; also adopted: the
   queue's 8 GB mention is stale — 12 GiB per D-073.)
2. **Order: P2-006 model/registry freeze BEFORE the broad AXI-SE freeze**
   (consult dissent adopted). AXI-SD dense/MoE deferred — one class first.
3. **Estimator discipline:** the suite position-in-block effect (audit
   P1.3) is absorbed conservatively by the frozen D-054 floor formula and
   reported as position means; no retroactive debiasing; randomization
   inference marked inapplicable; future condition experiments counterbalance
   condition-to-position allocation prospectively.
4. **Honesty line:** Mac-only work is a *Splitwise-style characterization
   reproduction* (phase asymmetry, prompt-length scaling, static-batch
   economics, model-size effects). It is NOT the heterogeneous-fleet
   disaggregation result: no NVML-style power capping on Apple Silicon, no
   A100/H100 heterogeneity, no InfiniBand KV overlap, no
   continuous-batching/SLO serving results (D-070 static-batch fence).

## Phase 0 — INSTRUMENT REPAIR [AGENT lane; blocks everything]

From the soundness audit; all prospective, no stored-summary rewrites:

- **T0.1 Trace-time anchor:** replace the pre-spawn/first-parse midpoint
  anchor with a tight causal anchor (design options to evaluate: workload
  power-pulse fiducial at window start; powermetrics interval-timestamp
  alignment against a synchronized start barrier; both). Acceptance: anchor
  uncertainty small relative to a quarter of the SHORTEST claimed window,
  live-validated against a known-shape pulse.
- **T0.2 Anchor-envelope reduction:** every reduced energy carries a
  conservative anchor-shift joule envelope; `window_evidence_precheck`
  becomes a hard extraction gate (no narrative may call a corpus
  "claim-eligible" on source provenance alone — rename/clarify fields).
- **T0.3 Extraction joins:** campaign-log cooldown evidence (cap hits) and
  admission records joined into extraction inputs; cap-hit members get the
  governed drift term or same-slot exclusion + n−1 guard.
- **T0.4 Analysis-engine wire compat:** accept reducer 0.5.0 +
  idle-variance method v2, verified against the exact stored wire.
- **T0.5 Idle admission hardening:** processor/combined-power admission
  criteria (the GPU-only `idle_window_suspect` hole), adapter-wattage
  continuity check, and a prospective NEG-8 bracket acceptance threshold.
- **T0.6 Metric hygiene:** phase floors extract `phase_energy_j.<target>`
  only; governed (N−1) throughput convention in reader-facing surfaces.

## Phase 1 — RE-COLLECTION [QUIET-MAC, after Phase 0]

Re-run the Window-A calibration design under the repaired instrument. The
2026-07-18/19 windows prove the operational cost: ~280 bundles in one
overnight chain, guard-protected, with operator interruptions handled.
Deliverable: the FIRST claim-bearing floors/MDEs (P2-015 verified extraction
+ P2-037), including suite, request, phase, and the four ABBA families.

## Phase 2 — CHARACTERIZATION SCIENCE [QUIET-MAC windows, in order]

| Window | Executes | ~Scale | Prereqs | Splitwise finding |
|---|---|---|---|---|
| W1 | P2-006 / AP-2 (1.5B + 7B, four shapes, drift sentinels) | 60–120 bundles, 2–4 h + 7B multiplier | Phase 1 floors; frozen 7B artifact receipt + load/memory evidence | Phase power/energy asymmetry; first model-size contrast |
| W1 tail | P2-010 affine smoke (B=5) | ~5 bundles | registered tail config | envelope validation (methods) |
| W1 opt. tail | P2-046B load transitions | 8 transitions, 20–40 m | frozen contract (done) | transition/provisioning overhead analog |
| W2 | P2-019 / AP-1 shape grid + 8192 anchors | 130–260 bundles, 4.5–9 h | AP-1 amendment registering the 8192 anchor cells | prefill prompt-length scaling; decode-length scaling |
| W3 | AP-BATCH pilot (B∈{1,2,4,8,16} static) | ~93 group executions, ~3 h | AXI-SB-ADAPTER (agent lane, can start NOW); AP-BATCH freeze; group-level floor/covariance path (single-request floors do NOT transport) | decode batching economics |
| later | AP-BATCH confirmatory | ~155 groups, ~5 h | clean pilot; prospectively frozen rule | confirmed batch scaling |
| methods tail | P2-047A design → P2-047B | 20–40 exec, ~1 h | P2-047A registry entry | controller-overhead credibility |

P2-020 / P2-012 deliberately stay out of these first windows.

## Phase 3 — SPLIT PoC [hardware-gated]

Unlock conditions (all): P1-006 operational 3080 Ti lane (SSH, CUDA,
numeric `nvidia-smi power.draw`, runner behavior, trace integrity); P1-004
measured Mac↔rig topology/throughput; a same-runtime KV-compatible path on
both nodes (e.g., llama.cpp adapters both sides, or a contracted portable
serialization boundary — MLX KV state is NOT assumed portable); split-pack
floor rows for split-total/serialize/transfer/deserialize; the pack's
pre-registered AP-1 compositional predictions. Mac SoC rails and NVIDIA
board power remain separate structural measurement boundaries without a
wall-power bridge (P1-003).

## Zero-new-measurement analysis (existing 288 bundles)

Post-audit status: absolute point energies are unusable, but trace-SHAPE
analysis (the workload blob's internal structure is anchor-independent)
supports exploratory-labeled figures: phase power-profile shapes
(high-power/short prefill vs lower-power/long decode), rail-composition
structure (GPU-rail share prefill vs decode), long-decode per-token
ramp/plateau traces, and the cross-window repeatability/methods figure.
Each requires the exploratory label and the audit caveat until Phase 1 data
exists.

## Standing risks

- The 07-17 published floor table is caveated pending re-adjudication
  (PROJECT_STATUS carries the caveat; advisor brief correction is Ed's
  deployment call).
- DF-TELEM (block 10) remains hardware-unavailable.
- 7B durations must be measured before W2 window budgeting (do not carry
  the 1.5B ~2 min/bundle figure).
