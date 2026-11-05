# Block-5 release runbook — 2026-11-05

Mission M0 intake: explicit owner documentation task, overriding normal queue
rank. Read repository AGENTS/CLAUDE, the active stop-card region (NONE), current
project/workspace/next-work pointers, generated queue and manual Do-Not-Do-Yet
list, source-of-truth map, orchestration roles, the block-5 registration/analysis
plan, D-188/D-189/D-190, and targeted implementation/test/record sources. Initial
checkout: clean, detached at `92026c184`. No delegated agents or external tools
were used. The explicit blinding and resource restrictions governed this lane.

## Delivered

- `docs/process/b5_release_runbook.md`: cited preconditions; exact blinded
  comparator/release commands; verdict/exit handling; ordered Release event and
  reader transition; same-commit equality and absent claim-side-bound custody
  verification; paper-fill path; Ed/lead responsibilities; failure branches and
  gaps. No helper script or production code change was needed.
- `TASK_QUEUE.md`: owner-request intake and documentation evidence pointer,
  outside generated regions. No phase exit-checklist row exists for this
  documentation deliverable; no phase/release completion is asserted.
- `RUN_STATE.md`: appended factual documentation checkpoint, preserving original
  citation line numbers and generated work selection.
- This run report. `PROJECT_STATUS.md` and the state kernel are unchanged:
  advisor-visible state and live work selection did not change.

Local Git objects confirm:

| Tag | Commit | Tree |
|---|---|---|
| `b5/analysis-r2` | `929fc65c9ce3ff82f0311d28acf76a682edd466f` | `9e89d7ff48999416467129c03ea171fc3a1f3f83` |
| `b5/analysis-r1-9bfix-ref` | `e7eb872d232ab58efe3ff861ae2c33dbfd8c0a33` | `de2e980edecf9047efd5c86dd4f31488a6d5a739` |

Both are annotated tags. The current comparator and its three equivalence
configuration files have no diff from r2. No tag, scientific pin, custody file,
sealed document or decision entry was changed.

## Verification

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m pytest tests/b5_analysis/test_release_equality.py -q -x -k ReleaseComparisonPrimitiveTests -p no:cacheprovider`
  — **could not start**, exit 1: `No module named pytest`. No test was collected
  or executed. Only the in-memory primitive class was selected; the joined and
  dispatch tests would access synthetic `restricted/` paths and were excluded
  under the owner's ban on any such access.
- Python 3.14.6 also reports `pytest_available=False`. No network/dependency
  installation was attempted. There is no claimed pytest pass.
- `python3.13 -B scripts/gen_state.py --check` — exit 0 before final close-out;
  generated regions agree with the unchanged kernel.
- Static document validation — exit 0:
  `DOC_CHECK_OK links=60 shell_blocks=4 python_blocks=1`. Every reference target
  and cited starting line exists inside the clone; all four shell blocks parse
  with `/bin/zsh -f -n`; the inline postcheck parses with Python `ast.parse`.
  No documented real-data command was executed. An initial naive reference
  scanner mistook Python indexing for Markdown references; excluding fenced
  code corrected the scanner, with no document defect exposed.
- `git diff --check` and explicit new-document whitespace checks — exit 0.
  Final diff review covers the four documentation files only. Existing source
  citations retain their original line numbers.

No full suite or long fixture run was invoked. No tests actually ran and no
workers were spawned. Documentation-only/static checks do not establish real
release equality or hardware/science validation.

## Blockers and uncertainty

- Branch creation command
  `git switch -c lane/2026-11-05-b5-release-runbook` failed, exit 128:
  `cannot lock ref ... unable to create directory for .git/refs/heads/lane/2026-11-05-b5-release-runbook`.
  The session's filesystem policy gives `.git` read-only access and approval is
  unavailable. No bypass or alternative Git directory was attempted.
  **Commits: none. Branch: still detached.**
- dry-j's finished status is supplied by the task, not observed locally;
  `RUN_STATE` item 165 still has its older running status. dry-i's result and
  the final blinded comparison remain unverified. No real measurement data or
  custody contents were accessed, and no path below any `restricted/` directory
  was read, listed or inspected.
- The runbook flags: no located r2 analysis-file/hash seal addendum; placeholder
  Release event; unspecified extra release-attestation format/Ed ceremony;
  literal record-equality wording versus modes/salted audit sidecars; the old
  independent-recompute gate wording versus the latest release pointer; no
  block-5 Results renderer; and live-ledger appends potentially violating the
  driver's whole-input-census equality. These are carried as evidence gaps or
  lead dispositions, not new policy rulings.
- The approximately 19-hour SIGSTOP deadline scenario is requested in the
  brief, not observed in this clone. Its branch cites the monotonic elapsed-time
  budget and existing fresh-root rerun rule; it does not infer an actual code
  or measurement defect.

## Exact next steps

In a session permitted to write this clone's `.git`, inspect the diff, then
create the requested branch and commit only these four documentation files:

```sh
git switch -c lane/2026-11-05-b5-release-runbook
git add -- docs/process/b5_release_runbook.md RUN_STATE.md TASK_QUEUE.md \
  docs/run_reports/2026-11-05-b5-release-runbook.md
git commit -m "docs: add block-5 release and unseal runbook"
```

No push. With a locally available pytest installation, rerun the single selected
primitive class above; do not install dependencies or expand test scope from
this handoff. Separately, the authorized release lead follows the runbook,
starting with dry-i's terminal structural record and pre-event evidence. This
documentation lane grants no real-data access or release authority.
