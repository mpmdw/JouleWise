```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Argv portability fix preserves the large frame and catches the original defect, but moves the ACK deadline earlier.",
  "workspace": {
    "base_requested": "6ec5b460",
    "base_mode": "exact",
    "head_start": "e32ea56cf962b185d223e6df43de8ec406f339a0",
    "head_end": "e32ea56cf962b185d223e6df43de8ec406f339a0",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 0},
    "findings": [
      {
        "id": "C3-01",
        "severity": "should_fix",
        "title": "ACK timeout now includes task construction and submission",
        "path": "tests/night_gate_fixtures/bind_supervision.py",
        "line": 177
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-contract-28ff4b28/audit.py static",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["EXISTING_TEST_BYTE_IDENTICAL"]},
      "expected": {"exit_code": 0, "tail_regex": "EXISTING_TEST_BYTE_IDENTICAL"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-contract-28ff4b28/ack_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["head {\"ack_until\": 11.0, \"check_at\": 11.1, \"outcome\": \"fault ACK missing: normal sample-4\"}"]},
      "expected": {"exit_code": 0, "tail_regex": "fault ACK missing"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-contract-28ff4b28/audit.py base",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (errors=7)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(errors=7\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-contract-28ff4b28/audit.py mutant",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-contract-28ff4b28/audit.py census > /tmp/ref-contract-28ff4b28/census.out 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-contract-28ff4b28/journal_probe.py base > /tmp/ref-contract-28ff4b28/journal-base.out 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-contract-28ff4b28/journal_probe.py head > /tmp/ref-contract-28ff4b28/journal-head.out 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The permitted class fails the journal_block 8-second watchdog; that failure also reproduces with the base fixture. No native Linux execution was performed.",
      "needs": "Lead retains final class verification and hosted Linux CI verification."
    }
  ]
}
```

## Findings

**C3-01 — should_fix: restore the ACK deadline’s original starting point.**

At head, `ack_until=time.monotonic()+1` is evaluated at `tests/night_gate_fixtures/bind_supervision.py:177`, **before** `_BindTask(...)` at line 183. At base, construction occurred at lines 173–175 and the deadline was evaluated afterward at line 178. Construction creates the pipe and submits the task (`scripts/run_night.py:2102–2117`).

This reduces the ACK allowance by time spent constructing/submitting the task, including scheduling delays. The existing enforcement at `tests/night_gate_fixtures/bind_supervision.py:239` can therefore reject head where base still waits.

The controlled probe in [ack_probe.py](/tmp/ref-contract-28ff4b28/ack_probe.py:9) advances mocked time by 250 ms during submission, then checks the unchanged `Bench.sleep` logic at time 11.1:

- Base: deadline **11.25**, continues waiting.
- Head: deadline **11.0**, raises **`fault ACK missing: normal sample-4`**.

This is a behavior change beyond argv size, contrary to C3. Set `row['ack_until']` after `_BindTask` returns, before appending the row. No repository edits were made.

**C1 — frame semantics preserved.** Worker expansion is at `tests/night_gate_fixtures/bind_supervision.py:32–33`; dispatch supplies the count at lines 173–174. Both versions reach `qa.publish_observation` at line 109. Its compact JSON serialization and four-byte header are defined at `joulewise/quiet_admission.py:303–310`.

V2 invoked both worker implementations with equivalent sample specifications and captured their publication values:

| Measurement | Base | Head |
|---|---:|---:|
| JSON body | 200,757 bytes | 200,757 bytes |
| Transmitted frame, including header | 200,761 bytes | 200,761 bytes |

The frame bytes were identical. The actual head scenario in V6 returned **GO**, `max_buffer=200761`, `max_reads=2`, and `max_bytes=65536`. A frame larger than the per-tick byte allowance necessarily spans multiple ticks. The four assertions remain at `tests/test_run_night.py:4607–4611`.

**C2 — assertions unchanged; regression is defect-shaped with instrumentation retained.** V2 compared the complete existing test method against `git show 6ec5b460:tests/test_run_night.py`; it was byte-identical.

The base fixture was extracted without modifying the worktree:

