```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Both fixes verified; no new source defect found. Whole-class green remains blocked by a journal watchdog failure reproduced once alone.",
  "workspace": {
    "base_requested": "e32ea56c",
    "base_mode": "exact",
    "head_start": "3855ad25bc405236032daf53dfbc472c67ccdf03",
    "head_end": "3855ad25bc405236032daf53dfbc472c67ccdf03",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [],
  "flags": [
    {
      "id": "V-GAP-01",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "D4 is not green: the class had two external-watchdog failures. One passed its isolated rerun; journal_block again exceeded 8 seconds.",
      "needs": "Lead to resolve the remaining watchdog failure and obtain a green class run."
    },
    {
      "id": "ENV-01",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Required fixture-orphan census could not observe processes because the sandbox denied ps.",
      "needs": "Lead to run the read-only fixture census in an environment permitting ps."
    }
  ]
}
```

## Findings

No new source defect found. D1–D3 and D5 passed; D4 remains unverified as green. Repository files were unchanged. Scratch probes are under `/tmp/ref-delta-28ff4b28/`.

**D1 — Ordering restored.**

Executed:

```sh
nl -ba tests/night_gate_fixtures/bind_supervision.py | sed -n '175,187p'
git show 6ec5b460:tests/night_gate_fixtures/bind_supervision.py | nl -ba | sed -n '173,179p'
rg -n 'ack_until' tests/night_gate_fixtures/bind_supervision.py
```

At `3855ad25`, `_BindTask(...)` is constructed at line 183; `row['task']` is assigned at 184; the deadline is evaluated at 185; the row enters `self.tasks` at 186. At base `6ec5b460`, construction occupies lines 173–175, followed by deadline evaluation in the appended dictionary at 178.

The only deadline read is enforcement at head line 240, inside `Bench.sleep`’s iteration over `self.tasks`. `controls()` also traverses that list. Neither can observe the unpublished row’s temporary `None`. The launcher closure accesses `max_arg_bytes`, not `ack_until`.

Executed the [mocked-time probe](/tmp/ref-delta-28ff4b28/ack_probe.py):

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-delta-28ff4b28/ack_probe.py
```

It uses the real `_BindTask` constructor, a launcher whose submission consumes 250 ms, and real `Bench.sleep`/`controls`. It also invokes the argument closure during submission and verifies that the row remains unpublished.

```text
6ec5b460: construction=0.250s deadline=11.25 sleep_at=11.10 -> waited 0.001s; row unpublished during submit
e32ea56c: construction=0.250s deadline=11.00 sleep_at=11.10 -> fault ACK missing: normal probe; row unpublished during submit
3855ad25: construction=0.250s deadline=11.25 sleep_at=11.10 -> waited 0.001s; row unpublished during submit
```

Exit 0. Head is base-equivalent for the reported regression.

**D2 — Positive floor bites.**

The [mutation probe](/tmp/ref-delta-28ff4b28/floor_probe.py) runs the actual new test against scratch fixture copies. Both copies redirect imports to this audited worktree; only the mutant deletes the recording assignment. Temporary test artifacts remain under the scratch directory.

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-delta-28ff4b28/floor_probe.py intact
```

```text
intact: tasks=7 max_arg_bytes=[271, 1932, 2647, 936, 271, 2667, 2667]
Ran 1 test in 2.354s
OK
```

