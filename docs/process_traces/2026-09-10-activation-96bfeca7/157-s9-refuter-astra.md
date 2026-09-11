```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One blocker and one should-fix: historical acceptance can change FAIL to PASS; case variants bypass the calibration output guard.",
  "workspace": {
    "base_requested": "d1c3d0c5",
    "base_mode": "exact",
    "head_start": "d1c3d0c551dc34e09e9a1f3f9b9ca465c6239368",
    "head_end": "d1c3d0c551dc34e09e9a1f3f9b9ca465c6239368",
    "upstream_end": "d1c3d0c551dc34e09e9a1f3f9b9ca465c6239368",
    "branch": "feat/2026-09-10-epoch-equivalence-check"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "scripts/epoch_equivalence_check.py",
        "line": 190,
        "title": "The reference is not restricted to the directive's r6 generation",
        "input": "Twelve valid, anchor-v3-resolved captures at 0.033 s; --acceptance configs/calibration/calibration_acceptance_d079_v2.json",
        "actual": "PASS against authenticated n19; the required r6 comparison is FAIL.",
        "recommendation": "Require the explicit r6 acceptance ID after authentication; reject other generations."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "scripts/epoch_equivalence_check.py",
        "line": 155,
        "title": "Case-sensitive path components bypass the output prohibition on this filesystem",
        "input": "--out CONFIGS/CALIBRATION/refuter-probe.json",
        "actual": "Guard accepts although its parent is the same directory as configs/calibration.",
        "recommendation": "Make the forbidden-directory check account for filesystem case equivalence and add a regression."
      }
    ],
    "audit": {
      "authority": "Issue 316 body verified through the GitHub connector after gh failed to connect.",
      "retention": "Declared slots and finalized_slots agree with the ledger model. Non-valid dispositions, unresolved/non-v3 anchors and absent rows are excluded.",
      "authentication": "Issuer checks manifest and evidence hashes before parsing; numeric tokens remain strings; checker requires exact equality with the row's bound lexeme.",
      "terminality": "Open, bracket-kind and unresolved-kind sessions refuse; aborted derivation sessions retain finalized slots.",
      "arithmetic": "Decimal lexemes at precision 80; inclusive comparisons; m<6 returns before comparisons.",
      "outputs": "Normal PASS/FAIL/INCONCLUSIVE paths write records and return 0/4/5; semantic refusal returns 3 without writing.",
      "supplemental_execution": "32 in-memory assertions passed with filesystem writes intercepted; these are isolated checks, not fixture or hardware validation."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_artifact_and_registry_disagreement_refuses tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_an_operative_the_loader_does_not_police_still_refuses tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_a_disagreeing_corpus_size_refuses tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_help_says_what_the_tool_never_does_and_glosses_its_terms tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_print_envelope_only_needs_no_session_and_writes_nothing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 5 tests in 0.004s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B -c 'from pathlib import Path; from types import SimpleNamespace as N; from unittest.mock import patch; from scripts import epoch_equivalence_check as c; s=N(session_kind=\"derivation\",state=\"finalized\",abort_reason=None,declared_slots=tuple(range(12))); r=[dict(slot=str(i),attempt_id=str(i),b_fiducial_s=\"0.033\") for i in range(12)]; p=patch.object(c,\"_slot_outcomes\",return_value=([],r)); p.start(); print([(c.reference_envelope(a)[\"acceptance_id\"],c.evaluate_session(s,\"night\",c.reference_envelope(a))[\"verdict\"]) for a in [c.DEFAULT_ACCEPTANCE_BOUND_PATH,Path(\"configs/calibration/calibration_acceptance_d079_v2.json\")]])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["[('d079_calibration_acceptance_v2_n17_r6', 'FAIL'), ('d079_calibration_acceptance_v2_n19', 'PASS')]"]
      },
      "expected": {"exit_code": 0, "tail_regex": "n17_r6.*FAIL.*n19.*PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -B -c 'from pathlib import Path; from scripts.epoch_equivalence_check import _refuse_out_path; p=Path(\"CONFIGS/CALIBRATION/refuter-probe.json\"); print(\"same_directory:\", p.parent.samefile(Path(\"configs/calibration\"))); _refuse_out_path(p, False); print(\"ACCEPTED\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["same_directory: True", "ACCEPTED"]
      },
      "expected": {"exit_code": 0, "tail_regex": "same_directory: True\\nACCEPTED"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "shasum -a 256 scripts/epoch_equivalence_check.py tests/test_epoch_equivalence_check.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ee55b8981a563b3e30cc26f29a43d5d7bec7f4a0624296c6c8a55b6280cfa348  scripts/epoch_equivalence_check.py",
          "af82b97a0767c548448b7bbb1b95a1c807735747054ed535a2babfe52289ae30  tests/test_epoch_equivalence_check.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "af82b97a0767c548448b7bbb1b95a1c807735747054ed535a2babfe52289ae30"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Fixture-backed tests and source mutations were not executed under the read-only instruction. Three mutation kills were assessed by inspection. Both file hashes are unchanged.",
      "needs": "Lead should run fixture-backed regression tests after fixing F1 and F2."
    }
  ]
}
```

## Findings

**F1 — blocker:** [epoch_equivalence_check.py:190](/Users/edr/code/JouleWise-wt-s9-eq-check/scripts/epoch_equivalence_check.py:190) accepts any authenticated registered generation. [Issue 316](https://github.com/mpmdw/JouleWise/issues/316) fixes **r6**.

Concrete counterexample: twelve retained values of `0.033`. R6’s operative level is `0.032898493715362`, so the result must be FAIL. Passing the checked-in n19 artifact through `--acceptance` selects level `0.033558756679900`, producing PASS. Both artifacts authenticate and pass registry cross-checks. Require the explicit r6 ID, while allowing alternate paths containing its authentic bytes.

**F2 — should-fix:** [epoch_equivalence_check.py:155](/Users/edr/code/JouleWise-wt-s9-eq-check/scripts/epoch_equivalence_check.py:155) compares directory names case-sensitively. On this machine, `CONFIGS/CALIBRATION` and `configs/calibration` identify the same directory, but the uppercase spelling passes the guard.

Concrete input: a valid terminal session with `--out CONFIGS/CALIBRATION/refuter-probe.json`. It reaches the write under the forbidden directory. With `--force`, an existing calibration artifact is also exposed. The guard bypass was reproduced without writing.

## Residual risk

Five existing tests and 32 isolated in-memory assertions passed. Fixture-backed tests were not run because they create files.

Three requested mutation assessments—**predicted kills, not executed**:

- Remove the non-valid disposition exclusion: [test_m_counts_only_valid_and_resolved_rows_and_lists_the_rest:199](/Users/edr/code/JouleWise-wt-s9-eq-check/tests/test_epoch_equivalence_check.py:199) gets `m=11`, violating its `m=10` assertion.
- Change verdict `and` to `or`: [test_one_value_above_the_level_screen_fails:122](/Users/edr/code/JouleWise-wt-s9-eq-check/tests/test_epoch_equivalence_check.py:122) returns PASS/0 instead of FAIL/4.
- Convert retained lexemes through `float` before Decimal: [test_full_precision_lexemes_survive_the_check_unrounded:462](/Users/edr/code/JouleWise-wt-s9-eq-check/tests/test_epoch_equivalence_check.py:462) fails its exact maximum assertion.

The committed tests lack exact-six, exact-bracket-equality, and raw-range-versus-operative boundary cases. Those passed the supplemental in-memory checks. Both reviewed files retain their original SHA-256 hashes.