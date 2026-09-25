```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIT AFTER LISTED FIXES: bundle provenance, retry counting, and observation failures can silently compromise cells or verdicts.",
  "workspace": {
    "base_requested": "5029f206",
    "base_mode": "exact",
    "head_start": "5029f206b27b46716c935eaf9d9a275d44599ab8",
    "head_end": "5029f206b27b46716c935eaf9d9a275d44599ab8",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "FIT AFTER LISTED FIXES",
    "findings": [
      {"id":"F1","severity":"blocker","location":"scripts/diagnostics/osctx_mvp/analyze.py:168","summary":"Unbound bundle references and stage-blind pairing permit foreign evidence and mixed cells."},
      {"id":"F2","severity":"blocker","location":"scripts/diagnostics/osctx_mvp/runner.py:302","summary":"Invalid-cell counting deduplicates separate failed attempts and misses the C5 stop threshold."},
      {"id":"F3","severity":"blocker","location":"scripts/diagnostics/osctx_mvp/cell.py:155","summary":"Unreadable HID and unknown display observations fail open during U cells."},
      {"id":"F4","severity":"should_fix","location":"scripts/diagnostics/osctx_mvp/analyze.py:191","summary":"CPU census flags exclude the idle baseline."},
      {"id":"F5","severity":"should_fix","location":"scripts/diagnostics/osctx_mvp/analyze.py:36","summary":"Decoded-text fallback accepts missing output-token identity."},
      {"id":"F6","severity":"should_fix","location":"scripts/diagnostics/osctx_mvp/analyze.py:625","summary":"Sizing reuses two-run cell spread without accounting for one-run U cells."}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"suite",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_osctx_mvp",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 15 tests in 1.036s","","OK"]},
      "expected":{"exit_code":0,"tail_regex":"Ran 15 tests.*OK"}
    },
    {
      "id":"V2","kind":"inspection",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit/bench_check.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["BENCH_CHECK PASS"]},
      "expected":{"exit_code":0,"tail_regex":"BENCH_CHECK PASS"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit/probes.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["scratch /tmp/4b-osaudit/audit/probe-lshiv4pf"]},
      "expected":{"exit_code":0,"tail_regex":"scratch /tmp/4b-osaudit/audit/probe-.*"}
    },
    {
      "id":"V4","kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit/stop_power.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["scratch /tmp/4b-osaudit/audit/stop-zs7ambkm"]},
      "expected":{"exit_code":0,"tail_regex":"scratch /tmp/4b-osaudit/audit/stop-.*"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — BLOCKER: foreign bundles and mixed-stage pairing.** `analyze.py:168` trusts each absolute bundle path without checking cell ownership, expected run ID, materialized config, or duplicate use. Recursive discovery at `:568` admits arbitrary cells; pairing at `:308` keys only on block and silently overwrites duplicate arms. Reproduction: **18 cells referencing one foreign fixture bundle produced all four EQUIVALENT verdicts, with no errors**. A separate probe paired U1 D rows with U2 I rows. Bind analysis to the rendered schedule, expected bundle/config identities, and unique stage/block/attempt/slot membership; reject duplicates and cross-stage pairs.

**F2 — BLOCKER: C5 undercounts failed cells.** `runner.py:302` counts `(block, slot)` rather than individual attempted cells; `analyze.py:575` repeats that deduplication. Two failed SH attempts in block 1 followed by one failed SH attempt in block 2 yielded **three failures, reported count two, and `stage_done`**. Count failed attempts toward the per-arm threshold. The independent three-failures-of-one-block limit and same-order retries are otherwise implemented.

**F3 — BLOCKER: U observations fail open.** `cell.py:155–159` records HID read errors but substitutes infinity when deciding interruption; unknown display state also passes. `runner.py:175` permits unknown display at admission. A scratch observation with unreadable HID and unknown display returned `interrupted=False`, allowing an unverifiable U cell into analysis. Refuse admission or invalidate/retry when required state observations cannot be established.

**F4 — SHOULD_FIX: idle-baseline contamination escapes census flags.** `analyze.py:189–192` constructs census windows only for the measured request. CPU activity confined to the 30-second idle baseline cannot flag the cell, although that baseline directly determines E. A daemon consuming 10% of a core during idle produced no flag. Include idle-baseline segments. The implemented CPU-time delta arithmetic and PID exclusions otherwise work for observed process pairs.

**F5 — SHOULD_FIX: missing token IDs remain valid.** `analyze.py:36–38,73–75` falls back to response-text hashing plus a metadata token count. Removing token IDs and supplying text with `output_token_count=512` still returned VALID. This does not establish identical output-token IDs; require their recorded sequence and hash.

**F6 — SHOULD_FIX: power table mismatches the default U replication.** `analyze.py:625` uses stage-0 spread between two-run cell means for U, whose default is one run per cell. The measured within-cell spread is reported but unused; table rows do not identify replication. Under independent within-cell noise, reducing two runs to one increases paired SD by approximately √2. Illustratively, at n=6, SD=.015 gives estimated power .4675; SD=.015√2 gives .13745. Publish sizing appropriate to the frozen U replication.

The requested positive checks passed: rendered D omits ProcessType, I uses Interactive, B uses Background; plists have zsh-exec arguments, PATH and WorkingDirectory. SH renders detached `nohup caffeinate -is /bin/zsh -c exec`. Production is a direct wrapper child, awaited without detachment. Every production argv includes dwell60; materialization asserts only run ID and tags changed.

**Bench results:** `osctx-smoke-shell-dwell60` is **VALID**, anchor **0.003499999 s**, 512 tokens. `osctx-smoke-shell-1` is **INVALID**, anchor absent, with `clock_anchor_unresolved` and `clock_bound_unrecorded`. Both token hashes match. The declared-reason set is exact.

Paired-t confidence, materiality boundaries, C3 energy drift gate, C4 D/I edge downgrade, and widening without √n shrinkage are implemented. Independent power integration at n=6, SD=.015 used t-critical **4.525716**, yielding **.468910**, consistent with harness **.467500 ± .003528 MC SE**.

## Residual risk

Context inheritance was inspected in code, not verified on live children. No prohibited commands ran; the live stage-0 directory was untouched. Repository state remained clean. The lead should resolve these findings and re-audit before U1.