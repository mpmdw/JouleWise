# Fable cold review: `sm-analysis-hygiene` (audit Q12, code part; two invariants of section 8.3)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 05:58 PST. Reviewed head `31490f548`
(`test/2026-11-11-sm-analysis-hygiene`, base `origin/main`). Builder: Sol xhigh, one round.

**Verdict: ADMIT.** It does less than the audit's invariant asked for, and says so; the reason is a fact about
the repository, recorded below for the orchestrator.

## What the audit asked, and what is true

The invariant: "the tag, the test constant, the record field and the pinned-commit argument name the same
analysis commit". The seat first established what each one is today:

| Notion | Value today |
|---|---|
| (a) `B5_ANALYSIS_COMMIT` in `tests/b5_analysis/test_frozen_files.py` | `b13a510dc…` |
| (b) tag `b5/analysis-r4`, peeled | `ab1e0098d…` |
| (c) `analysis_commit` in a committed release or dry-run record | none is committed on `main` |
| (d) the runbook's `--pinned-commit` | a parameter (`PINNED=<record analysis_commit>`), not a literal |

So the four cannot be asserted equal: two are different commits and two are not in the repository. What git
does prove, and what the new test asserts: (a) is an ancestor of (b), and across the 388 frozen files the two
commits differ in exactly two, `joulewise/b5/harvest.py` and `joulewise/calibration_bracketing.py`, which is the
set the existing frozen-files test already names as evolved on `main`.

## What the PR adds

- `tests/b5_analysis/test_analysis_commit_agreement.py`: the relation above; the tag's identity as DLE-5 names
  it; the runbook's binding of `--pinned-commit` to the record field; and a fence that no test under
  `tests/b5_analysis/` resolves a remote branch by name. Missing tags or history skip with a message; they do
  not pass silently.
- `scripts/release_b5.py`: the verdict record gains `checkout_head` and `checkout_relation`
  (`equals_pinned`, `descends_from_pinned`, `unrelated`, `unknown`). No comparison, refusal or exit code changes.

## What I ran

- `tests.b5_analysis.test_analysis_commit_agreement` and `tests.b5_analysis.test_frozen_files`: 17 tests, OK,
  one explicit skip (no committed record).
- `python3.13 -B scripts/repin.py --check`: `PASS 16 pin families current`. The two new record fields move no pin.
- Read the `release_b5.py` diff (21 lines): the relation is computed with `git merge-base --is-ancestor` and is
  only written into the verdict.

## For the orchestrator

- **H-1.** `scripts/release_b5.py` is Block 5's release tool, and Block 5 is released. This is a record-field
  addition for later runs of the same tool; RL-51's reasoning for changes on `main` to a closed block's code
  applies. Say if you want the research lead to see it before merge.
- **H-2.** Notions (c) and (d) stay unverifiable from the repository: no release or dry-run record is committed,
  and the runbook takes the commit as an argument. If the released run's record digest and commit were written
  into a tracked file, the four-way test could become an equality.
- **H-3.** Still open from Q12 and not in this PR: the second `B5-ARM-RELEASED` line and the ledger-pin note
  are the orchestrator's edits; the duplicate archive branch is already deleted.
