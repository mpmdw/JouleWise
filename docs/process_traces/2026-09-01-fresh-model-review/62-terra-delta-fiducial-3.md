```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The bench edit implements the nine-member closure mechanism, but the contract is not self-rerunnable and says CALL while the test records LINE events.",
  "workspace": {
    "base_requested": "a7a2917c",
    "base_mode": "exact",
    "head_start": "a2f99b09c67b2ff743ddbbc11a796523efd6deec",
    "head_end": "a2f99b09c67b2ff743ddbbc11a796523efd6deec",
    "upstream_end": "a2f99b09c67b2ff743ddbbc11a796523efd6deec",
    "branch": "feat/transfer-fiducial-01"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "location": "docs/contracts/transfer_fiducial.md:246",
        "title": "Closure procedure lacks an executable regression-test anchor",
        "detail": "“The regression test”, “synthetic fixture bundle”, and “fixture plan” are not bound to a test name or command, so a first-use reader cannot rerun the stated procedure from this prose alone."
      },
      {
        "id": "F2",
        "severity": "nit",
        "location": "docs/contracts/transfer_fiducial.md:251",
        "title": "CALL definition does not exactly match LINE instrumentation",
        "detail": "The contract defines execution as a code object receiving a call; both tracer paths record the file only on LINE. They give the same current pre-imported fixture membership, but are not the same stated procedure."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check a7a2917c..a2f99b09",
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
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import pkgutil, joulewise; names=sorted(m.name for m in pkgutil.walk_packages(joulewise.__path__, \"joulewise.\")); print(\"count\", len(names)); print(\"contains_main\", \"joulewise.__main__\" in names); print([n for n in names if n.startswith((\"joulewise.adapters.\", \"joulewise.analysis_engine.\"))])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "count 84",
          "contains_main True",
          "nested adapters and analysis_engine modules listed"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "count 84"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -l --glob '!docs/site/**' --glob '*.py' --glob '*.json' --glob '*.md' 'source_inventory_sha256' tests docs configs | sort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/contracts/transfer_fiducial.md",
          "tests/test_transfer_fiducial.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "transfer_fiducial"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": [
          "Not run: managed read-only sandbox cannot create the temporary directories required by the suite."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No unittest was run. A py_compile attempt also failed before compilation because the sandbox denied its temporary pycache directory.",
      "needs": "Lead rerun the focused test and canonical suite in a temp-capable environment."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Closure covers the one supported synthetic fixture path, not every refusal/verdict branch; this is the magistrate-registered limitation.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — should_fix** — [transfer_fiducial.md](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:246): Name the regression method (and preferably its unittest invocation). As written, “the regression test” does not let a reader independently locate the fixture construction and reproduce the asserted nine-member result.

- **F2 — nit** — [transfer_fiducial.md](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:251), [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:457): The contract’s CALL-event definition is not literal implementation. `sys.monitoring` records `LINE`; the fallback receives `call` only to install a handler that records on the first `line`. With all modules pre-imported, current file-membership results are equivalent for ordinary in-file Python code, including the measured nine; they are nevertheless distinct event definitions.

## Clause table

| Contract clause | Test/code | Implemented? |
|---|---|---|
| Nine named modules, each with a reason | Code tuple [transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:64); receipt membership test [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:796) | Yes |
| Pre-import every `joulewise` module except root `__main__` | Helper [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:411); use/assertions [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:602) | Yes |
| Call-receipt definition | LINE tracer / line-only fallback [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:457) | No — F2 |
| Run `fit_run` on `synthetic-transfer-r01` | [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:610) | Yes |
| Run `build_capture` with that fit plus nine fixture fits | Ten bundles are created at [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:203); patched capture at [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:619); loop calls `fit_run` once per bundle at [transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:1352) | Yes |
| Named trace-blind `clock.py`; blind subset and disjointness | [transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:75), [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:639) | Yes |
| Two-way closure equality | [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:648) | Yes |
| No duplicates and every inventory path exists | [test_transfer_fiducial.py](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:628) | Yes |
| Reader can rerun the procedure from the prose | Contract procedure [transfer_fiducial.md](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:246) | No — F1 |

`pkgutil.walk_packages` currently finds 84 children including `joulewise.__main__`; it includes nested `joulewise.adapters.*` and `joulewise.analysis_engine.*`. The helper skips the former, so it imports the other 83 plus the root package. Thus the current tree satisfies the pre-import clause.

## 59c items

- **(a) Subprocess isolation — defensible.** Pre-importing the complete package tree before tracing removes the import-order variable identified by 59b; its a#2 and c measurements both yielded seven. A subprocess would further isolate arbitrary process-global state, but no evidence shows such state affects this fixture.

- **(b) Explicit pre-import list — defensible for the present tree.** The walker reaches both relevant nested package families, root `__main__` is excluded, and any non-`__main__` import failure aborts the helper. The returned-name assertion is weak evidence by itself, but dynamic traversal better normalizes future modules than a stale explicit list. Minor future caveat: the predicate skips any nested module named `__main__`, while the contract excludes only `joulewise.__main__`.

- **(c) Per-outcome fixture and refusal-vocabulary closure — omission is defensible only as the registered limitation.** The harness honestly closes the exercised supported path; it does not establish receipt coverage for unexercised refusal/outcome branches. That is residual coverage risk, not a contradiction in the stated narrow procedure.

- **(d) Per-function digests — defensible.** The contract explicitly states the whole-file blast radius for `bundle_read.py` and `adapters/powermetrics.py`, including reissue-before-data and refusal-after-data behavior. The 59c churn argument remains operationally important, but it is disclosed policy rather than an unacknowledged fence failure.

## Receipt fixtures / goldens

No stored JSON under `tests/`, `docs/`, or `configs/` contains a `source_inventory` object or old 24-member `source_inventory_sha256`. The only current `source_inventory_sha256` references are the implementation, its dynamic test receipt, and the contract. Historical process traces and unrelated campaign provenance still mention mock telemetry, but are not transfer-receipt fixtures, goldens, or expected-key inventories.

## Residual risk

The closure test was not rerun here because the managed read-only sandbox denies required temporary directories; rely on the magistrate’s stated mutation and interpreter evidence until lead-side replay. The one-fixture-path limitation remains as recorded.

VERDICT: SHOULD-FIX