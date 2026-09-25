```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIT AFTER LISTED FIXES: earlier witnesses are cured, but bundle-file substitution and torn ownership recovery remain unsafe.",
  "workspace": {
    "base_requested": "64d79ad5",
    "base_mode": "descendant",
    "head_start": "69faf9aa84b60df0e87f7c2d540a0d1c7437c432",
    "head_end": "69faf9aa84b60df0e87f7c2d540a0d1c7437c432",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "FIT AFTER LISTED FIXES",
    "findings": [
      {
        "id": "F10",
        "severity": "blocker",
        "location": "scripts/diagnostics/osctx_mvp/analyze.py:649",
        "summary": "Ledger custody checks do not bind bundle evidence bytes; copied summary files silently change verdicts."
      },
      {
        "id": "F11",
        "severity": "blocker",
        "location": "scripts/diagnostics/osctx_mvp/runner.py:764",
        "summary": "A torn owned.jsonl append aborts recovery before cleanup or network-time restoration."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit3 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit3/suite.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["AUDIT3_SUITE_PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AUDIT3_SUITE_PASS"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit3 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit3/probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["AUDIT3_PROBES_PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AUDIT3_PROBES_PASS"
      }
    }
  ],
  "flags": []
}
```

## Findings

**F10 — BLOCKER: bundle contents remain unbound.** Copying I’s `summary_metrics.json` over D’s corresponding file in six accepted blocks changed **D/I:E from DIFFERENT to EQUIVALENT**, with zero errors. Neither ledger nor cell records were edited. The analyzer checks bundle location, metadata run ID, and materialized-config digest, but trusts the replacement metric bytes. Accidental file copying is within D-161’s mistake model. Bind analysis-consumed bundle files to acceptance-time digests and verify before producing verdicts.

**F11 — BLOCKER: torn ownership journal defeats recovery.** Starting with complete network-time and job acquisitions, then appending an incomplete update line, made `recover()` raise `ValueError` with **zero backend calls**. Thus neither recorded ownership nor network time was recovered. `ledger.owned()` runs outside the recovery error handler, before restoration. Always attempt protected network-time restoration despite journal errors; conservatively recover the valid journal prefix while preserving unresolved ownership and reporting failure.

**Earlier witnesses:** all refused or cured. Foreign bundles and six-block mixed-attempt pairing refuse; cross-stage D/I pairing yields no pairs. The 2+1 failure threshold stops execution; unknown observations interrupt/refuse admission; idle-only CPU activity flags; text-only identity invalidates; one-run sizing applies the √2 correction. Signals injected during restoration and bootout allow restoration/proof/release to finish before interruption propagates. An exited SH leader’s surviving member receives TERM, then KILL.

**Recovery positive case:** injected-backend `--recover` releases launchd, SH, and network-time ownership. Starting with unreleased ownership refuses before any backend call. Cleanup/restoration commands receive 60-second timeouts.

**Nine additional mutations beyond the property test:**

| Mutation | Result |
|---|---|
| Reverse independent block-record order | Accepted; unchanged verdicts, per-block histories preserved |
| Point accepted cell into another block’s directory | Refused |
| Mark warm-up non-discard | Refused |
| Copy U2 ledger into U1 | Refused |
| Edit timestamp and recompute seal | Accepted; deliberate resealing is outside D-161, not a security failure |
| Replace ledgered bundle summary files | Accepted; F10 |
| Swap bundle metadata file | Refused |
| Reverse accepted cell-slot order | Refused |
| Delete accepted cell’s completion marker | Refused |

Semantic ledger mutations were resealed to exercise invariant checks independently of checksum rejection.

**Positive analysis:** the valid synthetic stage0U/U1/U2/S session produced 53 retained rows, twelve D/I pairs, zero errors, D/I:E DIFFERENT, and the other three verdicts EQUIVALENT. No false refusal occurred.

The focused suite passed **39 tests**, including **200/200 seeded property cases**. Replay scripts and logs reside under `/tmp/4b-osaudit/audit3/`. Next step: fix F10/F11 and replay these probes.

## Residual risk

Evidence is offline and simulated; live process behavior remains lead-owned. No prohibited commands executed, no repository files changed, and the live rehearsal was untouched.