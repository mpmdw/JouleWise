# Run report — suite-science hardening + benchmark expansion (2026-07-08)

**Deliverable check (Ed's session ask, restated):** harden the science the
prompt/workload suite can answer; decide and begin what to build next;
expand toward multi-prompt/difficulty/type suites and benchmark interop.
SHIPPED: the science-hardening contract stack, the expansion design, the
Window-A capture + sentinel code, and the cross-checked implementation
research for the suite itself. NOT YET SHIPPED: the suite implementation
(P2-010a/P2-012/P2-020 code) — build lane reopened by D-042; the handoff is
`docs/phase_2/suite_implementation_research.md` (adjudicate its amendments
first). Mid-session, Ed had to point out the suite itself wasn't being
built — recorded as a process lesson (skill-usage log).

## Product outcomes (all merged to main, HEAD `fcd111a`)

- **PR #14 (suite-science-hardening, 4 commits, merged `5c19099`):**
  - `docs/contracts/analysis_plans.md` (D-038): pre-registered analysis
    plans binding L2/L3 claims; AP-1..AP-6 seeded; MDE arithmetic
    (`MDE95 ~= 1.46xCV`, 80%-power `~2.0xCV` t-based); pseudo-replication
    rule; floor gate `max(floor_abs, floor_cmp)`.
  - Program v2 (D-039): `q4_l3_shape_grid_v1` (4x3 + interpolation/
    extrapolation holdouts — the only current path to L3), P2-015 expanded
    to per-metric/window-class floors + comparative MDE, jw_mixed
    common-shape stratum + 3-phase sequencing, P2-010a/b split,
    two-quiet-window plan, Phase 4 figures F9-F12.
  - Suite architecture v2 + interop (C-015, D-040/D-041): one generic
    suite mechanism (B×k bundles, r_within=1, per-item status model,
    difficulty as quarantined metadata); `benchmark_import` manifest
    (HumanEval smoke first, FLORES second); marker-shim energy layer
    (contract in `adapter_contracts.md`; P2-022 verdict-shaped spike);
    kill list; capability map by claim ceiling (bank).
  - `docs/phase_2/suite_implementation_research.md`: 4 cross-checked
    research reports (execution architecture, category generators,
    affine ladder, licensing) — amendments unresolved by design.
  - D-042: owner directive reopens the suite BUILD lane pre-2M; campaign
    execution ordering unchanged.
  - Queue: P2-019..P2-024 added; P2-010/012/015/016/020 amended.
- **PR #15 (p2-021-drift-sentinels, merged `8765ee1`):** P2-021 DONE —
  `short_short_sentinel` at each model-block boundary (self-identifying
  tags), block/position covariates in the order manifest + campaign-log
  echo, fail-loud on sentinel-less blocks. Suite 602.
- **PR #16 (window-a-capture, merged `fcd111a`):** the C-015/R2
  collect-before-Window-A set: per-run env snapshots at prepare-end
  (+2s settle; failure_fallback scope for early failures), cooldown-gate
  trace preservation, signed inter-run gaps + `clock_step_suspect`,
  `tokenize`/`generation_setup` phase markers, MLX memory snapshots
  (prepare_end/cleanup_start), powermetrics sampler metadata,
  connected-display semantics via system_profiler (framebuffer pipes
  separated). Suite 611.
- Councils C-014 + C-015 (full entries); decisions D-038..D-042.
- Global: skill-usage logging started (`~/.claude/skills/skill-usage-log.md`,
  Ed's standing instruction; memory entry added).

## Verification evidence

- Merged main (fcd111a): `python3 -m unittest discover -s tests` → 617 OK
  (skipped=10), lead-run post-merge (PR heads were 602/611 standalone;
  the merge union adds the cross-stream tests).
- Live lead gates on the capture head (real MLX 1.5B + mock telemetry,
  `.venv` python): strict-valid bundles at both 740c32c and db54cc2;
  no run_end snapshot (blocker fix live-proven); all 4 phases paired and
  honestly `not_resolvable` at sub-sample durations; prepare_end snapshot
  871MB active; display 1 built-in/0 external with pipes 5/4 separated;
  clock probe correct on host (`timed_running: true`).
- 6/6 real corpus bundles strict-valid under the new code (run twice:
  pre- and post-fix rounds).
- CI green both matrix legs on every PR final head.
- Review stack: C-014 (scout + 3 lenses + peer), C-015 (2 reach + 2
  design lenses + peer), pre-commit docs-verify workflow (1 blocker +
  6 should-fixes), stream reviews (S: 7 should-fixes; C: 1 BLOCKER —
  in-window run_end snapshot — + 8 should-fixes), pre-merge oversight
  (3 reviewers + refuters; AP-4 self-contradiction caught), final-head
  passes on every post-review commit (3 wording fixes on #14; #16 clear).
- Post-merge integration review: launched post-fcd111a; its findings and
  the stale-line bookkeeping fixes land in the checkpoint commit
  (see RUN_STATE for outcome).

## Restart instructions (next agent)

1. Read RUN_STATE, then this report, then
   `docs/phase_2/suite_implementation_research.md`.
2. **Suite build (D-042, [AGENT], unblocked):** adjudicate the four
   reports' cross-check amendments (recorded dispositions), then
   implement P2-010a substrate → P2-010b smoke ladder → P2-012 phase-1
   generators + P2-020 sentinel content, per the execution-architecture
   report. Full review tier (measurement-semantics).
3. **Quiet Window A ([QUIET-MAC], next machine-quiet opportunity):**
   P2-015 expanded floors (incl. lead-run tasks-sampler + settle smoke)
   then P2-006 2M with drift sentinels. Corpus now carries covariates.
4. Window B (P2-019 q4 grid + P2-020 campaign) sized from Window A.

## Process trace appendix

- **Shape:** 1 design stream → re-decomposed to 3 (L docs / C capture /
  S sentinels) on Ed's worktree directive; ultracode → 6 Workflow runs
  (2 stream reviews, docs-verify, oversight, suite research, +
  final-head codex passes) over ~60 workflow agents + ~25 codex-run
  sessions. Tiers: full pipeline for capture (measurement semantics) and
  all contract docs; standard for sentinels.
- **Catches (unique, by layer):** lead pre-lens audit 4 (incl. Q4-at-L3
  gap); scout 4; C-014 lenses 16; C-014 peer overturned 2 lead designs
  (4x3 grid, two windows); C-015 peer 1 unique (per-item failure
  economics); docs-verify 7 (incl. 1 blocker: 2O self-contradiction);
  stream-S review 7; stream-C review 9 (incl. THE blocker: run_end
  snapshot inside the measured window — all 3 code lenses independently,
  refuters confirmed with line chains); oversight 8 (incl. AP-4
  equivalence self-contradiction, display pipe-counting via live DUT
  repro); final-head passes 3; lead diff/live gates 4 (C-014 impl 2,
  deprecation fix, venv/runtime_unavailable diagnosis).
- **Deliberations:** P2-010 split (consensus), jw_mixed phasing
  (supersedes C-005 sequencing, consensus), window packing (peer
  OVERTURNED lead single-window — position reversal), Q4 grid (peer
  AMENDED 3x3→4x3 — position reversal), D-042 gate reopening (owner
  directive, recorded not re-decided).
- **Interventions:** zero wake stalls across all codex-runs/workflows.
  Worktree-commit sandbox block hit 2x (lead commits at gate — skill
  fold staged). Ed interventions: worktrees directive; ultracode;
  skill-usage logging; hold-skill-folds-for-full-evidence; the
  object-level suite catch (the session's most important correction).
- **Delegation calibration (schema v2):**

| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| scout-1 | codex | review packet | pinned-spec | good | 4 unique | none |
| lenses x9 | codex | design/reach/review | design-freedom | good-excellent | 40+ unique | none |
| peers x2 | codex | counterreview | judgment-invited | excellent | 2 overturns + 1 unique | none |
| impl-docs x2 | codex | doc batches | pinned-spec | good | — | 2 inline gate fixes |
| impl-code x2 | codex | streams C/S | pinned+design | good; review layers caught 1 blocker + 15 SF | — | 1 deprecation fix |
| fix rounds x5 | codex | pinned fixes | pinned-spec | clean one-shot each | — | none |
| workflows x6 | workflow(codex) | review/research fan-outs | pinned-spec | high precision (~2 refuted / ~30 confirmed) | — | none |
| research x4 | 2 codex + 2 claude(web) | suite research | design-freedom | sound-with-amendments x4 | 37 amendments self-caught | none |

- **Yield/spend:** ~2.3M workflow-agent tokens + ~25 codex sessions.
  Pre-merge catches that would have been expensive post-2M: the
  sacred-window blocker (would have contaminated the entire 2M corpus),
  the AP-4 unfalsifiable-null (would have poisoned pre-registration),
  dead probes (silent evidence loss on every Window-A bundle).
- **Skill-usage:** full entry + staged folds in
  `~/.claude/skills/skill-usage-log.md` (folds applied at session close
  per Ed's full-evidence hold).


## Addendum — post-large-workload meta-reassessment (same day, C-016)

Run after all merges as the session's final step (now standing per
operation-loop §10 / Ed's directive). Shape: 4 parallel analysts over the
full council log, decision log, and skill stack + a cold-start
derivability audit + a completeness critic; then a pre-commit docs-verify
pass over its own batch (5 should-fixes caught, two by D-043's self-test).
Landed: D-043 supersession-closure discipline + back-annotations
(ef37128), scripts/codex-run committed, orchestration.md refreshed with
the clean-machine reconstruction pointer map, playbook/CLAUDE.md routing
fixes, 5 skill-stack divergences fixed, codex-delegation structurally
rewritten (procedure-first), §10 standing trigger encoded. Full analyst
outputs: session scratchpad + `~/.claude/skills/skill-usage-log.md` entry.
