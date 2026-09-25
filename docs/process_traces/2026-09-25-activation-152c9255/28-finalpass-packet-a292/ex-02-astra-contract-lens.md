```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two reducer SHOULD-FIX findings and one oracle SHOULD-FIX finding; 53 focused tests pass; three adversarial generated nights expose contract gaps without demonstrating incorrect counted totals or silent item loss.",
  "workspace": {
    "base_requested": "8d06633e",
    "base_mode": "exact",
    "head_start": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
    "head_end": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
    "upstream_end": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
    "branch": "feat/2026-09-25-a292-scored-reduce"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "joulewise/scored_reduce.py",
        "line": 103,
        "summary": "Window binding uses the placement index rather than the window's declared envelope_index, reversing E2 refusal outcomes.",
        "fix": "Evaluate _in_force(roster, w['envelope_index']); retain binding before duplicate and envelope checks. Update the oracle and add both cross-event index/stamp witnesses."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "path": "tests/scored_reduce_checker.py",
        "line": 286,
        "summary": "Oracle completeness interleaves missing-window, anchor and missing-row checks per placement, violating E2's ordered completeness passes.",
        "fix": "Use separate passes: all missing live windows, live null anchors in window input order, then all missing live rows."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "path": "joulewise/scored_reduce.py",
        "line": 56,
        "summary": "math.isfinite coerces arbitrary-size integers to float and raises OverflowError for contract-valid integer anchors and contract-invalid negative anchors.",
        "fix": "Use type(v) is int or (type(v) is float and math.isfinite(v)); independently correct the oracle's _number and add positive/negative 10**400 anchor regressions."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B /tmp/152c9255/a292-lens-astra/run_focused.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 53 tests in 88.004s", "FOCUSED_53=PASS", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FOCUSED_53=PASS"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -B /tmp/152c9255/a292-lens-astra/adversarial.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ADVERSARIAL_3_NIGHTS_10_PROBES_COMPLETE"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ADVERSARIAL_3_NIGHTS_10_PROBES_COMPLETE"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /tmp/152c9255/a292-lens-astra/numeric_followup.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "negative_finite_anchor_current=OverflowError:int too large to convert to float",
          "negative_finite_anchor_proposed_fix=window_domain; oracle=[]",
          "positive_finite_anchor_proposed_fix=accepted; oracle=[]",
          "NUMERIC_FIX_PROBE=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "NUMERIC_FIX_PROBE=PASS"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## feat/2026-09-25-a292-scored-reduce...origin/feat/2026-09-25-a292-scored-reduce",
          "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
          "8d06633ea6ea3591ac78cb8da400ea6ac26e109c"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The 200-night differential and M8 mutation sweeps were not rerun. V2 reports completed diagnostic execution, not universal E2 conformance. No full discovery or hardware measurement was run.",
      "needs": "Lead retains the differential, mutation-sweep and final cold-gate obligations."
    },
    {
      "id": "R2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Individually finite gross_j values of 1e308 can overflow math.fsum. E2 specifies finite output but does not assign aggregate overflow a refusal code or numeric range.",
      "needs": "Define the aggregate-overflow disposition before claiming total coverage of E2's unrestricted numeric domain."
    }
  ]
}
```

## Findings

**F1 — SHOULD-FIX: the in-force stamp is checked against the wrong index.**  
At `joulewise/scored_reduce.py:103`, the reducer uses `placement["envelope_index"]`. E2’s capture-window definition binds `roster_sha256` to `in_force(envelope_index)` on that window; placement equality is a separate, later check.

On generated night `(937, 2)`, choose a different envelope across an event-digest boundary:

| Window mutation | E2 first refusal | Reducer and oracle |
|---|---|---|
| Change index, retain original stamp | `window_binding` | `window_envelope` |
| Change index and stamp to match that index | `window_envelope` | `window_binding` |

Both implementations agree on the wrong operand (`tests/scored_reduce_checker.py:247` repeats it). Existing envelope-mismatch coverage does not establish behavior across a digest boundary.

**Exact fix:** use `_in_force(roster, w["envelope_index"])`; preserve the prescribed check order. Correct the independent oracle and add both witnesses. Neither input is accepted today, so this is refusal-contract corruption, not demonstrated energy miscounting.

**F2 — SHOULD-FIX: the oracle contradicts completeness precedence.**  
`tests/scored_reduce_checker.py:286–297` checks all three completeness conditions for one placement before visiting the next. The reducer’s separate passes at `joulewise/scored_reduce.py:162–171` follow E2.

Generated night `(929, 1)` demonstrates:

| Combined defects | Reducer/E2 | Oracle expects |
|---|---|---|
| Early null anchor; later missing live window | `missing_live_window` | `anchor_energy_envelope_unrecorded` |
| Early missing row; later missing live window | `missing_live_window` | `row_missing` |
| Early missing row; later null anchor | `anchor_energy_envelope_unrecorded` | `row_missing` |

**Exact fix:** three oracle passes: missing live windows in placement order; null live anchors in window input order; missing live rows in placement/item order. Add these simultaneous-defect witnesses. Do not change the reducer to satisfy the current oracle.

