# Sol 266 (gpt-5.6-sol xhigh, implementation, wt-decode-id @ 791a2522) — fix round 3 report

Custodied verbatim (scratchpad paths redacted). Returned NEEDS_RULING on R3-A's cross-profile assertion; ruled at the bench in file 35.

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "R3-B/C/D and the R3-A generator cure are implemented and green; R3-A's final cross-profile assertion requires a ruling because its two required objects have incompatible key sets.",
  "workspace": {
    "base_requested": "e3f52884",
    "base_mode": "descendant",
    "head_start": "791a2522513dc0de91c786025ba52a3f20031037",
    "head_end": "791a2522513dc0de91c786025ba52a3f20031037",
    "upstream_end": "791a2522513dc0de91c786025ba52a3f20031037",
    "branch": "fix/2026-09-02-decode-identity-set"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "docs/contracts/identity_pin_projection.md",
    "docs/decision_log.md",
    "tests/test_analysis_inputs.py",
    "tests/test_d117_contrast_v5_pack.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=<scratchpad>/tmp266/full-suite python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 487 tests in 107.752s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 487 tests .* OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
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
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff -- docs/paper/draft-v1.md",
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
      "id": "V4",
      "kind": "inspection",
      "cmd": "shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b  configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R3-A requires an exact four-key plan workload to equal each declared_identity.workload_profile after removing only suite_manifest_set, but both resulting declarations additionally contain prompt_tokens:null, prompt_text:null, and dataset_ref:null.",
      "needs": "Rule whether the test should also remove those three null typed-only fields (recommended), compare only the four shared fields, or use another explicitly authorized projection."
    }
  ]
}
```

## Change

### R3-A

Removed only the arm-A `prompt_tokens` literal from `workload_for`. The plan assertion at `tests/test_d117_contrast_v5_pack.py:867` pins the exact four-key workload and `:876` separately excludes `prompt_tokens`. `DECODE_PROMPT_TOKENS[arm]` remains at generator lines 1366 and 1551.

Initial RED:

```text
AssertionError: ... 'prompt_tokens': 42 ... != ... four-key profile ...
Ran 1 test in 0.453s
FAILED (failures=1)
```

The in-memory restoration counterfactual also failed:

```text
AssertionError: ... 'output_tokens': 512, 'prompt_tokens': 42} != ...
Ran 41 tests in 10.689s
FAILED (failures=1)
```

NEEDS_RULING:

- Question: how should the four-key plan workload be compared with each decode declaration?
- Observed generated declarations after removing `suite_manifest_set`:

```text
A/decode {'name': ..., 'repetitions': 1, 'warmup_runs': 1,
          'prompt_tokens': None, 'output_tokens': 512,
          'prompt_text': None, 'dataset_ref': None}
