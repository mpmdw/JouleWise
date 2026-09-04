```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Implemented both D-105 recognizer corrections with counterfactual tests; closure awaits the required independent exact-head delta audit.",
  "workspace": {
    "base_requested": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "base_mode": "exact",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-C3-RECOGNIZER-EXACT-01"
  },
  "pathspec": [
    "docs/contracts/campaign_log_tail_recognizer.md",
    "docs/process_traces/2026-09-04-fanout/C3-RECOGNIZER-EXACT-01/01-sol-report.md",
    "joulewise/campaign_provenance.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_run_campaign.CampaignLogTailGrammarTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 17 tests in 5.965s",
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
          "Ran 274 tests in 293.977s",
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
      "cmd": "python3 - <<'PY'\nimport subprocess\nimport sys\nimport types\n\nsource = subprocess.run(\n    [\"git\", \"show\", \"HEAD:joulewise/campaign_provenance.py\"],\n    check=True,\n    capture_output=True,\n    text=True,\n).stdout\nmodule = types.ModuleType(\"campaign_provenance_counterfactual\")\nsys.modules[module.__name__] = module\nexec(compile(source, \"HEAD:joulewise/campaign_provenance.py\", \"exec\"), module.__dict__)\nf1 = b'{\"\\\\ue000\": 1, \"\\\\ud83d'\nf2 = b'{\"a\": 1e+1000'\nobserved = (module.parse_campaign_log_bytes(f1), module.parse_campaign_log_bytes(f2))\nexpected_old_failures = ((None, \"invalid\"), ([], \"torn_prefix\"))\nif observed != expected_old_failures:\n    raise SystemExit(f\"unexpected counterfactual behavior: {observed!r}\")\nprint(\"counterfactual HEAD parser reproduces F1 false refusal and F2 over-acceptance\")\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "counterfactual HEAD parser reproduces F1 false refusal and F2 over-acceptance"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "counterfactual HEAD parser reproduces F1 false refusal and F2 over-acceptance"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "python3 -m py_compile joulewise/campaign_provenance.py",
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
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
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
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "D-105 requires an independent delta audit at the exact landed head; this session neither commits nor starts another agent by instruction.",
      "needs": "After harvest and commit, run a fresh independent audit over the exact commit and re-run the focused recognizer class if the audit changes code or tests."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The tracked D-105 and kernel text describe the counterexample classes but do not point to the original cold-gate packet bytes; the tests pin minimal literal members that reproduce both defects at the requested base.",
      "needs": "During the independent audit, compare the literals with the archived cold-gate packet and add any distinct historical literal without weakening the property tests."
    }
  ]
}
```

## Change

The campaign-log tail parser now decides escaped-key ordering from the exact
range of characters that an unfinished hexadecimal escape can still encode.
It carries a completed high surrogate into the following partial low
surrogate, applies the standard surrogate-pair arithmetic, and then uses the
first undecided character to answer whether any later-sorting key completion
exists. This closes the false refusal for non-Basic-Multilingual-Plane keys.

The former open-ended number heuristic is replaced by the D-105 decidable
superset. It preserves the writer's fixed/scientific notation boundary,
normalized coefficient, explicit exponent sign, exponent padding, and bounded
exponent width without claiming to decide Python's shortest-round-trip image.
The separate contract document records the forcing problem, rejected options,
ruled recommendation, grammar, worked examples, and proof obligations.

The tests convert the old expected misclassification into literal positive
assertions, add Basic-Multilingual-Plane/non-Basic-Multilingual-Plane boundary
properties, refuse numeric strings outside the superset, admit deliberate
superset-only prefixes, and check deterministic randomized binary floating-
point spellings. The counterfactual replay executes the base parser and
reproduces both defects, so removing the implementation makes the new tests
fail.

| Finding | Evidence | Decision | Closure |
|---|---|---|---|
| Escaped-key false refusal | Base parser returns `invalid` for the literal high-surrogate prefix; the new boundary property accepts every proper writer prefix. | Implement D-105 interval derivation, surrogate arithmetic, and prefix extension. | Implemented; focused and touched-module tests pass. |
| Number-prefix over-acceptance | Base parser accepts a four-digit scientific exponent as `torn_prefix`. | Replace the heuristic with the documented finite superset. | Implemented; refusal and randomized completeness properties pass. |
| Custody and release-path hygiene | Inspection finds preserve-before-truncate, recursive ASCII key enforcement, explicit in-flight exception chaining, and their existing regressions. | Preserve the D-105 compensating controls unchanged. | No additional mechanical change needed. |
| Independent audit | D-105 requires a fresh audit at the exact landed head. | Defer only this verification layer to the magistrate after harvest. | Pending; see flag F1. |

## Verification notes

The repository-wide unit-test suite was not run, exactly as the preflight rule
requires. Verification was limited to the touched module, its recognizer class,
syntax compilation, the counterfactual base replay, and whitespace/error-marker
inspection.

## Residual risk

NEEDS_RULING is not required for the design: D-105 selects the interval method
and the decidable-superset method. Acceptance nevertheless remains pending
until a different reviewer performs the exact-head delta audit. The reviewer
should also reconcile the pinned minimal byte strings with any archived cold-
gate packet because the tracked decision and kernel entries do not provide
that packet's literal byte sequence.
