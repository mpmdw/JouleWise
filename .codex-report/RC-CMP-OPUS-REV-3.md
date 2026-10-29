# RC-CMP-OPUS-REV-3: Opus delta review of the RC-CMP-5 structural fix

**Verdict: ACCEPT_WITH_FIXES on `7fede8c7`.**

Every probe from all four prior reviews now fails closed. S1, S2 and S3 close the false-agreements that earlier rounds
found. I found two shapes that still give exit 0 on wrong printed values: F1 and F2. L9's current producer emits
neither shape, and each fix is a few lines. I also found three narrow gaps (F3-F5).

Setup: branch `review/2026-10-29-rc-cmp-opus-rev-3` at `7fede8c76`, `/usr/bin/python3.13`, `TMPDIR=/tmp/rcrevtmp`.
Synthetic fixtures only. No real block-5/6/BYTES data was opened.
Suite: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
gives `Ran 235 tests in 136.611s OK (skipped=18)`. Output: `rc-cmp-opus-rev-3/suite.out`.

## Findings (ranked)

1. **F1 (S2 gap): a nested object can re-route its own leaves.** `leaves()` merges each object's scalar fields over
   its parents' fields, nearest first (`scripts/compare_b5_recompute.py:1313`). `binding()` then reads the identity
   fields from that merged context (`:1337`). So an object inside a fill contrast can carry its own `contrast_id`,
   and that id beats the contrast's id for every leaf below it.
   - Probe Q3c: the two contrasts' `floor` objects are swapped, and each one names the other contrast. The comparator
     exits 0:
     `Q3c floors swapped, each floor object naming the other contrast: exit=0 … unbound=[]`.
     The nested `floor/contrast_id` is even reported as `routing_id`.
   - Control Q3b, the same swap without the nested id, refuses with `value_differs`.
   - In L9's verdict producer (`joulewise/analysis_engine`), `contrast_id` appears only at contrast level, so this
     shape is not live today.
   - Fix: take each identity field only from the line or list-item object that owns the leaf. Or refuse when an
     identity field appears at two depths with different values. Add Q3c as a test.
2. **F2: duplicate JSON object keys are read silently.** `loads()` (`:251`) keeps the last value for a repeated key.
   - Probe Q4: a fill object with `"estimate": 999.0, "estimate": -1.25` gives `exit=0 … unbound=[]`.
   - A reader that keeps the first value would print 999.0. L9 writes its outputs with `json.dumps`, which cannot
     produce this, so the shape is not live.
   - Fix: an `object_pairs_hook` that raises `Refusal("duplicate_object_key:<source>")` for every input. That covers
     L9's files, the recompute output and the meter records.
3. **F3 (S1 is by JSON type only): a number written as a string passes as text.** `numeric()` (`:1304`) and
   `admits()` (`:1384`) treat a string as non-numeric, so a numeric string reaches the `uncovered:` catch-alls.
   - Under an `uncovered-by-name:` rule such a string is also left out of `uncovered_numeric`, because only numbers
     are listed (`:1419`).
   - Q1b: `"123.4"` under `fill:campaigns` gives exit 0, while the number refuses (Q1a).
   - Q1d: `"41.7"` as `battery_discharged/value_j` gives exit 0 with `uncovered_numeric=[]`, while the number is
     listed (Q1c).
   - Q1e: any new string field under `window_lines/.*` passes.
   - L9's producer prints numbers as numbers. The exceptions are block numbers (strings by design) and `text`
     (deferred to the post-release reader).
   - Fix: treat a string that parses as a finite float as numeric-class, except under the TEXT rule. Then give the
     block-number fields an `uncovered-by-name:` rule.
4. **F4: the AST test (S3) checks only `for` loops and comprehensions, and only `numeric`/`exact` calls**
   (`tests/independent_recompute/test_structural_rules.py:345,356`).
   - I appended three one-sided shapes to the script. The structure tests report `failures=0` for all three: a
     `while` loop in a `compare_*` function, a helper calling `c.add` in a loop, and a helper calling a `compare_*`
     function in a one-sided loop.
   - The control, a one-sided `for` loop, gives `failures=1`.
   - The shipped script has none of these shapes, so this is a guard gap, not a defect.
   - Fix: reject `ast.While` in `compare_*` functions, add `add` to the row-building attributes, and forbid calls to
     `compare_*` functions from outside `run` and `compare_*`.
5. **F5 (breadth, listed only in the restricted file): some `uncovered-by-name:` patterns accept any number below a
   broad name.** Examples are `(.*/)?attempt` (Q5a: `floor_attempt/attempt` 87.25) and
   `(conditions|metric|equivalence)(/.*)?` (Q5b: `equivalence/margin_j`, `equivalence/anything/x`). Exit 0 in both
   cases, and the numbers appear in `uncovered_numeric`. The public line gives only the count, and real windows will
   always have a non-zero count. Narrow these to the field names L9 actually prints. Not blocking.

Observation, not a finding: coverage checks the leaves that are printed, not completeness. A fill with no contrasts,
or with a contrast replaced by `{}`, gives exit 0 (Q2d, Q2e). No number is printed wrongly. Completeness of the fill
belongs to L9's fill validator.

## 1. Prior probes against 7fede8c7

All 17 scripts were rerun (`rc-cmp-opus-rev-3/prior_probes_rerun.out`). Every comparator probe fails closed:

