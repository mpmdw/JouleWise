```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No blocker found; 13 of 29 isolated cuts lack killing tests. Real census and requested 52-test suite pass; retained assertions and worktree are unchanged.",
  "workspace": {
    "base_requested": "68c4dd46",
    "base_mode": "exact",
    "head_start": "59873a5cbbb72395388df88100ddf9f59ef3d416",
    "head_end": "59873a5cbbb72395388df88100ddf9f59ef3d416",
    "upstream_end": "59873a5cbbb72395388df88100ddf9f59ef3d416",
    "branch": "fix/2026-09-12-git-fixture-maintenance-sweep"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R3",
        "severity": "should_fix",
        "path": "tests/test_git_fixture_maintenance.py",
        "line": 73,
        "title": "Folding clauses lack isolated killing tests",
        "cuts": ["C02","C04","C05","C06","C07","C11","C18","C23","C24","C26","C27","C28","C29"],
        "evidence": "Each listed cut survives all five maintenance tests and all five hygiene tests.",
        "recommendation": "Add the targeted tests named below; consider removing the behaviorally redundant integration Add guard."
      }
    ],
    "real_census": {},
    "retained_assertions_changed": 0,
    "final_git_status_short": ""
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/gitfix-delta-audit.eHcUKc:. python3 -m unittest test_delta_audit.Audit.test_01_cuts -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 1 test in 51.035s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/gitfix-delta-audit.eHcUKc:. python3 -m unittest test_more_cuts.Audit.test_01_cuts -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 1 test in 11.201s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/gitfix-delta-audit.eHcUKc:. python3 -m unittest test_container_type_cuts.Audit.test_01_cuts -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 1 test in 10.935s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/gitfix-delta-audit.eHcUKc:. python3 -m unittest test_delta_audit.Audit.test_02_real_census test_delta_audit.Audit.test_03_assertion_fence -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["REAL_CENSUS {}","Ran 2 tests in 5.404s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene tests.test_identity_pins -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 52 tests in 14.457s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":[]},
      "expected": {"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags": []
}
```

## Findings

**No blocker found. R3 — should-fix:** The new concatenation test does not independently protect every folding clause. Thirteen cuts survive all ten scanner tests, partly because the existing recursive fallback still detects their command fragments.

All mutations were compiled and monkeypatched **in memory**, independently restored. Temporary harnesses and logs remain under `/private/tmp/gitfix-delta-audit.eHcUKc/`. V1–V3 report successful audit execution; individual mutant outcomes follow.

Test names used below:

- **H:** `GitFixtureHygieneTests.test_constant_concatenation_cannot_bypass_census`
- **R:** `GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper`

Every H selection ran **1 test**. R rows report its containing maintenance suite, which ran **5 tests**; R was the sole failing test. For every “survives” row, both complete modules additionally reported **Ran 5 tests / OK**, separately.

| Cut | Independent clause cut | Selected test: count and result |
|---|---|---|
| C01 | Remove constant AST-type guard | H: Ran 1; `FAILED (errors=6)` |
| C02 | Remove constant string-type guard | H: Ran 1; `OK` — survives |
| C03 | Constant value return → `None` | H: Ran 1; `FAILED (failures=6)` |
| C04 | Remove `ast.List` support | H: Ran 1; `OK` — survives |
| C05 | Remove `ast.Tuple` support | H: Ran 1; `OK` — survives |
| C06 | Replace element recursion with raw AST elements | H: Ran 1; `OK` — survives |
| C07 | Remove all-elements-are-strings guard | H: Ran 1; `OK` — survives |
| C08 | List result → `[]` | H: Ran 1; `FAILED (failures=2)` |
| C09 | Tuple result → `()` | H: Ran 1; `FAILED (failures=2)` |
| C10 | Remove folder `BinOp` guard | R: Ran 5; `FAILED (errors=1)` |
| C11 | Remove folder `Add` guard | H: Ran 1; `OK` — survives |
| C12 | Left recursive value → `None` | H: Ran 1; `FAILED (failures=6)` |
| C13 | Right recursive value → `None` | H: Ran 1; `FAILED (failures=6)` |
| C14 | Remove supported-left-type guard | R: Ran 5; `FAILED (errors=1)` |
| C15 | Remove same-type guard | R: Ran 5; `FAILED (errors=1)` |
| C16 | Addition result → `None` | H: Ran 1; `FAILED (failures=6)` |
| C17 | Remove integration `BinOp` guard | H: Ran 1; `FAILED (errors=6)` |
| C18 | Remove integration `Add` guard | H: Ran 1; `OK` — survives |
| C19 | Remove integration non-`None` guard, retaining assignment | R: Ran 5; `FAILED (errors=1)` |
| C20 | Remove string wrapping; always `tuple(folded)` | H: Ran 1; `FAILED (failures=2)` |
| C21 | Remove container flattening; always `(folded,)` | H: Ran 1; `FAILED (errors=4)` |
| C22 | Disable integration folding branch | H: Ran 1; `FAILED (failures=6)` |
| C23 | Reject empty containers | H: Ran 1; `OK` — survives |
| C24 | Unsupported fallback `None` → `""` | H: Ran 1; `OK` — survives |
| C25 | Remove `str` from supported left types | H: Ran 1; `FAILED (failures=6)` |
| C26 | Remove `list` from supported left types | H: Ran 1; `OK` — survives |
| C27 | Remove `tuple` from supported left types | H: Ran 1; `OK` — survives |
| C28 | Remove tuple conversion; always return list | H: Ran 1; `OK` — survives |
| C29 | Remove list type preservation; always return tuple | H: Ran 1; `OK` — survives |

Missing tests, named concretely:

- **C04/C06/C23/C26/C29:** `test_constant_folder_preserves_list_values_and_type`, asserting exact folded values and list type, including empty and nested operands.
- **C05/C06/C23/C27/C28:** `test_constant_folder_preserves_tuple_values_and_type`, with equivalent tuple cases.
- **C02/C07/C24:** `test_constant_folder_rejects_nonstring_and_dynamic_nodes`, asserting `None` for numeric constants, mixed containers, names, and calls.
- **C11:** `test_constant_folder_rejects_non_add_operators`, including nested unsupported operations.
- **C18:** `test_resolver_skips_folder_for_non_add` would require a dispatch spy. With the current folder, this guard duplicates its `Add` check and removal is behaviorally equivalent; removing the redundant clause is preferable to inventing a behavioral killing test.

**R2 deletion is safe.** Maintenance remains the real-tree census home. Line **291** is:

`self.assertEqual(_git_init_violations(TESTS_ROOT), {})`

The unmodified real census returned exactly **`{}`**. No folding-induced false positive was observed in existing `tests/` modules.

**Assertion fence passes.** Comparing assertion ASTs against `68c4dd46`:

| Module | Retained tests | Unchanged assertions |
|---|---:|---:|
| `test_git_fixture_maintenance.py` | 5 | 6 |
| `test_git_fixture_hygiene.py` | 4 | 5 |
| `test_identity_pins.py` | 42 | 177 |

Only the authorized duplicate `test_repository_census` disappeared; the concatenation test was added.

The requested combined run reported:

```text
Ran 52 tests in 14.457s

OK
```

Final `git status --short` was empty; HEAD remained unchanged. Next step: lead disposition of R3 and targeted coverage additions.

## Residual risk

This was a delta-only audit. Full discovery, hosted CI, and hardware validation were outside its scope.