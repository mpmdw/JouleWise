# BFG-S S0 (helper and arm fence): cold Fable final pass (gate row 7; also the row-10 fresh-eyes review of the post-lens bench commit)

You are a COLD reviewer: a fresh session with no loop context. Your working tree is the exact merge candidate `b7df341b` on branch `feat/2026-09-26-bfgs-s0-helper-fence`. It contains main `5d5a0b75`, and main has not moved since. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md or the decision log. **Contamination disclosure first.**

**The change.** `git diff 5d5a0b75 b7df341b` touches:
- `joulewise/battery_float.py`, `joulewise/evidence_night.py` and `joulewise/night_kinds.py`;
- tests `test_battery_float*.py`, `test_evidence_night.py` and `test_night_kinds.py`.

S0 is the first of four PRs (S0–S3) that install Ed's binding battery-float gate (directive #421) for every non-derivation window kind. It adds:
- the `PairVerdict` helper `authenticate_pair` and its wrappers for quiet envelopes, controller bundles and captures;
- the arm fence;
- the frozen-function pins;
- the consumer guard.

**Rulings that govern, in precedence order.** The newest wins where they conflict.
1. The addendum-3 erratum, `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/20-coldgate/30-erratum/21-coldgate-fable-erratum-ruling.md`: amendments 30 (re-issued), 31, 26, 32, 33 and 34, and T30-a…j.
2. Addendum 3, `.../10-s0-delta/20-coldgate/10-coldgate-fable-ruling.md`: amendment 29, T16, and the §4 class table.
3. Addendum 2, amendments 20–28: `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/40-addendum2/21-coldgate-fable-addendum2-ruling.md`.
4. Final texts v1.1 §4, texts 1–4, 15 and 17, and T1–T4: `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md`.
5. The round-3 fix contract and lead rulings: `.../2026-09-26-activation-6bec2aa6/60-bfgs-s0/41-fix-contract-round3.md` and `44-lead-rulings-round3.md`.

**Review trail** (under `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/`):
- `10-sol-execution-lens.md` and `11-opus-contract-lens.md`: the delta of rounds 3/3b.
- `41-seat-report-round4.md`: round 4, `c9081c6e`.
- `51-astra-execution-lens.md`: round-4 delta, R1 BLOCKER and R2 SHOULD-FIX.
- `52-opus-contract-lens.md`: round-4 delta, PASS with five NITs.

The lead bench commits are:
- `783a09be`: restored the frozen `CustodyFailure` byte-identical to main, after round 3 had widened it and pinned its own bytes, and added `CustodyUnreadable`;
- `b7df341b`: Astra R1, a strict UTF-8 decode of the containers, since `json.loads(bytes)` auto-detects UTF-16/32.

**Magistrate's proposed dispositions** (you may overrule any of them):
- **Astra R2 / Opus NIT-5.** A shape-(iii) envelope carrying only the pre record returns `evidence_missing` with the reason `post evidence missing: phase not recorded`, not the erratum's "single reason `quiet span unavailable`". The status is the same non-pass. The erratum's own text also says rung order (a)–(f) is unchanged, and rung (a) precedes the span rung (f). Proposal: the code stands, text 2's order governs, and the erratum sentence is read as "the verdict is `evidence_missing`; when both phase records are present, its single reason is `quiet span unavailable`". Rule on this reading.
- **Opus NITs 1–4:**
  - whitespace-only journal lines are skipped;
  - a 200,000-deep JSON nest escapes as `RecursionError`, which is uncaught and so still refuses the computation;
  - `match`/`case` rebinding is not counted by S-1;
  - "unreadable" is worded where the text says "missing" for a symlinked or directory journal.

  Proposal: deferred to a follow-up lane. None changes a number.
- **The Opus residual.** Consistent edits of `session.json` fields (for example `journal_rows: 0`) plus an emptied journal pass. This is out of scope under D-161, as the erratum states.

**Questions you must answer.**
- **Q1.** Is the candidate a faithful, complete implementation of the governing texts for S0's scope, including every T-row the rulings assign to S0? Probe by execution in /tmp, and include the honest-failure shapes P-A and P-B and the same-signature class.
- **Q2.** Is the frozen closure byte-identical to `5d5a0b75`, and does the pin table equal the base segments under the test's own rule? Recompute this yourself.
- **Q3.** Review the post-lens commit `b7df341b` fresh (row 10). Is it correct and complete for R1 across all three containers, and does anything else in S0 still auto-detect an encoding?
- **Q4.** Do you accept each proposed disposition above?
- **Q5.** Anything design-level that should stop S0 before S1 and S2 build on it.

**Verdict.** MERGE, FIX-FIRST (with exact changes) or REFUSE. A refusal is a stop.

**Protocol.**
- A single non-interactive session: no background tasks, no subagents, every probe in the foreground.
- Write your verdict with the Write tool to `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/60-s0-gate/21-fable-final-pass.md`. Ending before that file exists is a protocol failure.
- Budget: 45 minutes.
