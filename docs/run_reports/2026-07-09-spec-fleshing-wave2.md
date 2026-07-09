# Run Report — Spec-Fleshing Wave 2, Ultracode (2026-07-09, C-025)

**Primary deliverable (user ask):** wave 2 of the no-hardware work order —
5.5 implements, lead orchestrates/specs, ultracode multi-agent
orchestration. **SHIPPED:** PRs #33..#38 merged on green CI; suite 877 OK
lead-run on main after integration fixes (875 at merge head `039c052`;
integration fixes added 2 linter tests).

## What landed

- **PR #33 / P2-029 (D-057)**: reducer/aggregator uncertainty propagation
  + claim gates per detection_floor §3 — uncertainty status, variance
  terms, deterministic bounds (drift-is-a-bound), claim_eligibility with
  stable machine reason codes; strict-validation additive compatibility;
  legacy + 6 real corpus bundles verified.
- **PR #34 / P2-030 (D-056)**: ordering executability — rotation policies
  (round-robin, Williams Latin square), controller-derived order_row,
  fail-closed strict verification of realized order + recomputed
  order_seed; MLX/mock parity; pinned manifests byte-identical; the
  C-023 pre-campaign blocker is closed.
- **PR #35 / P2-031 (D-058)**: token-normalization + stack-identity
  contract (11 fields, anti-silent-omission, all governed surfaces).
- **PR #36 / P2-032**: plug-in-day campaign packs (Q1–Q3 split suite with
  D-048/D-049 obligations, Q6 rail-vs-wall, C5-2.3 KV economics);
  quiet-machine step 0; live-verified KV numbers (14/56/224 MiB).
- **PR #37 / P2-033 (D-059)**: claims-lint v1, CI-wired; satisfies the
  broad-packs cut-line. First run caught a real registry defect.
- **PR #38 / RQ-ENERGY-VARIANCE**: candidate design sketch (Ed's variance
  question) — replay-decomposition protocol with statistically honest
  path-selection and censoring rules; named harness gaps G-RQVAR-*.
- **Integration fixes on main**: pack-mode README exemption
  (marker-gated AP enforcement), ordering-mechanisms operator note.

## Verification

- CI green on all six PRs (py3.11 + py3.14); lead-run suite after
  integration fixes: `Ran 877 tests, OK (skipped=10)`; repo lint
  `errors=0`.
- Lead gates (never delegated): p2029 mock e2e + strict + uncertainty
  field inspection on my shell; p2030 live rotation campaign bundles
  strict-validated with per-rep order rows/seeds; combined-ref merge of
  all six branches + full suite + lint + e2e BEFORE merging (C-022
  lesson, first deliberate use — zero conflicts, green).
- Integration review ran a live rotated campaign and confirmed the
  p2029×p2030 interaction clean; its 2 findings fixed same-session.

## Process trace appendix

**Shape:** first Workflow-tool orchestration (46 agents, ~1.87M tokens,
57 min: 4 codex implement streams → 2 stream-specific lenses each →
severity-tiered refuters killing 10/30 findings pre-triage) + 2
lead-driven reinforcement streams (S9 linter, S10 rqvar — launched on
Ed's "more agents" directive after a fleet-health check showed nothing
wedged) + per-stream FIX-N rounds + 6 fresh final-heads + combined tail
verification + integration review.

**Catches by layer (unique):** lenses — mutation-testing debut
(5 mutations proving test gaps in p2029), live kv-size number check
(p2032), quiet-machine runbook omission; refuters — 10 false findings
killed; final-heads — 2 live-path defects no earlier layer saw (MLX
`position` missing under rotation → rotated MLX bundles would have
failed strict validation on real hardware; linter false-negative
parsing regression FROM the prior fix round); integration review —
pack-mode README failure (first activation of pack mode against real
packs) + ordering-mechanism confusability. Zero-yield layers: none.

**Interventions:** (1) user-reported stall → outside-evidence fleet
check (ps/worktree mtimes/journal) showed healthy-slow, not wedged;
response was additive streams, not kills. (2) One zsh for-loop launch
failure (replaced with separate codex-run calls). (3) PROCESS DEFECT:
lead bookkeeping edits ran concurrently with a workspace-write codex fix
round in the same main tree; the fix round's cleanup reverted the
uncommitted bookkeeping (recovered same-session — content was
deterministic from the lead's in-context sources). Lesson folded: the
two-writers rule binds the lead too; bookkeeping waits for tree
quiescence, or commits before any concurrent round launches.

**Delegation calibration (schema v2):**

| id | to | unit | altitude | outcome | catches vs it | lead rework |
|---|---|---|---|---|---|---|
| p2029 | 5.5 wf | uncertainty code | pinned-spec | accepted; 8 findings + FH 1 | mutation-proven test gaps | none |
| p2030 | 5.5 wf | ordering code | design-freedom (ratified round) | accepted; 2 findings + FH blocker | MLX position | none |
| p2031 | 5.5 wf | contract | pinned-shape | accepted; 3 findings + FH 2 | — | 3-line lead edit |
| p2032 | 5.5 wf | packs | pinned-shape | accepted; 7 findings; FH CLEAN | — | 1 ledger line |
| S9 | 5.5 direct | linter | design-freedom | accepted; 11 findings + FH regression | false-negative regression | none |
| S10 | 5.5 direct | design sketch | design-freedom | accepted; 2 findings | — | none |
| FIX rounds ×9 | 5.5 | fix contracts | pinned FIX-N | 9/9 one-shot | — | none |
| INT fix | 5.5 | integration fixes | pinned | applied clean; cleanup step reverted concurrent lead edits | — | bookkeeping regen |

Design-round-first (Ed's directive, now operation-loop §4a default for
design-bearing streams): P2-030's memo→ratify→implement produced zero
design rework. Codex worktree commits remain sandbox-blocked
(index.lock) — workflow wrapper agents committed/pushed successfully;
direct codex-run streams need lead commits.

**Yield/spend (rough):** workflow 1.87M subagent tokens + ~14 direct
codex sessions ≈ 3M total; all four wave-2 queue items + 2 pulled-forward
items landed reviewed and merged.

## Next actions

1. Broad campaign packs (C5-I.* + post-floor shortlist) now UNBLOCKED by
   the linter — queue row P2-034.
2. RQ-ENERGY-VARIANCE promotion needs a council round + the G-RQVAR-*
   harness gaps (seed recording, forced-token replay) — queue row
   P2-035, post-floor.
3. Quiet Window A unchanged: C-019 shakedown → P2-015 floors → P2-006.
4. Watch: transient `test_node_worker` flake seen once in a worktree
   (passed on rerun and in CI); queue if it recurs.
