# Wave-2 merge resolution: docs-vs-truth

Date: 2026-09-04  
Mission head: `c7c4930e358f6237a7e40dcb6d175842e4a56d23`  
Integration head: `ac7ca7f0e22e1806f0f085b81ca2988ba6780281`

The integration side is authoritative for paper-lane values and statuses. No
registry value, digest, paper status, or fill marker was changed in this
resolution. Mission-only consistency guards were reapplied after retaining the
reviewed integration wording.

## Hunk ledger

### `AGENT_PLAN.md`

1. Ground rules: kept wave 2's Mission M0/state-kernel wording.
2. source-of-truth table: kept wave 2's four owner descriptions; retained the
   mission's compatibility-only characterization without restoring the retired
   path as an intake route.
3. run-report intake bullet: kept wave 2's Mission M0 wording.
4. phase-checklist route: kept wave 2's fuller Mission M0/D-023 wording.
5. task-queue route: kept wave 2's kernel-first wording; retained the mission's
   already non-conflicting generated-lane-head override language.

### `PROJECT_STATUS.md`

1. Whole-file compact-status overlap: kept wave 2 verbatim. This preserves its
   reviewed Qwen3, DG-071/DG-075-adjacent paper, dominance, gate, measurement,
   and status values while retaining the mission's seven-section DOC-008
   compaction outcome.

### `README.md`

1. Energy-basis owner: kept wave 2's measurement-methodology contract link.
2. Q4 owner: kept wave 2's research-question-registry link.
3. agent intake route: kept wave 2's Mission M0/state-kernel wording.
4. documentation owners/site policy: kept wave 2's owner list and reapplied
   the mission's D-136 consistency correction: agents do not refresh,
   regenerate, or deploy the retired site lane; Ed owns any manual dispatch.

### `docs/agent_playbook.md`

1. live-work selection: kept wave 2's generated-view selection and
   multi-task/two-writer rule. Retained the mission's non-conflicting
   historical-wrapper fences and stale-pointer correction.

### `tests/test_docs_freshness.py`

1. path/headings constants: kept wave 2's complete `DOC008_PATHS` and added
   the mission's exact seven-heading tuple.
2. current-section helper: kept wave 2's `PROJECT_STATUS` key and added the
   mission's exact-heading guard.
3. owner test: kept wave 2's key and exact sequence assertion; retained the
   mission's compact-current/history-separation test.
4. mutation/history test: kept wave 2's renamed current-source test and
   retained the mission test identity plus its history-is-ignored assertion.
   The final module contains every test name from both parents.

## Verification

`git diff --check` returned exit 0 with no output.

`python3 -m unittest tests.test_docs_freshness` returned exit 1:

```text
Ran 31 tests in 0.878s

FAILED (failures=1)
```

The single failure is
`test_decision_index_matches_decision_bodies`: the pre-existing staged wave-2
`docs/decision_log.md` adds the D-172 body but its index ends at D-171. The
test was preserved and not weakened. Repairing that integration-owned index is
outside this seat's exhaustive write scope.

Staging the resolved paths was attempted with the exact command below, but the
managed sandbox cannot write the common worktree index outside this writable
root:

```text
git add AGENT_PLAN.md PROJECT_STATUS.md README.md docs/agent_playbook.md tests/test_docs_freshness.py docs/process_traces/2026-09-04-fanout/docs-vs-truth/09-wave2-merge-resolution.md
fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-fan-docs-vs-truth/index.lock': Operation not permitted
```

The five files contain no conflict markers, but the index will continue to
show them as unmerged until the magistrate runs that `git add` command from a
writer with common-index access.
