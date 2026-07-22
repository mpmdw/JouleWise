# 2026-07-20/21 — Phase 0 instrument repair: anchor estimator v2, two-edge energy envelopes, live pulse-fiducial calibration, cross-model convergence

Ed-directed ("spend serious time making sure the measurement instruments are
rigorous"; ultracode authorized). Executes roadmap Phase 0
(`docs/phase_2/splitwise_replication_roadmap.md`) against the D-078 soundness
gate. Branch: `impl/p0-instrument-repair` (from main `ccfa5c2`); final head
pending convergence sign-off (round-2 confirmation in flight at `233e9e3`).

## Build arc (2026-07-20)

1. **Design:** Sol xhigh pre-decision consult (thread 019f7df3-8120) rejected
   the lead's naive native-timestamp anchor (stamps are 1-second-quantized
   censored observations, lead-verified) and specified the
   censored-constraint interval estimator (N ∩ C), continuous common-shift
   energy envelopes (interior extrema required — endpoint-only evaluation is
   unsound), the 40-pulse fiducial protocol, and the stream split. Its
   288-bundle sweep: anchor intervals non-empty 288/288, median width 70 ms,
   max 116 ms.
2. **Implementation (ultracode workflow, 76 agents):** three worktree
   streams — A anchor+envelope+fiducial harness (reducer 0.5.1 + AXI 0.6.1,
   additive; 0.5.0/0.6.0 byte-frozen), B engine wire compat +
   cooldown/cap-hit joins + extraction hygiene, C idle-admission core.
   Per-stream review panels, severity-tiered refuters, fix-until-dry with
   delta re-audits (A: 1 round, B: 3, C: 1; zero unresolved). Integration
   head `3480f1b`.
3. **C2 hookup (Sol high):** live CPU-aware admission enforcement in the
   controller (production fail-closed, exploratory flagged), typed
   `idle_admission_extension` sidecar schema, adapter-power call site,
   `--whole-window-verdict` NEG-8 bracket pass, attempts ledger. Lead-verified
   fail-closed on missing telemetry under both policies; committed `d1c1538`.
4. **Lead physics verification (independent arithmetic, not the branch's
   code):** r01 anchor interval `[1784491122.657586, 1784491122.770690]`,
   midpoint matching the branch to the microsecond; corrected gross 7.6639 J
   (branch: 7.664159 J) vs the defective 0.274 J; envelope scan
   [6.765, 7.681] J with the maximum at an interior breakpoint.

## Live instrument validation (lead-owned [QUIET-MAC], Ed pre-authorized window, 2026-07-20)

- **Pulse-fiducial calibration VALID**
  (`runs/instrument_validation/20260720T185237-462076b9/`, worktree runs
  root): 40/40 commanded pulses detected, 0 spurious plateaus, residual
  median 10.5 ms / p95 19.0 ms. Declared B_fiducial 24.0028 ms under the v1
  method; head re-derivation from the same sealed raw bytes under protocol_v2
  (full 2-D `joint_loss_sublevel_interval_branch_v2` region + capture
  anchor-bound composition) gives **B_fiducial = 27.373 ms** — the value to
  quote (artifact re-emitted offline via the new `--rederive-from` mode as
  `runs/instrument_validation/20260721T042731-rederive-v2/`; no second live
  run needed).
- **Stability probe (probe-labeled, non-claim-bearing), 4/4 usable:** live
  short cells 7.278 / 7.750 J (plus 7.688 J in the earlier probe root), mid
  gross 38.060 J, NEG-8 idle bracket 38.521 J. The acid test passed: the
  short cell reads ~7.3–7.8 J with an honest envelope where the defective
  corpus recorded 0.274 J, while correctly REMAINING cadence-ineligible.
  Sealed-corpus coherence: the defective-era mid reduction (24.07 J) had an
  admissible corrected range reaching ~37.7 J; the live repaired measurement
  landed at 38.06 J, and an independent recomputation of a sealed recal5 mid
  cell gave 38.51 J.
- **Instrument refuses honestly:** at the head where the tail gate was first
  reachable, the mid cell's 46.1 ms post-window tail could not support the
  ~71.0 ms composed requirement (B_bundle + B_fiducial + span) and the
  reducer refused `post_window_trace_tail_shorter_than_anchor_bound` rather
  than licensing the claim; a clean-room recompute confirmed the gate flips
  exactly at the composed bound, erring toward refusal. At later heads the
  strict calibration gates (protocol-v2-only + freshness horizon) fire
  first on these pre-head probe artifacts — every layer fails closed
  (collection policy now enforces a 1.0 s post-window dwell so future cells
  cannot hit the tail case). The unbound first probe root correctly refused
  `instrument_calibration_missing`.

## Convergence loop (2026-07-20 → 21)

Round shape: fresh Sol xhigh whole-instrument adversarial audit + Fable
clean-room physics recomputers + Sol high contract/execution sweeps;
P0/P1 findings refuted by two distinct lenses; Sol fix rounds under binding
lead rulings; mandatory delta re-audit of every fix round; sign-off only when
a full confirmation round confirms zero P0/P1.

