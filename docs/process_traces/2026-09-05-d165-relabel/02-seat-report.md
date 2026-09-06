```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Relabeled the D-165 replay as a v2 shared-energy-sign/local-corner diagnostic while preserving v1 validation compatibility and unchanged replay behavior.",
  "workspace": {"base_requested":"0ed84b05","base_mode":"exact","head_start":"0ed84b0570fd5081b2cb4108085f575cbee978a7","head_end":"0ed84b0570fd5081b2cb4108085f575cbee978a7","upstream_end":null,"branch":"feat/2026-09-05-d165-relabel"},
  "pathspec": [
    "joulewise/dominance_closeout.py",
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "tests/test_d165_dominance_closeout.py",
    "tests/test_d117_contrast_v5_pack.py",
    "docs/process_traces/2026-09-05-d165-relabel/02-seat-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":[".......","----------------------------------------------------------------------","Ran 50 tests in 9.802s","","OK"]},
      "expected": {"exit_code":0,"tail_regex":"Ran 50 tests in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["........................","----------------------------------------------------------------------","Ran 40 tests in 14.625s","","OK"]},
      "expected": {"exit_code":0,"tail_regex":"Ran 40 tests in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":[]},
      "expected": {"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags": []
}
```

## Change

New replay results and the contrast registration now emit `d165_shared_sign_local_corner_replay.v2`, with the ratified absolute disposition and diagnostic label. The validator accepts both v1 and v2 sidecar results and both corresponding absolute-reason records. Regression coverage pins the P2 ten-block witness at ratio `1.500000`, `passes=False`, asserts the corrected reason, and retains the existing threshold, census, arithmetic, and branch checks.

## Verification notes

The mandated modules were run separately before and after implementation. The discovery suite was not run, as required by the preflight rule.
