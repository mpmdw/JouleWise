```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Design consult complete: no new defect found; existing class-IV failures call for a path-complete contract and a re-cut lane.",
  "workspace": {
    "base_requested": "c0998fdb55fedc90213697dfaa61cf87a66e80e1",
    "base_mode": "exact",
    "head_start": "c0998fdb55fedc90213697dfaa61cf87a66e80e1",
    "head_end": "c0998fdb55fedc90213697dfaa61cf87a66e80e1",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_reduce",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 1.482s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests in .*s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)\\s*$"}
    }
  ],
  "flags": []
}
```

## Q1 — Why Registration did not close class IV

The hypothesis holds. Exact keys, no defaults, and a digest establish that a value was supplied and preserved. They do not establish that the value governs every operation that needs it. The registered `item_set_sha256` is never compared with the items supplied to [`pack`](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_packer.py:212). [`requeue_overrun`](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_packer.py:287) checks caller supplied failed predictions instead of the predictions stored in the roster. The initial arranger limits a cell to one block per envelope; the retry append path does not. Registration also accepts spread minima of 1, although M8 rules 5.

The sweeps test record shape. The operand mutations test existing comparisons. Neither detects a missing comparison, an unauthorized input source, or a guard omitted from a later path. A digest authenticates the roster’s bytes; it does not prove that those bytes satisfy M8.

## Q2 — Acceptance shape and binding matrix

Yes, use the matrix. Assert mechanically that its field rows equal the 38 names in [`_FIELDS`](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_registration.py:15), and keep ruled invariants in a separately reviewed list. Each named path needs a violating example that refuses, or an explicit provenance-only outcome. A test that merely reads a field or observes a changed digest is insufficient for a behavioral guard.

Here **V** means registration validation, **P** initial pack, **W** whole-block retry, **S** split and single retries, **R** reduction, and **E** the deferred estimator. “Needed” identifies a missing binding, not a new finding.

| Field or rule | Current consumer; needed path | Acceptance probe |
|---|---|---|
| `schema` | V | Wrong schema refuses. |
| `mode` | V, P, W/S, R | Pilot stays unclaimable through retries and reduction. |
| `registration_id` | V, digest | Changed identity invalidates bound roster. |
| `plan_id` | V, digest | Changed plan invalidates bound roster. |
| `sizing_receipt_sha256` | V, digest; receipt gate needed | Missing registered receipt or wrong pinned receipt refuses. |
| `arm` | V, P, W/S, R | Altered arm or stale roster copy refuses. |
| `arm_to_family` | V, `family`; E | Selected arm derives one family; later decision binds it. |
| `role_to_model_id` | V, P, W/S, R | Swapped or stale model identities refuse. |
| `levels` | V, P, W/S, R | Missing, added, or aliased level refuses. |
| `merge_order` | V; E | Any other order refuses; estimator follows both chains. |
| `min_correct` | V; E | Value other than 3 refuses. |
| `alpha` | V; E | Invalid alpha refuses; estimator uses registered alpha. |
| `holm_m` | V; E | Value other than 5 refuses. |
| `n_boot` | V; E | Invalid count refuses; bootstrap uses it. |
| `seed` | V; E | Invalid seed refuses; replay is deterministic. |
| `floor_j` | V; E | Invalid bound refuses; estimator consumes it. |
| `anchor_j` | V; E | Invalid bound refuses; estimator consumes it. |
| `cap_tokens` | V, W/S, R; P needed | Over-bound prediction refuses at P; cap equality governs R. |
| `cap_bound_fraction` | V, R | Value other than .20 refuses; exact boundary stays unlabelled. |
| `block_size` | V, P; W/S roster check needed | Stale copy refuses; block membership and count agree. |
| `n_per_level` | V, P | Short or long item list refuses. |
| `min_blocks_per_cell` | V, P; W/S needed | Fewer than **five original sampling blocks** refuses. |
| `min_envelopes_per_cell` | V, P; W/S needed | Fewer than five distinct active envelopes refuses. |
| `envelope_s` | V, P; W/S roster check needed | Incoherent geometry or stale copy refuses. |
| `offset_s` | V, P; W/S roster check needed | Offset outside envelope or stale copy refuses. |
| `interior_s` | V, P; W/S roster check needed | Capacity breach on initial and tail paths refuses. |
| `guard_s` | V, P; W/S roster check needed | Nonpositive usable interior or stale copy refuses. |
| `pitch_s` | V, P; W/S roster check needed | Pitch below envelope or stale copy refuses. |
| `s_per_token_upper` | V, W/S; P needed | Prediction above derived worst case refuses at P, W, S. |
| `prefill_s` | V, W/S; P needed | Same derived-bound probe with nonzero prefill. |
| `ceiling_s` | V; P/W/S bound check needed | Derived worst case above ceiling refuses. |
| `retry_stages` | V, W/S, R | Unknown or skipped stage refuses on each transition. |
| `max_drift_lever_slots` | V, P, W/S, R | Initial excess refuses; retry excess is carried to R. |
| `delta_upper_j_per_block_slot` | V formula | Changed delta without matching limit refuses. |
| `budget_j` | V formula | Changed budget without matching limit refuses. |
| `declared_sensitivities` | V; E | Unsupported sensitivity refuses before decision use. |
| `scorer_id` | V, digest; scorer gate needed | Wrong scorer provenance refuses. |
| `item_set_sha256` | V; P needed | Same registration with different ordered IDs refuses. |
| **M7: gross only** | R | Offset, idle, and tail energy cannot enter cell joules. |
| **M8: spread** | P; W/S/R needed | Same-cell collision or fewer than five original blocks/envelopes refuses after each transition. |
| **M12: retry** | W, S, R | Each stage preserves items, parent, bounded packing, and typed terminal state. |
| **Drift rule** | P, W/S, R | Recompute on executed order; excess cannot silently remain claimable. |
| **Cap rule** | R | At cap, flags and reason must agree; capped correct refuses. |

