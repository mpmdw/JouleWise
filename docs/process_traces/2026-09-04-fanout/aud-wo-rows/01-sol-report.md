```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Closed the mechanical audit residue with counterfactual tests, confirmed later implementations, and recommended retirement of six untriggered roadmap rows.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-aud-wo-rows"
  },
  "pathspec": [
    "docs/contracts/bridge_protocol.md",
    "docs/process_traces/2026-09-04-fanout/aud-wo-rows/01-sol-report.md",
    "scripts/check-bridge-docs.mjs",
    "tests/test_bridge.py",
    "tests/test_rpt001_report_slice.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "node scripts/check-bridge-docs.mjs && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_bridge.BridgeDocumentationDriftTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "bridge docs check OK (5 consumers, 5 snippets)",
          "Ran 6 tests in 0.127s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "bridge docs check OK.*Ran 6 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rpt001_report_slice.TestRpt001Artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 22 tests in 3.901s",
          "OK (skipped=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 22 tests.*OK \\(skipped=3\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_claims_lint.ClaimsLintFixtureTests.test_unqualified_outcome_dependent_top_up_errors tests.test_claims_lint.ClaimsLintFixtureTests.test_frozen_axi_rules_pass_while_prior_unqualified_rule_still_fails tests.test_calibration_bracketing.CalibrationBracketingTests.test_v2_ledger_candidate_reports_era_rejection_not_custody_failure tests.test_floor_mint_pinsets_schema.FloorMintPinsetsSchemaTests.test_generation_screen_conditionals_match_python_registries tests.test_mint_policy_resolver_guard.MintPolicyResolverGuardTests.test_mint_lane_has_no_copied_bracket_screen_literals",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 0.030s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_rpt001_report_slice.TestRpt001Artifacts",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "SystemExit: 1",
          "Ran 22 tests in 4.176s",
          "FAILED (errors=1, skipped=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 22 tests.*OK \\(skipped=3\\)"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "report_json=$(sed -n '2,/^```$/p' docs/process_traces/2026-09-04-fanout/aud-wo-rows/01-sol-report.md | sed '$d'); test \"$(head -n 1 docs/process_traces/2026-09-04-fanout/aud-wo-rows/01-sol-report.md)\" = '```json' && test \"$(printf '%s' \"$report_json\" | wc -c | tr -d ' ')\" -le 8192 && printf '%s' \"$report_json\" | jq -e '.schema == \"claude-codex-report/v1\" and .genre == \"implementation\" and (.summary | length > 0) and (.pathspec | type == \"array\") and (.verification | type == \"array\") and (.flags | type == \"array\")' >/dev/null && printf 'report_contract=pass\\n'; git diff --check && printf 'diff_check=pass\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report_contract=pass",
          "diff_check=pass"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "report_contract=pass.*diff_check=pass"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The authoritative kernel and its generated queue/run-state projections still show all requested rows queued because those lead-owned files were explicitly excluded from this session.",
      "needs": "The magistrate should mark AUD-FOLLOWUPS and D144-SEATPASS-FOLLOWUPS complete, retire AUD-WO-033 through AUD-WO-038, and regenerate projections."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide suite was not run by preflight instruction; three existing private-corpus tests in the focused report class skipped because the corpus is unavailable.",
      "needs": "No action for this row harvest; the magistrate owns any broader final-head verification."
    }
  ]
}
```

## Change

A counterfactual test is one that fails after a specific wrong implementation
substitution. The work added such tests for the still-open mechanical residue
and used current-tree evidence for work that later commits had already closed.

