```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two promotion-validation gaps remain; executed probes confirm the committed pins, loader hold, R7 default and doubling thresholds.",
  "workspace": {
    "base_requested": "8458f797",
    "base_mode": "exact",
    "head_start": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "head_end": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "refuter": "DISSENT",
    "findings": [
      {
        "id": "S1",
        "severity": "should_fix",
        "file": "scripts/promote_calibration_candidate.py",
        "line": 80,
        "summary": "Deleting required citation fields bypasses citation authentication."
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "file": "scripts/promote_calibration_candidate.py",
        "line": 107,
        "summary": "An H1 identifier without its text satisfies the hold check; all substantive hold disclosures can be omitted."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/d138-contract2-d528efb2/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B -m unittest -v tests.test_calibration_dispositions tests.test_promote_calibration_candidate tests.test_claim_hold_routes tests.test_calibration_bracketing.DoublingTriggerDispositionTests tests.test_floor_mint_pinsets_schema > /tmp/d138-contract2-d528efb2/focused-tests.out 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/d138-contract2-d528efb2/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B -m unittest -v tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.test_every_issued_generation_and_genesis_fixture_load_byte_identically tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.test_every_registered_generation_row_carries_the_full_schema tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.test_range_equals_screen_rows_need_no_d125_ruling tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_cli_default_is_frozen_to_r7 tests.test_acc_25g83_rev5.RevisionFiveTests.test_revision_five_predecessor_default_and_simulation_are_frozen_to_r7 tests.test_gen_state.TestRefreshedStateFidelity.test_exact_live_id_set > /tmp/d138-contract2-d528efb2/retained-tests.out 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "TMPDIR=/tmp/d138-contract2-d528efb2/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B /tmp/d138-contract2-d528efb2/probes.py > /tmp/d138-contract2-d528efb2/probes.out 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PROBES_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "PROBES_COMPLETE"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/d138-contract2-d528efb2/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B /tmp/d138-contract2-d528efb2/mutations.py > /tmp/d138-contract2-d528efb2/mutations.out 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M1_drop_disposed_count KILLED tests=3 failures=3 errors=0",
          "M2_drop_loader_hold KILLED tests=2 failures=2 errors=0",
          "M3_drop_undeclared_decision KILLED tests=1 failures=1 errors=0",
          "M4_drop_input_seal_stop KILLED tests=1 failures=1 errors=0",
          "MUTATIONS_COMPLETE"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTATIONS_COMPLETE"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-contract2-d528efb2/audit_tests.py > /tmp/d138-contract2-d528efb2/test-audit.out",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["AUDIT_COMPLETE: 10 changed test files; no existing test method removed"]
      },
      "expected": {"exit_code": 0, "tail_regex": "AUDIT_COMPLETE: 10 changed test files; no existing test method removed"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Executed 37 focused tests and scratch probes, not the canonical whole suite or historical RED runs. No hardware collection or battery reads occurred.",
      "needs": "Lead retains whole-suite, historical RED-record and final verification ownership."
    }
  ]
}
```

REFUTER: DISSENT

## Findings

No BLOCKER demonstrated. Two SHOULD-FIX findings remain in regeneration validation; neither invalidates the currently committed bytes.

**S1 — Deleting citation fields bypasses authentication.**  
`scripts/promote_calibration_candidate.py:80`, `:100–102`, `:116–119`.

The recursive verifier checks an object only when **both** `relative_path` and `file_sha256` exist. Required nested structures are insufficiently checked before that walk.

Executed V3:

- P5a: delete `source_candidate.relative_path` → **ACCEPTED**.
- P5b: delete one network-time source ruling’s `file_sha256` and change its path to `does-not-exist` → **ACCEPTED**.
- P5f: delete `network_time_provenance.source_rulings` entirely → **ACCEPTED**.

The prescribed P4a–P4f all refuse now. These additional mutations expose an omission route around that repair. Require complete citation records for the required source fields before recursively authenticating them. Add refusal tests for deletion as well as alteration.

Evidence: [probe script](/tmp/d138-contract2-d528efb2/probes.py), [executed output](/tmp/d138-contract2-d528efb2/probes.out).

**S2 — A bare H1 identifier passes without any substantive hold disclosure.**  
`scripts/promote_calibration_candidate.py:106–108`.

Executed P5g replaces the entire holds list with:

```json
[{"id": "H1"}]
```

Promotion **ACCEPTED** it. This removes H1’s text and H5–H7 altogether, despite the issued-file structure specified in original ruling §7.1. The retained `hold_enforcement` sentence does not reproduce those conditions.

Require the prescribed hold entries and nonempty text. Add deletion and empty-text counterfactuals. This concerns the issued record’s completeness; the loader’s code-enforced hold remained effective.

**Other executed contract results:**

- Issued SHA-256 exactly equals the requested `d6de84…d5ea` and registry pin. Both seals verify; input seal remains `e7363b…b011`. Promotion reproduces the committed bytes.
- Byte-identical copies load with explicit non-claim opt-in. Whitespace changes, reserialization, resealed member/disclosure changes, candidate bytes and identifier substitutions refuse.
- Disposition-file changes refuse under the old pin; changing the file and production pin without updating the table also refuses. Table-only drift fails the equality check.
- Default loading returns R7, epoch 25F84. HR-1 through HR-8 passed, including held-default import refusal.
- DT-1 through DT-5 passed. Independent probes found no doubling trigger at 1, 2, 4 or 11 new captures; 12 and 13 trigger stale refusal. R7 remains below threshold at 33 valid rows and triggers at 34.
- Four in-memory implementation mutations were killed by the corresponding tests; no mutation touched repository files.

**Main-test comparison:** inspected all ten changed files against `9eab16f8`, supplemented by the AST audit. No existing test method disappeared and no calibration assertion from main was weakened. The new-generation exclusions preserve every old-generation check. The separate census delta in `tests/test_gen_state.py:23` and `:943` removes `WALLCLOCK-STEP-SOURCE-01`, adds five IDs and changes 281 to 285; this is outside the addendum’s calibration changes and comes from lead-committed bookkeeping `fbf0007d`. Exact set/count assertions remain, and the census test passes.

## Residual risk

The canonical suite, historical RED runs, real-ledger replay and live gates were not repeated. Synthetic bracket evidence is not hardware validation.

Repository files remained untouched; scratch evidence is confined to `/tmp/d138-contract2-d528efb2/`. The next step is lead adjudication of S1/S2, followed by focused refusal tests and a delta re-audit if changed.