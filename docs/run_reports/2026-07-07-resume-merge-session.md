# Run Report — 2026-07-07/08: Resume + Merge Session (C-009 topology, first full run)

Resumed the four checkpointed streams under the C-009 consensus topology
(lead-driven codex-run pipelines, NO subagent orchestrators), completed
every stream's implementation + review pipeline, and landed the merge
series: **PRs #8 (P2-013+P2-014), #10 (DOC-007), #9 (Stage 3.0.1) are
MERGED** (in that order, each after a 3-reviewer pre-merge oversight
pass, lead triage, and 5.5 fixes per Ed's directive); **PR #11 (2K
NVIDIA) is open and integration-reviewed, awaiting Ed's merge.**

## Product outcomes

- **P2-013 COMPLETE (PR #8):** all 31 audit pins fixed and flipped
  (27 defects, 8 invariant-shaped commit groups); `--strict` gains the
  powermetrics raw-to-trace gate (A-10: adapter-owned semantic
  re-derivation from raw plist evidence) and a legacy-additive summary
  compare; all 6 real corpus bundles strict-valid read-only, unrewritten.
- **P2-014 COMPLETE (PR #8):** `summary_provenance` +
  `workload_provenance` (D-033 realized prompt token-id hash, domain
  `joulewise.prompt_token_ids.v1`; MLX provably hashes the exact
  generation input); strict enforces full provenance shape on new-era
  bundles. Decision log: D-032 (phase_energy_j GROSS-ONLY), D-033
  (prompt provenance), D-034 (2O ownership), and post-merge D-035
  (fresh-process replay isolation) + D-036 (measured verdicts) — the two
  ratified 3.0.1 promotions.
- **DOC-007 MERGED (PR #10)** with a merge-time reconciliation pass
  (fresh pass under the checkpoint's adjudicated dispositions; the
  original 26-item list was ephemeral — see Process learnings 4).
- **Stage 3.0.1 MERGED (PR #9), verdict `replay_supported`** —
  lead-re-verified live this session (tokens_identical true, cache
  +0.0182% vs prediction; evidence line + exit-checklist row committed).
  Phase 3's central technical risk is retired on current hardware.
- **2K NVIDIA stack COMPLETE, fixture-first (PR #11 open):** protocol
  v1, SSH transport, node worker, nvidia-smi + vLLM adapters, registry
  wiring, live-verification checklist (P1-006 evidence script). ALL
  protocol pins PROVISIONAL pending live hardware. 545 CI-safe tests on
  the branch (rebased onto post-integrity main).
- **codex-run T4 patch landed** (~/.local/bin/codex-run): out-dir
  mkdir -p + absolute paths; `--resume` forwards cwd (via cd, also
  scoping `--last`) and sandbox (`-c sandbox_mode=`); thin-output
  warning in `.status`.

## Verification evidence (all lead-side, live)

- Merged main @ `76f0a4b`: suite **462 OK (skipped=10, 0 expected
  failures)**; `validate-bundle --strict` green over the 6 real bundles.
- Fresh mock e2e (run twice at different gates): strict-valid bundle
  with full provenance blocks, hash domain verified field-for-field
  against A-11.
- 3.0.1 headline command re-run fresh: `tokens_identical: true`,
  `replay_supported`.
- PR #11 branch @ `c487f6b`: suite 545 OK; synthetic 2K bundle passes
  strict; raw-CSV timestamp re-derivation from bundle evidence alone
  verified under forced TZ (integration-review probe, now a regression
  test).
- CI green on every PR head (both matrix legs).

## Review-pipeline yield (what each layer uniquely caught)

| Layer | Unique catches |
|---|---|
| Codex STOP-and-report (impl) | K5 pin unsatisfiable as authored (lead corrected it: shlex round-trip) |
| Lead live gates | corpus strict failure invisible in-worktree (legacy-additive key-set drift, pre-existing on main); worktree-lacks-runs/ env trap |
| 3-lens counterreview A | MLX provenance hash ≠ realized generation input (BLOCKER); raw-to-trace gate metadata-key bypass (BLOCKER, 2 lenses convergent); 6 should-fixes |
| 3-lens counterreview B | ssh argv `--` placement wrong in a PINNED contract (B-33 supersedes B-14); pending-run-id remote collisions (B-34 supersedes B-15); B-5 alignment evidence discarded; 5 more |
| Writer≠reviewer test audits | D-033 shape under-enforcement; tz fix not pinned end-to-end; PID same-argv reuse gap; 1 tautology |
| Pre-merge oversight (3 reviewers) | full D-033 key shape gap (2 convergent); 3.0.1 checklist row stale vs authority rule; unevidenced "lead-reverified" claim; 2K count stale |
| Lead diff gate (post-rebase) | 5.5's volunteered vLLM provenance hashed FABRICATED token IDs under the v1 domain (model-defect; B-44 fix: node-realized IDs via /tokenize or structured absence) |
| Integration review | telemetry worker metadata (node_utc_offset_s) not persisted → raw re-derivation impossible (-28800s probe); RuntimeResult.metadata dropped by controller; checklist flag typo — all invisible to single-stream review |
| Rebase gate | S3 mutually-exclusive prompt sources broke 16 2K tests + example config (cross-stream contract interaction) |

## How to restart / what is next

1. **Ed merges [PR #11](https://github.com/mpmdw/JouleWise/pull/11)**
   (2K; merges clean — branch is rebased onto current main).
2. Remove worktrees `../jw-p2013`, `../jw-doc007`, `../jw-spike301`
   (done this session if you are reading this on main) and `../jw-2k`
   after #11 lands.
3. **P2-006: the 2M two-model baseline campaign** [QUIET-MAC] — now
   fully unblocked (P2-013/P2-014 done, corpus born under the fixed
   validator with prompt provenance). Requires the no-agent quiet lock
   (C-009 T5): stop all fleets/cadence/Codex load first.
4. Then P2-010 → P2-012 (Slice 2O, D-034), 3.0.2 llama.cpp spike
   (needs installs → R-003 user approval), and the hardware-gated items
   when devices arrive (2K live checklist is ready).

## Process Trace Appendix

### Shape
- Resumed 4 checkpointed streams under C-009 T1: ALL pipeline-shaped
  (designs pinned in ledgers) → lead-driven codex-run, no Opus
  orchestrators. Result: ZERO wake-gap stalls, zero heartbeats needed,
  the entire session ran on codex-run's exit-reinvokes-lead guarantee.
  This is the topology's first full-session validation.
- A: 4 codex sessions (D groups 5-7, E g7-ruling, F g8, G P2-014) +
  fix/amp/test-review rounds. B: U3/U4/U5 + fix/amp/test-review +
  post-rebase rounds. C: lead-only verification. D: one reconciliation
  round. Merge order A→D→C→B held.
- Ed's directives mid-session: PRs are Ed-merged (classifier upheld the
  standing rule when the lead attempted a self-merge from the checkpoint
  plan's "merge A" shorthand — correct outcome); then explicit "merge
  all 3 after thorough codex review, lead triages, 5.5 fixes" — done.

### Catches (beyond the yield table)
- codex-run status sentinel is `<stem>.status` not `<out>.md.status`
  (lead misprobe, once).
- Codex sandbox cannot git-commit in WORKTREES (.git outside sandbox
  root) → lead commits by pathspec; two split techniques validated
  (ledger truncate-restore; .split diff + apply --cached). → folded.
- Worktrees share tracked files only: real corpus/venvs live in the
  main tree; stream acceptance steps referencing them must use absolute
  main-tree paths. → folded.
- Stale-worktree top-level docs are a standing lens-finding REJECT
  class (branch predates queue edits). → folded.

### Deliberations
- K5 adjudication: pin demanded `line.split()[1]` equal a space-bearing
  path — unsatisfiable; audit intent (quoted/path-safe) preserved via
  shlex round-trip at identical assertion strength.
- B-14/B-15 overturns: two pinned wire contracts refuted by lenses
  before hardware contact; unit tests had PINNED the broken argv shape —
  fixture-first's blind spot made real. Both superseded with ledger
  entries. → folded (fixture-first streams always get full lens tier).
- vLLM provenance rejection (lead gate): volunteered addition hashed
  fabricated IDs as realized evidence — model-defect, distinct from the
  MLX variant (which was in-spec drift). Ruling: node-realized IDs via
  /tokenize or structured absence; strict pressure on absence is
  intended.
- r3's "PRs don't reconcile RUN_STATE/queue" finding REJECTED as
  PR-blocker: bookkeeping is lead-owned post-merge by design
  (single-writer); landed this commit.

### Interventions
- None. No wedged runs, no fleet stalls, no manual wakes. (Contrast:
  the orchestrator-topology session logged I-1 fleet-wide stalls twice.)

### Delegation calibration ledger (final, lead-assigned)
| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| DL2-A5 | codex | P2-013 g5+6 | pinned-spec | clean-accept | K5 STOP (correct behavior) | ~10 min |
| DL2-A7 | codex | g7 + K5 ruling | pinned-spec + 1 adjudicated pin edit | clean-accept | — | 0 |
| DL2-A8 | codex | g8 strict gate | pinned-spec (A-10) | clean-accept | corpus-check env blocker was prompt-defect (lead assumed runs/ in worktree) | ~15 min (that WAS the live gate working) |
| DL2-A9 | codex | strict-legacy + P2-014 + 3 D-entries | pinned + lead-designed rule, challenge invited | clean-accept | A-19 reconciliation (found the invited hole) | ~10 min |
| DL2-B3/B4/B5 | codex | 2K U3/U4/U5 | pinned-spec + bounded design freedom | clean-accept ×3 | — | ~5 min |
| fix rounds A+B | codex ×5 | triaged findings | pinned dispositions | clean-accept ×5 | B-44 predecessor REJECTED at gate (fabricated IDs — model-defect) | ~10 min |
| lenses/audits/reviewers | codex ×12 | review | design-freedom | high yield (see yield table); zero lead-rejected-as-noise beyond 2 stale-worktree items | triage only |
| D recon | codex | docs reconciliation | pinned dispositions | clean-accept (1 count stale = lead prompt-defect: 491 vs 495) | ~5 min |
- Aggregate: pinned-spec delegation ran essentially defect-free; the two
  serious 5.5 defects were both in VOLUNTEERED additions (vLLM
  provenance) or design-freedom wire pins (B-14/B-15) — i.e. freedom
  needs the lens tier, pins don't need re-litigating. Lens yield stayed
  high through the LAST round (integration review found 2 uniques after
  ~20 prior review passes).

### Spend
- Codex: ~26 sessions (9 impl/fix, 12 review lenses/audits/reviewers,
  1 amplification ×2, 1 integration, 1 docs recon). Opus: 0. Fable:
  orchestration + all gates + merges + bookkeeping (this loop).
- Wall-clock: single evening; fleets of 2-3 codex sessions ran
  continuously with zero idle stalls.

## Workspace state

- main @ this commit (bookkeeping); PRs #8/#9/#10 merged, #11 open.
- Worktrees: `../jw-2k` kept until #11 lands. `../jw-p2013`,
  `../jw-doc007`, `../jw-spike301` removed post-report (branches merged;
  ledgers + all evidence live on main via the PRs).
- `/tmp/jw-lead-verify/*`, `/tmp/jw-shapefix` disposable.
- Git author remains `Ed R <edr@Eds-MacBook-Pro.local>`.

## Retired-artifact pointers (C-009 gap rule)

- Stream ledgers (now on main via PRs): p2013 A-1..A-30 →
  `docs/stream_logs/2026-07-07-p2013-integrity.md` @ PR #8 (4f0d7bc);
  2k B-1..B-45 → `docs/stream_logs/2026-07-07-2k-nvidia.md` @ PR #11
  head (c487f6b); kv-spike C-1..C-8 + doc007 D-1..D-9 → their files @
  PRs #9/#10. PROMOTED: D-032..D-036. NOT promoted (intentional): all
  code-shape entries (bind via the merged code + contracts docs).
- The pre-checkpoint session's 26-item staleness list: never committed
  (Opus orchestrator context, discarded at checkpoint); its adjudicated
  DISPOSITIONS survive in the checkpoint report §Stream D and were
  re-applied fresh (ledger D-9 on the doc007 branch).
