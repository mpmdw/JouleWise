# Audit fix-wave CHECKPOINT (2026-07-13, lead-written for Ed's resume)

Everything below is pushed. No agents are running. No leases are active
(the bench lease was abandoned with a recorded adjudication after a
lead sequencing error made its close report SCOPE_VIOLATION — the bench
DIFF itself was verified SCOPE_OK + Fable-checked before unrelated
register commits moved HEAD; see lease log).

## Where the audit stands

DONE (all committed, main):
- Charter frozen; Batch 0 manifests (443 files, invariant PASS).
- Batch 1: 15/15 scan receipts (85 rows; 10 scan-level blockers).
- Batch 2: C1 (25) + C2 (36) consolidated packets, accounting PASS.
- Fable review layer: 61/61 verdicts (46 confirmed, 15 narrowed, 0
  refuted) + register-integrity (benign cross-packet overlap resolved).
- Canonical register.jsonl: 43 operative findings (7 blockers), 39 work
  orders; fix-streams.json (S1–S5 scope-disjoint) + sol-final batches.
- Sol final round: 37 verdicts (7 proceed / 30 amend / 0 reject) — all
  amendments baked into the register by the second integrity pass.
- Ed-deferred rulings R1+R2: both Fable+Sol ALIGNED, lead accepted,
  folded into register (packets/ed-rulings.json): WO-021 = complete the
  state-kernel migration bounded to work-selection authority (schema
  v3, gates array, oracle fixtures, lead freezes then-current gate);
  WO-022 = ratified spend-guardrail bands (bench route).
- Fix wave, bench batch: WO-024/025/026/028/030 implemented (Sol high),
  lead-gated (SCOPE_OK pre-commit, suite 1389 w/ ONLY the known WO-018
  failure), Fable checker PASS ×5 → commit on branch `impl/audit-wave`.

## Known live defect (environment, adjudicated)

The canonical suite is RED on this machine and in clean clones:
`test_pack_capsule` measured-postcondition vs cached Lakebed 0.0.29
validator (finding C2-018/W4X-001; WO-018, stream S3). It predates the
fix wave and self-demonstrated when the live deploy pulled 0.0.29 into
the npx cache. S3 is the FIRST stream to run on resume.

## Resume plan (next session; everything needed is in-repo)

1. Streams branch from `impl/audit-wave` (bench batch included), one
   worktree + branch per stream (multi-stream convention):
   - S3 FIRST (WO-018 — restores suite green), then in parallel:
   - S1: WO-023 precursor → WO-001…WO-011 (order list in
     packets/fix-streams.json; largest stream).
   - S2: WO-032 → WO-012 → WO-013 → WO-014 → WO-015 → WO-016 → WO-029
     → WO-017 (WO-016's inputs.py admission hook folds into WO-004/S1
     per lead flag ruling).
   - S5: WO-020 (claude-consult REMOVED from scope per lead ruling).
   - S4 (WO-019 → WO-031) only AFTER S2 and S3 close (hard deps).
   Per work order: Sol high implementation (register row = full spec)
   under session-open/close ceremony in the stream worktree + a Fable
   checker on the diff before the next order (bench-batch pattern, it
   worked). Lead gates per stream close; integration tree before merge.
2. LAST, after streams: WO-021 (R1 spec; lead freezes the then-current
   global gate immediately before implementation) and WO-022 (lead
   pastes the R2-ratified guardrail text into docs/orchestration.md).
   WO-027 (codex-watch deletion) unblocked by Ed's deferral: preserve
   recipe + demonstrate replacement, then delete (bench).
3. Remaining audit close-out after the wave: deferred-roadmap work
   orders promoted to TASK_QUEUE rows in dependency order; report §7/§8
   synthesis (coverage table from receipts; findings tables; the
   MANDATORY rejected/downgraded-D7 table for Ed — note: 0 findings
   were rejected anywhere, so that table records the narrowings and the
   two ruled items); completeness critic (one Fable agent, §5 batch 5);
   one bounded closure loop if it finds gaps; queue promotion; council/
   decision entries; RUN_STATE refresh; site regen; PR(s) + merge gates.

## State pointers

- Register (single source): register.jsonl. Streams: packets/
  fix-streams.json. Verdicts: packets/fable-verdicts.json,
  packets/sol-final-verdicts.json. Rulings: packets/ed-rulings.json.
- Receipts + scan evidence: receipts/ (15 receipts + W4-exec).
- Method: report.md (charter), method/ (preamble + lenses),
  manifests/ (Batch 0 + ratifications).
- Branch: impl/audit-wave (bench batch, 1 commit). Main: audit records
  through the R1/R2 fold. All pushed.
