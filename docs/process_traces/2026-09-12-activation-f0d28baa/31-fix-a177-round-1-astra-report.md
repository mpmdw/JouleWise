```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Scoped sleep stress to the bounded sentinel; diagnostics now expose failure reasons, and the killed cut reproduces report 19.",
  "workspace": {"base_requested":"c85a171d","base_mode":"exact","head_start":"c85a171d84d81aa83668fe0bc63f11a649d831ff","head_end":"c85a171d84d81aa83668fe0bc63f11a649d831ff","upstream_end":"ace4cc3cf545728e7327c14ba1084cbabb47e3ad","branch":"fix/2026-09-12-fixture-sentinel-controller"},
  "pathspec": ["tests/test_controller.py"],
  "unowned_dirty": [],
  "verdict": {"cause":"probable","remediation":"fixed"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"FAKE_POWERMETRICS_SLEEP_SCALE=3.5 python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 22.842s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"FAKE_POWERMETRICS_SLEEP_SCALE=6 python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 33.325s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"test","cmd":"FAKE_POWERMETRICS_SLEEP_SCALE=10 python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 1 test in 19.071s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V4","kind":"test","cmd":"FAKE_POWERMETRICS_SLEEP_SCALE=8 python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 1 test in 18.685s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V5","kind":"test","cmd":"FAKE_POWERMETRICS_SLEEP_SCALE=7 python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 36.532s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V6","kind":"test","cmd":"FAKE_POWERMETRICS_SLEEP_SCALE=3.5 python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 25.309s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V7","kind":"test","cmd":"FAKE_POWERMETRICS_SLEEP_SCALE=6 python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 1 test in 29.627s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V8","kind":"test","cmd":"python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["KILLED_CAPTURE: TimeoutExpired timeout_s=15.7 count=76","Ran 1 test in 30.601s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=1\\)"}},
    {"id":"V9","kind":"test","cmd":"python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 16.838s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V10","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 74 tests in 62.035s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V11","kind":"suite","cmd":"python3 -B -m unittest tests.test_controller -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 74 tests in 56.644s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V12","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_run_campaign tests.test_idle_admission -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 325 tests in 239.846s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V13","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V14","kind":"inspection","cmd":"git status --short\ngit diff --stat\ngit rev-parse HEAD refs/remotes/origin/main","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" M tests/test_controller.py"," tests/test_controller.py | 40 ++++++++++++++++++++++++++++++++++------"," 1 file changed, 34 insertions(+), 6 deletions(-)","c85a171d84d81aa83668fe0bc63f11a649d831ff","ace4cc3cf545728e7327c14ba1084cbabb47e3ad"]},"expected":{"exit_code":0,"tail_regex":"ace4cc3cf545728e7327c14ba1084cbabb47e3ad"}}
  ],
  "flags": [{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Linux/Python 3.11 was not rerun. CI run 34690082410 sparse-window attribution remains probable because its assertion omitted the reason.","needs":"Lead reviews the diff and reruns PR #324 CI. No scope expansion or production ruling needed."}]
}
```

## Causal chain

V1–V5 used the diagnostic-only edit. Status was succeeded at 3.5×, 6× and 7×. **8× was the smallest tested failing scale**; 10× also failed. Both reported `unknown_error`: `powermetrics admission stream did not complete the idle slice before timeout`. Stress was reaching admission.

V6–V7 temporarily gave only the mock runtime a SystemClock subclass using real monotonic busy-waits for nominal sleep durations. At 6×, admission succeeded and post drift was bounded, but summary failed with `fewer than 2 power samples inside the measured_run window (1 found); cannot integrate the measured trace`. This probe was restored before curing.

The campaign regression uses the same whole-run stress, but discards summary status at `tests/test_run_campaign.py:9551`; it checks strict validity at 9616 and derives post count at 9627. [Consult 87](/Users/edr/code/JouleWise-wt-a177/docs/process_traces/2026-09-09-rehearsal-harvest/87-consult-fixture-regression-portability-astra-report.md:135), lines 135–138 and 174, explains the 112 ms/175 ms geometry and why strict validity need not imply succeeded status.

## Remediation

The assertion now includes failure reason/message and relevant metadata. A local adapter subclass scopes stress to bounded captures; continuous sampling and capability probes run at 1×. The bounded floor is 12×: even 30 × 50 ms requests 18 seconds of sleeping against the unchanged 15-second timeout. Post count remains derived; promotion and fresh reduction checks remain.

V8 temporarily removed bounded `--no-sleep`, adding only an exception-printing observer. It produced `TimeoutExpired`, `post_idle_unavailable`, and both strict mismatches: `idle_drift does not match pre/post raw sentinel derivation`; `idle_drift_bound_w does not match effective drift derivation`. Restoring SHA-256 `cc77b1cfd7d1080952f126f6cedabc405ba25824ec7bf3d3cee15d7a67410269` produced V9 PASS.

## Disproved alternatives

No OS branches or `os.sched_*` calls exist in the fixture. SIGTERM handling is shared; `-b` is ignored, and `--no-sleep` requires `-n`.

## Residual risk

Hosted Linux remains unverified; see F1. Python 3.13.1/3.14.7 checks passed. No production edits, commit, push or hardware measurement.