```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Replay-3 contains one pre-existing load-sensitive localhost-test timeout (c) and one wave-2 test-fixture defect exposed by removing a skip (a); neither identifies a wave-2 production defect.",
  "workspace": {"base_requested":"f14309066f762f7f70569af3d9732544b39c81d8","base_mode":"exact","head_start":"f14309066f762f7f70569af3d9732544b39c81d8","head_end":"f14309066f762f7f70569af3d9732544b39c81d8","upstream_end":null,"branch":"feat/2026-09-04-replay-diag"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/30-replay-3-failure-diagnosis.md"],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row":"node-worker-localhost","classification":"c","action":"wait_for","wait_for":"agent fan-out/load to quiesce before an optional socket-capable replay","basis":"identical on main and wave-2; failed before wave-2; historically passed 3x on this Mac; Linux PR #285 green; 15 s is test-only while production prepare uses 900 s"},
      {"row":"real-boot-arm-evidence","classification":"a","action":"start_now","wait_for":"","basis":"wave-2 removes the skip but compares a fabricated 2e18 ns R0 offset with a real Mac author anchor; production T-0 author bytes are unchanged"}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git diff --exit-code f1430906 c5218527 -- joulewise/adapters/node_worker.py joulewise/adapters/node_client.py tests/test_node_worker_subprocess.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V2","kind":"inspection","cmd":"git log f1430906 --format='%H %ad' --date=iso-strict -S'timeout_s=15.0' -- tests/test_node_worker_subprocess.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["7862eb5c8e59134d95753b42138061f07c9c4213 2026-07-10T21:59:34-07:00","b24f25c1ec66b7b6c889973d1e3e99aca7e65d44 2026-07-10T21:26:39-07:00"]},"expected":{"exit_code":0,"tail_regex":"7862eb5c[\\s\\S]*b24f25c1"}},
    {"id":"V3","kind":"other","cmd":"probe=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/jw-node-worker-manual-cucj7i13; PATH=$probe/bin:$PATH python3 $probe/remote/node_worker.py --task $probe/remote/nv5-localhost-contract/tasks/task-runtime-prepare.json --artifacts $probe/remote/nv5-localhost-contract/artifacts/task-runtime-prepare --work-root $probe/remote","cwd":".","observed":{"result":"fail","exit_code":1,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V4","kind":"test","cmd":"/usr/bin/time -p python3 -m unittest tests.test_node_worker_subprocess.NodeWorkerSubprocessTests.test_real_client_worker_artifact_contract_over_localhost","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["NV-5 ACCEPTANCE GATE SKIP: localhost sockets unavailable; real client-worker subprocess parity was not exercised (PermissionError: [Errno 1] Operation not permitted)","Ran 1 test in 0.000s","OK (skipped=1)","real 0.49"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)"}},
    {"id":"V5","kind":"other","cmd":"python3 -c 'from joulewise.clock_reference import sample_anchor; import time; r=[]; [(lambda a: (r.append((a.realtime_ns-a.monotonic_raw_ns,a.read_skew_ns)),time.sleep(.02)))(sample_anchor()) for _ in range(10)]; o=[x[0] for x in r]; s=[x[1] for x in r]; d=[abs(x-2_000_000_000_000_000_000) for x in o]; print(f\"10 samples: offset_ns {min(o)}..{max(o)} (spread {max(o)-min(o)} ns); read_skew_ns {min(s)}..{max(s)}; delta_from_fixture_ns {min(d)}..{max(d)}\")'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["10 samples: offset_ns 1788406507313462063..1788406507313462959 (spread 896 ns); read_skew_ns 125..709; delta_from_fixture_ns 211593492686537041..211593492686537937"]},"expected":{"exit_code":0,"tail_regex":"10 samples: offset_ns .*spread .* ns"}},
    {"id":"V6","kind":"inspection","cmd":"tail -n 180 /Users/edr/.claude/jobs/3c46c831/tmp/int-fan-wave2-replay-3.log","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5116 tests in 6929.138s","FAILED (failures=1, errors=1, skipped=110)","rc=1"]},"expected":{"exit_code":0,"tail_regex":"Ran 5116 tests[\\s\\S]*FAILED"}},
    {"id":"V7","kind":"inspection","cmd":"git diff --exit-code f1430906 c5218527 -- joulewise/arm_readiness_evidence_t0.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"environment","level":"nonblocking","text":"This managed seat denies localhost bind and kern.bootsessionuuid, so its direct worker probe takes the sandbox refusal path and its main test replay skips; the socket-capable failure evidence is the exact lead replay log plus the prompt's isolated-main observation.","needs":"If desired, repeat only the named localhost method after the concurrent seats exit."},
    {"id":"F2","kind":"residual_risk","level":"nonblocking","text":"The test passes the same 15 s value to the worker's inner readiness budget and the outer subprocess transport, leaving no status-write grace after an inner deadline. Production vLLM prepare uses 900 s, so this is not replay-3 evidence of a production regression.","needs":"Keep as ledgered environment sensitivity, or separately harden the test transport/budget on main."}
  ]
}
```

