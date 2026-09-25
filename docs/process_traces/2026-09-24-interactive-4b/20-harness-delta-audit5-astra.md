```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"clean",
  "completion":"complete",
  "summary":"FIT TO RUN: F13/F12 cured; offline replays pass; no acceptance-time manifest conflict found.",
  "workspace":{"base_requested":"3fa4dc84","base_mode":"descendant","head_start":"962de81c3544d2c7d13448e4d15ddfb6a0685fb3","head_end":"962de81c3544d2c7d13448e4d15ddfb6a0685fb3","upstream_end":null,"branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"result":"FIT TO RUN","findings":[]},
  "verification":[
    {"id":"V1","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit5 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit5/suite.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT3_SUITE_PASS"]},"expected":{"exit_code":0,"tail_regex":"AUDIT3_SUITE_PASS"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit5 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit5/replay.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT3_PROBES_PASS"]},"expected":{"exit_code":0,"tail_regex":"AUDIT3_PROBES_PASS"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit5 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit5/extra.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT4_EXTRA_PASS"]},"expected":{"exit_code":0,"tail_regex":"AUDIT4_EXTRA_PASS"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit5 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit5/timing.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT5_TIMING_PASS"]},"expected":{"exit_code":0,"tail_regex":"AUDIT5_TIMING_PASS"}}
  ],
  "flags":[]
}
```

## Findings

**F13:** unchanged B-cell CPU edits now refuse with `cell manifest mismatch`. **F12:** reviewer and log-viewer argv no longer match; recorded wrapper/production argv and relocated bare/sudo sampler forms still match.

Round-3/4 replay sets pass with stage-opening fixture adaptations; no earlier-cured witness regressed. Focused suite: **44 tests, 200 seeded property cases**. Render checks pass.

**Complete read inventory**, with line numbers and coverage classifications: [read-inventory.txt](/tmp/4b-osaudit/audit5/read-inventory.txt).

- `analyze.py`: tokens; bundle events, power trace, summary metrics, metadata; cell, done, census, discarded markers; materialized configs; schedules; sealed ledger; supplied stage0 summary.
- `ledger.py`: fingerprint streams, five bundle files, cell records, stage ledger, ownership journal. Append opens are write-only.
- `common.py`: effective configuration bytes.

No unbound verdict-bearing evidence was found for stable completed-stage analysis. Exceptions: recursive non-owning schedules are read solely for rehearsal-contamination refusal; ownership journals serve recovery; hypothetical `power --sd-*` loads unbound configuration. Supplied stage0 summaries must equal recomputed bound evidence.

**Write timing:** normal acceptance follows cell cleanup and descendant proofs. Cell stdout/stderr, production logs, census and bundle files are therefore complete before manifesting. Later events, ownership releases, summaries and session metadata reside at stage/session roots. The simulated session completed with **zero writes into already accepted trees**, unchanged manifests, and successful reanalysis.

## Residual risk

Offline evidence only; live process timing remains lead-owned. Concurrent filesystem mutation was not validated. Repository unchanged; rehearsal4 untouched. Next step: lead-owned live verification.