```sh
git show 6ec5b460:tests/night_gate_fixtures/bind_supervision.py > /tmp/ref-contract-28ff4b28/base/tests/night_gate_fixtures/bind_supervision.py
```

V4 ran the new test against that fixture using a `/tmp` fixture root and repository `PYTHONPATH`. It produced seven `KeyError: 'max_arg_bytes'` errors. That alone establishes an instrumentation dependency, not the size defect.

V5 retained head instrumentation and restored parent-side `'x' * 200000` expansion in a separate `/tmp` copy. The unchanged new test failed specifically on `sample-4`:

```text
AssertionError: 200885 not less than 131072
FAILED (failures=1)
```

The static probe’s fixed scratch path measured **200,884 bytes at base versus 916 at head**, including NUL. Runtime temporary-path length explains the one-byte difference.

**C3 — remaining timing and budgets unchanged.** Beyond C3-01, diff inspection found no changes to fake-clock advancement, ACK processing, sample release, or bind deadlines (`tests/night_gate_fixtures/bind_supervision.py:188–312`). Production files are unchanged:

```sh
git diff --exit-code 6ec5b460 e32ea56c -- scripts/run_night.py joulewise/quiet_admission.py
```

This returned 0. Production limits remain four reads and 65,536 bytes per tick (`scripts/run_night.py:1998–1999`, enforced at lines 2135–2168).

**C4 — no other oversized argv string found.** V6 collected the fixture’s launcher measurements across the permitted class. Measurements use `max(len(os.fsencode(arg))+1)` at `tests/night_gate_fixtures/bind_supervision.py:181`, including NUL.

| Scenario | Largest string, bytes |
|---|---:|
| census_hit | 2,628 |
| census_stall_hit | 2,648 |
| descendant_exit | 2,628 |
| descendant_hang_late | 2,650 |
| empty | 2,628 |
| journal_block | 2,648 |
| journal_error | 2,628 |
| journal_late_power | 2,648 |
| journal_saturation | 2,648 |
| journal_system_exit | 2,628 |
| large_frame | 2,648 |
| launch_pending | 252 |
| oversize | 2,628 |
| partial_body | 2,628 |
| partial_header | 2,628 |
| postsend_hang | 2,648 |
| presend_hang | 2,651 |
| presend_hang_late | 2,650 |
| recv_stall_late | 2,650 |
| round_cost | 2,648 |
| serialize_oversize | 2,628 |
| slow | 2,648 |
| startup_hang | 1,919 |
| term_delay_late | 2,650 |

For `journal_block`, V8 logged all 23 launches observed before its watchdog expired. The large data in `oversize` and `serialize_oversize` is already generated inside workers (`tests/night_gate_fixtures/bind_supervision.py:66–75`). Descendant argv is also fixed and small (lines 46–48).

**C5 — no platform condition introduced.** Full diff inspection and an added-line scan for `skip`, `sys.platform`, and `platform.` found none. `git diff --stat 6ec5b460 e32ea56c` lists only the two test files.

**C6 — production seam correctly distinguished.** Sample argv contains only interval, observer PID, job ID, descriptor, and fixed launch arguments (`scripts/run_night.py:2306–2310`, call site line 2550). Census uses an empty request, `{}` (line 2427). It follows the generic `--request` serializer at lines 2311–2313, but its payload is small.

Static/hard requests carry the plan and, for hard checks, the static receipt (lines 2542–2548). That uncapped serialized request is the separate **BIND-REQUEST-PAYLOAD-CAP-01** lane, explicitly recorded at `docs/process/state_kernel.json:697–717`. This test-only fix does not resolve that lane.

**same-signature: none found** for the oversized fixture argv defect. C3-01 is a separate timing regression.

## Residual risk

The permitted class ran 22 tests with one failure, `journal_block` exceeding its eight-second watchdog. The instrumented replay had the same result; the other 21 tests passed. V7 reproduced the watchdog failure with the base fixture. Its cause was not established, and it is not attributed to C3-01.

Native Linux execution remains unverified. No network, canonical suite, hardware collection, or repository writes occurred. Final status was clean, detached at `e32ea56cf962b185d223e6df43de8ec406f339a0`.

Next step: restore ACK deadline placement, then have the lead verify the permitted class and hosted Linux CI.