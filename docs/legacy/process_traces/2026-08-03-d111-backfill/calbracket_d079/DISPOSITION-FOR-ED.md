# CAL-BRACKET-D079-01 disposition — F1 confirmed, F2 magistrate-ratified, F3 → Ed (2026-08-03)

The fix round closed the first audit's three Decimal/freshness/auth
blockers cleanly (exact ceiling passes, rekey refuses, legacy hash
unchanged, suite 2433 OK), but the DELTA re-audit found three MORE, all
in the freshness/provenance domain — and estimator-digest incompleteness
was a REPEAT signature. Per the escalation trigger (consult, not blind
round three) a read-only Sol xhigh design consult ran; it resolves each
against D-102's actual text (full report: design-consult.md, this dir).

## F1 — freshness identity vs T1 selection — CONFIRMED (D-102-determined, no ruling needed)
D-102 clause 2 binds freshness to the SIX-field epoch {os_build,
hardware_model, power_policy, sampling_interval_ms, estimator_revision,
pulse_protocol_id}; its "new same-identity calibration expanding the
range" trigger uses THAT epoch. Full T1 (which adds mlx_version, anchor
method, protocol digest, etc.) governs SELECTION only. The fix conflated
them, so a same-epoch/different-mlx_version range-expander escaped the
freshness trigger. Fix = two named candidate sets (same_epoch for
triggers; t1_selectable for selection). Sub-bug also caught: member
comparison is basename-only (:658-677) — unsound; use content identity
(member_id, manifest_sha256, evidence_sha256, b_fiducial lexeme).

## F2 — estimator byte-digest module set — MAGISTRATE-RATIFIED
D-102 mandates "estimator byte change" as a trigger but does not
enumerate modules. The consult traced the b_fiducial_s dependency graph
to an exact FOUR-module closure with call-path evidence:
  joulewise/powermetrics_fiducial.py  (pulse detect + trace-anchor add + physics reverify)
  joulewise/uncertainty_evidence.py   (derive_powermetrics_anchor_v2 → effective_clock_anchor_bound_s)
  joulewise/adapters/powermetrics.py  (parse raw plist → interval endpoints/powers; anchor projection)
  joulewise/reduce.py                 (member auth/rederive; anchor-envelope re-reduction; bound compose)
OUT (with reasons): calibration_bracketing.py (policy, not physics),
whole_window.py (orchestration), protocol JSON (bound separately via
protocol_sha256), capture scripts (author-time, not claim-time),
generic helpers (clock/validation/bundle_read — would need a broad
dependency-lock policy D-102 did not adopt). RATIFIED as the estimator
bundle (this is implementation fidelity to D-102's "estimator byte
change", backed by the dependency graph — within magistrate authority).
The fix binds all four as estimator_code_sha256, one-byte change to each
independently stales, artifact regenerates its derivation digest + outer
pin.

## F3 — cross-root trigger observability — ESCALATED TO ED (decision-level)
D-102 clause 2 makes the triggers MANDATORY ("a new same-identity
expander", "corpus doubling 19→38", "a new systematic failure") but
defines NO authoritative universe, observation scope, registry, or
completeness proof — and NONE exists in the code. Current discovery
scans only the evaluated window's runs_root, so a same-identity expander
(or doubling member, or systematic failure) in ANOTHER root is never
observed and the old artifact silently keeps licensing. The consult:
"a within-window-only pass is not defensible unless a new decision
explicitly declares that window root the complete authoritative universe
— that would NARROW D-102." So the two honest options are BOTH decisions
Ed must make (claim-soundness + material scope; rule 11):

  OPTION A — BUILD the authenticated calibration-observation registry:
  a versioned append-only registry of every protocol-v3 observation
  (valid + systematic-failure) binding epoch/T1/hashes/bound/disposition/
  sequence; the artifact pins observation_scope_id + baseline high-water;
  evaluation authenticates the snapshot, requires baseline ⊆ snapshot,
  judges the delta under the prior artifact, fails CLOSED on any
  unproven completeness. Sound and fail-closed WITHOUT a global scan, but
  new infrastructure: one registry artifact, an authenticator/reader,
  capture-workflow append discipline, a mandatory registry arg threaded
  through whole_window.py + run_campaign.py + the secondary verifier.

  OPTION B — NARROW D-102: declare a bounded authoritative universe
  (e.g. the pinned n=19 corpus + the single evaluated window root) the
  complete universe for freshness, recording the residual (a
  same-identity expander in an unscanned root would not stale) as an
  accepted limitation. Cheaper; weakens the freshness guarantee; must be
  a recorded D-102 amendment Ed signs.

Magistrate lean (non-binding): for a capstone on the current timeline,
OPTION B with the residual honestly recorded is likely proportionate —
the freshness guarantee's cross-root hole is theoretical for the fixed
pinned corpus, and a full registry subsystem is heavy for what it buys
here. But this is a claim-soundness call and it is Ed's.

## Sequencing (consult's critical path — why no partial fix round now)
F3 controls the artifact SCHEMA (observation_scope_id etc.) and the
production API (registry arg vs none). Landing F1+F2 now would regenerate
the artifact and rewire callers twice. So: HOLD the fix round; on Ed's F3
ruling, F1 + F2 + F3 land together in ONE round, ONE artifact
regeneration, one byte-pin rotation. FIX-3 option (a) byte-pin is
compatible with all three (legitimate re-derivation = reviewed repo
update: regenerate artifact → recompute derivation_sha256 → update
DEFAULT_ACCEPTANCE_BOUND_SHA256, fail-closed mid-update).

## State
Branch impl/cal-bracket-d079, fix-round-1 diff UNCOMMITTED in worktree
(held; delta found blockers). Nothing landed. Standing lead-gate
obligations still owed at eventual merge: bench corpus tests, archived
raw custody + ≥2 more member re-fits, real passed-corpus basis replay.
On Ed's F3 ruling this + F1/F2 become D-109.
