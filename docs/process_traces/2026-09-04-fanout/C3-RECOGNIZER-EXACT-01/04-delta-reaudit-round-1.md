```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Both prior findings are cured, but the cure introduces exponential surrogate-alternative materialization, so the exact-head fix is not landable.",
  "workspace": {
    "base_requested": "cfe51555aa1e3156339fc1dbdac92592166ef783",
    "base_mode": "exact",
    "head_start": "cfe51555aa1e3156339fc1dbdac92592166ef783",
    "head_end": "cfe51555aa1e3156339fc1dbdac92592166ef783",
    "upstream_end": "cfe51555aa1e3156339fc1dbdac92592166ef783",
    "branch": "feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "disposition": "CURED",
        "location": "joulewise/campaign_provenance.py:334",
        "text": "The recognizer now retains both scalar and literal-surrogate origins, accepts the refuter's boundary-28 writer prefix, and passes the named regression; reverting the cure in a temporary package makes that regression fail."
      },
      {
        "id": "N1",
        "severity": "blocker",
        "disposition": "NEW",
        "location": "joulewise/campaign_provenance.py:360",
        "text": "Each completed high/low escape pair doubles a concrete string set. A valid 244-byte json.dumps prefix containing 20 pairs materializes 2^20 alternatives, measured at about 2.1 seconds and 418 MB; the parent handles the same input in about 0.00003 seconds. Longer valid or corrupt tails can exhaust memory or stall campaign-log loading."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "disposition": "CURED",
        "location": "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md:71",
        "text": "The recorded V3 now pins b0ed6991c11f3a515ad293760c6dfc031adda8e1 and replays successfully; changing that hash to HEAD in a temporary report reproduces the old replay failure. The textual cure resides in parent 58f64758 rather than git show HEAD, but it is present and durable at the requested exact head."
      }
    ],
    "same_signature": "No same-signature survivor was found: B1's false-refusal signature and S1's mutable-reference signature are absent at cfe51555; N1 is a distinct fix-introduced complexity and availability defect."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git branch --show-current && git status --short --branch && git show --name-status --format=fuller HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M\tdocs/contracts/campaign_log_tail_recognizer.md",
          "M\tjoulewise/campaign_provenance.py",
          "M\ttests/test_run_campaign.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "M\\tdocs/contracts/campaign_log_tail_recognizer.md\\nM\\tjoulewise/campaign_provenance.py\\nM\\ttests/test_run_campaign.py"
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
          "Ran 274 tests in 236.469s",
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
      "cmd": "python3 -m unittest tests.test_run_campaign.CampaignLogTailGrammarTests.test_c3_f1_every_bmp_non_bmp_key_boundary_is_tolerable",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.003s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "tmp=$(mktemp -d /tmp/c3-delta-b1-XXXXXX); cp -R joulewise \"$tmp/\"; git diff HEAD^ HEAD -- joulewise/campaign_provenance.py | patch -R -p1 -d \"$tmp\" >/dev/null; (cd \"$tmp\" && PYTHONPATH=\"$tmp:$OLDPWD\" python3 -m unittest tests.test_run_campaign.CampaignLogTailGrammarTests.test_c3_f1_every_bmp_non_bmp_key_boundary_is_tolerable); test $? -eq 1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.004s",
          "",
          "FAILED (failures=4)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FAILED \\(failures=4\\)"
      }
    },
    {
      "id": "V5",
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
      "id": "V6",
      "kind": "test",
      "cmd": "tmp=$(mktemp -d /tmp/c3-delta-s1-XXXXXX); cp docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md \"$tmp/report.md\"; perl -0pi -e 's/b0ed6991c11f3a515ad293760c6dfc031adda8e1/HEAD/g' \"$tmp/report.md\"; REPORT_PATH=\"$tmp/report.md\" python3 -c 'import json,os,subprocess; from pathlib import Path; s=Path(os.environ[\"REPORT_PATH\"]).read_text(); i=s.index(\"{\"); j=json.loads(s[i:s.index(\"\\n```\",i)]); c=next(v[\"cmd\"] for v in j[\"verification\"] if v[\"id\"]==\"V3\"); raise SystemExit(0 if subprocess.run(c,shell=True,executable=\"/bin/zsh\").returncode==1 else 1)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "unexpected counterfactual behavior: (([], 'torn_prefix'), (None, 'invalid'))"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "unexpected counterfactual behavior"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "python3 -c 'import json,resource,time; from joulewise.campaign_provenance import parse_campaign_log_bytes as p; n=20; w=json.dumps({\"\\U00010000\"*n:0},sort_keys=True).encode(\"ascii\"); raw=w[:w.index(b\":\")+1]; t=time.perf_counter(); assert p(raw)==([],\"torn_prefix\"); print(f\"valid_prefix pairs={n} bytes={len(raw)} seconds={time.perf_counter()-t:.6f} maxrss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "valid_prefix pairs=20 bytes=244 seconds=1.937989 maxrss=416743424"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "valid_prefix pairs=20 bytes=244 seconds=[0-9.]+ maxrss=[0-9]+"
      }
    }
  ],
  "flags": []
}
```

## Findings

### B1 — blocker — CURED

The exact refuter dictionary now accepts every proper prefix, including
boundary 28. The named regression passes at `cfe51555`; reverting the cure in
a temporary package makes it fail. A further 1,800-row ambiguity fuzz checked
133,179 proper prefixes without finding the same false-refusal signature.

### N1 — blocker — NEW

`_writer_string_alternatives` and the incomplete-string counterpart build a
set whose size doubles for every serialized high/low surrogate pair. The
244-byte proper prefix of `json.dumps({"𐀀" * 20: 0}, sort_keys=True)` therefore
creates 1,048,576 concrete strings. It measured 2.091 seconds and 417,579,008
bytes maximum resident set; 14/16/18/20 pairs grew from 0.013 to 0.070 to 0.386
to 2.031 seconds, while the parent implementation took about 0.00003–0.00006
seconds. This is an unbounded availability failure on valid writer prefixes,
not merely malformed input. Represent the alternatives compactly and compare
them with dynamic programming rather than materializing their Cartesian
product.

### S1 — should_fix — CURED

The report's V3 uses immutable merge-base `b0ed6991…` and replays successfully.
A temporary-copy mutation back to `HEAD` fails with the old observed mismatch.
The edit was harvested in parent commit `58f64758`, not the final fix commit,
but is present at the requested exact head.

Same-signature statement: neither prior finding signature survives. N1 is a
new complexity/availability signature introduced by the B1 cure.

## Residual risk

The ambiguity fuzz is finite, and timing is host-dependent. Neither limitation
weakens N1: the code constructs exactly two alternatives per pair, and the
measured 4–5× increase for each additional two pairs demonstrates the expected
exponential curve. Per the preflight rule, only the touched test module ran.
