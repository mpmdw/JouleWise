```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"FIT AFTER LISTED FIXES: R5 can report cure despite a failed I production attempt.",
  "workspace":{"base_requested":"7a1ba0b1^","base_mode":"informational","head_start":"ef04547f17a9fd5a26ca84f72b6f12943e6ce1f0","head_end":"ef04547f17a9fd5a26ca84f72b6f12943e6ce1f0","upstream_end":"39f2eaa9bb83f70577683733248da935087a1d4c","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"decision":"FIT AFTER LISTED FIXES","findings":[{"id":"F14","severity":"should_fix","file":"scripts/diagnostics/osctx_mvp/analyze.py","line":482,"summary":"R5 validity ignores discarded I production attempts."}]},
  "verification":[
    {"id":"V1","kind":"test","cmd":"TMPDIR=/tmp/4b-osaudit/audit6 PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B /tmp/4b-osaudit/audit6/suite.py > /tmp/4b-osaudit/audit6/suite.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 55 tests in 24.738s","OK","AUDIT3_SUITE_PASS"]},"expected":{"exit_code":0,"tail_regex":"AUDIT3_SUITE_PASS"}},
    {"id":"V2","kind":"test","cmd":"TMPDIR=/tmp/4b-osaudit/audit6 PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B /tmp/4b-osaudit/audit6/c_replay.py > /tmp/4b-osaudit/audit6/c_replay.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT6_C_REPLAY_COMPLETE"]},"expected":{"exit_code":0,"tail_regex":"AUDIT6_C_REPLAY_COMPLETE"}},
    {"id":"V3","kind":"test","cmd":"TMPDIR=/tmp/4b-osaudit/audit6 PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B /tmp/4b-osaudit/audit6/timing.py > /tmp/4b-osaudit/audit6/timing.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT6_C_TIMING_PASS"]},"expected":{"exit_code":0,"tail_regex":"AUDIT6_C_TIMING_PASS"}},
    {"id":"V4","kind":"test","cmd":"TMPDIR=/tmp/4b-osaudit/audit6 PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B /tmp/4b-osaudit/audit6/recovery.py > /tmp/4b-osaudit/audit6/recovery.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT6_RECOVERY_PASS"]},"expected":{"exit_code":0,"tail_regex":"AUDIT6_RECOVERY_PASS"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp/4b-osaudit/audit6 PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B /tmp/4b-osaudit/audit6/extra.py > /tmp/4b-osaudit/audit6/extra.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT6_ARGV_RENDER_PASS"]},"expected":{"exit_code":0,"tail_regex":"AUDIT6_ARGV_RENDER_PASS"}}
  ],
  "flags":[
    {"id":"B1","kind":"baseline_drift","level":"nonblocking","text":"Requested ref unavailable; used authorized display-fix fallback 3262e9a6..HEAD.","needs":""},
    {"id":"E1","kind":"environment","level":"nonblocking","text":"nice priority adjustment was denied; checks ran sequentially, focused suite once.","needs":""}
  ]
}
```

## Findings

**F14 — should_fix — `scripts/diagnostics/osctx_mvp/analyze.py:482` (also `:516`).** R5 requires every I production run valid, but these predicates inspect only accepted cells. A sealed C-session replay containing one failed I attempt with a 100 ms anchor, followed by a successful retry, reports `invalid_cell_counts_by_stage.C1.I = 1` while both `all_I_runs_valid` and `purpose_based_cure_test_met` remain true. Bind these predicates to the complete ledgered I production history; add this retry regression before arming.

Otherwise, the requested protections hold: frozen six-block 3/3 schedule and seed, discarded warm-up, C1→P ordering, no C extension, SH/I-only inference, C3 stability gates and attribution reporting, no R drift gate, probe-only execution and manifest custody. Adapted recovery and acceptance-timing replays passed, including no writes into already accepted cells.

## Residual risk

Offline fixtures and render-only verification only; no live machine validation. Repository remained clean; artifacts are under `/tmp/4b-osaudit/audit6/`.