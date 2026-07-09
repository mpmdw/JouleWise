# Live session ledger — pre-campaign methodology review (2026-07-08)

PURPOSE: near-live log of decisions/actions/reasoning for the
pre-campaign review session (Ed's directive: checkpoint frequently for
easy resumption). A fresh agent resuming from interruption: read this
top-to-bottom, then act on the RESUME line at the bottom.

## Session ask (Ed, verbatim intent)

1. MIT license — DONE (commit `9095b51`, pushed).
2. Assess whether TASK_QUEUE still reflects appropriate next steps given
   Mac-only hardware reality (M3 Max 128GB present; rest elsewhere) and
   the intent to START COLLECTING DATA.
3. Review the prompt/workload bundle: robust? scientific? as close to
   deterministic as possible? — same multi-agent + verified-findings
   rigor as the codebase merit review (C-020).
4. Ensure bundles capture ALL scientifically useful data BEFORE traces
   are generated at scale (retrofit-impossible).
5. Afterward: enumerate the questions askable of the corpus re: power
   consumption by inference DECOMPOSITION and by query HARDNESS/LENGTH.

## Checkpoint log (newest last; commit each entry)

### CP-1 — license + workflow launch
- LICENSE (MIT, (c) 2026 Ed R (mpmdw)) committed `9095b51`, pushed.
  Third-party-data note included (directory-scoped licenses when
  data/ lands).
- Pre-campaign review WORKFLOW launched:
  run ID `wf_efd7d9d2-c85`, script
  `~/.claude/projects/-Users-edr-code-JouleWise/ae807c57-7163-4f10-8532-42e8cfacdaff/workflows/scripts/workload-methodology-review-wf_efd7d9d2-c85.js`
  (resumable: Workflow({scriptPath, resumeFromRunId: "wf_efd7d9d2-c85"});
  completed agents replay from cache; journal at
  `.../subagents/workflows/wf_efd7d9d2-c85/journal.jsonl`).
  Shape: 4 codex inventory readers (generation chain / campaign designs /
  bundle capture fields / Mac-answerable questions) → 4 lenses
  (determinism auditor, scientific-design, capture gap-hunter,
  question-yield maximizer) → tiered adversarial verification →
  synthesis (5 sections incl. the askable-question list + queue fit).
- Lead quick-read on queue fit (pre-workflow, to be confirmed): the
  queue top is ALREADY Mac-aligned — shakedown gate → P2-015 floors →
  P2-006 2M are [QUIET-MAC] M3-Max-only; Window B (q4 grid, sentinels,
  jw_mixed core) likewise; agent-lane pre-work (envelope-gate script,
  real-tokenizer manifests, P2-025/026/027) is hardware-free; everything
  needing absent hardware is correctly gated. Expected adjustment
  candidates from the review: long-context arm (8k+; 128GB makes it
  cheap), model-load-energy capture, cache-state recording, third-model
  question for Q4 coefficients.

RESUME (if interrupted here): check the workflow run state
(`/workflows` or journal); if complete, read the synthesis + findings
from the journal, adjudicate findings (accept/amend/reject with
dispositions recorded HERE as CP entries), land accepted changes
(queue/plan/capture code rows), then write the final answer covering
asks 2-5. If the workflow died mid-run, resume it with
resumeFromRunId — do not relaunch from scratch.

### CP-2 — parallel build fan-out + real-tokenizer manifests LANDED
- Four [AGENT] implementation streams launched in worktrees (all
  pre-campaign prerequisites, independent of review outcome):
  `jw-wt-envgate`/branch `envelope-gate` (P2-010 remainder: E1-E5 gate
  script per D-047/D-036), `jw-wt-hashcheck`/`runner-hash-check`
  (P2-025 post-window expected-vs-realized hash fail-closed),
  `jw-wt-strictfix`/`strict-era-fix` (P2-026 D-033 legacy-bypass
  close), `jw-wt-bundlepack`/`bundle-pack` (P2-027 publishable pack
  tooling). Codex out-files: scratchpad/codex/{envgate,hashcheck,
  strictfix,bundlepack}.md. Each gets lens round → fix → lead gate →
  small PR (bases = main; retarget rule N/A, no stacking).
