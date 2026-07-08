# Run Report — 2026-07-07 PM: Multi-Stream Hardware-Prep Session (CHECKPOINTED)

User-directed session: continue post-C-007 work with worktree streams,
Opus orchestrators directing Codex 5.5, Fable apex-only; stopped early at
a clean checkpoint on the user's instruction. NOTHING IS LOST: all four
stream branches are pushed, every stream ledger carries a `*-CHECKPOINT`
entry with its exact resume action, and this report + the verbatim
session trace (`2026-07-07-checkpoint-session-trace.md`) carry the
process learnings.

## How to restart (the short version)

1. Read this report + `RUN_STATE.md` "What Is Next".
2. Resume per stream from each pushed branch's ledger
   (`docs/stream_logs/2026-07-07-*.md`, final `*-CHECKPOINT` entry).
3. Merge order when streams complete: A → (D reconciliation + merge) →
   C → B (rebase post-A first) → cross-stream integration review →
   bookkeeping → THEN the quiet-machine 2M campaign (P2-006).
4. Mind the SUBAGENT WAKE GAP (below) — it is the one operational trap.

## Stream states at checkpoint (all branches pushed, worktrees clean)

| Stream | Branch @ head | State | Resume point |
|---|---|---|---|
| A: P2-013+P2-014 integrity | `stream/p2013-integrity` @ `d08b118` | groups 1–4 done; 19/31 pins flipped; suite 423/10/12 in-worktree; corpus validates clean under the tightened validator | group 5 (S1/S3/S6/S7), then 6–8 (raw-to-trace gate per ledger A-10) + P2-014 (per A-11; owes 3 decision-log entries: phase_energy_j, prompt provenance, 2O ownership), then counterreview phase + lead live gates |
| B: 2K NVIDIA fixture-first | `stream/2k-nvidia` @ `5660fb5` | U1 (wire protocol v1 + zero-dep worker) + U2 (SshTransport + NodeWorkerClient) done; 438/10/31; ZERO shared-file edits (U5 = the sole shared-file commit, deliberately last); ALL protocol pins PROVISIONAL pending live hardware | U3 (nvidia-smi adapter; prompt ready at that stream's scratchpad, never launched) → U4 (vLLM; watch 8 GB 3050 fit, llama.cpp-CUDA fallback) → U5 registry wiring → 3-lens counterreview → amplification → test review → REBASE onto post-A main → lead gate → live-verification checklist (doubles as P1-006 evidence script) |
| C: Stage 3.0.1 KV spike | `stream/kv-spike-301` @ `54e4f18` | **DONE. Verdict `replay_supported`** — fresh-OS-process resume token-identical (64/64 at 1024 and 2048 prompt tokens); cache size vs kv-size prediction +0.018%/+0.009% (constant ~5.3 KiB safetensors header — Stage 3.0.0 size model needs no calibration); mlx-lm 0.31.3 | lead re-verifies headline: `.venv/bin/python3 scripts/spike_mlx_prompt_cache.py run --prompt-len 1024 --decode 64` → expect `tokens_identical: true`; ratify 2 PROMOTE-TO-DECISION-LOG candidates; 2 accepted-deferred lens fixes belong to 3.0.2 |
| D: DOC-007 docs/framing | `stream/doc007-docs` @ `c086442` | DONE + lead-reviewed (fidelity lens: fix-first, 4 accepted items; staleness lens: 26-item merge-time list) | merges AFTER A with one reconciliation pass: staleness items 1–12 with real post-A counts, items 13–14 reworded to re-validation truth, items 15–26 REJECTED (ledger immutability — historical entries are never rewritten; addendum entries only) |

Also this session, already ON MAIN: Slice 2O (workload program) added to
`phase_2_plan.md` + queue annotations + P2-014 item (e) prompt-content
provenance (commit `aa665e1`, two-lens placement council).

## Research outcome of the session

**Phase 3's central technical risk is retired on current hardware:**
KV-cache persist/resume works in mlx-lm with byte-exact decode
continuity, and the analytic size model is accurate to a constant
header. The offline-replay rung of the Phase 3 ladder is real. (Verdict
final pending the lead's one-command re-verification at resume.)

## Process learnings (all folded into global skills THIS session)

1. **Subagent wake gap (structural; multi-stream-worktrees skill):**
   codex-run's exit-re-invokes-you guarantee holds for the main loop
   ONLY. Subagent orchestrators stall at every round boundary; the lead
   heartbeat (5–8 min background sleep) is REQUIRED INFRA, orchestrator
   returns must name the out-files they're blocked on, and every
   orchestrator prompt needs the wake-sweep rule (sweep `.status`
   sentinels on every wake). For pipeline-shaped streams, lead-driven
   codex-run keeps the wake guarantee and may beat the orchestrator
   topology outright — evaluate at next meta-review.
2. **`codex-run --resume` BUG (codex-delegation skill):** drops `-C`/`-s`
   → resumed sessions silently fall to read-only sandbox. Fresh session
   with carried context instead, when writes are needed. (Fix the
   wrapper when convenient.)
3. **Stream decision ledgers v2 (operation-loop skill):** committed
   per-stream `docs/stream_logs/` ledgers with scope cap + mandatory
   evidence pointers WORKED — D's ledger carried a full dissent trail,
   A's carried design adjudications. v1's unbounded format bloated
   immediately and was overturned by a 5.5 review of the lead's own
   schema. Ledger entries are historical: staleness reviews will
   propose rewriting them; reject that class, use addendum entries.
4. **5.5-reviews-consequential-decisions doctrine (operation-loop):**
   validated — the lead-decision review packet overturned two lead
   schemas with better ones and contributed 7 reusable reviewer roles
   (Ledger Auditor, Merge-Order Simulator, Prompt-Contract Auditor,
   Outcome Label Arbiter, Claim-to-Evidence Tracer, Negative-Space
   Reviewer, Quiet-Machine Contamination Forecaster).
5. **Delegation calibration ledger v2 (operation-loop):** lead-assigned
   outcome labels + numeric rework fields; session aggregate says
   design-freedom delegation to 5.5 keeps outperforming expectations,
   and review lenses need lead judgment mainly at history-vs-live
   boundaries and thin-verdict detection.

## Verification evidence

- Lead-verified during session: A's pin math at each landing (31→18→12
  expected failures in-worktree), corpus clean under tightened
  validation, B's suite 438/10/31, C's suite at exact baseline. CI has
  NOT run on the stream branches yet (no PRs opened).
- Deferred to resume (lead-only): C's headline command; A's
  strict-over-corpus + mock e2e after group 8; B's live checklist
  (hardware-gated).

## Workspace state

- main @ `aa665e1` + this checkpoint's bookkeeping commit, pushed.
- FOUR worktrees kept deliberately: `../jw-p2013`, `../jw-2k`,
  `../jw-spike301`, `../jw-doc007` (clean, branches pushed). Remove each
  only after its PR lands.
- The session scratchpad's lens out-files are ephemeral; everything
  load-bearing was committed to stream ledgers or this report.
- Git author on this machine remains the auto-selected
  `Ed R <edr@Eds-MacBook-Pro.local>`.

## Decisions / risks

- No decision-log entries written on main this session (single-writer
  rule: stream A owns decision_log.md and carries D-011/D-027 amendments
  in its branch; owes 3 more entries at resume — see its checkpoint).
- Council-log entry C-008 (this session) added with pointers here.
- No risk-register changes; R-016 backup note: the new corpus this
  session is code + docs only (no new measurement bundles).
