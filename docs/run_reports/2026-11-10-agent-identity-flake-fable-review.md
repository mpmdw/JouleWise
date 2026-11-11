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

## Delta review, round 2

Reviewer: Claude Fable 5.2, same seat, 2026-11-10 21:07 PST.
Reviewed head: `0cafbe4bf60c8cdf721c8f08be8e936dbbea8ab7` (test commit
`6a3899361`). Round-2 report: `docs/run_reports/2026-11-10-agent-identity-flake-r2.md`.

### Final verdict: ADMIT, once the Linux shard is green

F1, F2 and F3 are closed on the evidence I can produce on Darwin. The flake
was Linux-only and the new waiters have not yet run on Linux: the PR's test
shards were still pending when I finished. Merge when the shard that runs
`tests.test_agent_identity` reports 14 tests, 0 failures, and exactly one skip
(the Darwin-only ancestor test).

### Closure

| Finding | Status | Evidence |
|---|---|---|
| F1 dead group leader | Closed | Fixture is `pgid = agent_pid + 1`. The foreign-group mutant now fails the hazard test (my own run, not the seat's). |
| F2 root cause | Closed | The first-round report drops the 60-second lifetime, cites the CI timings and image, and marks the multicall hypothesis unverified with the runner check. |
| F3 shared live fixture | Closed on Darwin; Linux pending CI | No `symlink_to("/bin/sleep")` remains. `_live` raises `AssertionError` on early exit, readiness timeout and argv timeout; no `SkipTest` path is left in it. |

`joulewise/` and `scripts/` are still unchanged against `origin/main`.
Native runs on the Air: 14/14 OK on 16 consecutive runs with
`-W error::ResourceWarning`, ancestor test active, no leftover children.

### Do the waiters still exercise what the matcher reads?

Yes. The matcher reads the kernel executable path and the kernel argv; it
never reads `comm`. For a live waiter named `claude` the kernel reported:

- executable: the real Homebrew Python binary (`.../Python.app/Contents/MacOS/Python`)
- `argv[0]`: the marker path ending in `claude`
- `identify` on that pair: `agent`; with `argv[0]` swapped for the executable
  path: `not_agent`

That is the same shape as the old fixture (non-agent executable, agent-named
`argv[0]`), so the live tests cover the `argv[0]` rule and the non-agent
executable rule exactly as before. An agent recognised by its executable
basename is covered only by the table tests, as it was on `main`.

Mutants against the kernel-read layer, whole module, in process:

| Mutant | Live tests that fail |
|---|---|
| kernel argv unreadable | listed-window, multiline, own-tree, node, ancestor |
| kernel `argv[0]` replaced by the executable path | the same five |
| kernel ppid and pgid lost | own-tree |
| `identify` ignores the `argv[0]` name | own-tree (plus three table tests) |
| `identify` always `agent` | listed-window, multiline (plus table tests) |

The round-1 wiring mutants give the same results as before.

### Notes (none blocking)

- D1. Linux exposure of the waiter. It starts the interpreter with a made-up
  `argv[0]`. I believe CPython on Linux derives its library path from
  `argv[0]` and falls back to the compiled-in prefix, which works for the
  hosted runner's Python but may not for a relocatable build such as a
  uv-managed one. I could not run Linux here. If it bites, the symptom is a
  hard `child exited without readiness`, not a flake. Adding the child's
  stderr to that assertion message would make it diagnosable in one read.
- D2. `AgentIdentityTests.setUp` still skips the whole class when
  `inspect(os.getpid())` returns None. With the kernel reader forced to None,
  11 tests skip. This is unchanged from `main` and outside this PR; it is the
  one remaining way a reader regression hides as skips.
- D3. `docs/run_reports/interp-energy-desk/flake-r2-sol-report.md` repeats the
  stale pattern N3 named: "no push performed" and a `/Volumes/JW-EXT/...` link.
- D4. `gate-ledger` still fails on the PR body (N2).
- D5. The multicall hypothesis is still unverified. The fix no longer depends
  on it being true.
