```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All required prior and new mutations refuse; only a non-soundness parser-maintainability NIT remains.",
  "workspace": {
    "base_requested": "2a6d3841ed6426c53d90820601f8622636f1fd3b",
    "base_mode": "exact",
    "head_start": "3f1677b79b5ba17ec4ee8ef1db8d5df431e71cee",
    "head_end": "3f1677b79b5ba17ec4ee8ef1db8d5df431e71cee",
    "upstream_end": "2a6d3841ed6426c53d90820601f8622636f1fd3b",
    "branch": "feat/2026-09-02-dx-registry"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "verdict": "NOT CLEAN",
    "same_signature": "no — prior registry/artifact/replay-fence mutation classes are closed",
    "findings": [
      {
        "id": "NIT-1",
        "severity": "nit",
        "lens": "maintainability",
        "file": "scripts/check_paper_round7_artifacts.py",
        "line": 237,
        "summary": "DX-027's required renderer is a row-specific literal in the parser. It is sound, but further row-specific renderer requirements would extend parser control flow rather than a declarative contract.",
        "replacement_text": "Optionally define REQUIRED_RENDER_RULES = {\"DX-027\": \"signed_2_percent\"} near EXPECTED_DX_IDS and validate it through one generic lookup after R7F_RENDER parsing."
      }
    ],
    "mutations": [
      {"id": "M1", "what": "DX-014 marker digit 2.5→2.6 ms", "result": "REFUSED rc=2: row DX-014"},
      {"id": "M2", "what": "DX-011 marker sign swapped", "result": "REFUSED rc=2: row DX-011"},
      {"id": "M3", "what": "Reissued F4 first onset-circle coordinate shifted +0.10 px", "result": "REFUSED rc=2: figure onset mark 0"},
      {"id": "M4", "what": "Reissued AQ population_size 15.9", "result": "REFUSED rc=2: row DX-020 names AQ#summary.population_size"},
      {"id": "M5", "what": "Reissued AQ adds other_refusal bucket", "result": "REFUSED rc=2: row DX-021 names AQ#summary.v3_refusals_by_token"},
      {"id": "M6", "what": "DX-003 command loses --svg", "result": "REFUSED rc=2: RegistryError names DX-003"},
      {"id": "M7", "what": "Reissued AQ population_size true", "result": "REFUSED rc=2: row DX-020 names AQ#summary.population_size"},
      {"id": "M8", "what": "Reissued AQ v3_derived_count 13 with matching DX-021 marker", "result": "REFUSED rc=2: row DX-021 rejects derived+refused != population"},
      {"id": "M9", "what": "DX-027 marker unsigned under signed renderer", "result": "REFUSED rc=2: row DX-027 expected 0.61 %, rendered +0.61 %"},
      {"id": "M10", "what": "DX-003 command uses a different --out path", "result": "REFUSED rc=2: RegistryError names DX-003"},
      {"id": "M11", "what": "Reissued AQ anchor_unresolved list shortened to two", "result": "REFUSED rc=2: row DX-021 rejects list/count mismatch"}
    ],
    "tests": "test_paper_round7_artifacts: OK (21 tests); test_paper_replay_fence: OK (skipped=1); test_docs_freshness: OK"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 21 tests in 461.657s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_paper_replay_fence",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 9 tests in 0.284s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK \\(skipped=1\\)$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 6 tests in 0.051s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --repository-root /Users/edr/code/JouleWise-wt-dx --corpus-root /Users/edr/code/JouleWise --registry /Users/edr/code/JouleWise-wt-dx/docs/paper/results-fill-registry.md --skeleton /Users/edr/code/JouleWise-wt-dx/docs/paper/draft-v2-skeleton.md --literals-only",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R7F COMPARED 181 / MISMATCHES 0"]},
      "expected": {"exit_code": 0, "tail_regex": "^R7F COMPARED 181 / MISMATCHES 0$"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --repository-root /Users/edr/code/JouleWise-wt-dx --corpus-root /Users/edr/code/JouleWise --registry /Users/edr/code/JouleWise-wt-dx/docs/paper/results-fill-registry.md --skeleton /Users/edr/code/JouleWise-wt-dx/docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ok   replay XD bytes", "ok   replay F4 bytes", "ok   replay AQ bytes", "R7F COMPARED 184 / MISMATCHES 0"]},
      "expected": {"exit_code": 0, "tail_regex": "^R7F COMPARED 184 / MISMATCHES 0$"}
    }
  ],
  "flags": []
}
```

## Findings

- NIT-1: The DX-027 guard is sound. This parser is already a fixed, closed-schema parser—see the comparable DX-003 literal guard at `scripts/check_paper_round7_artifacts.py:228` and fixed row set at `:272`—so this is only a maintainability preference, not a fence defect.

No blocker or SHOULD_FIX finding: M9 demonstrates that an unsigned `0.61 %` with the signed renderer is rejected by rendered-value comparison (`+0.61 %`), even though it is not rejected at parse time.

The DX-021 third field reference is redundant, not dead: it remains independently resolved by `check_supplier_fields` at `scripts/check_paper_round7_artifacts.py:345`, while the renderer directly validates the full bucket map and then reads `anchor_unresolved` at `:426-445`. The digest-half count therefore remains 181.

`grep` found no `0.61 %` literal in the skeleton or checklist. The checklist retains only `[FILL:DX-027]` at `docs/paper/round7/fill-checklist.md:268`.

## Residual risk

The full retained-corpus replay passed, but its AQ producer required 461.657 seconds because several retained raw traces are resolved through the configured backup mirror.