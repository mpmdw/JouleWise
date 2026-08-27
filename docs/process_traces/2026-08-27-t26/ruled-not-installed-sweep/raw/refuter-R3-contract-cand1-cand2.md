```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Both candidates are partially confirmed as post-transaction workflow defects; the twin environment parsers also diverge.",
  "workspace": {
    "base_requested": "0dd3b6dc",
    "base_mode": "informational",
    "head_start": "f4eac40b1ecb7003297d4393876fd942d8751548",
    "head_end": "f4eac40b1ecb7003297d4393876fd942d8751548",
    "upstream_end": "f4eac40b1ecb7003297d4393876fd942d8751548",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [
    "CANDIDATES.md"
  ],
  "verdict": {
    "findings": [
      {
        "id": "CAND-1",
        "severity": "should_fix",
        "disposition": "PARTIAL",
        "title": "Finalization is ruled post-collection, but no desk execution procedure schedules it"
      },
      {
        "id": "CAND-2",
        "severity": "should_fix",
        "disposition": "PARTIAL",
        "title": "The environment contradiction misses the freeze transaction but blocks later measurement-window choreography"
      },
      {
        "id": "CAND-2-TWIN",
        "severity": "should_fix",
        "disposition": "CONFIRMED",
        "title": "The two window.env parsers enforce different acceptance sets"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "if rg -n 'finalize_analysis_manifest|analyze-claims|finalize_prospective' docs/process_traces/2026-08-22-t20/real-transaction-runbook.md docs/process/rehearsal-operator-card.md docs/phase_2/window_runbook.md docs/process/phase2-transaction-runsheet.md; then exit 1; fi",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n '_ENV_KEYS|missing = _ENV_KEYS|unknown = set\\(values\\) - _ENV_KEYS|def _parse_shell_assignments|assignments.get\\(name\\)' scripts/capture_t0_step.py joulewise/arm_readiness_evidence_t0.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/capture_t0_step.py:102:_ENV_KEYS = frozenset(",
          "scripts/capture_t0_step.py:259:    missing = _ENV_KEYS - set(values)",
          "scripts/capture_t0_step.py:260:    unknown = set(values) - _ENV_KEYS",
          "joulewise/arm_readiness_evidence_t0.py:578:def _parse_shell_assignments(raw: bytes, *, kind: str) -> dict[str, str]:",
          "joulewise/arm_readiness_evidence_t0.py:672:    if any(assignments.get(name) != expected for name, expected in expected_env.items()):"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "arm_readiness_evidence_t0.py:672"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --quiet && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "?? CANDIDATES.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\\?\\? CANDIDATES.md"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "CANDIDATES.md names 0dd3b6dc as its baseline; the inspected checkout and origin/main are now f4eac40b.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "PR #205 content was inspected from the local origin/docs/launcher-confirmation-pair branch; live hosting metadata was not queried.",
      "needs": ""
    }
  ]
}
```

## Findings

### CAND-1 — PARTIAL

Severity: should-fix.

The missing *night* step is refuted. The adopted ruling makes the prospective manifest immutable and has an outcome-blind finalizer consume the passed whole-window verdict, bracket, terminal ledger head, and aggregate floor artifact—necessarily post-collection (`docs/decision_log.md:9119-9127`). The kernel likewise calls it a “post-collection finalizer” (`docs/process/state_kernel.json:4032`).

The missing desk route is confirmed. The only kernel/queue row schedules implementation and an L10 rehearsal, not execution after each window (`docs/process/state_kernel.json:4032-4038`; `TASK_QUEUE.md:588`). The earlier audit explicitly records that no operator or transaction step exists (`docs/process_traces/2026-08-19-prep-sprint/ready-packet-rows/19-ROW-L10-sacrificial-lifecycle.md:521-524`). Current `RUN_STATE.md` names W-10 and the A–H transaction sequence but does not register this desk step (`RUN_STATE.md:44-54`).

Verdict: the `_v4` transaction night is not blocked by CAND-1; post-window analysis is blocked until someone manually discovers and invokes the finalizer.

Cure — RUNBOOK change: add a scheduled post-window desk closeout that invokes `scripts/finalize_analysis_manifest.py`, validates its output, then invokes `analyze-claims`, with named ownership and attachment paths.

### CAND-2 — PARTIAL

Severity: should-fix.

D-155 settles the governing document: `real-transaction-runbook.md` is the operator procedure for the `_v4` freeze transaction (`docs/decision_log.md:182`; `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1-16`; `RUN_STATE.md:51-54`). No Phase A–H launches a measurement: Phase G is expressly dry-run-only, and the first real arm occurs later (`docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1416-1418`). The handoff to `window_runbook.md` occurs only for later measurement nights, outside the transaction session (`docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1394-1401`). Thus the contradiction does not block the D-155 transaction ceremony, but it is reachable—and blocking—on the later windows.

The contradiction itself is confirmed: §6 orders the extra bindings (`docs/phase_2/window_runbook.md:1337-1340`) and dereferences them under `set -u` (`docs/phase_2/window_runbook.md:1343-1359`), while the capture parser’s exact 25-key set omits both (`scripts/capture_t0_step.py:102-129`) and rejects unknown keys (`scripts/capture_t0_step.py:259-265`).

PR #205 preserves the instruction and restates it as an explicit open defect; it does not cure it (`origin/docs/launcher-confirmation-pair:docs/phase_2/window_runbook.md:1403-1424`). Its transaction-runbook delta correctly labels the defect as gating later windows, not the freeze session (`origin/docs/launcher-confirmation-pair:docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1399-1417`).

Cure — RUNBOOK change: remove the “additionally bind” instruction and derive/export `ARM_RECEIPT` and `LAUNCH_MANIFEST` after ARM, before E-10, mirroring `docs/process/rehearsal-operator-card.md:5,104-110`; do not widen `window.env`.

Separate `CAND-2-TWIN` — CONFIRMED, should-fix. The capture parser enforces exact equality (`scripts/capture_t0_step.py:259-265`), while `arm_readiness_evidence_t0.py` accepts arbitrary syntactically valid assignments and checks only eleven expected bindings (`joulewise/arm_readiness_evidence_t0.py:578-599,657-673`). Cure — CODE change: share one exact parser/key contract between both callers and add unknown/missing-key regressions at both boundaries.

## Residual risk

PR #205 was available only through its local remote-tracking branch; its current hosted open/merged state was not independently verified.