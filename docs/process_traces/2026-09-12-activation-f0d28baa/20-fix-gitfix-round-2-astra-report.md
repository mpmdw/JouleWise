```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Pruned container folding and redundant dispatch guards; all 14 remaining cuts are killed, census is empty, and three consecutive runs pass.",
  "workspace": {
    "base_requested": "59873a5c",
    "base_mode": "exact",
    "head_start": "59873a5cbbb72395388df88100ddf9f59ef3d416",
    "head_end": "59873a5cbbb72395388df88100ddf9f59ef3d416",
    "upstream_end": "59873a5cbbb72395388df88100ddf9f59ef3d416",
    "branch": "fix/2026-09-12-git-fixture-maintenance-sweep"
  },
  "pathspec": ["tests/test_git_fixture_maintenance.py", "tests/test_git_fixture_hygiene.py"],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "ready"},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_hygiene.Round2Audit.test_isolated_cuts -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.112s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/private/tmp/gitfix-delta-audit.eHcUKc:. python3 -m unittest test_delta_audit.Audit.test_02_real_census test_delta_audit.Audit.test_03_assertion_fence -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["REAL_CENSUS {}", "Ran 2 tests in 5.512s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 12 tests in 5.611s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 12 tests in 5.617s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 12 tests in 5.605s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

Clause count, using the audit’s cut inventory: **29 → 14** (folder **23 → 11**, integration **6 → 3**).

Removed container folding:

```python
if isinstance(node, (ast.List, ast.Tuple)):
    values = [_constant_command_value(element) for element in node.elts]
    if all(isinstance(value, str) for value in values):
        return values if isinstance(node, ast.List) else tuple(values)
```

Replaced `"isinstance(left, (str, list, tuple)) and type(left) is type(right)"` with `"left is not None and right is not None"`.

Removed integration `"isinstance(node, ast.BinOp)"` and `"and isinstance(node.op, ast.Add)"`; the folder owns those checks. Replaced `"(folded,) if isinstance(folded, str) else tuple(folded)"` with `"(folded,)"`.

The existing concatenation test still covers list/tuple commands through recursive fallback. Added two rejection tests; no pre-existing assertion changed.

Each retained clause has exactly one selected killing test below. All test names belong to `tests.test_git_fixture_hygiene.GitFixtureHygieneTests`:

- **H:** `test_constant_concatenation_cannot_bypass_census`
- **R:** `test_constant_folder_rejects_nonstring_and_dynamic_nodes`
- **O:** `test_constant_folder_rejects_non_add_operators`

| Cut | Retained clause and isolated mutation | Selected test | Observed result |
|---|---|---|---|
| S01 | Remove constant `isinstance(node, ast.Constant)` guard | H | Ran 1; FAILED (errors=6) |
| S02 | Remove constant `isinstance(node.value, str)` guard | R | Ran 1; FAILED (failures=3) |
| S03 | `return node.value` → `return None` | H | Ran 1; FAILED (failures=6) |
| S04 | Remove folder `isinstance(node, ast.BinOp)` guard | R | Ran 1; FAILED (errors=9) |
| S05 | Remove folder `isinstance(node.op, ast.Add)` guard | O | Ran 1; FAILED (failures=3) |
| S06 | `left = _constant_command_value(node.left)` → `left = None` | H | Ran 1; FAILED (failures=6) |
| S07 | `right = _constant_command_value(node.right)` → `right = None` | H | Ran 1; FAILED (failures=6) |
| S08 | Remove `left is not None` guard | R | Ran 1; FAILED (errors=1) |
| S09 | Remove `right is not None` guard | R | Ran 1; FAILED (errors=1) |
| S10 | `return left + right` → `return None` | H | Ran 1; FAILED (failures=6) |
| S11 | Unsupported fallback `return None` → `return ""` | R | Ran 1; FAILED (failures=9) |
| S12 | Integration non-`None` guard → true, retaining assignment | H | Ran 1; FAILED (failures=6) |
| S13 | `result = (folded,)` → `result = tuple(folded)` | H | Ran 1; FAILED (failures=6) |
| S14 | Integration folding condition → `False` | H | Ran 1; FAILED (failures=6) |

Final `git status --short`:

```text
 M tests/test_git_fixture_hygiene.py
 M tests/test_git_fixture_maintenance.py
```

Final `git diff --stat`:

```text
 tests/test_git_fixture_hygiene.py     | 22 ++++++++++++++++++++++
 tests/test_git_fixture_maintenance.py | 18 +++++-------------
 2 files changed, 27 insertions(+), 13 deletions(-)
```

HEAD unchanged; nothing committed or pushed. No NEEDS_SCOPE or NEEDS_RULING. Next step: lead delta review.

## Verification notes

V1 used a temporary audit driver inside the authorized hygiene module, subsequently removed. Each cut was independently compiled and monkeypatched **in memory**, with restoration between selections; recursive calls used the mutant’s own namespace. Replaying V1 requires reinstating that driver using the table above.

The initial S12 witness, `test_alias_cycles_terminate`, survived. Selecting H killed S12; the table records the complete successful rerun.

V2 reused the supplied audit harness without editing it. Its assertion fence compares against `68c4dd46`; the duplicate-census deletion it reports predates this session. Final diff review also confirmed existing assertions unchanged. Verification remained limited to the requested fixture-tooling modules and audit checks.