# Agent identity census test flake — 2026-11-10

Branch: `fix/2026-11-10-agent-identity-flake`.
Baseline: `origin/main` at `6b91f64284a79c30bb370e3fdccf8c205a24f9a6`.
Test fix: `bbb01c8c3` (`test: stabilize agent census wiring fixtures`).
This report is the companion documentation commit.

## Diagnosis and uncertainty

The defect is a test fixture consistency assumption. Both failing tests supply
**synthetic census output**, assembled from their own children's launch arguments,
then let the real matcher inspect those PIDs later. The census input does not
contain arbitrary processes from another test. In the reported diff, the extra
`.../night-custody/.../run_campaign 60` row belongs to the failing test's own
window fixture.

`filter_census` intentionally retains a row when the later kernel inspection
cannot verify its argv. Thus, a window that exits or becomes unreadable between
readiness and filtering remains in stdout, producing exactly the reported extra
window row. The tests incorrectly require that row to disappear regardless of
whether the kernel can still verify it. Waiting for argv once in `_live` does
not guarantee a later read of a finite-lived `sleep 60` child.

The hazard test adds another lifecycle problem: it deliberately orphans a
grandchild, registers only `os.kill` for cleanup, and cannot `wait()` for it.
Its readiness loop also falls through on timeout and rereads the process after
the loop. Neither that orphan nor another test's leftover process can directly
add an unlisted PID to these synthetic census inputs.

The spontaneous CI event was **not reproduced** here: the unchanged module
passed 50 serial runs and five rounds of three concurrent copies. An additional
100 repetitions of `AgentIdentityTests` recorded 1,400 inspections of tracked,
still-running children with no missing, empty, or changed argv. These results
do not establish which OS event caused the original verification failure, and
do not prove that a child actually reached its 60-second lifetime in CI.

A controlled replay does establish the failing mechanism. Against the unchanged
tests, a temporary in-process harness retained each `_live` child and killed and
waited for only the window fixture after census text construction, before the
second census was filtered. For the named-agent test this was the `codex`
subtest; for the hazard test it was the second arm call. Each test produced
exactly one assertion failure, zero errors, and the reported extra-window-row
shape:

```text
expected: <agent-pid> .../codex 60
actual:   <window-pid> .../night-custody/b5-gamma-attempt3/custody/run_campaign 60
          <agent-pid> .../codex 60
```

The hazard replay had the same shape with `claude`. This is a controlled
test-fixture replay, not evidence that an actual CI child exited. No matcher
bug was found; its conservative handling of unverifiable rows is intentional.

## Fix

Only `tests/test_agent_identity.py` changes executable content.

- Added `_census_process_table`, which calls the **real shared filter** using
  its existing `inspector` parameter and a closed table of `ProcessInfo` fixtures.
  Missing fixture PIDs return `None`; no live process table is consulted.
- Converted the two failing wiring tests to matching census text and fixed
  process records. Their PIDs are distinct from the caller, and explicit parent
  and group links model the window and foreign agent independently of the OS.
- Removed all child launches, the orphan, and readiness polling from these two
  cases. The hazard assertion now also checks the `own_tree` reason; the named
  agent test checks `not_agent_executable` for the ignored window.
- Retained the other live kernel tests, including window exclusion, multiline
  argv, own-tree exclusion, the Node launch, and the existing ancestor test.
  Exact filtered-output assertions remain in both repaired tests.

The helper supplies process facts; it does not stub matcher decisions or cache
production decisions. `joulewise/` and `scripts/` are unchanged.

## Verification

Environment: Darwin, Python 3.13.18. Every ordinary module run discovers 13 tests:
12 pass and the existing ancestor test skips because sandboxed `/usr/bin/pgrep`
returns exit 3, `Cannot get process list`.

| Check | Result |
|---|---|
| Unchanged baseline, `python3.13 -B -m unittest tests.test_agent_identity`, repeated 50 times | 50/50 successful; one existing skip per run |
| Unchanged baseline, five rounds of three concurrent module copies | 15/15 successful; one existing skip per run |
| Unchanged baseline, 100 diagnostic class repetitions | All passed; 1,400 tracked live reads, no observed argv mismatch |
| Controlled window-exit replay of the unchanged tests | Both reported failure shapes reproduced; one expected failure per case, zero errors |
| Repaired cases, forbid `_darwin_inspect` and `subprocess.Popen` after ordinary `setUp` | Both pass; both forbidden-call mocks remain uncalled |
| Mutation witness: replace the shared filter with `CensusFilter(stdout)` | Both repaired cases fail as expected; neither can pass with the matcher bypassed |
| `python3.13 -B -m unittest -v tests.test_agent_identity` | 13 discovered, 12 passed, one existing sandbox skip |
| Requested serial loop below, repaired module | 50/50 successful; 16.157 s elapsed |
| Five rounds of three concurrent repaired module copies | 15/15 successful; 1.930 s elapsed |
| `python3.13 -B -m compileall -q tests/test_agent_identity.py` | Exit 0 |
| `git diff --check` | Exit 0 |

Exact serial command:

```sh
for i in $(seq 50); do python3.13 -B -m unittest tests.test_agent_identity || break; done
```

The loop's captured output was checked for exactly 50 `Ran 13 tests` and 50
`OK (skipped=1)` records, and no `FAILED` or `ERROR`. This avoids mistaking the
shell loop's successful `break` status for 50 successful executions.

For concurrent verification, a Python harness repeated five rounds, each
starting three `subprocess.Popen([sys.executable, '-B', '-m', 'unittest',
'tests.test_agent_identity'])` children before collecting any output. It waited
for all three per round and checked each return code, discovery count, and OK
record. These are separate unittest processes, not delegated agent sessions.

Local diagnostic receipts, outside Git:

- Serial log: `/private/tmp/agent-identity-flake-proof-wnp0b8nb/serial-50.log`;
  SHA-256 `89c7482d926b1b5a20686c3eb348b16d6a8a125af49216af298636ace9b9ac51`.
- Parallel logs: `/private/tmp/agent-identity-flake-parallel-wi632xtd/`;
  SHA-256 of the 15 log files concatenated in filename order:
  `c780897ac88c3fd256e33f1a38ae5a6e583d47b9780884d9b09b95fe842e7bfb`.

## Scope and handoff

This was the user-selected `[AGENT]` test repair. The existing requested branch
started clean at `origin/main`; no stop card was active. No network, model
weights, real measurement inputs, or quiet-machine measurements were used.
The running analysis job was left alone. The full suite was not run, per the
binding task instructions; only this module was tested, well below the test
time budget. Coordination files and kernel registration were left untouched,
as requested. The changed paths are this report and `tests/test_agent_identity.py`.

No blocking question remains. The unresolved forensic detail is the exact
native event in the original CI failure. Python 3.11 and Linux were not exercised
in this local seat. Before claiming native ancestor coverage, the lead should run
`python3.13 -B -m unittest -v tests.test_agent_identity.AncestorCensusLiveTests`
outside the sandbox where `pgrep` can read the process list. No MLX tests apply.
Commits are local only; nothing was pushed.
