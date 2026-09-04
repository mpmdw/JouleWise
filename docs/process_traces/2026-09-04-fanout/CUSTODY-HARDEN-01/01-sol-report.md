```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "CUSTODY-HARDEN-01 is desk-complete: configuration-authoritative claim barriers, externally resolved drift-corpus identity, removal of the unissued freshness wire, and precise evidence-binding diagnostics are implemented and focused tests pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-CUSTODY-HARDEN-01"
  },
  "pathspec": [
    "docs/contracts/adapter_contracts.md",
    "docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/01-sol-report.md",
    "joulewise/analysis_engine/inputs.py",
    "joulewise/reduce.py",
    "joulewise/whole_window.py",
    "tests/test_reduce.py",
    "tests/test_run_campaign.py"
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
      "cmd": "python3 -m unittest tests.test_reduce.D078R01RegressionTests.test_metadata_mock_label_cannot_bypass_current_environment_barrier tests.test_reduce.D078R01RegressionTests.test_metadata_mock_label_cannot_bypass_cpu_admission_barrier tests.test_reduce.D078R01RegressionTests.test_environment_claim_reason_channel_is_closed_and_decision_bound tests.test_reduce.D078R01RegressionTests.test_cpu_admission_ledger_shape_and_top_decision_are_fail_closed tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_drift_bound_corpus_identity_requires_external_bytes tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_drift_bound_accepts_exact_custodied_manifest_bytes tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_unissued_prefreshness_bound_wire_is_malformed_and_underived tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_governed_neg8_bound_derivation_cli_writes_sealed_artifact tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_neg8_reference_campaign_corpus_is_accepted_by_derivation_cli",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 9 tests in 0.055s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 272 tests in 199.399s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 272 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_reduce tests.test_whole_window tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 246 tests in 467.202s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 246 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "python3 -m py_compile joulewise/reduce.py joulewise/whole_window.py joulewise/analysis_engine/inputs.py && git diff --check",
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
    }
  ],
  "flags": []
}
```

## Change

The reducer now decides whether telemetry is simulated from the parsed,
hash-bound configuration. The copied telemetry labels in metadata and the
summary remain diagnostics; changing either label to `mock` can no longer
suppress the current environment or central-processing-unit admission
barriers. A genuine mock configuration still follows the existing
development-only exemption because the caller selects that path before either
barrier runs.

The NEG-8 drift bound is a limit derived from repeated reference measurements.
Its internal SHA-256 seal—a cryptographic digest of bytes—still proves that its
arithmetic and fields agree with one another, but no longer authenticates its
own corpus identity at file ingress (the point where an artifact enters from
disk). The corpus ID, condition ID, ordered member IDs, and manifest digest
must also match either the tracked settled-corpus manifest or exact manifest
bytes supplied by a custody caller. Minting checks the exact source bytes;
loading and claim-row verification require repository registration.

The never-issued dual-family artifact without freshness data is removed from
the accepted wire shapes. Missing freshness now produces the existing
underived refusal instead of entering a compatibility branch. The contract
records why: the dual-family and freshness fields were introduced together,
so there are no issued bytes to preserve.

The existing `artifact_schema_invalid` diagnostic is retained to avoid a
reason-code registry change. Its two evidence-binding emission sites now state
that “schema” includes externally re-derived agreement between the artifact's
calibration membership and its named source bundles; the label does not mean
JSON syntax alone.

### Scoped design

**Forcing problem.** An attacker or defective producer could choose a corpus
digest, choose matching measurements, and recompute the artifact's internal
seal. Every field would agree internally while no external record established
that the named corpus existed.

**Options considered.** Keeping the self-seal was rejected because it restates
the defect. Embedding another copy of the manifest was rejected because an
artifact could forge that copy and its digest together. Resolving identity
against bytes outside the artifact was selected because the row explicitly
requires repository-registered or custody-bound bytes and the repository
already contains the governed manifest.

**Recommendation and worked example.** Keep structural validation available
for pure builders and fixtures, but require external identity resolution at
every disk-loading or claim-verification boundary. The regression constructs
an arithmetically valid artifact with a self-chosen corpus digest: structural
validation accepts its internal consistency, while authenticated validation
rejects it and the file loader returns no bound. Supplying exact independent
manifest bytes with matching identity makes the same authentication step pass.

