# terra 257 (gpt-5.6-terra, high, read-only) — operation-loop §5 delta fresh pass over `e17ea794`

Custodied verbatim from the seat's report (scratchpad paths redacted). Brief: `fresh-t26b-257.md` (D1–D3). Disposition: file 22 packet → cold gate (files 23–24) → synthesis (file 25).

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Delta has one should-fix: a literal from-import can shadow _fresh_probe while surviving the new AST guard; origin recovery is otherwise exact.",
  "workspace": {
    "base_requested": "7488a3c0",
    "base_mode": "exact",
    "head_start": "e17ea794bd7e5695f316e018664bd683570e6b27",
    "head_end": "e17ea794bd7e5695f316e018664bd683570e6b27",
    "upstream_end": null,
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 1,
      "nit": 0
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Literal from-import rebinding of _fresh_probe survives the claimed no-indirect-reference guard"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=<scratchpad>/tmp257b/delta-suite.t4x0U7 python3 -m unittest tests.test_arm_readiness_evidence_t0 tests.test_gen_state tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 131 tests in 221.611s",
          "OK (skipped=7)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK \\(skipped=7\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "build",
      "cmd": "TMPDIR=<scratchpad>/tmp257b/delta-suite.t4x0U7 python3 scripts/gen_state.py --check",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "String-concatenated globals/importlib lookups remain outside this static AST guard; these require deliberate obfuscation and are operator-only under D-161.",
      "needs": ""
    }
  ]
}
```

## Findings

- F1 — should_fix: The new guard misses an `ast.ImportFrom` rebinding such as `from joulewise.unrelated import _fresh_probe` placed after the local definition. The AST census still sees one local `FunctionDef` and the same twelve direct `Name` calls, so it passes while runtime calls can target the imported function.

  Add an indirect-reference rejection for `ast.alias` nodes whose `name` or `asname` is `_fresh_probe`. This is a small, ordinary refactor/mistake class—not deliberate-only adversarial construction—so it should be closed.

## D1

The unmutated module is clean: its only `_fresh_probe` references are one `FunctionDef` and twelve direct-call `ast.Name` nodes (one R1, eleven post-R1). It has no prohibited decorator, re-export, docstring/string literal, `__all__` entry, annotation, or default-argument reference.

Executed in-memory AST mutations:

| Mutant | Result | Assertion |
|---|---|---|
| Alias assignment | Killed | indirect `ast.Name` |
| Literal `globals()["_fresh_probe"]` | Killed | indirect string `ast.Constant` |
| Stored callback list | Killed | indirect `ast.Name` |
| Twelfth direct call | Killed | post-R1 site count |
| `functools.partial(_fresh_probe, ...)` | Killed | indirect `ast.Name` |
| Nested `def _fresh_probe` | Killed | exact `FunctionDef` count |
| Literal `from … import _fresh_probe` shadow | Survives | missed `ast.alias`; F1 |
| `globals()["_fresh_" + "probe"]` | Survives | computed name |
| `getattr(importlib.import_module(__name__), "_fresh_" + "probe")` | Survives | computed name |

The computed-name residual is deliberate obfuscation: neither form is a normal accidental use of this private helper, and evading the literal AST checks requires consciously constructing its name. Under D-161’s mistake-versus-deliberate boundary, it is operator-only and not worth expanding this static guard for.

## D2

Yes—the recovered origin is exact for authored receipt bundles.

- The author sets one `validity_origin = context.clock.monotonic_ns()` after all derivations, then emits every receipt as `validity_origin + _validity_horizon_ns(item.kind)`.
- All 13 governed receipt kinds partition exactly into the volatile and nonvolatile frozensets; `_validity_horizon_ns` reads only `kind` and fixed constants.
- `_fresh_clock_reference_batch` records `r1_batch_finished_monotonic_ns = context.clock.monotonic_ns()` immediately after R1, and the clock-row payload publishes that exact value.
- `_production_clock()` binds `monotonic_ns` to `time.monotonic_ns`; RAW values are separately sampled and explicitly named `*_monotonic_raw_ns`.

Thus `valid_until_monotonic_ns - _validity_horizon_ns(kind)` equals the shared ordinary-monotonic validity origin for every receipt in an authored bundle.

## D3

Requested suite: pass, 131 tests, 7 skipped, 221.611 s.  
`gen_state.py --check`: pass, silent exit 0.

## Residual risk

The static census does not prove runtime reachability or ordering, and deliberate computed-name lookup remains unguarded as described above.

## What this pass did NOT check

Only `git diff 7488a3c0 e17ea794` was reviewed. I did not audit parent changes, run full discovery, perform live/quiet-Mac work, or read loop briefs/transcripts (file 19 was not read).