B/decode {same seven keys}
```

- Options considered:

  1. Also remove the three null typed-only fields before equality. Recommended; this expresses the four emitted common fields.
  2. Compare only the four plan keys against each declaration. Weaker because it permits undeclared extras.
  3. Remove the null fields from the declarations. Rejected: this exceeds “delete the line and nothing else” and conflicts with typed-profile comparison.

- Blocked work: only the requested exact equality assertion against both identity-unit declarations.

### R3-B

Installed the dictated freeze procedure and authentication paragraph at contract lines 451–501. No factual correction was needed.

| Clause | Proving production line |
|---|---|
| Read every inventoried configuration | `identity_pins.py:1436-1441` |
| Require the inventory digest | `identity_pins.py:1440,1446-1450` |
| Parse a JSON object | `identity_pins.py:1441-1455` |
| Type later, per configuration | `identity_pins.py:1592,1635-1636,1262-1278,1675` |
| Validate exact members and remove `suite_manifest_set` | `identity_pins.py:1465-1538` |
| Require a relative POSIX reference | `identity_pins.py:1505-1517` |
| Keep only the suffix after the pack name | `identity_pins.py:1544-1560` |
| Resolve below the root as a regular non-symlink | `identity_pins.py:1245-1259,1561-1568` |
| Read and authenticate manifest bytes | `identity_pins.py:1610-1630` |
| Authenticate manifests before declaration comparison | `identity_pins.py:1610-1630` precedes `:1635-1649` |
| Require the exact declared digest/reference pair | `identity_pins.py:1658-1670` |

Biting tests: `tests/test_d117_contrast_v5_pack.py:1087` and `:1118`.

`NOT PINNED: restoring the false contract denial changes prose only; no semantic documentation test can distinguish it. The existing manifest-tamper tests pin the production behavior.`

Contract-wide relevant hits:

| Contract hit | Action |
|---|---|
| Vocabulary, lines 81–108 | Checked; consistent, unchanged |
| Projection-input table, lines 309–310 | Checked; consistent, unchanged |
| Arm re-verification, lines 572–576 | Checked; consistent, unchanged |
| Receipt storage, lines 737–744 | Checked; consistent, unchanged |
| Refusal vocabulary, lines 755–769 | Checked malformed-vs-environment distinction; unchanged |
| Executable evidence, line 1019 | Added both manifest-byte authentication tests |
| Executable evidence, line 1022 | Added the direct missing-root test |

First-use audit:

| Term | First use | Definition |
|---|---:|---:|
| SHA-256 | 22 | 22–24 |
| campaign pack / pack root | 34 | 34–35 |
| declaration | 83 | 83–85 |
| common workload profile | 86 | 86–89 |
| `suite_manifest_ref` / digest | 87 | detailed constraints at 90–94 |
| declared manifest member | 90 | 90–98 |
| configuration inventory | 112 | 112–115 |
| reason code | 151 | 150–151; vocabulary at 755–760 |
| `BenchmarkConfig` typing | 453 | operation defined inline at 453–454; code at `identity_pins.py:1262-1278` |
| repository-relative manifest path | 462 | 90–93 |
| regular non-symlink below-root file | 463 | inline at 461–465 |
| unauthenticated manifest binding | 496 | inline at 496–501 |

Confirmed: “declared manifest member” is defined at its first use, lines 90–98.

### R3-C

Added the dictated lineage limitation at contract lines 609–621 and the direct-seam regression at `tests/test_analysis_inputs.py:706-727`.

| Clause | Proving production line |
|---|---|
| Arm records an absolute pack root | `arm_readiness.py:5242-5259` |
| Bundle loading authenticates lineage before evidence construction | `inputs.py:2768-2783` |
| Bundle authenticator enters launch-lineage authentication | `arm_readiness.py:10608-10670` |
| Consumption receipt is resolved/read; missing receipt gets its label | `arm_readiness.py:8960-8966,8835-8859` |
| Consumed arm is replayed | `arm_readiness.py:10127-10144` |
| Recorded pack root resolves strictly | `arm_readiness.py:9333-9352` |
| Launch manifest resolves/authenticates | `arm_readiness.py:8996-9028,10187-10192,10222` |
| Window root resolves strictly | `arm_readiness.py:10200-10205` |
| Lifecycle receipts resolve/authenticate | `arm_readiness.py:10233-10252,9794-9811` |
| Direct missing-root gate refusal | `inputs.py:3897,4039-4048,4082-4089` |

Removing `OSError` from the catch tuple in memory produced the required RED:

```text
FileNotFoundError: [Errno 2] No such file or directory: '.../missing-pack-root'
----------------------------------------------------------------------
Ran 1 test in 1.758s
FAILED (errors=1)
```

### R3-D

Appended the dictated addendum at `docs/decision_log.md:8464-8467` without changing the original R-1 sentence.

`NOT PINNED: the ruling-number correction is semantic prose; docs freshness does not distinguish R-1 from R-5.`

## Verification notes

```text
----------------------------------------------------------------------
Ran 487 tests in 107.752s

OK (skipped=1)
```

`git diff --check` and the paper-draft diff both returned zero with empty output. The D-166 registration remains:

```text
1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b
```

## Residual risk

Acceptance remains blocked only on the contradictory R3-A cross-profile assertion described above. No production file under `joulewise/` was changed.