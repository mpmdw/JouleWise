```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIT AFTER LISTED FIXES: F10/F11 witnesses cured; unbound cell evidence and sampler false positives remain.",
  "workspace": {
    "base_requested": "69faf9aa",
    "base_mode": "descendant",
    "head_start": "3fa4dc84ddd9e49a0a8394b094cfecc8415edb11",
    "head_end": "3fa4dc84ddd9e49a0a8394b094cfecc8415edb11",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "FIT AFTER LISTED FIXES",
    "findings": [
      {
        "id": "F13",
        "severity": "blocker",
        "location": "scripts/diagnostics/osctx_mvp/ledger.py:65",
        "summary": "Analysis-consumed cell evidence remains unbound; CPU edits silently alter the background-control result."
      },
      {
        "id": "F12",
        "severity": "should_fix",
        "location": "scripts/diagnostics/osctx_mvp/runner.py:404",
        "summary": "Sampler pattern permits arbitrary leading argv and falsely matches reviewers/log viewers."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit4 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit4/unchanged.py",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["AUDIT4_UNCHANGED_PASS"]},
      "expected": {"exit_code":0,"tail_regex":"AUDIT4_UNCHANGED_PASS"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit4 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit4/replay.py",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["AUDIT3_PROBES_PASS"]},
      "expected": {"exit_code":0,"tail_regex":"AUDIT3_PROBES_PASS"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit4 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit4/suite.py",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["AUDIT3_SUITE_PASS"]},
      "expected": {"exit_code":0,"tail_regex":"AUDIT3_SUITE_PASS"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit4 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit4/extra.py",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["AUDIT4_EXTRA_PASS"]},
      "expected": {"exit_code":0,"tail_regex":"AUDIT4_EXTRA_PASS"}
    }
  ],
  "flags": []
}
```

## Findings

**F13 — blocker: remaining silent-wrong path.** After acceptance, editing only B cells’ `cell.json` CPU seconds changed `background_cpu_ratio` from **0.0196 to 2.0** and removed `background_control_investigate`, with zero errors and no ledger edits. Bind analysis-consumed cell evidence at acceptance and verify before analysis.

**Read inventory:** all five bundle inputs are fingerprinted: `summary_metrics.json`, `metadata.json`, `outputs/tokens.jsonl`, `power_trace.csv`, `events.jsonl`. Independent byte mutations all refused. Files read without acceptance fingerprints: `cell.json`, `done.json`, `census.jsonl`, `command_sequence.json`, `discarded.json`, and optional `--stage0-summary`. Materialized `run-r*.json` files have separate SHA checks; `ledger.jsonl` has seals. `owned.jsonl` is read for ownership recovery. Configuration is loaded indirectly through `common.load_config`, outside these fingerprints.

**F12 — should fix: insufficient sampler anchoring.** All patterns start with `^`, but the sampler prefix accepts arbitrary tokens. POSIX-regex replay matched both `/python reviewer.py --argv /usr/bin/powermetrics … -o <cell>/runs/joulewise-powermetrics-abc.plist` and a grep log viewer. Restrict the prefix to actual sampler/sudo executable forms.

Recorded rehearsal2 wrapper and production argv match, including the executable from child `ps` records and materialized config paths. Historical sampler argv **does not match** because its output is in the global temporary directory. With only the output relocated according to fix-6’s `TMPDIR`, recorded bare/sudo forms match; the production temporary-file helper independently confirms that location.

**F10/F11:** unchanged witness bodies now demonstrate summary-copy refusal and network-time restoration first, followed by recoverable-job cleanup, retained ownership, and nonzero recovery failure for the torn journal.

**Regression:** round-3 replay passed; no earlier-cured witness regressed. Focused suite: **42 tests**, including **200/200 property cases**. Rehearsal/session render-only checks passed. Next step: bind cell evidence and tighten sampler matching, then replay.

## Residual risk

Offline evidence only. Regex checks used the native POSIX engine through Python; no processes were launched. Repository unchanged; rehearsal3 untouched.