# NV-GATE-2 Idle-Capture Regression Fix

Date: 2026-07-10
Branch/worktree: `impl/nvgate2-codenow`
Lane: `[AGENT]`; no live NVIDIA or quiet-machine measurement was performed.
Authority: lead-directed targeted DEBUG+FIX; no commits requested.

## Root cause

`handle_nvidia_smi_measure_idle` started the requested idle-duration deadline
immediately after `subprocess.Popen`, before the worker had observed any
sampler output. Under child-start or scheduling delay, the complete idle
interval could expire before the fake (or real) sampler ran. The worker then
terminated the sampler and only afterward checked the CSV, producing the
observed zero-byte artifact and structured `telemetry_unavailable` result.

The FIX-1 PID-fingerprint path was ruled out as the direct cause: idle capture
uses its local `Popen` object and never calls `_pidfile_matches_live_process`.
PATH was also correct: the worker metadata carried the expected command and a
direct capture with the same environment resolved and ran the fake sampler.
The defect was the ordering at the old deadline assignment (pre-fix
`joulewise/adapters/node_worker.py:803`), not the fake executable.

## Fix

Idle capture now uses the existing first-parseable-row NVIDIA readiness gate,
records its diagnostics in worker metadata, and starts `idle_seconds` only
after readiness succeeds. A readiness failure is returned with the gate's
specific diagnostic. The requested 80 ms NV-5 measurement duration is
unchanged; sampler startup is no longer charged against it.

A regression test delays the sampler's first output by 100 ms while requesting
a 10 ms idle capture. It proves the worker waits for readiness and then runs
the requested duration; the old ordering terminates before the first row.

## Verification

- The historic in-process fake-sampler test and the delayed-readiness
  regression passed together in three consecutive fresh Python processes.
- The exact localhost contract test was attempted in each of the three runs,
  but this managed sandbox denied its initial localhost bind with
  `PermissionError: [Errno 1] Operation not permitted`; all three invocations
  loudly skipped before worker execution. This is not recorded as a pass.
- Canonical unpiped suite:

```text
Ran 1023 tests in 35.164s

OK (skipped=13)
```

- `python3 -m py_compile joulewise/adapters/node_worker.py
  tests/test_node_worker.py` passed.
- `git diff --check` passed.

## Handoff

The lead's next exact NV-GATE-2 step is to run both named tests three
consecutive times in a socket-capable session, then review and land the three
code/test/report/bookkeeping file groups by pathspec. Live NVIDIA promotion
remains gated by P1-006.