- **Round 1** (2026-07-20, checkpointed): fixes lead-committed as `ca6861b`.
- **Rounds 2–3** (overnight): ~160 agents; 27 confirmed P0/P1 fixed —
  headline items: additive causal-bound composition minted as reducer
  0.5.2 / AXI 0.6.2 (0.5.0/0.6.0/0.5.1/0.6.1 byte-frozen replay arms),
  calibration physics re-derivation at claim time, whole-window
  attempt-ledger validation, environment-admission closed vocabulary,
  cooldown physics rederivation, derived-output clobber guards, fail-closed
  rollover gate. Landed as `5093355` (suite 2003 passed / 0 failures).
- **Confirmation round 1** over `5093355`: correctly WITHHELD sign-off — 8
  confirmed findings, headline **P0: the claim envelope modeled one common
  trace shift while the calibration measures independent start/stop edge
  lags** (omits up to 2·P·B_fiducial; NEG-8 demo: attainable 38.831 J vs
  licensed 38.574 J). Fixed under lead rulings as the **corner-composed
  two-edge envelope** (exact by per-edge monotonicity; corners at
  ±(B_fiducial + wall-minus-monotonic span), common shift scanned
  breakpoint-exact per corner), plus: negative-power refusal, 24 h
  calibration validity horizon (`instrument_calibration_stale`), claim-time
  custody-manifest verification, environment-admission full-object
  fail-closed including the post-run observation, universal 1.0 s dwell
  floor, declared NEG-8 role provenance, runtime-observed
  binding_observations.
- **Delta re-audits caught real fix-round defects every time they ran** (the
  standing doctrine held): a lost early-return changing frozen replay
  semantics (round 2), and in the confirmation-fix wave a frozen-arm replay
  purity break (custody/protocol-sha checks firing on 0.5.1/0.6.1 — one
  direction admission-widening) plus the idle-subtracted envelope
  under-coverage (duration varies under independent edges) — the latter two
  found by the delta agent, the corner-span omission found by the lead's own
  diff review. All bench-fixed with defect-shaped regressions. Landed as
  `233e9e3` (suite 2027 passed / 0 failures).
- **Confirmation round 2** over `233e9e3`: withheld sign-off with 9 confirmed
  findings — but the character shifted decisively: the physics verified clean
  from every lens (clean-room recompute, dense attainable-set scans,
  sealed/live coherence), and every finding is provenance/governance:
  headline **P0: the declared calibration capture time was never
  authenticated against the raw event bytes**, so a stale calibration could
  be relabeled fresh and defeat the 24 h horizon. Fixed in the round-3 wave
  under the third D-078 amendment (capture-time authentication ±1 s against
  hash-verified events; horizon binding the measured-window end; generic
  version-coherence validation; structured CLI refusals; whole-window
  verdict re-derivation + NEG-8 duplicate rejection; protocol shape
  authentication; attempt-window timing semantics).
- **Confirmation round 3** over `0925480`: withheld sign-off with 7 confirmed
  — and the frontier moved up a layer again: the physics lens explicitly
  recorded "the instrument CAN take a defensible measurement on a fresh head
  collection"; all four P0s sit in the CLAIM-AGGREGATION layer (floor
  statistics used a max-width shortcut instead of exact linear-corner
  widening over member envelopes; admission evidence was not causally bound
  to its measured window; the whole-window verifier trusted stored
  CPU/adapter labels; NEG-8 references were read from stored summaries
  rather than re-reduced from primary evidence). Fixed in the round-4 wave
  under the fourth D-078 amendment addendum (exact corner widening; 600 s
  causal admission gap; primary-evidence re-derivation throughout;
  frozen-golden checksum pins).

Decision-log record: four 2026-07-21 D-078 amendments/addenda (identity bump
+ vocabulary registrations; two-edge envelope + horizon/custody/dwell
rulings; provenance authentication; claim-aggregation rulings).

## Consequences for the measurement program

- Quote **27.4 ms** (never 24.0) as the instrument emission-lag bound.
- Effective per-window anchor bound = B_bundle + B_fiducial + span
  (additive; disjoint causal links). Live request-level bounds land around
  68–86 ms; quarter-window claim gating therefore keeps short (~130 ms)
  phase windows ineligible — request-level and longer windows are the
  claim-bearing surface, as designed.
- The 24 h calibration validity horizon means **Window-A re-collection needs
  a fresh [QUIET-MAC] pulse calibration** (chain staged; ping Ed first).
- Live probe summaries were minted pre-fix; envelopes must be re-quoted from
  a final-head re-reduction before any claim-adjacent use (the probe roots
  are probe-labeled and non-claim-bearing regardless).
- Salvage of the 288-bundle corpus remains a separate Ed ruling under D-078;
  DF-TELEM unchanged.

## State at writing

Branch pushed at `233e9e3`; PR opens after confirmation-round sign-off.
Remaining after sign-off: PR per the operation-loop gate shape →
RUN_STATE/PROJECT_STATUS/DRIFT refresh → then Phase 1 re-collection per the
roadmap (fresh calibration first).
