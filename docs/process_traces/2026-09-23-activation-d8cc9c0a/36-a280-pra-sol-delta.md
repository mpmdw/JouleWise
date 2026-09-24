```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No live behavior drift found beyond the ruled manifest delta; two test-strength findings remain.",
  "workspace": {
    "base_requested": "cdc05e9b",
    "base_mode": "exact",
    "head_start": "50dc22721c5a24966438870b6295b3a6ffa30116",
    "head_end": "50dc22721c5a24966438870b6295b3a6ffa30116",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 2, "nit": 0},
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "summary": "The idle-row window mutant survives both K3 and gate tests."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "The prefix/suffix mutation regression passes even when prepare ignores both mutated row fields."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B /tmp/a280-delta.uRSYCw/compare.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS: eight artifacts; sole manifest entry night_kinds.py; only downstream digest substitutions", "PASS: 15 direct parity cases"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS: 15 direct parity cases"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a280-delta.uRSYCw/check_edges.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["P1: 114 payload strings, zero differences", "wrong root suffix: Refused candidate is not a completed, owned preparation"]},
      "expected": {"exit_code": 0, "tail_regex": "wrong root suffix: Refused"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /tmp/a280-delta.uRSYCw/mutate.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["window: K3 exit 0; gate exit 0", "notice_followup: K3 exit 1; gate exit 0"]},
      "expected": {"exit_code": 0, "tail_regex": "notice_followup"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_kinds tests.test_night_gate",
      "cwd": "/tmp/a280-delta.uRSYCw/mutation",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 99 tests in 73.243s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 99 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_evidence_night.PrepareTests.test_real_composition_idempotence_and_never_invokes",
      "cwd": "/tmp/a280-delta.uRSYCw/base_git and /tmp/a280-delta.uRSYCw/mutation",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["base: Ran 1 test in 8.599s — OK", "head: Ran 1 test in 9.521s — OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -B /tmp/a280-delta.uRSYCw/tautology_probe.py",
      "cwd": "/tmp/a280-delta.uRSYCw/mutation",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["mutation regression PASS with prepare ignoring both row mutations"]},
      "expected": {"exit_code": 0, "tail_regex": "regression PASS"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The bench run was in progress, so this review used targeted tests and probes; no live night or full importer set was run.",
      "needs": ""
    }
  ]
}
```

### (a) Base versus head execution

The replay used separate `/tmp` copies of `cdc05e9b` and `50dc2272`. The worktree remained clean.

| Entry point or input | Result |
|---|---|
| `prepare`, plan authoring, locations, candidate sealing | The real prepare composition test passed at both revisions. Candidate-head `prepare` and `sealed_candidate` also passed in head K3. Plan bytes and locations matched. |
| Generator, manifest, notices | Eight artifacts matched after adding only `joulewise/night_kinds.py` to the manifest and substituting the resulting manifest and wrapper digests. |
| Gate and arm | Idle spent the scoped predicates; calibration skipped them. Four focused arm/gate tests passed at each revision. |
| Refusals | Unknown kind, calibration at the idle `prepare` entry, wrong prefix, wrong root suffix, wrong protocol path, window 8999, alternate chain, and source-digest mismatches retained their refusal outcomes. |
| Direct parity probe | All 15 result groups matched. |

### (b) P5: window pin

The exact condition at base `cdc05e9b` [quiet_predicate_campaign.py:158](/Users/edr/code/wt-d8cc9c0a-a280a-review/joulewise/quiet_predicate_campaign.py:158) was:

```python
if plan.window_max_s != protocol["window_max_s"]:
```

At `50dc2272`, [line 161](/Users/edr/code/wt-d8cc9c0a-a280a-review/joulewise/quiet_predicate_campaign.py:161) is exactly the same condition. The intermediate `702afd8d` condition also compared against `row.window_max_s`; that added comparison is gone. With the row patched to 8999, **both base and head accepted a 9000-second plan and refused an 8999-second plan** with the same `ValueError`. No plan acceptance or refusal difference was found beyond the ruled manifest change.

### (c) P1: payload strings

| Constructed inputs | Base versus head |
|---|---|
| Idle, absent declaration/calibration, calibration declaration, unknown kind, duplicates, ledger co-export, empty text | Identical |
| Quotes, comments, non-export assignments, CRLF, spaces and tabs around exports, empty or expanded values | Identical |

All **114 strings** matched. For today’s table, `quiet_predicate_evidence` is the sole row with `payload_kind=True`; the declaration parser and ledger/duplicate guards are unchanged. Thus the new table predicate has the same accepted strings as the base’s fixed-kind comparison.

### (d) P6: calibration `None`

| Call | Base | Head |
|---|---|---|
| Live `prepare(kind="calibration", t0="next")` | `Refused: invalid or unresolved kind` | Same |
| Direct `locations()` after patching `KIND` to calibration | Returned idle paths | `Refused: kind has no preparation path identity` |

The second call is a test-only path. The live `prepare` entry refuses calibration before reaching `locations`, so no live path was found that now hits the new `None` refusal after proceeding at base.

### (e) Idle-row mutation table

“Killed” means the named test failed on a single-field mutant in the `/tmp` candidate copy.

| Mutant | K3 golden | Gate module |
|---|---|---|
| Plan prefix; root suffix | Killed; killed | Survived; survived |
| Chain path; protocol path | Killed; killed | Killed; killed |
| Window 9000 → 8999 | **Survived** | **Survived** |
| Chain authentication; chain-bound registration | Survived; survived | Killed; killed |
| Corecaptured flag; non-observer flag | Survived; survived | Killed; killed |
| Four notice text fields | Killed all four | Survived all four |

The separate row-constant test kills the window mutant (`8999 != 9000`), but K3 and the gate tests do not prove that plan authoring consumes that field.

### Same-signature check

| Signature | Yes/no | Finding |
|---|---|---|
| Live behavior drift beyond the manifest delta | No | — |
| Prior F2 literals in `verify_manifest` and the generator left outside the table | No | — |
| Mutation regression that stays green under the intended fault | Yes | F2 |

The notice literals expressly deferred to PR B by brief 28 remain outside this fix-round judgment.

## Findings

**Blocker:** None.

**Should fix — F1.** K3’s candidate-head preparation reads the committed table, so an uncommitted mutation of the row’s `window_max_s` is invisible to its authored-plan check. Executed counterexample: changing that field to 8999 in the `/tmp` candidate left both [K3](/Users/edr/code/wt-d8cc9c0a-a280a-review/tests/test_night_kinds.py:228) and all gate tests at `OK`. K3 should establish the row-to-authored-plan relationship while preserving P5’s protocol-only verification rule.

**Should fix — F2.** The prefix/suffix mutation regression can pass because [its helper](/Users/edr/code/wt-d8cc9c0a-a280a-review/tests/test_night_kinds.py:392) first asserts that each row field equals a fixed literal. Executed counterexample: a `/tmp` probe made `prepare` use the original row while each test mutation was active. Both plans retained the original prefix and suffix, yet `test_k3_kills_prefix_and_suffix_mutations` passed. A direct prefix mutant failed K3 at the row-literal assertion, before that failure could establish that `prepare` used the mutated value.

**Nit:** None.

## Residual risk

This was a targeted, read-only re-audit during a bench run. The full importer set and live hardware gates were not run.