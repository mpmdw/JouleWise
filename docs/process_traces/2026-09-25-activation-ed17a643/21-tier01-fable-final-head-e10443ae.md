# Cold Fable final-head pass: PR #419, merge candidate e10443ae

Role: cold Fable 5.1 final-head judge, gate-ledger rows 7 and 10.
Worktree: `JouleWise-wt-ed17a643-t1fp`, HEAD `e10443aedd93d54361c70d88ecb75f6e3e0b1323`.
Date: 2026-09-25. Single foreground session; no subagents, no background tasks.

## Contamination disclosure

- Context carried at launch: the global `~/.claude/CLAUDE.md`, the project
  `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers only;
  one pointer names PR #419 as merged-adjacent work). No memory file body was
  opened.
- Not read: `RUN_STATE.md`, `TASK_QUEUE.md`, any memory file, any council log.
- The brief said the previous cold pass (`60-fable-final-head-5cfc2f39.md`)
  is not in this checkout. It IS present here as an untracked file. I did not
  open it; this ruling is independent of its text.
- Brief-supplied facts I relied on without re-deriving: the previous cold
  pass ruled MERGE on 5cfc2f39; hosted fences/quick on 5cfc2f39 failed on
  `test_current_sections_do_not_copy_volatile_literals` with the tuple
  ('orchestration process', 'pull-request literal', 'PR #419').

## (1) Diff 5cfc2f39 -> e10443ae

```
$ git diff --stat 5cfc2f39 e10443ae
 docs/orchestration.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

-   installation PR #419 on 2026-09-25. The 30-day revert window and the
+   installation PR on 2026-09-25. The 30-day revert window and the
```

Confirmed: exactly one file, one line, one literal (` #419`) removed. No
other content differs between the two candidates.

## (2) Tests

```
$ python3 -m unittest tests.test_docs_freshness tests.test_check_gate_ledger tests.test_gen_state
..................................................................................................................
----------------------------------------------------------------------
Ran 114 tests in 6.785s

OK
```

The fence has a live counterfactual (`tests/test_docs_freshness.py` ~line
1233) that asserts a planted PR literal DOES trip `pull-request literal`, so
the green result is a meaningful pass, not a vacuous one.

## (3) Sentence and fence scope

Resulting sentence in `docs/orchestration.md` §5 item 5, closing paragraph:

> Ruled 2026-09-24 by cold gate COUNCIL-407-01 §G5 as a D-184 addendum; Ed
> was informed with veto by Gmail `1a0d364481dec249` and endorsed the rule
> in GitHub issue #415 on 2026-09-25. Installed at the merge of the
> installation PR on 2026-09-25. The 30-day revert window and the day-30
> review run from that merge: day-30 review 2026-10-25. Material defects and
> the suspension trigger are tracked in `docs/process/tier01_defect_log.md`.

Reads correctly. "The installation PR" is defined two clauses earlier
(clause 4: "Installation is one FULL-TIER PR editing together ..."), so the
definite article resolves without the number. The PR number remains
recoverable through the defect log the sentence points to.

Fence scope, from `_current_sections()` in `tests/test_docs_freshness.py`
lines 444-471: the volatile-literal fence scans exactly four regions:

| section key | source |
|---|---|
| README | all of `README.md` |
| PROJECT_STATUS | all of `PROJECT_STATUS.md` |
| orchestration process | `docs/orchestration.md` from `# The Orchestration Process` to `## Spend guardrails` |
| orchestration reconstruction | `docs/orchestration.md` after `## Reconstructing the loop on a clean machine` |

`docs/process/tier01_defect_log.md` is not a scanned region, so its line 5
("installed at the merge of the installation PR #419 on ...") cannot trip
this fence. Verified empirically by the passing test above. The `issue #415`
reference in the same paragraph does not match the pattern
`\bPRs?\s*#\d+` and is not a violation.

Remaining PR-literal grep over the three scanned files: none.

## (4) Ruling

**MERGE e10443ae.**

- The delta from the previously-passed head is the minimal fix for the
  exact hosted failure and nothing else.
- The three named test modules are green locally (114 tests).
- The sentence remains correct and self-resolving; the defect log's retained
  literal is outside the fence and is the appropriate durable home for it.

Non-blocking observation, unchanged from 5cfc2f39 and not introduced by this
delta: the paragraph states the rule is "installed at the merge of the
installation PR on 2026-09-25" inside the PR that performs the installation.
That is true on merge day only if the merge lands today; if the merge slips
past 2026-09-25 the date and the derived day-30 date (2026-10-25) need a
one-line follow-up. No text change is required for this ruling.
