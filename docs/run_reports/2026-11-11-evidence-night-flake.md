# Evidence-night builder-error cleanup flake — 2026-11-11

Branch: `fix/2026-11-11-evidence-night-flake`, based on local `origin/main`
at `f6b1573bd`. This is offline fixture/tooling work; no measurements were
collected and no study outcomes, model weights, network operations, or
coordination-state updates were needed.

## Root cause and change

`tests.test_evidence_night` imports `joulewise.evidence_night` as `entry`.
`prepare` waits for `git clone`, checkout and fetch through `subprocess.run`.
Waiting for fetch does **not** wait for the automatic maintenance it can
detach. The traced production command chain was:

```text
prepare
  git -C MEASUREMENT fetch -q origin main
    git maintenance run --auto --quiet --detach
      git gc --auto --quiet --no-detach
        git repack ...
          git pack-objects ...
```

The injected builder raises immediately after the clone checkpoint and
checkout checks. `main` prints the unexpected-exception traceback and
returns 1, while that maintenance child can still write under the
measurement clone's `.git`. A later builder/plan/render path usually gives
it more time, explaining why this early-error test exposes the race.

The controlled reproduction held the real maintenance child in a synthetic
`pre-auto-gc` hook until the CLI returned, then released it and awaited its
terminal Git Trace2 event. Native Git commands subsequently changed
`.git/objects/pack/*`, `.git/objects/info/commit-graph`,
`.git/objects/info/packs`, `.git/info/refs`, and reflogs. Both native child
commands and before/after file metadata were recorded. The harness hook
only coordinates scheduling; Git itself performs the observed clone writes.

Production now uses `fetch --no-auto-maintenance`. It prevents the writer
from starting, including when a builder raises. This avoids adding process
census, termination heuristics, persistent clone configuration, cleanup
retries, or suppressed cleanup errors. Clone, checkout, fetch, ancestry
verification and the existing exit-1 traceback remain in place.

## Changed files

- `joulewise/evidence_night.py`: suppress automatic maintenance on the
  preparation fetch, with an explanation of the detached-child boundary.
- `tests/test_evidence_night.py`: extend the existing failing test to inspect
  real Git Trace2 `child_start` events and reject maintenance launches. This
  assertion fails deterministically even when maintenance finishes quickly.
- `scripts/stress_evidence_night_cleanup.py`: reusable offline stress loop
  using the exact CI test with a tiny synthetic remote containing three
  packs. Aggressive Git settings force the maintenance path; a bounded hook
  makes post-return liveness and writes reproducible. The harness releases
  and awaits the real writer before normal test cleanup and reports a
  failing assertion for the observed leak. It never retries cleanup.
- `docs/contracts/evidence_night_entry.md`: document the fetch flag and its
  child-lifetime requirement.
- This report. `scripts/test_timings.json` and the lead-owned coordination
  files are unchanged.

## Verification

Environment: macOS sandbox, Python 3.13, Apple Git 2.50.1. Test commands
used `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` to avoid personal
Git configuration. All remotes were local fixtures. No full suite was run
because the brief explicitly forbids it.

| Check | Before fix | After fix |
| --- | --- | --- |
| `python3.13 -B -m unittest tests.test_evidence_night` | 168 passed, 481.503 s | 168 passed, 268.213 s |
| Existing single test, before adding the new assertion | 1 passed, 2.932 s | Covered by module |
| Single test with new Trace2 assertion | 1 failed as expected, 2.178 s: detached maintenance launched | Covered by module |
| Initial unheld stress, 200 repetitions | Existing assertions: 200 passed; 4 returns had live Git children; 143.935 s | Superseded by controlled stress |
| `python3.13 -B scripts/stress_evidence_night_cleanup.py --runs 20` | 20 expected assertion failures, 0 errors; 20 live children and 20 post-return write observations; 5.639 s | See 200-case run |
| `python3.13 -B scripts/stress_evidence_night_cleanup.py --runs 200` | See controlled 20-case run | Final script: 200 passed, 0 failures/errors, 0 live children, 0 post-return writes; 51.934 s |

Two harness development errors (trace destination and Git's hook placement)
were corrected before the definitive controlled counts above. Their runs
are excluded from those counts. An attempted `nice` adjustment was denied
by the sandbox; no extra CPU workers were started. The initial stress used
a temporary script; the controlled reproducer is the committed script.
The initial 2.932-second single-test probe briefly overlapped the baseline
module; subsequent test runs were sequential.

Syntax parsing passed for all three changed Python files, and
`git diff --check` passed. An earlier post-fix 200-case run also passed
(38.369 s); the final run above additionally verifies the script's
personal-config isolation and missing-zsh guard. Total test execution,
including short development probes, stayed below approximately 20 minutes.

## Limits and handoff

The initial module and unheld stress did not reproduce the original Ubuntu
`ENOTEMPTY` exception. The deterministic failure is the lifetime assertion:
a real child remains active and writes after the CLI returns.
This establishes the production leak without relying on deletion timing;
it does not claim an independently reproduced hosted cleanup traceback.
Hosted Ubuntu/Python 3.13 confirmation remains the next CI check.

No MLX code changed and no native MLX validation is required for this fix.
No scientific or contract-semantics ruling is outstanding. The final local
commit contains these changes and this report; no push is authorized.
