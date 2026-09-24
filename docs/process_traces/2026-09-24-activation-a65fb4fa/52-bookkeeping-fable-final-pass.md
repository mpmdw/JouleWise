VERDICT: FIX-FIRST

# Cold Fable final pass — bookkeeping PR, candidate f3d4448f (base edcd045b)

Judge: Claude Fable 5.1, fresh non-interactive session, worktree `wt-a65fb4fa-fable-bk` at `5aa52eef` (= f3d4448f + charge 51 only; `git diff --stat f3d4448f..HEAD` shows one file). Foreground only, no subagents, no background tasks. Read-only except this file. Written 2026-09-24.

## Disclosure
Auto-loaded before the charge: `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the memory index `MEMORY.md` (index lines only). `CLAUDE.local.md` was not loaded and not opened; no memory file was opened. Rule 11's wording was checked from the tracked `docs/process/coldgate_charter.md` §9 ("two consecutive rounds failing with the same signature … the next spend is a consult or redesign, not round three"), not from doctrine files.

## Executed evidence
- `python3 scripts/gen_state.py`: rc 0, `git status --short` empty afterwards (TASK_QUEUE.md regenerates with no diff).
- `python3 -B -m unittest tests.test_gen_state`: Ran 44 tests, OK.
- `git log -1 edcd045b`: merge of PR #403, parents `bd80d169` + `69fd5daf`; `gh pr view 403`: MERGED, mergeCommit `edcd045b…`, headRefOid `69fd5daf…`. Matches RUN_STATE, kernel, README and record 00 item 32.
- `/tmp/a65fb4fa-replay-2235eecb.log` tail: `WORKERS SUMMARY shards=8 modules=254 tests=7044 failures=0 errors=0 skipped=103 … result=PASS`; matches item 32 and the RUN_STATE "7,044 tests with 0 failures".
- `origin/feat/2026-09-24-a291-packer-recut` = `20cd29de`, history `d917bf77 → b8962fd0 → ef1c5e48 → 01badd6a (cherry-pick of b8fae7b3) → 20cd29de`. Commits `1f07c4ec`, `2235eecb`, `b8fae7b3`, `bd80d169` all resolve with the described subjects.
- Record 50: B1 BLOCKER (`_TRUSTED_OUTPUTS` cache skips requeue-entry replay; `_seal` accepts a forged root with two live placements that the checker flags INV-11/INV-36), S1 (ZeroDivisionError from count/positions split), S2 (index-driven generator), D5 same-signature YES. RUN_STATE, kernel A291 note and record 00 item 36 state exactly this.
- Record 36: I1 at `ef1c5e48`, `STRESS seeds=(291013,) registrations=300 … violations=0` against the old checker, with the B2 disagreement reported not worked around. Matches RUN_STATE.
- Gmail `get_message 1a0d2c87919abfe3` (MINIMAL): SENT 2026-09-24T09:39Z, threadId `1a0d069e15a52ba9`, to `claude2.glaring610@passmail.net`, subject "Re: MATH headline analysis plan: five decisions, reviewed draft ready (09-24)". Matches RUN_STATE and kernel A282 note.
- Ledger rows vs records: L-043 ↔ 15/10 (M1, M2 "missed by the charge", 5 MATERIAL total) ✓; L-044 ↔ 15/11 (R1 BLOCKER, R2–R9 MATERIAL, R10–R12 NIT = 12) ✓; L-045 ↔ 30/10 (Q1–Q18, T-1..T-23, BLOCKER Q1/Q2/Q3) ✓; L-046 ↔ 30/11 ("1 BLOCKER (R1); 12 MATERIAL; 4 NIT" = 17) and 30/21 (no verdict reversed, T-24..T-28, O-21 to Ed) ✓; L-047 ↔ 37 ("2 BLOCKERS, 1 MATERIAL, 8 test-strength survivors") and 44 ("1,500 random capture sets … 0 mismatches") ✓; L-048 ↔ 41 (VERDICT MERGE, six real-git scenarios at base and head) ✓; L-049 ↔ 27 (F1, F2 BLOCKER; F3–F7 MATERIAL; F8 NIT) ✓. Ledger `grep -c '^| L-'` = 49; rows without `unknown` = 31; the footer says 49 / 31 ✓. L-046's addendum path `21-coldgate-fable-addendum-ruling.md` is relative to packet 30 (no `20-addendum/` subdirectory there), which is where the file is ✓.
- Kernel diff: A294/A295 rows removed; test EXPECTED_IDS/TERMINAL_IDS and count 247 → 245 follow; A291 `queued → active`; A282 note says adoption "remain pending Ed"; A280 PR B note carries FT-9 and S3 call-site list; `updated` 2026-09-24. Every cited record path exists.
- Post-merge hosted CI on `edcd045b`: `gh run list --commit` shows `ci` still `in_progress` at ruling time; next action (1) correctly leaves confirmation to the successor.

## Q1 — FIX-FIRST (one README sentence); every checked claim otherwise matches
All spot-checks above pass. The single defect is in the README "Now" paragraph (commit `0f02008d`, the magistrate's own edit made after delta 50). It says the packer "now passes two stress runs of 300 planned problem schedules each. It still needs tests …, and final independent reviews." That is literally true of `20cd29de` but omits the state the same commit records everywhere else: the latest independent review found a BLOCKER and the lane is paused for a structural consult. A technical reader with no project grounding would conclude the packer is correct pending tests. Required replacement (README.md, the "Now (2026-09-24)" paragraph), replace exactly the sentence

> It still needs tests that vary every registered field and required rule, tests that deliberately break individual checks, and final independent reviews.

with

> The most recent independent review then found a blocking defect: the packer's own self-check accepts a schedule that the separate checker rejects, so the two do not enforce the same rules, and a cached result lets a re-sealed schedule skip its replay. Packer coding is paused while two independent advisers propose a structural fix, which a fresh reviewer must approve before any more code is written. After that it still needs tests that vary every registered field and required rule, tests that deliberately break individual checks, and final independent reviews.

No other change is required. After this edit the PR may merge without a further cold pass; the edit is prose only and its content is record 50 §Findings and record 00 item 36.

## Q2 — next exact action: complete, correctly ordered, executable cold
(1) CI confirmation and supervisor head ≥ `edcd045b` before any arm; (2) A291: blind Sol 6.0 high + Opus 5.5 consult on the structural cure (three named candidates), then a cold Fable gate on the fix-round-2 plan before any code, then I2 (with a seed-driven generator, curing S2), I3, cold delta gate, cold final pass; (3) A282 on Ed's reply via a normal PR to `docs/contracts/analysis_plans.md`; (4) A280 PR B brief with the S3 call-site list and FT-9. This respects the charter §9 escalation exactly (consult, then gate, no round 2) and matches record 36 and the kernel A291 note. It names branch, head, records, candidates and order; a fresh session can execute it. One optional clarity nit, not required: RUN_STATE says the checker was "fixed at `b8fae7b3`"; that commit lives on `fix/2026-09-24-a291-checker-r1` and reaches the A291 branch as cherry-pick `01badd6a`. Suggested text: "fixed at `b8fae7b3` (cherry-picked onto the A291 branch as `01badd6a`)".

## Q3 — no ratification, no adoption
Files changed outside the record directory are exactly README.md, RUN_STATE.md, TASK_QUEUE.md (generated), the kernel, the ledger and `tests/test_gen_state.py`. No decision log, contract, skill or process doc changes. The kernel A282 summary and note say adoption and installation "remain pending Ed"; RUN_STATE says "The magistrate has not adopted claim policy"; the README says "Ed must decide whether to adopt it". Kernel A292/A293/A280 notes carry cold-gate rulings (15/10 Q1/Q16, addendum FT-9) as consumer obligations, which records rulings already issued and creates no new rule. The `ex-repo-docs-decision_log.md` in packet 30 is a pinned exhibit copy, not a live edit.

## Q4 — README register
Plain words throughout: no lane ids, record numbers or internal shorthand; "packer" is defined at first use; "MATH competition problems", "capture-window length", "dedicated copy of the code" are readable cold. Only the omission in Q1 fails; the replacement text above stays in the same register.

## Ruling
FIX-FIRST: apply the one README sentence replacement in Q1, then MERGE f3d4448f-plus-that-edit. Everything else on the candidate is verified against the cited records and executed commands.