### Finding and decision table

| Acceptance seam | Finding | Decision | Executed evidence |
|---|---|---|---|
| Environment and processor admission | Diagnostic telemetry labels could suppress current barriers | Remove label-derived early returns; retain configuration-derived dispatch | V1, V3 |
| Drift-corpus custody | The artifact's seal authenticated only its own assertions | Resolve corpus identity against external exact bytes | V1, V2, V3 |
| Missing freshness | Compatibility code represented no issued artifact | Reject as malformed and report the existing underived conditions | V1, V2, V3 |
| Evidence-binding diagnostic | The label could be read as syntax-only | Define its broader artifact/evidence-binding meaning at both emission sites | Code inspection and V4 |

No hardware, quiet-machine work, Ed action, dependency, scope expansion, or
new reason-code ruling is required for acceptance.

The magistrate-owned follow-up is to mark `CUSTODY-HARDEN-01` complete in the
state kernel with this report and the focused test commands as evidence, then
regenerate the task-queue and run-state projections. Those files were not
modified here. No paper-skeleton or decision-log edit is indicated: the kernel
acceptance already settles external corpus resolution, and the diagnostic
vocabulary did not change.

## Clause map

| Contract clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| “typed config's `hardware_target.telemetry_backend` is the mockness authority” (`docs/contracts/adapter_contracts.md:681`) | `joulewise/reduce.py:694` | `tests/test_reduce.py:2546` | Restore the metadata-label `mock` early return; an awake post-run display produces no refusal. |
| Same telemetry-authority clause | `joulewise/reduce.py:784` | `tests/test_reduce.py:2650` | Restore the metadata-label `mock` early return; duplicated CPU-attempt rows leave every claim gate eligible. |
| “artifact without the freshness block is therefore malformed” (`docs/contracts/adapter_contracts.md:414`) | `joulewise/whole_window.py:1623` | `tests/test_run_campaign.py:8540` | Re-enable the pre-freshness compatibility branch; the self-sealed no-freshness artifact validates instead of remaining underived. |
| “resolve against the exact bytes” (`docs/contracts/adapter_contracts.md:421`) | `joulewise/whole_window.py:1552` | `tests/test_run_campaign.py:7922`; positive arm `tests/test_run_campaign.py:8109` | Trust only the artifact's self-seal; the self-asserted corpus authenticates without external bytes. |
| “no other JSON file in that directory is a registered corpus authority” (`docs/contracts/adapter_contracts.md:428`) | `joulewise/whole_window.py:1601` | `tests/test_run_campaign.py:7967` | Glob sibling `*.json` files; a matching `untracked.json` authenticates the forged corpus. |
| “At file ingress” (`docs/contracts/adapter_contracts.md:422`) | `joulewise/whole_window.py:1740` | `tests/test_run_campaign.py:7922` | Remove `require_corpus_identity=True`; the forged artifact loader returns a bound. |
| “exact bytes of either the tracked settled-corpus manifest or a manifest held by the calling custody boundary” (`docs/contracts/adapter_contracts.md:423`) | `joulewise/whole_window.py:3707` | `tests/test_run_campaign.py:7817` | Remove the mint postcondition; the real derivation CLI writes a self-sealed artifact whose manifest digest disagrees with the tracked source bytes. |
| Same exact-byte clause at claim admission | `joulewise/whole_window.py:5439` | `tests/test_run_campaign.py:7990` | Remove `require_corpus_identity=True`; a claim row carrying a structurally valid forged drift artifact validates. |

## Verification notes

The repository-wide unit-test suite was intentionally not run, per the
preflight rule. Only the named focused modules and regression methods were
executed.

An intermediate combined run completed with one failure: an older test still
expected synthetic ten-member corpus IDs after its shared fixture was changed
to the tracked settled corpus. The expectation was updated to the manifest's
ordered members; its exact rerun passed, followed by clean V2 and V3 runs at the
final code shape. A later intermediate internal-API run exposed a mocked launch
lineage being re-authenticated by the new mint-time corpus check. The check was
narrowed to the intended exact-manifest invariant; the exact regression and
final V3 run passed.
