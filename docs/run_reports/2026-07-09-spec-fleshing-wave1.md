# Run Report — Spec-Fleshing Wave 1 (2026-07-09, C-024)

**Primary deliverable (user ask):** start the post-review planning/build
phase — flesh out specs and plans for the suite's no-hardware pieces, with
5.5 implementing under lead orchestration, so hardware plugs in at the end.
**SHIPPED (wave 1 of the C-023 work order):** PRs #29..#32 merged on green
CI; suite 822 OK (lead-run) on merged main `f75134d`; integration fixes
landed on main after review.

## What landed

- **PR #29 (D-053)**: contrast-level statistical inference replaces
  interval separation; three-way `not resolvable` / `unresolved` /
  predeclared-equivalence rule; analysis registry with enumerated
  contrast_id freeze and multiplicity fields; AP-1..AP-6 amended.
- **PR #30 (D-052)**: `docs/contracts/capstone_scope.md` — frozen umbrella
  headline, per-result ceilings, three-rung contribution ladder (encodes
  Ed's filled-matrix novelty position with auditability as the warrant),
  MVC stop-lines deferring to R-012, single-unit caption templates,
  consumer/decision table.
- **PR #31 (D-054)**: `docs/phase_2/detection_floor.md` — P2-015 design
  (queue rank 0 CLOSED): false-effect guard floor (replaced the
  percentile-UCB after counterreview proved it unidentifiable at n=10),
  per-backend error budgets with unknown-term claim-ceiling policy,
  campaign economics (180-340 total bundles incl. Window-B, 2.4-11.3 h; 170 is the Window-A request/phase subset), uncertainty-propagation
  spec for P2-029, telemetry-trust hierarchy, pre-registered wall/USB-C PD
  bridge-model runbooks.
- **PR #32 (D-055)**: `docs/research_question_registry.md` — canonical live
  index, 75 rows, aliases normalized, 7 C-023 coverage-gap candidates.
- **Integration fixes on main** (post-merge review, 5 findings, 0
  blockers): three-way rule alignment in the scope contract, telemetry
  equivalence-gate wording, registry-ownership note in the floor doc,
  PROJECT_STATUS pointers.
- **Lakebed feedback log** (`site_capsule/LAKEBED_FEEDBACK.md`): standing
  alpha-feedback rule + backfilled and same-day field reports (Ed's
  directive).

## Verification

- CI green on all four PRs (py3.11 + py3.14); lead-run suite on merged
  main: `Ran 822 tests, OK (skipped=10)`.
- Docs-only series; no runtime surface beyond the suite. Integration
  reviewer independently re-ran the suite and recomputed the floor-doc
  campaign arithmetic.

## Process trace appendix

**Shape:** 4 worktree streams (disjoint footprints pinned in prompts),
lead-driven codex-run pipelines; per stream: implement → fresh counterreview
lens → FIX-N round → lead gate → fresh final-head pass → tail-verification
pass over post-review commits → CI → merge; then one integration review.
No Opus orchestrators (C-010 default held).

**Catches by layer (unique):** counterreview lenses — R1 scope
ladder-consistency blockers (2), R2 estimator kill (percentile-UCB
unidentifiable at n=10; the session's decisive catch) + bridge-model fix,
R3 D-014/D-037 wording conflict + gameable freeze, R4 missing
content-sentinel row + C5-W.3 un-merge (overrode the original C-023 lens's
duplicate call with bank citations); final-head passes — stale
ledger-promotion blocker on the rejected estimator (would have promoted the
wrong rule to the decision log), ABBA economics ambiguity (40 vs 80
bundles), 3 wording/ID defects; tail verification — 1 residual unqualified
L1 sentence; integration review — 5 cross-stream seam drifts (S1/S2 were
written against pre-S3 contract text). Zero-yield layers: none.

**Interventions:** one launch failure (zsh parse error on a 4-prompt
for-loop — relaunched as separate codex-run calls; instant-completion
diagnostic worked as documented).

**Delegation calibration (schema v2):**

| id | to | unit | altitude | outcome | catches vs it | lead rework |
|---|---|---|---|---|---|---|
| S1 | 5.5 | scope contract | design-freedom | accepted after 7-finding fix round | R1 2 blockers | 1-line tail edit |
| S2 | 5.5 | floor design doc | design-freedom | accepted after 7-finding fix round | R2 estimator blocker | none |
| S3 | 5.5 | stats/registry amendment | design-freedom | accepted after 7-finding fix round; FH CLEAN | R3 2 blockers | none |
| S4 | 5.5 | RQ registry | pinned-spec | accepted after 3-finding fix round | R4 1 blocker | none |
| F1-F6 | 5.5 | fix rounds | pinned FIX-N | 6/6 one-shot clean | — | none |

Design-freedom delegation ran hot again (S2's estimator was wrong but the
counterreview layer caught it — the pipeline, not the prompt, is the
quality mechanism). FIX-N one-shot record now 13/13 across sessions.

**Cadence amendment (Ed, mid-session):** per-artifact commit+push; stream
branches push at every pipeline checkpoint. Folded into the operation-loop
skill same-session. Trigger: a parallel agent missed a just-created file.

**Yield/spend (rough):** ~20 codex sessions (4 impl, 4 lenses, 6 fix
rounds incl. integration, 4 final-head, 1 tail verification, 1 integration
review) ≈ 2.5M codex tokens; all four C-023 blockers (B1-B4) now have
landed artifacts.

## Next actions

1. Wave 2 per queue ranks 0a-0d: P2-029 uncertainty propagation (code),
   P2-030 ordering executability (pre-campaign blocker), P2-031
   token-normalization contract, P2-032 campaign packs.
2. Quiet Window A unchanged: C-019 shakedown → P2-015 floors (now per the
   merged false-effect guard design) → P2-006.
3. Ed: Lakebed redeploy when convenient (site regen committed;
   `cd site_capsule && npx lakebed deploy`).
