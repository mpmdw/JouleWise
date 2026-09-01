# Magistrate ruling — D-165 close-out artifact ownership (2026-09-01)

Input: `06-ratio-closeout-scout.md` (Sol xhigh, read-only), which established
that (1) the ordinary ratio operands already exist in every minted
`joulewise.detection_floor_artifact.v2` cell (`corner_widened_unguarded_floor_j`
as numerator; the point floor reconstructible as
`max(max_abs_residual_j | max_abs_delta_j, prediction_component_j)`,
`joulewise/detection_floor.py:787`), (2) no issued artifact preserves the
per-block shared/local width split that R_cm needs — extraction sums them at
`joulewise/floor_extraction.py:460` and the mint discards the private records
at `joulewise/floor_mint_estimator.py:465`, and (3) the frozen 109-key
renderer cannot carry the 126-key `_v5` registry; the successor renderer is
required.

## Ruling (to be logged as D-168 once the D-167 kernel PR merges, to avoid a
decision-log collision)

1. **Ownership: sidecar.** `joulewise.detection_floor_artifact.v2` is not
   changed. The mint emits a separately hash-bound
   `joulewise.d165_dominance_replay.v1` sidecar carrying, per comparative
   cell, the authenticated shared-edge bound, every block's raw replay
   inputs, each derived `shared_width_j` / `local_width_j`, and the replayed
   point floor, common-mode corner floor, ratio, and pass flag; per cell and
   component, the independent ratio record. Reason: smallest collision
   surface; the floor artifact keeps its present meaning; finalization
   (`joulewise/analysis_manifest_v3.py:3624`) remains outcome-blind because
   the close-out artifact binds the finalized manifest, the floor artifact,
   and the sidecar by hash instead of finalization reading outcomes.
2. **Close-out artifact** `joulewise.d165_dominance_closeout.v1`: exactly
   eight ordinary ratios (2 components × 4 cells) and four comparative R_cm
   values; global fields `all_independent_pass`,
   `all_required_common_mode_pass`, `branch` (A/B), `dominance_sentence_licensed`,
   `subtitle_licensed`, `refusal_reason`. Any missing, unauthenticated, or
   zero-denominator result selects neither branch and stops filling.
3. **The predicate has one home.** `dominance_ratio`,
   `split_common_mode_block_width`, and `replay_common_mode_dominance` move to
   `joulewise/dominance_closeout.py`; the `_v5` generator imports them so the
   registration and the production path cannot drift (terra's 20-vs-16 cap
   finding is the drift this prevents).
4. **Order of work:** core + close-out builder (now) → sidecar emission in
   the mint (next) → successor renderer (after the G2-a selection record, per
   the RENDERER-V5-SUCCESSOR-01 note) → end-to-end fixture-backed replay.
   Each stream: exhaustive `WRITE_SCOPE`, refuter with a distinct lens, delta
   re-audit of fix rounds.
5. `RENDERER-V5-SUCCESSOR-01` and the close-out rows are registered in the
   kernel by the D-167 follow-up, not by the implementers.
