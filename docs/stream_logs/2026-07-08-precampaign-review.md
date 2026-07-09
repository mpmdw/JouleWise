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
