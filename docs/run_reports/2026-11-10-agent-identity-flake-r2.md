# Agent-identity flake round 2 — Fable F1–F3

Date: 2026-11-10. Seat: local Sol, `flake-r2`.
Branch: `fix/2026-11-10-agent-identity-flake` (the brief's branch, already
checked out). Starting head: `b1c98c80f33ceb49db34394bf268488a97060072`.
Review: [Fable cold review](2026-11-10-agent-identity-flake-fable-review.md).
Commit subject: `test: harden remaining live agent identity fixtures` (this
report accompanies the implementation in the same local commit).

## Changes and disposition

**F1 addressed.** The hazard wiring fixture now models an orphan with parent 1
and `pgid = agent_pid + 1`. Its group leader is absent from the closed process
table. This exercises `in_tree`'s group ancestry branch, keeping the foreign
agent outside the caller's tree. The matcher and production code are unchanged.

The in-process mutation witness produced:

| Fixture and matcher | Hazard test result |
|---|---|
| Corrected fixture, real matcher | PASS, no skips |
| Corrected fixture, any foreign group counts as owned | FAIL at `assertFalse(census["clean"])`, no errors or skips |
| Previous `pgid == pid` fixture, same mutant | PASS, no skips (demonstrates the lost coverage) |

The mutant retained the real ancestry behavior and added the erroneous group
acceptance, using `mock.patch.object(agent_identity, "in_tree", mutant)`:

```python
original = agent_identity.in_tree

def mutant(pid, root, inspector=agent_identity.inspect, info=None):
    if original(pid, root, inspector, info):
        return True
    info = info if info is not None else inspector(pid)
    return bool(info is not None and info.pgid and info.pgid != pid and info.pgid > 1)
```

Each run loaded just
`AgentIdentityTests("test_the_hazard_arm_census_uses_the_same_matcher")`
into `unittest.TestSuite` and checked failure/error/skip counts. For the third
row, an in-memory copy of the test module changed only the new `agent_pid + 1`
group back to `agent_pid`; no on-disk mutation was made.

**F2 addressed.** The [first-round report](2026-11-10-agent-identity-flake.md)
now states that CI timing rules out 60-second expiry (0.040 s for the module,
about 3 ms for the sampled hazard test). It attributes the five sampled
ubuntu-26.04 failures and their timings to Fable's review; this seat did not
fetch logs. Multicall coreutils dispatch on argv[0] is the leading hypothesis,
explicitly unverified on an ubuntu-26.04 runner. That report includes the
one-line symlink invocation check. Local Darwin success does not establish the
Linux runner's behavior. The forced-exit replay remains a mechanism witness,
not evidence that expiry happened in CI.

**F3 addressed in code; native runner confirmation remains open.** Every live
sleep symlink in the module is replaced by `_named_waiter`, including the
Darwin ancestor test's foreign window and owned `codex` child. The waiter runs
the current interpreter with an explicit argv[0], writes a readiness byte, and
blocks reading the parent's stdin pipe. Its lifetime has no sleep deadline.
The trailing `60` argument is inert, retained for the multiline census-row
assertion. The live Node fixture now also sends the readiness byte.

The matcher reads the kernel executable path and argv[0]; `comm` is not used
for identity. A prototype found that Homebrew's `sys.executable` wrapper on
Darwin replaces argv[0] during re-exec, so the fixture instead uses the native
executable path returned by `inspect(os.getpid())`. A second live prototype
confirmed exact kernel argv and an `agent` verdict with a `codex` argv[0].
The own-tree case now exercises both `claude` and `codex`, first proving that
the real census keeps each as an agent, then that it ignores each as owned.

`_live` requires both child readiness and exact kernel argv before returning.
Early exit, readiness timeout, and argv timeout raise `AssertionError`, never
`SkipTest`. Failure cleanup kills and waits for the owned child and closes
all three pipes. Successful children are registered for unittest cleanup;
named waiters also exit on parent pipe closure. A committed regression test
checks that a real early-exiting child fails and is reaped with its pipes
closed. The real `inspect`, `identify`, `in_tree`, and `filter_census` still run
unmodified in the live cases; no decisions are mocked or cached there.

The [interp-energy-desk report](interp-energy-desk/agent-identity-flake-sol-report.md)
now uses repository-relative links and removes the stale publication claim.
The committed Fable review is preserved unchanged.

## Verification

