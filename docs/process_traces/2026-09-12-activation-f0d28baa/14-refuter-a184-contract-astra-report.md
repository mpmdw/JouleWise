```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One runbook blocker: the armed clone cannot print the newly documented code. Registry projection and focused regression pass; no registry-freeze blocker found.",
  "workspace": {
    "base_requested": "ace4cc3c",
    "base_mode": "exact",
    "head_start": "7014dd0e0d5a13fce0762e91f0f7541ae8a91d1d",
    "head_end": "7014dd0e0d5a13fce0762e91f0f7541ae8a91d1d",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 1665,
        "summary": "Unqualified output promise is false for the armed night's frozen clone.",
        "evidence": "Harvest selects the measurement clone at lines 1493-1502 and 1646-1649. At f90cb8c0, recover_calibration_ledger.py:62-66 lacks window_exhausted; lines 376-378 fall back to SESSION_NOT_OPEN. Line 1665 is also the runbook's first and only mention of session-refusal and calibration_window_exhausted.",
        "reproduce": "git show f90cb8c0:scripts/recover_calibration_ledger.py | nl -ba | sed -n '62,66p;376,383p'",
        "requested_change": "Replace line 1665 with checkout-qualified wording that defines the subcommand and distinguishes the frozen clone's output from A184's output."
      }
    ],
    "contract_checks": [
      {
        "topic": "Generated projection",
        "result": "No blocker found.",
        "detail": "calibration_ledger_append.md:348-349 says: 'This table is generated from REFUSAL_INVENTORY. Its exact freshness is a test gate; edits belong in the Python registry and are projected here.' The test at tests/test_calibration_exits.py:1501-1527 constructs all ten columns from each record and compares the entire region exactly. No standalone generator or documented regeneration command was found. The documented requirement is registry-first editing plus exact projection; manually populating the matching row satisfies that requirement, although hand-editing is not explicitly named as the procedure. No skipped regeneration step was identified."
      },
      {
        "topic": "Freeze, counts and digest authority",
        "result": "No registry-freeze blocker found.",
        "detail": "Searched docs/decision_log.md, docs/contracts/*.md, state_kernel.json fences and preregistration_d079_epoch_25g83_rev1.md. A184 explicitly authorizes this mapping and has no dependencies or fences (state_kernel.json:5450-5460). The inventory is dynamically constructed (calibration_exits.py:556-558); its count is now 75, checked against enum membership rather than a pinned number (test_calibration_exits.py:1546-1551). The contract's 'immutable registry' wording at calibration_ledger_append.md:24-25 does not impose a source-change freeze: lines 348-349 explicitly allow registry edits. Decision-log freezes concern other registries: contrast membership at 3002-3006 and D-078 claim vocabulary at 4230-4233. No applicable ruling requirement or pinned calibration-refusal digest was found."
      },
      {
        "topic": "Armed-night pins and merge timing",
        "result": "No armed calibration-refusal-registry digest found in inspected evidence.",
        "detail": "docs/process_traces/2026-09-12-activation-b58fb582/02-equivalence-night-arm-record.md:16-18 pins H=f90cb8c0; lines 72-75 enumerate frozen-plan, registration, wrapper and input pins. Its published-night_plan.json records DIAGNOSTIC_NO_PACK and both heads at H. Pre-registration lines 135-150 pin binary, estimator/protocol, ledger and chain identities, not REFUSAL_INVENTORY. These five changed files leave those named inputs unchanged. This lens therefore finds no registry-pin reason to defer the code change until after the night; the frozen clone remains unchanged. B1 must be corrected before landing the runbook guidance."
      },
      {
        "topic": "Every row column and sibling comparison",
        "result": "No should-fix found.",
        "detail": "calibration_ledger_append.md:345 exactly projects code=calibration_window_exhausted, witness_class=operational, component=writer, phase=pre-slot-or-capture, exit_id=abort-session, terminal_result=session_aborted, night_loss=true, witness_id=witness.calibration_window_exhausted, correction_surface='', corrected_success=''. Full RefusalRecord comparison against the three siblings at rows 342-344 found differences only in code, description and witness_id. Defaults and routing derive these values at calibration_exits.py:145-188, 449-450 and 469-476. The record's command is the governed abort-session action; session-refusal is the observer, so the Exit ID column is not a mistaken copy of the observer name."
      },
      {
        "topic": "Powermetrics contract",
        "result": "Seat judgment confirmed.",
        "detail": "powermetrics_fiducial.md:460-464 says: 'Before baseline, warmup, or protocol pulses, the live harness must observe an advancing native plist timestamp. Failure to observe rollover within the bounded gate terminates powermetrics and refuses with pulse_calibration_rollover_gate_timeout; no calibration evidence artifact is minted from that capture.' This specifies the rollover gate, not an exhaustive automatic-abort set; no window_exhausted addition is required there."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_generated_contract_projection_and_runbook_anchors_are_fresh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.001s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_session_refusal_reports_window_exhausted_derivation_abort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.626s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check ace4cc3c..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Worktree is detached at the requested one-commit candidate, rather than attached to the named branch. The diff matches five files, +53/-1; workspace remained clean.",
      "needs": ""
    }
  ]
}
```

## Findings

**B1 — blocker, runbook line 1665 only.** “The desk tool’s `session-refusal` reports this reason as `calibration_window_exhausted`” describes A184’s checkout, but harvest uses the frozen clone. That clone returns `calibration_session_not_open`. Neither the subcommand nor the new code is introduced earlier in this section.

Exact replacement:

> The recovery tool’s `session-refusal` subcommand reports a stored abort as a refusal code: for `window_exhausted`, the armed night’s measurement clone at `H=f90cb8c0` still reports `calibration_session_not_open` (read the actual reason from the chain log), while a checkout containing A184 reports `calibration_window_exhausted`; harvest must use the night’s frozen clone.

No additional should-fix or nit findings. The projection test does **not** validate this sentence: its runbook checks target `window_runbook.md`, not `derivation_night_runbook.md`.

## Residual risk

Neither fenced checkout was accessed; historical behavior was inspected through this worktree’s Git objects and committed arm evidence. The killed cut and 48-test module pass remain seat-reported evidence; this read-only review independently ran only the two focused tests above.