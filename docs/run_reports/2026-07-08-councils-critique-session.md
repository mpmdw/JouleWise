# Run Report — 2026-07-08: Site Redesign + Twin Councils + Critique Counter-Review (C-011)

Continuation of the resume+merge session (same conversation, Ed-directed
second phase). Three deliverables: (1) the docs/site rebuilt as a
designed reading experience; (2) a consensus council over that site;
(3) a full counter-review of an independent 5.5 critique of the project,
adjudicated in council C-011 and implemented same-session as PR #12
(MERGED).

## Product outcomes

- **docs/site redesigned** (5cdc9b4): four hand-authored pages
  (story/results/process/research) in a dark instrument aesthetic —
  embedded Fraunces/IBM Plex (self-contained), palette validated by the
  dataviz six-checks, animated power-trace hero, readout tiles,
  catch-record and topology-evolution visuals — plus the 11-doc library
  restyled; `scripts/build_site.py` now generates only the library.
  Claims fidelity gated twice: a fresh 5.5 review (11 findings) then a
  council discussion round (FULL consensus; 3 additional findings from
  the discussion itself). Every number traces to a named source.
- **C-011 (PR #12, MERGED @ bef8ab6):** the independent critique
  (`docs/project_critique_review.html`, now committed) was
  counter-reviewed by 4 verification lenses, adjudicated with 5.5-high
  (6 contested points, consensus on all, zero dissent), and its
  survivors implemented top-down:
  - **Fail-closed campaigns** — per-member strict validation after
    every run and before every skip; usable = succeeded + strict-valid
    + quality-pass + unwaived; typed exact-match waivers with a CLOSED
    scope-class set, fail-closed duplicates, manifest-level only (never
    in bundles); end-of-campaign verdict
    (publishable|partial|blocked|invalid).
  - **Counterbalanced 2M ordering** — model-blocked, workload-rotated
    order manifests (rotation + seeded rep-5 + recorded imbalance),
    consumed by the runner with executed-order logging; loud warning on
    fallback-sorted (D-014).
  - **Reducer honesty flags** (additive) — `phase_identifiability`
    (≥3 summed-curve samples per nonzero interval, else
    `not_resolvable_sample_count`) and `token_counts_source`
    (config-fallback nulls token-derived metrics; only decode/output
    token events count as runtime-observed). Era-gated into strict: new
    -era summaries must carry both fields.
  - **Claims ladder** — `docs/contracts/claims_ladder.md` (L0–L4,
    binding from 2M; D-037) + Phase 4 §4.3 acceptance hook; riders:
    cross-boundary comparisons descriptive-only without a named
    calibration bundle; config-fallback token denominators force L0
    wording.
  - **Docs** — flagship-report ADDENDUM superseding the
    active-parameter wording (record untouched; immutability); question
    -bank softening; stale-line batch; R-002/R-003 → closed-residual;
    PROJECT_STATUS Process Note re-anchored (middle path honoring Ed's
    showcase instruction — the one partial deviation from the critique,
    recorded in C-011).
  - **Queue** — P2-015 detection-floor calibration campaign at rank 1
    (same quiet window as 2M, runs first); P2-006 acceptance extended
    (fail-closed runner + order manifest + ladder wording); P2-016
    deferred batch (post-2M architecture, 2K-live telemetry/protocol
    items, claims-index seed) with rejected items recorded
    (RemoteNodeSession per B-1; run-ID randomization per D-010/D-022;
    console script pre-2M).

## Verification evidence (lead-side)

- Merged main @ bef8ab6: suite **564 OK (skipped=10)**; 6/6 real
  bundles strict-valid (spot-checked post-merge); CR fix round included
  a numeric identity check (stored vs fresh energy/ttft/throughput
  exactly equal on a legacy bundle after the decode-event filter).
- Site preview-verified in a live browser (fonts, charts, hover, doc
  pages); palette passed the dataviz validator on the dark surface.
- CI green on every PR #12 head.

## Review-pipeline yield (this phase)

| Layer | Unique catches |
|---|---|
| Site claims review (5.5) | 27-defects-vs-31-pins conflation ×2; sourcing overclaims; MVO floor drop; 6 more |
| Site council discussion | precision-card 87-vs-99.19 workload collision; summary-scoped trust wording; catch-table taxonomy — 3 findings its own source review missed |
| Critique verification lenses ×4 | fail-closed cluster CONFIRMED with line cites; reducer config-token denominator (sharper than the critique); flagship overclaim survival; 2 settled-rejections (D-010/D-022, B-1) |
| Adjudication discussion (5.5-high) | C5 tightened to the exact ≥3-sample rule; C6 tightened to the concrete counterbalance scheme |
| Branch 2-lens review | waiver cross-namespace leak (BLOCKER); era-tolerance shielding the new honesty fields (BLOCKER, convergent); prompt-tokens-as-output-provenance (BLOCKER) |
| Lead gate | worktree-predates-designed-site rebase collision caught before PR |
| Final-head review | waiver scope not validated against a closed set; verified era-gate safe on no-phase bundles + decode-filter numerics + no site clobber |

## Process notes

- **Adjudicated specs still need the lens tier:** CR-1 implemented a
  council-pinned design and shipped 3 blocker-class defects only the
  adversarial round caught — one of them an interaction with the lead's
  own earlier design (the era tolerance). Consensus ≠ safe
  implementation.
- **Deliberation has independent yield:** both discussion rounds
  produced findings/designs beyond what they were adjudicating (site: 3
  new findings; critique: 2 mechanical rules). Folded into C-011's
  process note.
- **Final-head rule boundary (lead ruling, this session):** a commit
  that implements the final-head reviewer's own specified fix, written
  by the lead and verified by the suite, stays within the reviewed
  envelope — no infinite recursion. New functionality post-review still
  triggers the rule.
- The one knowing deviation from the critique (process-section
  compression declined in part) rests on Ed's explicit instruction;
  residual tension is his call.

## What is next

Unchanged from the queue: **P2-015 detection-floor calibration then
P2-006 2M baselines in one quiet window** (no-agent lock; fail-closed
runner; order manifest; ladder wording). Then P2-010/P2-012, 3.0.2
(R-003 approval), hardware-gated items.

## Workspace state

- main @ bef8ab6 + this bookkeeping, pushed. Worktree `../jw-critique`
  removed post-report (PR #12 merged). No worktrees remain.
- Session scratchpad lens/council out-files are ephemeral; all
  load-bearing content lives in C-011, the CR ledger
  (`docs/stream_logs/2026-07-08-critique-response.md`), and this report.

## Addendum — 2026-07-08 Second-Pass Critique Reassessment

- A second-pass reassessment was added to `docs/project_critique_review.html`
  after the critique-response work. The second pass updated several first-pass
  passages in place and marks them in-document; the verbatim C-011 first-pass
  text remains in git history at commit 6418084.
- Lead fact-check verified 16/17 checkable claims against file evidence; the
  one stale claim was the risk-register row wording, now annotated because
  R-002/R-003 are closed-residual as of 2026-07-08.
- A counterreview flagged the preservation overclaim as a blocker; the lead
  chose accurate labeling over content revert to keep reader-facing numbers
  current, with git as the verbatim record.
- A follow-up fix pass added layering annotations, hardened the reassessment
  wording against repo evidence, and recorded this addendum-only process
  footprint; the process-doc entries themselves are addendum-only.
- Session-end: consistency sweep (Opus) found one real drift (phase-2 exit
  checklist test count, fixed); the final-gate 5.5 review's unique catch was
  the `build_site.py` provenance stamp mislabeling dirty-tree regens with the
  prior commit hash — queued as P2-017; this session adopted the interim
  sources-first/site-second two-commit pattern. Session learnings encoded in
  the global codex-delegation and adversarial-review skills (history-vs-live
  refinement for living reader-facing docs; self-provenance lens for
  self-edited review artifacts; codex-run `.status` naming).