Environment: Darwin, Python 3.13.18. Before edits the module discovered 13
tests: 12 passed, one sandbox skip. After edits it discovers 14: 13 pass,
one sandbox skip. The sole skip is `AncestorCensusLiveTests`, because
`/usr/bin/pgrep` exits 3 with `Cannot get process list`; none comes from `_live`.
Fable's native 13/13 first-round results are distinguished from these sandbox
counts in the corrected first-round report.

| Command/check | Result |
|---|---|
| Baseline: `python3.13 -B -m unittest -v tests.test_agent_identity` | 13 discovered, 12 passed, one sandbox skip |
| `python3.13 -B -W error::ResourceWarning -m unittest -v tests.test_agent_identity` | 14 discovered, 13 passed, one sandbox skip; no resource warnings |
| Same final command, 50 serial processes | 50/50 successful; 17.322 s wall time |
| Same final command, 25 rounds of two concurrent processes | 50/50 successful; 10.044 s wall time |
| Foreign-group mutation witness above | Corrected test kills mutant; previous fixture admits it |
| Readiness timeout fault injection (`select.select` returns no ready fd) | Hard failure; real child reaped; all pipes closed |
| Kernel-argv timeout fault injection (bounded mocked clock after readiness) | Hard failure; real child reaped; all pipes closed |
| `python3.13 -B -m compileall -q tests/test_agent_identity.py` | Exit 0 |
| `compile(_ANCESTOR_CENSUS_CHILD, '<ancestor census child>', 'exec')` | Pass; syntax only, no native ancestor claim |
| `git diff --check` | Exit 0 |
| Production and coordination path diff checks | No changes to `joulewise/`, `scripts/`, or the user-protected coordination paths |

The stress harness launched exactly the final unittest command above with
`subprocess.Popen`, captured combined stdout/stderr, and imposed a 60-second
timeout per process. Serial width was one; concurrent width was two, launching
both before collecting either. Every receipt required return code 0, `Ran 14
tests`, `OK (skipped=1)`, exactly the named sandbox skip, and no `FAILED`,
`ERROR`, or `ResourceWarning`. It checked that each phase wrote 50 logs.
These were test subprocesses, not additional agent sessions.

Local diagnostic receipts (not committed):

- Directory: `/private/tmp/agent-identity-flake-r2-hrqo4pf5/`.
- `summary.json` records the executable, Python version, counts, and timings.
- Serial logs `serial-01.log` through `serial-50.log`, concatenated in filename
  order, SHA-256:
  `eb9a43f8d7cfd7419145bfc30d26a6412d49f7476e86b85fd6b2015cdca26ef2`.
- Concurrent logs `concurrent-01.log` through `concurrent-50.log`, concatenated
  in filename order, SHA-256:
  `63df34c17c712084d0c783484eaa8bc371d0fdd9fc5ee7da857435f185818c0c`.

## Scope, uncertainty, and next exact steps

The explicit brief selected this bounded `[AGENT]` repair over the ordinary
queue. Intake found no active stop card and a clean tree at the specified
head. This seat made no network requests, downloaded no weights, read no real
measurement inputs or sealed custody, and left the running analysis job alone.
The speed toolbox was read from `origin/main`; this is a fixture repair with
no pipeline optimization or measurement behavior change. The full suite was
not run under the user's machine-load restriction. Focused checks and stress
runs stayed far below the approximately 20-minute test budget.

Changed repository files:

- [tests/test_agent_identity.py](../../tests/test_agent_identity.py)
- [First-round report](2026-11-10-agent-identity-flake.md)
- [Interp-energy-desk Sol report](interp-energy-desk/agent-identity-flake-sol-report.md)
- This round-2 report.

No coordination files or kernel tasks were edited or registered. No pushes,
merges, deployments, or external PR edits were performed by this seat. The
review's N2 PR-body gate-ledger finding is outside this offline code repair and
remains for the lead; N4's optional wrapper cleanup was not taken.

There is no blocking implementation question. Linux and Python 3.11 were not
available in this seat. To finish runner validation, the lead should:

1. On ubuntu-26.04, run the first-round report's one-line `/bin/sleep` check
   and `python3.13 -B -m unittest -v tests.test_agent_identity`; also run the
   module with Python 3.11. Repeat the bounded serial/concurrent stress checks
   there before calling the runner-specific failure closed.
2. Outside the Darwin sandbox, run
   `python3.13 -B -m unittest -v tests.test_agent_identity.AncestorCensusLiveTests`.
   That test's new waiter integration has syntax verification here, but its
   real `pgrep` ancestor path has not run in this seat.

No MLX code changed, so no native MLX test is required for this repair.
