# Cold review: agent-identity test flake fix (PR #712)

Reviewer: Claude Fable 5.2, cold seat, 2026-11-10 20:54 PST.
Reviewed head: `fb54125f81ad04f7b33418a9c4d36fbaefd4d927` on
`fix/2026-11-10-agent-identity-flake`, against `origin/main` at `6b91f6428`.
Subject report: `docs/run_reports/2026-11-10-agent-identity-flake.md`.

## Verdict: ADMIT-WITH-FIXES

The two repaired tests still test what they were written to protect, and they
are not tautologies. The measurement code is unchanged. Two things need
fixing: a one-line fixture change that restores a check the rewrite dropped
(F1), and the root-cause account, which the CI logs contradict in one
respect and sharpen in another (F2). F3 is a follow-up, not a blocker.

## What was checked

| Question | Result |
|---|---|
| Is `joulewise/` or `scripts/` changed? | No. The diff is `tests/test_agent_identity.py` and two report files. |
| Does the module pass natively on the Air? | Yes: 13/13 OK on 11 consecutive runs, python3.13, Darwin. The ancestor live test ran (no skip). |
| Do the repaired tests still fail when the wiring breaks? | Yes; see the mutation table. |
| Do they exercise the real matcher? | Yes. The helper swaps only the `inspector` argument (process facts). `identify`, `in_tree` and `filter_census` run unmodified. |
| Linux CI result for this head | Not available: the test shards were still pending at review time. |

### Mutation witnesses (old tests from `origin/main` vs. new tests, same mutant)

Each mutant was applied in process with `mock.patch`; "hazard" and "named" are
the two repaired tests.

| Mutant | old hazard | new hazard | old named | new named |
|---|---|---|---|---|
| `arm` bypasses the shared matcher | FAIL | FAIL | pass | pass |
| `night_gate` bypasses the shared matcher | pass | pass | FAIL | FAIL |
| `identify` always `not_agent` | FAIL | FAIL | FAIL | FAIL |
| `identify` always `agent` | pass | pass | FAIL | FAIL |
| `arm` stops passing `own_tree_root` | pass | **FAIL** | pass | pass |
| `in_tree` always False | pass | **FAIL** | pass | pass |
| `in_tree` always True | FAIL | FAIL | pass | pass |
| `AGENT_PREFIXES` loses `codex` | pass | pass | FAIL | FAIL |
| `AGENT_PREFIXES` loses `claude` | FAIL | FAIL | FAIL | FAIL |
| group rule accepts any foreign group (see F1) | FAIL | **pass** | pass | pass |

The new tests kill every wiring and identity mutant the old ones killed, and
two more (the `own_tree` reason assertion). They lose one: the last row.

## Findings

### F1 (fix before merge, one line): the foreign agent no longer has a dead group leader

The old hazard test's agent was a real orphan: parent 1, process group led by
the exited shell. That shape drove `in_tree`'s group branch with a leader that
cannot be inspected. The fixture models it as `ProcessInfo(agent_pid, 1,
agent_pid, ...)`, so its own pid leads its group and the branch is skipped.

A mutant where any process in a foreign group counts as own tree fails the old
hazard test and passes the new one. On Linux CI nothing else in the module
catches it, because `AncestorCensusLiveTests` is Darwin-only.

Fix: give the agent a group leader outside the table, for example
`ProcessInfo(agent_pid, 1, agent_pid + 1, "/bin/sleep", agent_argv)`. I ran
this variant from a scratch copy: it passes unmutated and fails under the
mutant, as the old test did.

### F2 (correct the report): the CI logs point at the runner image, not at a 60-second lifetime

The mechanism in the report is right in shape: the matcher keeps a row it
cannot verify, and the window's row was kept. The report could not name the
event and discusses the child reaching its 60-second lifetime. The CI logs
rule that out and suggest a specific cause.

Observed in the failed jobs (`gh run view --job ... --log`):

- The whole module ran in 0.040 s. In job 130308306392 the hazard test took
  about 3 ms. The window was verified by the first census and unverifiable at
  the second, a few milliseconds later, with one `sh` spawn in between.
- All five failed `test_agent_identity` jobs I sampled ran on image
  `ubuntu-26.04` (runs 42954521391, 42956849799, 42954417422, 42953253289,
  42945046694). Four were the hazard test and one was the named test's
  `codex` subtest. I read the assertion diff in two of them (both the extra
  window row) and only the failing test name in the other three.
- The two failed shards I sampled from 2026-11-08 ran on `ubuntu-24.04` and
  failed in a different module. That is a small sample and I did not confirm
  those shards ran this module.

Inference, not verified: on the 26.04 image `/bin/sleep` is a multicall
coreutils binary that dispatches on `argv[0]`. A symlink to it named
`run_campaign`, `claude` or `codex` is not a known utility, so the child exits
within a millisecond or two of exec. It is then a zombie with an empty
`/proc/<pid>/cmdline`, the matcher cannot verify it, and the row stays. That
fits the timing, the fact that only the window row is ever extra (an
unverifiable agent row is kept either way), and the onset with the image.

One command on an `ubuntu-26.04` runner settles it:

```sh
readlink -f /bin/sleep; ln -s /bin/sleep /tmp/run_campaign; /tmp/run_campaign 60; echo "exit $?"
```

The report also says verification was Darwin-only. The flake is Linux-only on
this evidence, which is why 50 local serial runs never reproduced it.

### F3 (follow-up, not blocking): the retained live tests share the fixture

If F2's inference holds, every test that still uses `window_process()` or
`marker()` races the same early exit on CI:
`test_a_listed_window_process_is_not_an_agent`,
`test_the_callers_own_tree_is_ignored_even_when_agent_named`, and
`test_a_multiline_argv_record_is_decided_as_one_record`. Their window between
spawn and inspection is shorter, so they fail more rarely; none appeared in
the five failed jobs I read. `_live` can also lose the race outright, poll for
10 s and raise `SkipTest`, which would hide the loss as a skip.

So this PR makes the two reported tests deterministic, not the module. The
title overstates it. The durable fix is a live fixture whose lifetime does not
depend on `argv[0]`, and it should be tried on a 26.04 runner before it is
called done.

### Notes

- N1. After this PR the arm's live-inspector path is covered only by
  `AncestorCensusLiveTests`, which is Darwin-only. The measurement machines are
  Darwin, so I accept this. The repaired hazard test would still fail if `arm`
  passed its own `inspector` (duplicate keyword) or imported the filter by name.
- N2. `gate-ledger` fails on the PR: `row 1` and `row 5`: `evidence must be RUN
  <path-or-sha>`. That is PR-body ledger formatting, not this diff.
- N3. `docs/run_reports/interp-energy-desk/agent-identity-flake-sol-report.md`
  says "nothing pushed" and links to `/Volumes/JW-EXT/...` paths. Both are
  stale now that the branch is pushed. The main report's "12 pass, one sandbox
  skip" is the sandbox seat's count; natively it is 13 pass.
- N4. `CodexAppServerCensusTests` repeats the wrapper that
  `_census_process_table` now provides. Optional tidy.

## Reproduction

```sh
python3.13 -B -m unittest -v tests.test_agent_identity   # 13 OK, repeated 11 times
```

The mutation harness loaded `tests/test_agent_identity.py` from this branch and
from `origin/main`, ran the two tests under each `mock.patch` listed above, and
printed pass or fail per cell. It lived in the session scratchpad and is not
committed. Copies of the test file loaded from outside `tests/` fail the
ancestor live test for an unrelated reason (it derives `PYTHONPATH` from its
own location), so that test was excluded from the comparison.
