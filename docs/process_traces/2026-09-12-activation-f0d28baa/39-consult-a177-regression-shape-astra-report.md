```json
{
"schema":"claude-codex-report/v1",
"genre":"implementation",
"status":"clean",
"completion":"complete",
"summary":"Simplified the regression by 63 lines; all 33 negative cuts failed and both controller suites passed.",
"workspace":{"base_requested":"0ff8ac04","base_mode":"exact","head_start":"0ff8ac046a1a370d08bb94b2140653942c41d2a1","head_end":"0ff8ac046a1a370d08bb94b2140653942c41d2a1","upstream_end":"0ff8ac046a1a370d08bb94b2140653942c41d2a1","branch":"fix/2026-09-12-fixture-sentinel-controller"},
"pathspec":["tests/test_controller.py"],
"unowned_dirty":[],
"verdict":{"implementation":"implemented","acceptance":"ready"},
"verification":[
{"id":"V1","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 74 tests in 67.843s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V2","kind":"suite","cmd":"python3 -B -m unittest tests.test_controller -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 74 tests in 63.662s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V3","kind":"test","cmd":"A177_CUT=no_sleep /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["A177_CAPTURE_EXCEPTION TimeoutExpired","Ran 1 test in 34.942s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=1\\)"}},
{"id":"V4","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
{"id":"V5","kind":"inspection","cmd":"git status --short\ngit diff --stat\ngit rev-parse HEAD '@{upstream}'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[" M tests/test_controller.py"," tests/test_controller.py | 105 ++++++++++-------------------------------------"," 1 file changed, 21 insertions(+), 84 deletions(-)","0ff8ac046a1a370d08bb94b2140653942c41d2a1","0ff8ac046a1a370d08bb94b2140653942c41d2a1"]},"expected":{"exit_code":0,"tail_regex":"0ff8ac046a1a370d08bb94b2140653942c41d2a1"}}
],
"flags":[{"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Hosted CI and full discovery were not run; this test-local change used both requested controller-module suites.","needs":"Lead final diff review and PR #324 CI."}]
}
```

## Change

**Part 1, recorded before editing:** use one bounded-capture witness, fixed 12x bounded stress, 1x surrounding execution, and direct real-validator assertions before and after fresh reduction. Preserve promotion, retry, teardown, and digest assertions. Remove scale-policy branches, validator mocks/probes, diagnostic payloads, the duplicated drift assertion, and the duplicated post-count formula.

I agree with eliminating validator delegation. I disagree with dropping witness consistency: timeout zero or an inflated count/interval can satisfy the stress inequality. Retain timeout-formula and argv agreement checks. All constants describe fixture policy, units, or production deadlines; no observed host count/duration is pinned.

The numbered clause inventory below also records Part 2’s observed killers. Direct assertions are terminal oracles: their cuts falsify inputs, rather than adding recursive assertions about assertion deletion.

**Part 2:** implemented; **net -63 LOC** versus the requested HEAD. No commit, HEAD movement, NEEDS_SCOPE, or NEEDS_RULING.

## Verification notes

Every table row ran the selected `HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` through unittest, with its mutation compiled **in memory**. `1/F1` means **Ran 1 test; FAILED (failures=1); exit 1**. Each row is a separate invocation.

| Clause | Cut ID / change | Killing assertion | Ran/result |
|---|---|---|---|
| 1 | wiring: registration removed | Witness exists | 1/F1 |
| 1,17 | combined: registration + cure removed | Witness exists | 1/F1 |
| 2 | inheritance: production parent | Summary succeeded | 1/F1 |
| 3 | outer_reset: remove 1x reset; external 12 | Summary succeeded | 1/F1 |
| 4 | stress_patch: bounded scale 1 | Scale >= 12 | 1/F1 |
| 4 | stress_scope: remove bounded env change | Scale >= 12 | 1/F1 |
| 5 | forward: bounded return empty bytes | Witness exists | 1/F1 |
| 6 | command_forward: bypass fixture policy | First strict result [] | 1/F1 |
| 6 | command_return: return [] | Summary succeeded | 1/F1 |
| 7 | guard: recording condition false | Witness exists | 1/F1 |
| 8 | record: append removed | Witness exists | 1/F1 |
| 9 | record_scale: report 1 | Scale >= 12 | 1/F1 |
| 10 | record_count: count + 1 | Argv/count equality | 1/F1 |
| 11 | record_interval: conversion doubled | Argv/interval equality | 1/F1 |
| 12 | record_timeout: report zero | Timeout formula equality | 1/F1 |
| 13 | record_argv: record [] | Bounded flag present | 1/F1 |
| 14 | floor: effective stress 3.5 | Scale >= 12 | 1/F1 |
| 15 | nominal_count: zero multiplicand | Timeout formula equality | 1/F1 |
| 15 | nominal_interval: zero multiplicand | Timeout formula equality | 1/F1 |
| 15 | stress_nominal: nominal operand -> 1 | Stressed duration > timeout | 1/F1 |
| 15 | stress_scale: scale operand -> 1 | Stressed duration > timeout | 1/F1 |
| 16 | timeout_floor: 15 -> 0 | Timeout formula equality | 1/F1 |
| 16 | timeout_factor: 1.5 -> 0 | Timeout formula equality | 1/F1 |
| 16 | timeout_offset: 10 -> 0 | Timeout formula equality | 1/F1 |
| 16 | timeout_max: max -> min | Timeout formula equality | 1/F1 |
| 17 | no_sleep: cure removed | First strict result [] | 1/F1 |
| 18 | continuous_argv: add bounded-only flag | Continuous flag absent | 1/F1 |
| 19 | post_count: local count + 1 | Capture/post count equality | 1/F1 |
| 20 | drift_status: local status unknown | Drift bounded | 1/F1 |
| 10 | argv_count: parsed value + 1 | Argv/count equality | 1/F1 |
| 11 | argv_interval: parsed conversion doubled | Argv/interval equality | 1/F1 |
| 21 | strict_before: nonempty result | First strict result [] | 1/F1 |
| 21 | strict_after: nonempty result | Final strict result [] | 1/F1 |

Clause 5 failed earlier than planned: skipping forwarding prevents command recording. The table names the actual arithmetic cuts.

In-memory timeout conditioning used 1.5 seconds for the floor and 5 seconds for factor/offset. Both controls ran 1 test / OK (21.189s, 22.011s); ordinary control: Ran 1 / OK (21.905s).

**Canned []:** report 37’s `wraps=validate_bundle -> return_value=[]` cut is impossible here: no validator mock, callback, or wrapper remains. Construction inspection plus the selected test passed: Ran 1 / OK, 18.497s. Arbitrarily replacing the real validator itself remains possible oracle tampering; it is not claimed impossible. Both nonempty-result boundary probes above fail.

The isolated cure cut retained these reason strings:

```text
A177_CAPTURE count=94 scale=12 timeout=17.05
A177_CAPTURE_EXCEPTION TimeoutExpired
A177_DRIFT {'reason': 'post_idle_unavailable', 'status': 'unknown'}
strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation
strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation
Ran 1 test in 34.942s
FAILED (failures=1)
```

Cut commands (V3; substitute `A177_CUT`) require the temporary driver in this turn’s tool trace. It was removed before both suites; candidate SHA-256 remained `a702785318eaddef9385882930ac120a73d4c5b7a22ab2aa249664f2e4531e2b`.

V1 used Python 3.13.1; V2 used system Python 3.14.7. Verification is synthetic fixture evidence. The next step is lead review and hosted CI.