| Kernel row | Audit source | Decision | Evidence or retirement reason |
|---|---|---|---|
| `AUD-WO-033` | C1-011; audit report lines 276 and 369 | Retire | The audit found code concentration but no defect and made the refactor conditional on a later campaign-scale or split/multi-node trigger. The kernel still records that hard dependency as pending. A belated extraction against a substantially evolved campaign runner would no longer be the bounded, behavior-parity change that was audited; any future modularization should be specified from the then-current runner. |
| `AUD-WO-034` | C1-012; audit report lines 277 and 370 | Retire | The owner lint was conditional on Phase-3 split scheduling. That hard dependency remains pending, so there are no executable split commands to own. If split work returns, its current commands and owners should be registered in a fresh work order before execution. |
| `AUD-WO-035` | C2-011; audit report lines 285 and 371 | Retire | The original defect remains dormant: `tests/test_2k_amplification.py:431-445` still sends a transfer discriminator with a telemetry block, while `joulewise/adapters/node_worker.py:89` has no transfer block. The split-transfer trigger remains pending. Defining the transfer fields now would invent a wire design; a fresh versioned protocol task is required if split transfer is scheduled. |
| `AUD-WO-036` | C2-012; audit report lines 286 and 372 | Retire | The audit verifier recorded sequential execution with no automatic retries, and the kernel's retry/concurrency trigger remains pending. Resource leasing is concurrency-sensitive design, not a mechanical hardening change; specify it anew if concurrent node or graphics-processor use is introduced. |
| `AUD-WO-037` | C2-013; audit report lines 310 and 373 | Retire | The audit found no NVIDIA claim at risk and conditioned the work on live promotion; the kernel still records promotion as pending. The earlier fixture-first NV-GATE-2 code landed without creating a non-self-asserted promotion authority. If NVIDIA claims return, a fresh pre-promotion work order must establish that authority before admission. |
| `AUD-WO-038` | C2-030; audit report lines 320 and 374 | Retire | The audit found no current defect and deferred boundary consolidation to a multi-node roadmap decision, which remains pending. Because this order permits destructive surface removal and its caller census predates extensive remote-lifecycle changes, it is unsafe to apply without a new census and compatibility ruling. |
| `AUD-FOLLOWUPS` | Audit report line 547 and ULTRA findings F7, F9, F11, F12, F22 | Implement remaining residue; complete | D-062 lint and positive/negative coverage already landed in `d916bffc` (`scripts/claims_lint.py:410-422`, `tests/test_claims_lint.py:246-264`). This change makes the realized-token test distinguish the configured cap from the two realized tokens (`tests/test_rpt001_report_slice.py:190-224`), asserts the default absence of an evidence-handoff contract (`:483-489`), adds the prescribed standalone bridge checker and a mutated-consumer refusal (`tests/test_bridge.py:1653-1697`), scans authored instructions for workstation paths (`tests/test_rpt001_report_slice.py:491-503`), and runs source-only checking in a real pristine Git clone (`:505-541`). The absolute-path production cleanup itself landed in `2cc7c570`. |
| `D144-SEATPASS-FOLLOWUPS` | D-144 seat-pass ruling, should-fix findings SF-1, SF-3, SF-5 | Already done | Commit `bea06481` is an ancestor of this head. The persisted, non-gating mixed-era diagnostic is at `joulewise/calibration_bracketing.py:2118-2134` and its valid-current-era regression at `tests/test_calibration_bracketing.py:2148-2198`; schema-to-registry synchronization is tested at `tests/test_floor_mint_pinsets_schema.py:48-74`; the mint-lane-wide copied-scalar scan is at `tests/test_mint_policy_resolver_guard.py:10-24`. |

The new counterfactuals are direct: substituting the configured cap for
realized tokens changes the expected value from the fixture's realized count;
adding the optional handoff contract violates the default-branch assertion;
adding a workstation path violates the authored-source scan; depending on an
untracked input breaks the real clone check; and changing one canonical bridge
snippet makes the standalone checker return failure. The already-landed D-062
and D-144 tests likewise include rejected unqualified top-up prose, a retained
superseded-era observation beside valid current-era candidates, schema registry
equality, and a repository-wide mint-source census.

## Verification notes

The first report-module run intentionally made several evidence channels
different and was too broad: production correctly rejected metadata that said
forty-one realized tokens beside a two-line token artifact. The fixture was
corrected so both realized channels say two while the configured cap remains
ninety-seven; the repeated focused run passed. This preserves the intended
counterfactual without constructing an invalid bundle.

The three skipped tests require the private run corpus and are unrelated to
the source-only and audit-residue assertions exercised here. Per the explicit
preflight rule, no repository-wide test discovery was run.

## Residual risk

Retiring the six dormant rows must not be read as enabling their future
capabilities. A new transfer wire, concurrent remote execution, claim-bearing
NVIDIA promotion, or multi-node consolidation must install a current design and
counterfactual tests before use. In particular, NVIDIA claim admission still
has no non-self-asserted live-promotion authority; it is safe only while live
promotion remains unscheduled.
