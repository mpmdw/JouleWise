# Charge: review of TIER-01 installation (TIER01-GATE-01)

Assembled 2026-09-25 ~14:25 PDT by the resident magistrate (Opus 5.5, activation 817355d2). Nothing is armed.

## What you review

- **Merge candidate:** branch `feat/2026-09-24-tier01-install` at **7c9dadc4** (the 09-24 implementation commit `e2511043` plus a clean, conflict-free merge of main `c6814dd8`). Review `git diff origin/main...7c9dadc4` (six files: `.github/pull_request_template.md`, `.github/workflows/gate-ledger.yml`, `docs/orchestration.md`, `docs/process/tier01_defect_log.md`, `scripts/check_gate_ledger.py`, `tests/test_check_gate_ledger.py`).
- **Authority:** rule TIER-01 was ruled by cold gate COUNCIL-407-01 §G5 (text in `docs/orchestration.md` as added by this diff; the ruling file is `docs/process_traces/2026-09-24-activation-278ebc9e/` — find it by grepping for `COUNCIL-407-01` and `G5`). Ed endorsed it in GitHub issue #415 (body, verbatim below).
- **Issue #415 body (Ed, 2026-09-25):** "gates are only meant to keep science defendable, not to overly red-tape dumb stuff like docs changes." Ruling: 1. Light gate: docs-only, bookkeeping-only or test-only changes (no production code under `joulewise/` or `scripts/` executed by nights, windows, analysis or claims) take a light gate: one fresh non-author review plus green CI; the 12-row full ledger does not apply. 2. Full gate: anything touching measurement, calibration, night machinery, analysis or claim code, or anything that can change a number. 3. When unsure, full. Apply: the magistrate lands TIER-01 accordingly. The gate-ledger CI check needs a matching light-tier path, "for example a declared `Risk tier: light` that the checker validates against the diff's paths."

## Questions (executed evidence; paste commands and output)

- **T1. Conformance.** Does the diff implement the ruled TIER-01 text (§G5) and the six-file installation it prescribes? Anything missing or overbuilt?
- **T2. Checker correctness.** Is `scripts/check_gate_ledger.py`'s light-tier path correct and fail-closed: a missing or malformed `Tier:` falls back to full; duplicate `Tier:` refuses; `N/A (light tier)` is accepted only in rows 2–8 and 10 under `Tier: light`; rows 1, 9, 11, 12 still need RUN evidence; the item-12 head-sha rule is unchanged. Try adversarial bodies (Tier line inside a code block or table, leading spaces, `Tier: Light`, CRLF). Run `python3 -m unittest tests.test_check_gate_ledger`.
- **T3. Against #415.** #415 suggests the checker validate a light tier against the diff's paths. The ruled design instead relies on the independent reviewer confirming the tier. Is that difference a merge condition for scientific defensibility, or a follow-up? If a merge condition, give the exact design (which paths make light tier illegal, how the workflow obtains the diff).
- **T4. Doc accuracy.** Are the workflow header and orchestration text accurate about the current branch-protection state (gate-ledger is a required check on main), and is the "(proposed; …; Ed … may veto)" wording now stale given #415? If it needs changing, give exact replacement text (you may only rule on text; do not edit).
- **Verdict:** MERGE / FIX-FIRST (exact texts) / REFUSE; findings as BLOCKER / MATERIAL / NIT.

## Rules

Single foreground session; no background tasks or subagents; ending before your report file exists is a protocol failure. Wall budget 30 minutes; mark anything not run NOT EXECUTED. No full test discovery. Read-only on the repository; write only your report file. Do not read `RUN_STATE.md`, `TASK_QUEUE.md`, memory or activation records beyond the ruling file named above.