Exit 0.

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-delta-28ff4b28/floor_probe.py mutant
```

```text
mutant: tasks=7 max_arg_bytes=[0, 0, 0, 0, 0, 0, 0]
AssertionError: 0 not greater than 0
Ran 1 test in 2.531s
FAILED (failures=7)
```

Exit 1, as expected. Each failure points to the added assertion at `tests/test_run_night.py:4619`.

**D3 — Nothing else moved.**

Executed:

```sh
git diff e32ea56c 3855ad25
git diff --numstat e32ea56c 3855ad25
git diff --check e32ea56c 3855ad25
```

```text
2	1	tests/night_gate_fixtures/bind_supervision.py
1	0	tests/test_run_night.py
```

The complete diff contains only:

- `ack_until=time.monotonic()+1` → `ack_until=None`.
- Post-construction assignment `row['ack_until'] = time.monotonic() + 1`.
- `self.assertGreater(task['max_arg_bytes'], 0)`.

`git diff --check` exited 0. The D1 probe also compared the complete original incremental-test method from both revisions and counted its assertions:

```text
D3: full incremental method byte-identical to base; four assertions unchanged; base/head lines 4605-4611
```

**D4 — Whole class did not pass.**

Executed with `pipefail` and a retained log:

```sh
set -o pipefail
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests 2>&1 | tee /tmp/ref-delta-28ff4b28/class.log | tail -4
```

```text
----------------------------------------------------------------------
Ran 22 tests in 80.086s

FAILED (failures=2)
```

Exit 1. Both failures were exclusively the external 8 s watchdog:

- `test_blocked_journal_never_blocks_deadline_or_grants_go`: `journal_block`.
- `test_blocking_join_startup_and_post_publication`: `startup_hang`.

Each was rerun once, separately:

```sh
set -o pipefail
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go 2>&1 | tee /tmp/ref-delta-28ff4b28/rerun-journal.log | tail -4
```

```text
----------------------------------------------------------------------
Ran 1 test in 8.007s

FAILED (failures=1)
```

Exit 1; again `external watchdog (8 s): bind supervisor blocked in journal_block`.

```sh
set -o pipefail
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_blocking_join_startup_and_post_publication 2>&1 | tee /tmp/ref-delta-28ff4b28/rerun-startup.log | tail -4
```

```text
----------------------------------------------------------------------
Ran 1 test in 9.505s

OK
```

Exit 0. This method runs two scenarios, each with its own watchdog.

Load averages were sampled using:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -c 'import os; print(os.getloadavg())'
```

| Run | Before: 1/5/15 min | After: 1/5/15 min |
|---|---|---|
| Whole class | 6.260 / 3.310 / 2.253 | 6.396 / 4.192 / 2.697 |
| Journal alone | 6.396 / 4.192 / 2.697 | 5.938 / 4.199 / 2.725 |
| Startup/post-publication alone | 5.938 / 4.199 / 2.725 | 5.393 / 4.185 / 2.754 |

Load may contribute; these observations do not establish causation.

**D5 — No new matching defect found.**

The probe compared every pre-task dictionary initializer across base, round 0, and head:

```text
D5 round-1 initializer delta: ack_until only; began=self.now unchanged expression
```

Inspection covered all fields at head lines 175–177:

- `kind`, `mode`, `control`, `child`: already-bound local values.
- `buffer`, `events`, `ack`, `eof`, `sent`, `max_bytes`, `max_reads`, `max_buffer`, `result_checked`: constant initial state.
- `began=self.now`: fake time changes only during initialization and `Bench.sleep` (lines 123 and 310), not task construction/submission.
- `max_arg_bytes=0`: initialized before the launcher can record it and never reset afterward; D2 demonstrates the added assertion rejects the default.
- `ack_until=None`: replaced before publication, as demonstrated in D1.

The test exercised seven task rows; the fix introduced no new conditional or iteration that bypasses the assertion.

## Residual risk

A green whole-class result remains outstanding. No Linux execution or full-suite replay was performed.

The required observational census was attempted:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B scripts/fixture_orphan_census.py --fail-on-orphans
```

```text
{"error": "PermissionError: [Errno 1] Operation not permitted: 'ps'"}
```

Exit 2; orphan count is unknown.

Final `git status --short --branch` reported only `## HEAD (no branch)`. HEAD remained `3855ad25bc405236032daf53dfbc472c67ccdf03`; tracked diff and untracked-file checks were empty. The next step belongs to the lead: resolve the journal watchdog gate and obtain a green class run.

same-signature: none found