**F3 — SHOULD-FIX: finite integer anchors escape the refusal contract.**  
`joulewise/scored_reduce.py:56` calls `math.isfinite()` on integers. An anchor of `10**400` satisfies E2’s finite, nonnegative `int` domain but raises `OverflowError`. An anchor of `-10**400` also raises that exception instead of `window_domain`. The oracle has the same defect at `tests/scored_reduce_checker.py:33`.

**Exact fix:**

```python
return type(v) is int or (type(v) is float and math.isfinite(v))
```

Keep the separate sign checks. An in-memory application of this fix to each implementation made the positive anchor succeed and the negative anchor refuse `window_domain`, with oracle agreement. No repository file was modified. This fixes numeric validation; aggregate energy overflow remains the separate ruling gap R2.

**Disposition of the implementer’s four choices**

| Disclosed choice | Ruling |
|---|---|
| Per-window/per-row checks in input order; separate completeness passes | **Conforms.** Missing entries have no input position; placement/item order is the safer deterministic traversal. F2 concerns the oracle. |
| Binding uses the placement’s envelope index | **Contradicts E2**, for the reasons in F1. Checking the declared window index is safer because it preserves the specified binding-before-envelope precedence. |
| `k`, `mode`, and `claim_ready` sources | **E2 silent on these derivations.** `k = len(window_keys)`, registration mode, and roster `claim_ready` are the safer readings: they preserve window multiplicity and existing provenance without inventing a new eligibility decision. They do not establish registered claim validity. |
| Sparse `retry_stage_counts` | **E2 silent on absent-stage representation.** Sparse observed-stage counts are the safer reading of `{stage: I over paired items}`; E2 supplies no required stage-key set. |

**Remaining clause audit**

The following passed inspection and the focused checks, subject to F1/F3:

- **Entry:** five positional parameters without defaults; verifier is the first statement; packer refusals propagate; arguments remain unchanged. `sr.CAP_BOUND_FRACTION` is read at call time. The corrected **0.30** witness passes.
- **Refusal surface:** all 22 codes are present and disjoint from registration/packer codes. Nine window keys are enforced.
- **Window order:** `window_keys → window_domain → window_unknown → window_binding → window_duplicate → window_envelope → window_unstarted`. F1 affects binding’s operand; F3 affects numeric-domain evaluation.
- **Row order, including superseded rows:** `row_keys → row_domain → row_stop_reason_unknown → row_scorer → row_unknown → row_binding → row_duplicate → row_unstarted → row_tokens_over_cap → row_cap_disagreement`. Domains, coherence, membership, final-digest binding, and token-cap predicates match E2. Additional competing-defect probes confirmed input-list priority.
- **Completeness/status:** `reduce_input` follows verification; windows precede rows; completeness orders `missing_live_window → anchor_energy_envelope_unrecorded → row_missing`. Missing-window details name the key. `executed_status` receives exactly `frozenset(live keys)`, and its output is copied. The independent spread comparison raises `internal_disagreement`; its injection test passes.
- **K3/K24:** capped rows cannot be correct. Paired items control all specified counts, token sums, retry-stage counts, and division-form `cap_bound`. `n_counted`, `k24_dropped`, and parent `unpaired_item_ids` disclose excluded counterparts. Registration enforces globally unique item IDs, making the reducer’s `(model, item_id)` lookup sufficient for the stipulated level pairing.
- **Energy:** parent and cell sums use each live window once, in placement order. Non-live windows remain in their ledger. Unattributed terminal records carry null energy; ceiling records carry their optional window energy as E2 requires. Terminal items do not duplicate energy.
- **Output:** inspected key sets, ordering, nullable terminal fields, parent positions, level fields, superseded-row preservation, and canonical SHA-256 conform. No block or cell identifier is parsed to recover semantics.

**Adversarial evidence**

Three new generator nights were constructed through `generate_case` and the public packer:

1. **`(919, 0)`** combined all started optional captures, mixed capped/malformed/correct rows, reversed input order, and energies `1e16`, `1`, and `0.125`. Its 60 placements, 162 rows, 57 windows, and 11 unattributed terminal items reconciled. Reducer accepted; oracle returned `[]`; item/window conservation and the exact live-key call were asserted.
2. **`(929, 1)`** supplied simultaneous completeness defects and competing window/row errors, exposing F2.
3. **`(937, 2)`** crossed digest boundaries with mismatched window indices and exercised numeric extremes, exposing F1/F3 and R2.

Replay scripts and detailed results are under `/tmp/152c9255/a292-lens-astra/`. No successful probe produced an incorrect counted number or silently lost an item. That is a bounded finding, not a proof over every possible input.

**Next exact step:** correct F1/F3 and the oracle defects, retain these adversarial regressions, then perform the lead-owned mutation and final verification gates.

## Residual risk

The 200-night differential and M8 sweeps were not rerun. Aggregate overflow remains unspecified: individually finite positive energies can make `math.fsum` raise `OverflowError`; this produces no counted result, but lacks a ruled typed disposition. E2 v1 also remains pilot-complete only; registered claim validity requires the specified v2 floor/below-floor work.