## Scheduling matrix

Row | action | wait_for | collision surface
---|---|---|---
localhost worker | wait_for | Optional socket-capable replay after agent fan-out quiesces | None: all three files are byte-identical `f1430906..c5218527`
real-boot ARM test | start_now | — | `tests/test_arm_readiness_evidence_t0.py` only; fixture-modernization ownership

## Critical path

None. The two rows are independent.

## Diagnosis

### 1. Localhost node worker — verdict **(c)**

This is a pre-existing **test-harness load/environment sensitivity**, not a wave-2 defect and not evidence of a production timeout. Replay 3 fails on the first `runtime.prepare`: the outer `subprocess.run` kills `node_worker.py` at 15.0 s, collection finds no `status.json`, and the exact suite tail is:

```text
Ran 5116 tests in 6929.138s
FAILED (failures=1, errors=1, skipped=110)
rc=1
```

The same signature is already in the wave-1 replay. `git diff` proves worker, client, and test bytes identical between main and wave-2. `git log -S` dates the 15 s literals to the July 10 NV-GATE-2 test work; `cd6e2cba` records a socket-capable lead 3× green replay on this Mac. PR #285's Linux CI is green, and the prompt records the current isolated failure on main.

What occupies the worker interval is bounded by source: after logging `worker started` and `task validated`, `handle_vllm_prepare` chooses a port, starts the fake `vllm`, samples `ps` (2 s cap), and polls `/health`. The task JSON turns the caller's 15 s into the inner readiness deadline, while `LocalSubprocessTransport` uses the same 15 s as the outer kill deadline. If health is late, the worker reaches its own deadline with no time to terminate the child and atomically write status. Worker stderr is normally empty; diagnostics go to `worker.log` and `state/vllm.stderr`. The managed-seat hand replay of the same prepared JSON took 0.129469 s with empty stdout/stderr, but its socket bind was denied before launch; it wrote a structured failure status, so it cannot reproduce the ordinary-host wait.

Production constants differ: `VllmRuntimeAdapter.prepare` supplies **900 s**; the worker's default readiness ceiling is 300 s. The 15 s value is confined to this integration test. Minimal disposition: no wave-2 cure. Exact ledger wording:

> ENVIRONMENTAL / PRE-EXISTING TEST SENSITIVITY: NV-5 localhost fake-vLLM prepare exceeded the test-only 15 s budget under concurrent Mac load; identical main/wave-2 bytes, earlier same-Mac 3× green, and green Linux CI exclude a wave-2 regression. Re-run after fan-out quiesces; production prepare remains 900 s.

If recurrence itself is unacceptable, a separate main-side harness cure is to give the fake prepare a materially larger test budget and an outer status-write grace; do not change production's vLLM budget for this evidence.

### 2. Real-boot ARM transaction — verdict **(a)** (test defect)

Main has a structural `@unittest.skip` for `FIXTURE-MODERNIZATION-01`; wave-2 removes it after modernizing R1 fixtures. `joulewise/arm_readiness_evidence_t0.py` is byte-identical. The newly active real-boot case passes `synthetic_clock=False`, yet its R0 capture still comes from `_clock_reference_value` with the default fictional offset:

```text
anchor_realtime_ns = 2_000_000_000_000_000_000 + anchor_monotonic_raw_ns
```

The author anchor is real. Ten current samples under load measured real `realtime_ns - CLOCK_MONOTONIC_RAW` at `1788406507313462063..1788406507313462959 ns`: only **896 ns** spread, with **125..709 ns** read skew. The fixture-to-real delta is therefore `211593492686537041..211593492686537937 ns` (about 6.71 years), deterministically over 5 ms. This is not scheduler load.

The **5 ms ceiling is a production invariant**, enforced by the T-0 author and ARM consumer and explicitly declared authoritative/non-waivable in `scripts/quiet_window_clock.sh`; it must not be relaxed. The artefact is the incoherent test R0. Minimal cure: for `synthetic_clock=False`, construct R0 from a contemporaneous real `realtime_ns - CLOCK_MONOTONIC_RAW` offset (or keep this real-boot-only test on one coherent synthetic clock), then retain boundary tests at 5 ms ± 1 ns. Exact failing tail:

```text
joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError:
R0-to-author RAW anchor delta exceeds 5000000 ns
```
