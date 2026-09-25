# 118 — Magistrate terminal review of PR #409 at `c5cbfd9eeefe6aa3dc7f323f1da7f6593b069a59` (gate-ledger row 12)

Reviewer: resident magistrate, activation 278ebc9e (Opus 5.5), with this activation's full context. Not delegable.

**Exact candidate.** PR #409 head `c5cbfd9e` (branch `fix/2026-09-24-a291-merge-candidate`). Branch protection is non-strict, so GitHub's merge commit adds only main's newer docs-only commits (interactive-4b `docs/process_traces` records; checked at ruling time by the final pass: the merge probe is clean and `gen_state --check` returns rc 0).

**What merges.**
- A291 scored-roster packer (`joulewise/scored_packer.py`, `joulewise/scored_registration.py`) with the round-3 ownership view (closed INV-11, contract v4.1).
- The independent checker, the ownership-forgery harness, and the fuzz and stress modules.
- Post-review commits:
  - d2e751df (`-> dict`; RecursionError → `inv_52` at two sites, plus a regression test);
  - 37f47475 (kernel retirement of ED-BRANCH-PROTECTION-E1-01, which cures main's generated-region drift);
  - b1913497 (hosted-CI patch target).
- This activation's and 7370d0fb's docs-only records.

**The chain I hold in context, verified at the bench where marked.**
- Two same-signature escalations produced the structural cure. Three text rounds (R3, R3b, R4) hit refuter BLOCKERs, which the harness-as-gate method resolved (A291-ESC2-02).
- Harness RED set at `0fa4e6e3` matches the ruling (bench-verified). The harness is GREEN at the round-3 head (bench: 10 tests OK). The five scored modules pass (bench: 75 OK).
- Mutation kills m1–m5 all kill at reference counts.
- Two independent forger seats (F-C and F-B, fresh Fable; F-A escalated on a vendor refusal and was replaced by ruling) each reached COMPLETED_NO_ESCAPE. The magistrate adjudicated all 18 accepted candidates with the oracle and checker: all OUT_OF_ROUND, all refused by `_replay_roster`.
- Entry-path witnesses for INV-23/36/37 were added (asserting inv_38/inv_38/inv_11, recorded).
- Paired lenses: Astra contract (a nit), Sol execution (RecursionError).
- Opus counter-review: safe to merge; R6-1 gates the first REGISTERED night, not this merge.
- Pre-merge ruling A291-PREMERGE-01 applied exactly. Three fresh-eyes reviews are CLEAN or have their findings dispositioned.
- Full suite at `c5cbfd9e`: 7,131 tests, 1 out-of-lane timing flake that passes isolated and in hosted CI.
- Hosted CI run 36098330718 on `c5cbfd9e`: success.
- Cold Fable final pass run 2: **MERGE**. Run 1 was REFUSE for a packet-hygiene defect, cured.

**Open items that do not gate this merge (all recorded).**
- The R6-1 level/night confound: it gates the first registered night, and the proposed rule is unratified and goes to the cold gate/Ed.
- Follow-up lanes: CI-A291-TIMINGS-01, A291-STRUCTURE-INDEX-01, and `_digest` finalize-path hardening.
- The INV-12 reconciliation queue (C1/C1b single-as-parent).
- Runner obligations for A292 (requeue outside envelope interiors; truncated-night close-out).
- The TASK_QUEUE hand-maintained count line (next bookkeeping).

**Verdict: MERGE `c5cbfd9e` as PR #409.**
