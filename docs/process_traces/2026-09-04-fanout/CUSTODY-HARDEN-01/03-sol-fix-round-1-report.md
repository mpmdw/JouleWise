```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Fix round 1 cures all three refuter blockers with exact-path corpus registration, biting mint and claim-row regressions, and the mandatory clause map.",
  "workspace": {
    "base_requested": "fa0944575534fb66c7366e7906c22f9ce0a2c894",
    "base_mode": "exact",
    "head_start": "fa0944575534fb66c7366e7906c22f9ce0a2c894",
    "head_end": "fa0944575534fb66c7366e7906c22f9ce0a2c894",
    "upstream_end": "fa0944575534fb66c7366e7906c22f9ce0a2c894",
    "branch": "feat/2026-09-04-fan-CUSTODY-HARDEN-01"
  },
  "pathspec": [
    "docs/contracts/adapter_contracts.md",
    "docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md",
    "docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/03-sol-fix-round-1-report.md",
    "joulewise/whole_window.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_untracked_sibling_manifest_cannot_authenticate_forged_corpus tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_derivation_cli_mint_rejects_source_identity_postcondition_failure tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_claim_row_rejects_structurally_valid_unregistered_drift_corpus",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 0.033s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 275 tests in 270.230s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 275 tests in .*s[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_reduce tests.test_whole_window tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 246 tests in 509.111s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 246 tests in .*s[\\s\\S]*OK"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "python3 -m py_compile joulewise/reduce.py joulewise/whole_window.py joulewise/analysis_engine/inputs.py tests/test_reduce.py tests/test_run_campaign.py && git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n '^## Clause map$' docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["177:## Clause map"]},
      "expected": {"exit_code": 0, "tail_regex": "177:## Clause map"}
    }
  ],
  "flags": []
}
```

## Change

F1 is closed by resolving repository registration only through the governed
`settled_corpus.json` filename. A matching `untracked.json` sibling now has no
authority, while caller-supplied exact bytes retain their existing custody
path. The contract states the sibling exclusion explicitly.

F2 is closed by two site-specific regressions. The mint regression sends the
tracked settled corpus through the real derivation CLI while injecting an
internally self-sealed wrong manifest digest; the mint postcondition refuses
before publication. The claim-row regression supplies an otherwise-valid row
whose drift artifact names an unregistered corpus; its sole refusal is
`whole_window_verdict_provenance_invalid`.

F3 is closed by the complete `## Clause map` added to `01-sol-report.md`.

| Finding | Cure | File:line |
|---|---|---|
| F1 arbitrary sibling registration | Replace the sibling glob with the single governed filename; add the exact attacker-input regression and contract sentence. | `joulewise/whole_window.py:1601`; `tests/test_run_campaign.py:7967`; `docs/contracts/adapter_contracts.md:428` |
| F2 mint postcondition not pinned | Add real-CLI fault injection using the tracked settled corpus and assert no output is published. | `joulewise/whole_window.py:3707`; `tests/test_run_campaign.py:7817` |
| F2 claim-row enforcement not pinned | Add an otherwise-valid direct claim row carrying a structurally valid unregistered drift artifact; assert the exact provenance refusal. | `joulewise/whole_window.py:5439`; `tests/test_run_campaign.py:7990` |
| F3 clause map absent | Add the full eight-row production-site map. | `docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md:177` |

## Clause map

| Touched row | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| Repository registration is only the governed settled filename. | `joulewise/whole_window.py:1601` | `tests/test_run_campaign.py:7967` | Restore the `*.json` glob; a directory containing only matching `untracked.json` authenticates the forged corpus. |
| Mint output must bind to the exact source manifest bytes. | `joulewise/whole_window.py:3707` | `tests/test_run_campaign.py:7817` | Remove the postcondition; the real CLI publishes a self-sealed artifact with a wrong manifest digest. |
| Claim-row drift artifacts require external corpus identity. | `joulewise/whole_window.py:5439` | `tests/test_run_campaign.py:7990` | Remove `require_corpus_identity=True`; the otherwise-valid forged claim row passes. |

Magistrate-owned closure text, to apply after final re-audit/merge:

```text
| CUSTODY-HARDEN-01 | P2 Next Slice | 2026-09-04 | Custody hardening follow-on from the screen+budget gauntlet | Completed on the reviewed landing: configuration-authoritative reducer barriers, externally authenticated NEG-8 corpus identity restricted to the governed settled manifest or caller-custodied exact bytes, unissued no-freshness wire removed, and artifact_schema_invalid evidence-binding meaning documented. Evidence: docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/03-sol-fix-round-1-report.md; focused suites Ran 275 tests OK and Ran 246 tests OK. |
```

Remove `/tasks/CUSTODY-HARDEN-01` from
`docs/process/state_kernel.json`, regenerate `TASK_QUEUE.md` and `RUN_STATE.md`,
and use this report as the kernel `latest_report` only after the magistrate's
final re-audit accepts the landing.

## Verification notes

The repository-wide discovery suite was not run, per the runner preflight.
The first three-regression run exposed one test-only constant lookup error;
switching the test to the owning `joulewise.whole_window` module fixed it, and
the exact rerun passed before both affected module suites ran cleanly. The
refuter's sibling-manifest input was also replayed directly and printed
`untracked_manifest_accepted=False` with exit 0.
