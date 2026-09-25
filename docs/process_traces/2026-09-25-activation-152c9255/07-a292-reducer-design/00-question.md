# 07/00 — Design consult A292-REDUCER-DESIGN-01: the sealed scored reducer's schema, completeness and cap rules

Assembled 2026-09-25 ≈04:58 PDT by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## Terms

- **Scored night.** An unattended run that generates MATH answers, scores them, and records power.
- **Packer.** It assigns fixed problem blocks to power-capture envelopes and seals a replayable **roster**. It merged as PR #409 (`joulewise/scored_packer.py`, main `75d04e9e`).
- **Reducer.** Lane A292, HEADLINE-REDUCER-SEALED-01. It reads the sealed roster plus per-problem score rows plus capture windows, and attributes gross energy to each executed problem block. Every registered item ends as exactly one counted row or one typed terminal refusal.
- **Harness-first method.** A seat writes executable acceptance tests (RED) from ruled text and commits them. A second seat then implements to GREEN without touching the tests.

## Why this consult

A read-only scout assembled every ruled clause that binds the reducer ([02-scout-report](02-scout-report.md): binding clauses with path:line, the merged packer interface, and a proposed RED test list). It found six items the rulings leave OPEN (scout §"OPEN items"). The RED harness cannot be written until they are ruled.

## Questions (answer each with exact executable text, and tier concerns BLOCKER / MATERIAL / NIT)

- **R1 — Schemas and refusal vocabulary.** Give the exact score-row keys and types (including `scorer_id` and both digests), the capture-window keys and types (keyed by `(block_id, attempt)`), the reducer output schema, and the typed refusal codes. Reuse the packer's `inv_*`/`PackingRefusal` idiom or justify a separate namespace.
- **R2 — Window completeness.** Which attempts must have a capture window (live, voided, `unattributed_overrun`, `ceiling_violation`), and which missing-window cases refuse and with which code. Do not inherit the stopped draft's "all active windows required" rule without a reason.
- **R3 — Cap policy.** The sealed v4 rule derives a cap hit from `generated_tokens ≥ cap_tokens[arm]`. The unadopted AP-5M v5 draft (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:41,53`) distinguishes thinking-cap hits from answer-allowance hits, keys cells by `(model, level, budget)`, and has `night_exhausted` transitions. Should the reducer implement v4 now, with v5 as a later versioned change, or wait for v5 adoption, or be parameterized? It must never be a silent hybrid.
- **R4 — Executed-status presentation.** Contract v4.1 marks the executed-status return shape as proposed, not ruled, and notes tension between per-level and per-cell spread wording (`docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:393-398,788`). Rule how A292 presents executed spread and drift.
- **R5 — INV-12.** The checker's INV-12 is stricter than the contract on a single's `predicted_item_s` (lane A291-INV12-RECONCILE-01). Does A292 depend on the outcome? If it does, say how the harness stays neutral until that lane is ruled.
- **R6 — The stopped draft `c0998fdb`.** Use it as an untrusted source of test cases only, or reuse parts of it? Give the reason.
- **R7 — Delegation.** The harness seat's WRITE_SCOPE and the implementation seat's WRITE_SCOPE, and whether an independent reducer oracle (a separately written checker) is needed, as it was for the packer.