- GEN-CHECKPOINT DISCHARGED (lead-side, .venv): real-tokenizer
  manifests generated and verified —
  configs/suite_manifests/jw_mixed_v1_qwen25_15b.json (48 items,
  6 categories x 8, all shapes 512/256, effective sha 06d5199a…) and
  jw_sentinel_v1_qwen25_15b.json (5 ids-native conditions, sha
  66f45283…), master seeds jw-{mixed,sentinel}-v1-2026-07-08,
  tokenizer = mirrored Qwen2.5-1.5B-Instruct-4bit @ 8b403126.
  VERIFIED: substrate-valid (from_mapping); ALL realized counts == 512
  on the real tokenizer; regeneration BYTE-IDENTICAL (manifest +
  sidecar); B7 tokenizer file rows present (4 files) with folded id;
  ground truth sidecar-only. Ed's determinism question: demonstrated,
  not asserted.
- Methodology-review workflow wf_efd7d9d2-c85 still running.

RESUME (if interrupted here): harvest the four codex out-files, run
lens rounds per stream, gate/commit/PR each; adjudicate the
methodology-review synthesis when wf_efd7d9d2-c85 completes; then the
final four-part answer (queue fit / determinism / capture changes /
askable questions).

### CP-3 — stream landings + live-gate catch on strictfix era rule
- All four streams landed green (envgate OK; hashcheck 738; strictfix
  OK; bundlepack 737). Final messages: scratchpad/codex/*.md.
- LEAD LIVE GATE CATCH: strictfix's era rule (base-field presence)
  FAILED all six real corpus bundles — legacy carries joulewise_version
  0.1.0 same as current; version does not discriminate. Lead-pinned
  replacement: frozen six-identity LEGACY ALLOWLIST
  (run_id + config_sha256 pairs extracted from the local corpus),
  everything else current-era → provenance required; honest
  identity-clause-not-crypto limit documented. Fix round 2 running
  (strictfix-r2). Live-only catch count this session: 4.
- Lens rounds for envgate/hashcheck/bundlepack running as Workflow
  wf_c5294fe5-a32 (2 lenses + tiered refuters per stream).
- Methodology-review workflow wf_efd7d9d2-c85 still running.

RESUME (if interrupted here): read wf_c5294fe5-a32 results → triage →
fix rounds where needed → lead gates → commit per worktree → 4 small
PRs (base main); re-verify strictfix-r2 against the REAL corpus
(all 6 must pass strict; tamper test must fail) before its PR.

### CP-4 — quota clarification + full resume via direct codex-run
- CORRECTION (Ed): the 10:10pm session limit is CLAUDE-side (workflow
  wrapper agents), NOT Codex — Codex is near-unlimited. All paused work
  resumed immediately via direct codex-run (no Claude-side wrappers):
  (a) envgate fix round — 2 lead-confirmed defects pinned (fail-open
  verdict without profile/level-set pin; uncaught BundleReadError
  breaching D-036) + all sustained lens findings; (b) hashcheck fix
  round; (c) bundlepack fix round — both self-triage sustained findings
  from the extracted lens JSON; (d) methodology-review COMPLETION —
  codex self-verifies unverified high-materiality findings against the
  repo and writes the 5-section synthesis (the Workflow's 36 failed
  verify agents + synthesis are NOT being re-run Claude-side).
- Key verified finding already in hand (methodology review, narrowed by
  refuter): text-item realized-vs-manifest hash never compared at run or
  verify time (bundle_read skips text items) — fix must be
  HASH-DOMAIN-AWARE (affine source_sha256 is a TEXT hash; jw_mixed's is
  a token-ids hash; naive comparison malforms every affine item) + a
  realized-vs-planned count check. Gating gap, not capture gap (drift is
  post-hoc detectable; harm = silently succeeded off-grid campaign).
- Strictfix: PR #22 OPEN, CI green both legs, live-gated both
  directions (6/6 corpus valid; tamper fails named). Awaiting merge
  gate (fresh reviewer pass) with the other three PRs.
- Durable artifact copies (survive /tmp cleaning):
  ~/.claude/projects/-Users-edr-code-JouleWise/<session>/checkpoint-2026-07-08/
  (codex out-files, debate papers, extracted workflow results,
  trace-notes). Workflow journals (authoritative):
  .../subagents/workflows/wf_c5294fe5-a32/journal.jsonl (lens rounds,
  complete) and wf_efd7d9d2-c85/journal.jsonl (methodology, 20/56 —
  completion delegated to codex, do NOT resume the workflow).

RESUME (if interrupted here): read scratchpad/codex/{envgate-fix,
hashcheck-fix,bundlepack-fix,methodology-synthesis}.md (or the durable
copies); lead-gate each stream diff (suite green + live checks where
relevant: envgate against a real affine mock bundle), commit per
worktree, small PRs base=main; merge gate for PRs #22 + the three new
ones = fresh codex final-head passes + CI; then adjudicate the
methodology synthesis (dispositions as CP entries), land accepted
pre-campaign changes, and write Ed's four-part answer (queue fit /
determinism verdict / capture changes / askable questions).

### CP-5 — STABLE STOP (Ed directive: checkpoint, do not finish)
All four resumed Codex sessions COMPLETED and wrote final reports;
nothing has been gated, committed from worktrees, merged, or
adjudicated since — that is deliberately the resume work.

State at stop:
- Worktree diffs (uncommitted, fix rounds APPLIED, suites reported
  green by the implementers — NOT lead-verified): jw-wt-envgate
  (3 files), jw-wt-hashcheck (4), jw-wt-bundlepack (2). jw-wt-strictfix
  is clean (its work is committed on branch strict-era-fix, PR #22
  OPEN, CI green, live-gated 6/6 corpus + tamper-fails — unmerged).
- Codex reports (per-finding dispositions + test lines) and the
  COMPLETED METHODOLOGY SYNTHESIS (5 sections: determinism verdict,
  pre-campaign changes, cheap window additions, askable-question list,
  queue fit — UNREAD by the lead, unadjudicated):
  durable copies in ~/.claude/projects/-Users-edr-code-JouleWise/
  ae807c57-7163-4f10-8532-42e8cfacdaff/checkpoint-2026-07-08/codex/
  ({envgate-fix,hashcheck-fix,bundlepack-fix,methodology-synthesis}.md)
  + scratchpad originals. Lens findings + methodology partials:
  same checkpoint dir, checkpoint/*.json.
- Main is pushed through CP-4 (6a558ad) + this CP-5 commit; manifests
  committed ec5224e; LICENSE 9095b51.

EXACT RESUME SEQUENCE (Fable directs, Codex executes):
1. Lead-gate each worktree diff (read diff; envgate additionally gets a
   live run against a real affine mock bundle incl. wrong-profile and
   malformed-evidence cases); fix rounds via codex-run if gates find
   issues; commit per worktree; small PRs base=main.
2. Merge gate for PR #22 + the three new PRs: fresh codex final-head
   pass each + CI green; merge; post-merge integration codex review
   (4 streams touch validation/runner/CLI surfaces).
3. Read + adjudicate methodology-synthesis.md (dispositions as CP
   entries here); land accepted pre-campaign changes (note: the
   hash-domain-aware realized-vs-manifest check is expected among them
   — verify the fix shape against the narrowed finding in
   checkpoint/methodology-review-results.json before implementing).
4. Then Ed's four-part answer (queue fit / determinism verdict /
   capture changes / askable questions) + Window-A go/no-go checklist.