Its main failure mode is **circular acceptance**: a matrix copied from code can omit the same rule as the code. Derive the invariant rows from the ruling text, and require counterexamples for every transition. Fields reserved for E need a stated deferred gate; their presence must not imply that this infrastructure is claim ready.

## Q3 — Constants and caller arguments

Make ruled values constants, or assert exact equality if they must appear in a signed registration: levels 1–5, merge order, `min_correct=3`, `holm_m=5`, both spread minima of 5, `cap_bound_fraction=.20`, and the five retry stage names. If AP-5M fixes envelope geometry, bind its exact profile too; coherence alone does not authorize arbitrary geometry. Keep empirical quantities such as cap tokens, block size, timing bounds, delta, and budget registered, with their source receipts.

Replace free `items_by_level` authority with registered ordered IDs, or require a canonical manifest whose hash is checked against `item_set_sha256` at P. Remove `failed_prediction_s` from W and split decisions: use the roster’s bound predictions. Keep separately named, item-keyed **observed elapsed seconds** for single-stage attribution. Pin the prediction table to the sizing receipt and check each item against its derived worst case at P.

## Q4 — M12 and M8 on retry tails

Both rulings can stand. M12 permits several single-problem **blocks** in an envelope; M8 permits at most one from each cell. Thus singles from different cells may share an envelope when capacity allows, while sibling singles from one cell go to distinct envelopes. Recheck M8 after every append. Count the original parent blocks for the five-block sampling minimum, so splitting one block cannot manufacture replication. The amendment needs this explicit sentence in AP-5M; its current wording left the retry path ambiguous.

## Q5 — Continue or re-cut

Re-cut. The round-2 stop rule calls for a consult, not another patch round under the same acceptance brief. First close registration, canonical item and prediction binding, initial packing, and **all retry transitions** against the matrix. Then take the executed roster and evidence-row contract into a separate reducer slice, with its own path probes. Keep `claim_ready` from asserting claim eligibility until those slices and the deferred estimator gates are integrated.

## Findings

No new defect beyond the prior delta reviews was established in this consult.

## Residual risk

The named suite passes, but its 13 tests do not establish the missing semantic bindings. This review did not exercise a scored-night runner or live evidence.