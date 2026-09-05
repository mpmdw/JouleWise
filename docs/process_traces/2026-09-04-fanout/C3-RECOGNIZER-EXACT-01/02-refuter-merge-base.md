```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The refreshed mission delta is scope-clean and its claimed tests pass, but a real sorted-writer surrogate-key prefix is still falsely refused.",
  "workspace": {
    "base_requested": "74f21a1714af623a99db9d9530b6b71594cf5092",
    "base_mode": "exact",
    "head_start": "74f21a1714af623a99db9d9530b6b71594cf5092",
    "head_end": "74f21a1714af623a99db9d9530b6b71594cf5092",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "location": "joulewise/campaign_provenance.py:541",
        "text": "A completed key escape pair is collapsed by json.loads to one astral scalar, although json.dumps emits the same bytes for a Python key containing two literal surrogate code units. sort_keys orders the original Python strings, so this loss of alternatives makes the recognizer reject a proper prefix of a real writer output, violating D-105's completeness direction.",
        "counterfactual": "json.dumps({'\\ud83d': 1, '\\ud800\\udc00': 2}, sort_keys=True) emits b'{\"\\\\ud800\\\\udc00\": 2, \"\\\\ud83d\": 1}'; the proper prefix ending after the second closing quote is currently classified (None, 'invalid') instead of ([], 'torn_prefix')."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "location": "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md:68",
        "text": "Claimed test V3 is not replay-stable: it names mutable HEAD as the old implementation. At the reviewed landing head the exact recorded command exits 1 because it observes both fixes, contrary to the recorded expected old failures.",
        "counterfactual": "Replace HEAD in git show and the compile label with the immutable merge-base b0ed6991c11f3a515ad293760c6dfc031adda8e1; the counterfactual then reproduces both old defects."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-status \"$base\"..HEAD; git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "A docs/contracts/campaign_log_tail_recognizer.md",
          "A docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md",
          "M joulewise/campaign_provenance.py",
          "M tests/test_run_campaign.py",
          "state-doc delta: empty"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "four declared paths; state-doc delta: empty"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_run_campaign.CampaignLogTailGrammarTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 17 tests in 5.371s",
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
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 274 tests in 270.721s",
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
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -c 'import subprocess,sys,types; b=subprocess.check_output([\"git\",\"merge-base\",\"origin/main\",\"HEAD\"],text=True).strip(); s=subprocess.check_output([\"git\",\"show\",b+\":joulewise/campaign_provenance.py\"],text=True); m=types.ModuleType(\"cf\"); sys.modules[\"cf\"]=m; exec(compile(s,b+\":campaign_provenance.py\",\"exec\"),m.__dict__); assert m.parse_campaign_log_bytes(bytes.fromhex(\"7b225c7565303030223a20312c20225c7564383364\"))==(None,\"invalid\"); assert m.parse_campaign_log_bytes(bytes.fromhex(\"7b2261223a2031652b31303030\"))==([],\"torn_prefix\"); print(\"merge-base reproduces F1 false refusal and F2 over-acceptance\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "merge-base reproduces F1 false refusal and F2 over-acceptance"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "merge-base reproduces F1 false refusal and F2 over-acceptance"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -c 'import json; from joulewise.campaign_provenance import parse_campaign_log_bytes as p; w=json.dumps({chr(0xd83d):1,chr(0xd800)+chr(0xdc00):2},sort_keys=True).encode(\"ascii\"); bad=[(i,p(w[:i])) for i in range(1,len(w)) if p(w[:i])!=([],\"torn_prefix\")]; assert not bad,bad[:1]'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: [(28, (None, 'invalid'))]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "all proper prefixes accepted"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -c 'import json,subprocess; from pathlib import Path; s=Path(\"docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md\").read_text(); i=s.index(\"{\"); j=json.loads(s[i:s.index(\"\\n```\",i)]); c=next(v[\"cmd\"] for v in j[\"verification\"] if v[\"id\"]==\"V3\"); raise SystemExit(subprocess.run(c,shell=True,executable=\"/bin/zsh\").returncode)'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "unexpected counterfactual behavior: (([], 'torn_prefix'), (None, 'invalid'))"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "counterfactual HEAD parser reproduces F1 false refusal and F2 over-acceptance"
      }
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "python3 -m py_compile joulewise/campaign_provenance.py && git diff --check",
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

## Findings

### B1 — blocker

The parser treats a completed `\\ud800\\udc00` key as only U+10000 because
`json.loads` combines the escapes. That byte spelling can also have been
emitted from a Python string containing two surrogate code units. Python
`sort_keys=True` orders those original code units before the lone high-surrogate
key `\\ud83d`, but the recognizer compares `\\ud83d` against U+10000 and
refuses boundary 28. This is a real `json.dumps(dict, sort_keys=True)` proper
prefix and directly violates D-105's required completeness direction. Add this
row to the BMP/non-BMP boundary property and preserve all feasible decoded-key
alternatives when checking order.

The intended F1 fix is otherwise defect-shaped: on the merge-base parser,
`b'{"\\ue000": 1, "\\ud83d'` and
`b'{"\\ue000": 1, "\\ud83d\\ud'` make the new registered test fail. The
intended F2 fix is also defect-shaped: on that parser,
`b'{"a": 0.0000'` and `b'{"a": 1e+1000'` make the new refusal test fail.

### S1 — should_fix

The implementation report's V3 says `git show HEAD:...`, so its meaning
changed when the implementation was committed. Exact replay at `74f21a17`
fails with the fixed outcomes. Pinning `b0ed6991c11f3a515ad293760c6dfc031adda8e1`
instead reproduces both old defects and makes the evidence durable.

The refreshed scope check is clean: the merge-base delta has exactly the four
paths declared in `01-sol-report.md`. `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta.
No previous refuter verdict exists at this path in HEAD or repository history,
so there is no previous-round non-staleness blocker to re-test. The current
mutable-HEAD counterfactual issue was independently replayed as S1.

## Residual risk

The deterministic 4,096-value float sample is not exhaustive, but no additional
numeric defect was found; B1 is sufficient to prevent landing.
