VERDICT: FIX-FIRST

# 48 — Cold Fable final pass on bookkeeping PR #402 (1246b299..cce85bf8)

Judge: Claude Fable 5.1, fresh non-interactive session, 2026-09-24, worktree `wt-d8cc9c0a-fable-bk`. Read: the diff, record 00 (items 1–16), 43, 21/10, 21/11, 45/10, 45/11, 45/21, lens 29, kernel/queue/test diffs. Not read: CLAUDE.local.md, memory bodies, other traces. No tracked file edited; nothing outside this worktree touched.

## Executed checks (both pass)
- `python3 scripts/gen_state.py --check` → rc 0.
- `python3 -B -m unittest tests.test_gen_state` → Ran 44 tests, OK. Count 242 + 5 = 247 matches the five new tasks; A281 retained as shelved.
- `git branch -r --contains 1246b299` includes `origin/main`: PR #401 is merged on the base.

## (1) Factual claims vs records
RUN_STATE top block: every claim traced — launch 19:11 and usage-exhausted exit (item 1); clean canonical at cdc05e9b, E1–E4 unanswered at Gmail 1a0d069e15a52ba9 (item 2); PR #401 merged as 1246b299, record 43 MERGE, 7,029/0 at 6532182f, two Linux-only fixture defects, green CI (item 15); fast-forward and stale supervisor (item 16); S3 call sites (lens 29); two failed gate rounds (items 5–6); consults found the rule incomplete (item 8); first cold gate ruled the table and split (21/10 Q1, Q3); c0998fdb stopped (item 12, 45/10 §0); addendum corrected retry and seal text (45/21 A1, A2, A4); checker-first by a different seat (45/21 §7 G). All correct.

Kernel notes A280, A281, A282, A291–A295: traced to 43 Q2 F1/Q3, 29 S3/R3, 21/10 Q1–Q4, 21/11 R3/R4/R6/R7/R9, 45/10 Q1–Q5, 45/21 §7 W/T/N/E/S/R/G/X/P. The 1,764 superset, 676 reachable inputs, share-scaled bound u = k·(floor_j+anchor_j)·s, 8999-vs-9000 mutant, `git status --porcelain=v1 --untracked-files=all`, (block_id, attempt) window key, generated_tokens ≥ cap rule, NE-over-NR precedence: all present in the cited texts. "25-row table": the gate-21 table has 25 worked patterns plus one catch-all ceiling-violation row; acceptable as written.

**Defect F1 (must fix): README contradicts the PR's own record.** README line 13 says the night-kind-table pull request "passed its final independent review and awaits the final-head replay and merge" and "Next: finish that pull-request gate". Record 00 item 15, RUN_STATE and the A280 note in this same PR say PR #401 is MERGED (1246b299). Commit 67794c84 wrote the README before the merge; e23a0ce4 updated the kernel, RUN_STATE and record 00 but not README. The professor-facing surface must not disagree with the record it ships with.

**Defect F2 (small, fix in the same pass): A294 evidence citation.** T0-CLEAN-TREE-CHECK-01 evidence cites "00-activation-record.md items 10 and 14 (registration direction)". Item 14 is bench hygiene (shell-`&` PIDs). The registration direction is item 10 and NEXT EXACT ACTION (4). Replace that evidence string with:
`docs/process_traces/2026-09-23-activation-d8cc9c0a/00-activation-record.md item 10 and NEXT EXACT ACTION (4) (registration direction)`
then regenerate (`python3 scripts/gen_state.py`) so TASK_QUEUE matches.

## (2) Nothing claimed landed that is not
A281 shelved with "no claim module has landed"; A291 "no draft is gated"; A292/A293 BLOCKED with the c0998fdb and d2f9a273 drafts named as stopped/ungated; A282 "adoption remains Ed's E2 decision"; A280 "PR B is not started". RUN_STATE: "neither draft is claim ready … Nothing is armed." No over-claim found. F1 is the reverse error (a landed merge reported as pending).

## (4) Register
README paragraph is otherwise readable by a technical outsider, but "final-head replay" and "the cold review's rules" are unglossed shorthand. Both disappear in the replacement below.

## Exact replacement for README line 13, from "A separate pull request" to the end of the paragraph
"A separate pull request adding a table of measurement-night kinds, which preserves the existing idle night's behaviour byte for byte, was merged after an independent final review, a full local test run and green hosted checks. Review of the draft code that schedules scored problem blocks, sums their measured energy and estimates energy per correct answer found defects, so that work has been split into three parts: a packer that assigns problem blocks to power-capture windows, a reducer that attributes energy only from sealed capture records, and an estimator governed by an explicit decision table. Next: write the packer's specification from the independent review's exact wording, with a separate checker written first by a different reviewer; add the scored measurement night; and draft the revised analysis plan for Ed to decide. Ed's choices about publishing problem text, adopting the analysis plan, model decoding, and sample counts are still pending. Nothing is armed."

## Disposition
FIX-FIRST: apply the README replacement and the A294 citation, regenerate, re-run the two checks, then merge. No further cold gate is needed for these two text edits.
