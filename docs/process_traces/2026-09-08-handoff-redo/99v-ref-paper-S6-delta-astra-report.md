```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Fix round passes executable checks; clearance first-use and the DS-33 gloss remain incorrect.",
  "workspace": {
    "base_requested": "ce4a3ee4",
    "base_mode": "exact",
    "head_start": "89384243dcd2e0cb4f827b8f2b507a910ddced78",
    "head_end": "89384243dcd2e0cb4f827b8f2b507a910ddced78",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 1,
      "nit": 1
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "docs/contracts/paper_comparison_rendering.md",
        "line": 29,
        "summary": "Clearance still precedes its definition.",
        "evidence": "The first occurrence is interval/clearance display vocabulary at line 29; the gloss first appears at line 78.",
        "cmd": "rg -n 'clearance|shortfall' docs/contracts/paper_comparison_rendering.md",
        "requested_change": "Move or add the clearance gloss at line 29."
      },
      {
        "id": "F2",
        "severity": "nit",
        "file": "docs/contracts/paper_comparison_rendering.md",
        "line": 14,
        "summary": "The new DS-33 gloss misidentifies the registered slot.",
        "evidence": "The new gloss says prefill identity, repeating the existing line-95 description. Registry line 944 defines DS-33 as the Table 3 prompt floor requiring a prefill claim-floor token.",
        "cmd": "rg -n 'prefill identity|DS-33 identity' docs/contracts/paper_comparison_rendering.md\nrg -n '^\\| DS-33' docs/paper/results-fill-registry.md",
        "requested_change": "Describe DS-33 as the prefill claim-floor slot, preserving its unresolved token and G2-a binding."
      }
    ],
    "cures_verified": [
      "All five family names, supply-map roles, ordered input-role lists and fixture modes match supply_map.json exactly; the pending production role also matches.",
      "D-173 confirms the supplementary custody locators, source census and production floor_acceptance requirement.",
      "G2-a is correctly identified as g2a_selection inside Reported energy; characterization has no existing family.",
      "No shared-error or dominan matches remain. Replacement terminology agrees with the D-165 addendum.",
      "D-168 specifies eight ordinary ratios and four comparative R_cm values; fixture defaults and rejection tests enforce 8+4.",
      "F+B matches detection_floor.py planning_sizing_expression; Holm members match D-139 A2 and D-166.",
      "All requested first-use glosses pass except clearance.",
      "The six counterfactuals use assertRaisesRegex with distinct rule messages.",
      "Contradiction rejection remains effective without the arity guard.",
      "No additional regression or inconsistent duplicate definition was found in the diff."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_comparison_contract",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 14 tests in 0.002s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250"]
      },
      "expected": {"exit_code": 0, "tail_regex": "METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "grep -n 'shared-error\\|dominan' docs/contracts/paper_comparison_rendering.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\nimport tempfile, subprocess, os\nsource=Path('tests/test_paper_comparison_contract.py').read_text()\narity=\"    if len(case.stops) > 1:\\n        raise ValueError('stage precedence UNBOUND or conflicting stages')\\n\"\nassert source.count(arity)==1\nmutant=source.replace(arity,'')\nname='PaperComparisonContractTests.test_known_stage_order_does_not_license_contradictions'\nwith tempfile.TemporaryDirectory(prefix='paper-s6-delta-',dir=os.environ.get('TMPDIR')) as d:\n p=Path(d)/'test_contract.py'\n p.write_text(mutant)\n r=subprocess.run(['python3','-B',str(p),name],capture_output=True,text=True)\n print('ARITY REMOVED:',r.returncode,r.stderr.strip())\n assert r.returncode==0\n start=mutant.index('    if output.stop != canonical.stop:')\n end=mutant.index('    if (output.repeated_decode',start)\n p.write_text(mutant[:start]+mutant[end:])\n r=subprocess.run(['python3','-B',str(p),name],capture_output=True,text=True)\n print('ARITY AND CONTRADICTION CHECKS REMOVED:',r.returncode,r.stderr.strip())\n assert r.returncode==1 and 'does not match' in r.stderr\n print('PASS: contradictions rejected independently of arity; specific checks mutation-killed')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: contradictions rejected independently of arity; specific checks mutation-killed"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: contradictions rejected independently of arity; specific checks mutation-killed"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check HEAD~1 HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

- **F1 — should_fix:** Define “clearance” at its first occurrence, line 29; its current definition at line 78 is too late.
- **F2 — nit:** Correct the new DS-33 gloss to “prefill claim-floor slot.” The registry does not define it as an identity slot.

## Residual risk

Verification covers the synthetic contract and fallback validator, not production issuance or hardware. The full repository suite was not run for this documentation/test-only delta. Repository files and HEAD remained unchanged.