- **Round 1, Sol `probe_comparator`:**
  - `missing_l9_run_cli 1`.
  - `wrong_fill_cli 2`.
  - `infinite_override` raises `Refusal bars_invalid:contrast_j` uncaught, which is the refusal. The guarded copy
    finishes: `public_counts_after (1, …)`, `wrong_machine_median_cli 2`, `missing_harvest_member_cli 2`.
- **Round 1, Opus `probe_comparator`:** P1-P12 all `exit0=False`, `REFUSED` or with failures.
- **Round 2, Sol `probe_new_paths`:**
  - `arm_wrong_id … cli 2`.
  - `arm_correct_id` gives `no_row`. This is a fill gate with no verdict gate, refused by design (RC-CMP-5 decision 2).
  - `new_nonfinite_leaf` is flagged.
  - `assist_recompute_only {'count': 1, 'routing_id': 1}`.
- **Round 2, Opus `probe_delta`:**
  - N1a-d: exit 2 (`step11_unmapped_fill` or `step11_nonfinite_value`).
  - N2: no duplicated keys. N2a: exit 2.
  - N3a/N3b: `{'rho': 2, 'routing_id': 1}`.
- **Meter, stream and archive probes** (both rounds, including `probe_meter_adversarial`): largest difference 0 ns at
  every origin, and the compressed plist is stopped. These found no defect before and still find none.

## 2. Attacks on the structural rules

`rc-cmp-opus-rev-3/probe_structural.py` and `.out`:

- **Strings that hold numbers:** F3.
- **Booleans:** pass `uncovered:` rules by design (Q2a exit 0). A boolean where a number is compared gives
  `value_differs`.
- **Nested lists:** a number in `[[123.4]]` refuses (Q2b). An empty nested list passes as an empty container (Q2c).
- **Empty containers:** no number printed. See the completeness note.
- **A key routed by its own line's value:** F1. The line-level identity fields (`contrast_id`, `pack`, `cell_id`,
  `model`, `run_id`, `block_number`) do route keys. Each one is checked by its `routing_id` row, and a same-path
  double binding refuses. The `text`-derived ratio label remains (RC-CMP-5 open issue 2).
- **Families compared outside `pairs`:** none in the shipped code. Every one-side map is built by `keyed()` or
  `items()`. The constant-keyed rows (brackets, branch, holm order, exclusions) build both sides from fixed keys.
  The L9-side-only conditions are `"arm_gates" in floor` and the projection's `refused is not None`. They create no
  row when L9 prints nothing, so any fill leaf that does print then refuses (`no_row`). The AST test's guard gaps are
  F4.
- **Duplicate keys across families:** the row space is (family, key), and a second row refuses
  (`row_key_duplicated`). Within one JSON object, duplicate keys are F2.
- **Broad by-name rules:** F5.
  - `uncovered-null-by-name:` covers only `j_per_token`. It accepts a null for any contrast, including a J/token
    contrast. That is an omission, not a wrong number.
  - A null elsewhere refuses (Q5c).

## 3. Over-refusal on a real full-size window

Every check below fails closed, and none of them is a false agreement. Each could stop a sound window:

- **A refused v3 arm gate.** L9's artifact validator requires `floor_gate_j: null` for a refused gate
  (`analysis_engine/artifact.py`). The fill copies it, and the comparator then refuses (Q6: exit 2, `row_disagrees`).
  Whether block 5 can release with a refused gate is a ruling for the lead.
- **The central band.** L9 calls a window clean when it has no window flags and no `meter.battery_activity`
  (`disclosures.py:677`). The recompute uses its own `clean` (`independent_recompute_b5.py:2087`). If the two rules
  differ on a real window, the band's `routing_id` disagrees.
- **List order.** L9 orders arm gates and resolutions by `floor_selector.condition_family_ids` = [A, B]
  (`analysis_engine/__init__.py:506-519`). Condition A is `sw-<phase>-a-qwen3-1p7b` in the v5 campaign configs. This
  matches the comparator's position rule and its id format, so I expect no refusal from order. Multi-source floor
  cells still refuse at source position 1 (RC-CMP-5 open issue 3).
- **Routing ids written differently:**
  - Band pack: L9 prints lowercase (`PACK_ORDER`), and the comparator lowercases its own side.
  - Block numbers: L9 prints them as strings, which `block_key` accepts.
  - Reported cell ids: mapped `d117-reported-mean-ph-` → `df-ph-`.
- **Other RC-CMP-5 candidates:** a missing p42 cell or `loo_magnitude` line, a repeated step-11 line, or an
  extraction report with no p42 cell.

**What settles it:** RC-CMP-4 (`report/2026-10-28-rc-cmp-4`) ran at `e5ccf720b`, and its report is still IN
PROGRESS, with no comparator result. Rerun the comparator at `7fede8c7` on its full-size custody, then read three
things from the restricted output: `coverage.unbound` reasons, `coverage.unmapped`, and the failing `routing_id`
keys. A sound window should show none of them. Any that appear is either a check to loosen or a real L9 or
recompute difference.

## Files

- `.codex-report/rc-cmp-opus-rev-3/suite.out`
- `prior_probes_rerun.out`
- `probe_structural.py` and `probe_structural.out`

The prior reviews' probe folders were extracted for the reruns. They are untracked and not committed.
