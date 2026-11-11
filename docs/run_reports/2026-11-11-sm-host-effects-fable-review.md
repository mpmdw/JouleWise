# Fable cold review: `sm-host-effects` (audit section 8.2 item 3, shadow step; two invariants of 8.3)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 06:02 PST. Reviewed head `8d24e8053`
(`feat/2026-11-11-sm-host-effects`, base `origin/main`). Builder: Sol xhigh.

**Verdict: ADMIT-WITH-FIXES.** HE-1 is a wrong answer in the two cases this module exists for.

## Note on the push

The seat's custody audit reported one hit and the launcher did not push. I read the event: it is a heredoc that
writes test source, and the matched text is a test creating a synthetic `restricted/measurement-secret` file in
a temporary directory to prove the reader ignores it. No restricted path was accessed. I pushed the branch by
hand and said so in the commit message.

## What I did

- Read `owed_effects` and the span helper; ran `tests.test_host_effects` (30 tests, OK, default temp directory).
- Probed the night-label rows directly with four cases (below).
- Mutation-tested five points: four killed, one survived (HE-2).

## Findings

| # | Severity | Finding | Fix |
|---|---|---|---|
| HE-1 | **Blocking** | A loaded night label is classified from "is its span active now" and "is a result present" only. Two cases come out as unknown. (a) Installed and waiting, before its span starts, no result yet: reported `LABEL_SPANS_OR_RESULT_UNKNOWN`. That is the normal armed state and should be explained. (b) After its span has ended, with no result: also unknown. That is the silent case the audit is about (the job never fired, or died without a record) and should be owed. | Use the span's own times. Before `start`: explained, `AWAITING_PLAN_SPAN`. Inside: `ACTIVE_PLAN_SPAN`. At or after `end` with a result: owed, as now. At or after `end` with no result: owed, `NIGHT_LABEL_AFTER_SPAN_WITHOUT_RESULT`. A result present before the span starts is a contradiction: report it as its own unknown, `RESULT_BEFORE_PLAN_SPAN`, not as owed. Boundary tests at `start` and `end`. The same three-way timing for network time off and the night lock where an owner plan is known. |
| HE-2 | Low | Surviving mutant: AC power mode treated as set only when it equals 2. No test uses another nonzero mode. | One test with mode 1: set and, without the lock, owed. |
| HE-3 | Low | `active_plan_spans` is named for active spans but must carry a plan's span before and after it is active for HE-1. | Rename to `plan_spans` (keep the old keyword as an alias if the CLI used it) and say in the docstring that it lists every known plan with its start and end. |

## What is sound

- Unobserved facts are never clean: each yields a row with `owed=None`, and the CLI's exit 3 separates
  "unknowns only" from "nothing owed".
- The reader touches only an allowlist of marker and receipt names, refuses symlinks at and below the
  directory, and never runs a host command; live facts are passed in.
- Both host invariants of audit 8.3 are separate named checks.
