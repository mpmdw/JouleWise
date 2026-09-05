```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured the surrogate-origin false refusal and made the prior counterfactual replay immutable; all scoped and importing test modules pass.",
  "workspace": {
    "base_requested": "74f21a1714af623a99db9d9530b6b71594cf5092",
    "base_mode": "exact",
    "head_start": "74f21a1714af623a99db9d9530b6b71594cf5092",
    "head_end": "74f21a1714af623a99db9d9530b6b71594cf5092",
    "upstream_end": "74f21a1714af623a99db9d9530b6b71594cf5092",
    "branch": "feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01"
  },
  "pathspec": [
    "docs/contracts/campaign_log_tail_recognizer.md",
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md",
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/03-sol-fix-round-1-report.md",
    "joulewise/campaign_provenance.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m py_compile joulewise/campaign_provenance.py && python3 -c 'import json; from joulewise.campaign_provenance import parse_campaign_log_bytes as p; w=json.dumps({chr(0xd83d):1,chr(0xd800)+chr(0xdc00):2},sort_keys=True).encode(\"ascii\"); bad=[(i,p(w[:i])) for i in range(1,len(w)) if p(w[:i])!=([],\"torn_prefix\")]; assert not bad,bad; print(\"all 31 proper surrogate-key prefixes accepted\")' && python3 -m unittest tests.test_run_campaign.CampaignLogTailGrammarTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 17 tests in 9.097s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 17 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 274 tests in 256.683s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 274 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_analysis_integration tests.test_mint_floor_artifact_generalized tests.test_supersession_cross_consumer tests.test_whole_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 270 tests in 154.152s",
          "",
          "OK (skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 270 tests in [0-9.]+s\\n\\nOK \\(skipped=2\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -c 'import json,subprocess; from pathlib import Path; s=Path(\"docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md\").read_text(); i=s.index(\"{\"); j=json.loads(s[i:s.index(\"\\n```\",i)]); c=next(v[\"cmd\"] for v in j[\"verification\"] if v[\"id\"]==\"V3\"); raise SystemExit(subprocess.run(c,shell=True,executable=\"/bin/zsh\").returncode)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "counterfactual merge-base parser reproduces F1 false refusal and F2 over-acceptance"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "counterfactual merge-base parser reproduces F1 false refusal and F2 over-acceptance"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -c 'import json,subprocess,sys,types; from joulewise.campaign_provenance import parse_campaign_log_bytes as p; w=json.dumps({chr(0xd83d):1,chr(0xd800)+chr(0xdc00):2},sort_keys=True).encode(\"ascii\"); s=subprocess.check_output([\"git\",\"show\",\"74f21a1714af623a99db9d9530b6b71594cf5092:joulewise/campaign_provenance.py\"],text=True); m=types.ModuleType(\"old\"); sys.modules[\"old\"]=m; exec(compile(s,\"74f21a17:campaign_provenance.py\",\"exec\"),m.__dict__); assert m.parse_campaign_log_bytes(w[:28])==(None,\"invalid\"); assert p(w[:28])==([],\"torn_prefix\"); print(\"refuter boundary 28 fails at 74f21a17 and passes after the fix\")' && python3 -m py_compile joulewise/campaign_provenance.py && git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "refuter boundary 28 fails at 74f21a17 and passes after the fix"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "refuter boundary 28 fails at 74f21a17 and passes after the fix"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The fix-round working tree is uncommitted, so D-105's required fresh independent audit cannot yet target its exact landed commit.",
      "needs": "Harvest and commit this scoped fix, then run a fresh independent delta audit at that exact commit before merge."
    }
  ]
}
```

## Change

| Finding | Cure | File:line |
|---|---|---|
| B1 blocker — json.loads collapsed the completed \ud800\udc00 key spelling to one scalar and falsely refused the refuter's real sorted-writer prefix at boundary 28. | Decode both feasible Python originals for each completed surrogate pair, propagate every still-orderable alternative across object keys, and exercise every proper prefix of the refuter's exact dictionary. | joulewise/campaign_provenance.py:298, :334, :387, :503; tests/test_run_campaign.py:627; docs/contracts/campaign_log_tail_recognizer.md:23 |
| S1 should-fix — the first seat report's counterfactual used mutable HEAD. | Pin both git show and the compile provenance label to immutable merge-base b0ed6991c11f3a515ad293760c6dfc031adda8e1; V4 parses the report and replays that exact recorded command. | docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md:71 |

No magistrate-owned state row is required by either cure.

## Verification notes

The repository-wide suite was not run, per the mission preflight rule. V2 is
the touched module. V3 is the complete mechanically identified set of other
test modules that directly import joulewise.campaign_provenance. V5 proves the
refuter's exact boundary-28 input fails at the requested head and passes with
this fix.

## Residual risk

D-105 still requires a fresh independent audit after the magistrate harvests
and commits this fix, because an uncommitted working tree has no immutable
exact head for that audit.
