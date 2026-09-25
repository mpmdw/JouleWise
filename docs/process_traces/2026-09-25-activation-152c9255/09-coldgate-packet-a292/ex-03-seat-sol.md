```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a sealed-v4 reducer with explicit row and window schemas, live-window completeness, typed terminals, and an independent reducer oracle.",
  "workspace": {
    "base_requested": "75d04e9e",
    "base_mode": "descendant",
    "head_start": "23289fc5ef71664d6a59161d79be4720d6e53b6f",
    "head_end": "23289fc5ef71664d6a59161d79be4720d6e53b6f",
    "upstream_end": "75d04e9ee7b6ee23df25fed0a30478a45f97090b",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "The sealed rulings require row and window binding but leave their complete A292 schemas and reducer refusal codes open; R1 and R2 propose exact text for the magistrate."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "text": "The merged executed-status shape is implemented but was marked proposed in contract v4.1; R4 proposes affirming that shape and its per-cell/per-level split."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "text": "Checker INV-12 is stricter than the ruled contract; A292's harness must avoid treating agreement on that predicate as a gate until reconciliation."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_scored_packer tests.test_scored_roster_checker",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 65 tests in 13.730s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 65 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "R1–R7 are design recommendations, not adopted A292 contract text.",
      "needs": "Magistrate rules the proposed text before the RED harness is frozen."
    }
  ]
}
```

## Findings

### R1 — Schemas and refusal vocabulary — BLOCKER

I recommend an exact, versioned JSON interface. `reduce(registration, roster, predicted_decode_s, item_rows, block_windows)` must call `verify_executed_roster(registration, roster, predicted_decode_s)` as its **first statement**, allowing its `PackingRefusal.code` to pass through unchanged. This is the ruled real-entry gate, and the merged verifier checks the seal, root re-pack, event replay, and reporting completeness. [Cold ruling Q16](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:47); [merged verifier](joulewise/scored_packer.py:471).

Each score row is a **counted, live item**: exact keys `registration_sha256, roster_sha256, scorer_id, item_id, model_id, arm, level, block_id, attempt, retry_stage, parent_block_id, prompt_tokens, generated_tokens, outcome, stop_reason, truncated`. Digests are lowercase hex64 and equal `registration.digest` and the **final** `roster["sha256"]`; `scorer_id` equals `registration.scorer_id`. IDs, arm, stage, attempt, parent, model, and level must match the live placement and block. Token counts are exact nonnegative integers; `truncated` is bool; `stop_reason` is a nonempty string; `outcome` is one of `correct, incorrect, malformed, truncated`. Do **not** import the stopped draft’s `stop_reason ∈ {stop,length}` equivalence: the ruling requires a reason and agreement with cap flags but does not standardize the runner’s stop-reason vocabulary. A capped row cannot be `correct`; `outcome="truncated"` requires a cap hit. These are proposed schema choices that make the ruled scorer and digest binding executable. [Kernel acceptance](docs/process/state_kernel.json:3832); [scorer registration field](joulewise/scored_registration.py:28); [stopped draft’s unruled vocabulary](joulewise/scored_packer.py:16).

Each window has exact keys `registration_sha256, roster_sha256, block_id, attempt, gross_j`. Its digests have the same bindings, `(block_id, attempt)` must name one reported placement observed as `completed` or `cut_off`, and `gross_j` is a finite, nonnegative JSON number, excluding bool. Duplicate keys and unknown or `not_started` placements refuse. The packer’s placement and observation shapes support that match. [Roster contract §§2.6–2.7](docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:228); [window-key ruling Q11](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:37).

Return one exact object with `schema="joulewise.scored_reduce.v1"`, `registration_sha256`, `roster_sha256`, `counted_rows`, `counted_windows`, `excluded_windows`, `terminal_refusals`, `cells`, and `executed_status`. Preserve each accepted input row; append derived `cap_hit: bool` to its counted copy. A counted window copy adds `model`, `level`, `envelope_index`, and `items`; an excluded window copy adds `reason ∈ {voided, ceiling_violation, unattributed_overrun}`. Each terminal refusal copies the roster’s seven fields and adds `gross_j: number|null`. Emit exactly ten `cells`, keyed `"{model}:{level}"`, each with `model, level, arm, attempts, correct, prompt_tokens, generated_tokens, cap_hits, cap_hit_fraction, cap_bound, gross_j, counted_parent_blocks, counted_envelopes, spread_exceeded`. Sum each counted **block window once**, even when its block contains several scored items. `cap_hit_fraction` is null for zero counted rows; `cap_bound` is false then, otherwise true strictly above `CAP_BOUND_FRACTION`. `executed_status` has R4’s three exact maps. The ten-cell identity and terminal types follow the sealed roster; the output names and denominator here require magistrate adoption. [Roster terminal shape](docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:248); [CARRIED cap constant](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:17).

Use `ReductionRefusal(ValueError)` with `.code` and optional detail, matching `PackingRefusal`. Reserve packer `inv_*` codes for verifier failures. A292 codes: `row_shape`, `row_binding`, `row_roster_mismatch`, `row_tokens`, `row_cap_disagreement`, `item_partition`, `window_shape`, `window_binding`, `window_unmatched`, `window_duplicate`, `window_energy`, `missing_live_window`, `missing_ceiling_window`. `ceiling_violation` and `unattributed_overrun` remain terminal **types**, never exception codes. [Packer idiom](joulewise/scored_packer.py:16); [terminal/code distinction](docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:412).

**Executable text:**
```python
assert first_statement(reduce) == "verify_executed_roster(registration, roster, predicted_decode_s)"
assert set(row) == set("registration_sha256 roster_sha256 scorer_id item_id model_id arm level block_id attempt retry_stage parent_block_id prompt_tokens generated_tokens outcome stop_reason truncated".split())
assert set(window) == set("registration_sha256 roster_sha256 block_id attempt gross_j".split())
assert set(result) == set("schema registration_sha256 roster_sha256 counted_rows counted_windows excluded_windows terminal_refusals cells executed_status".split())
assert result["schema"] == "joulewise.scored_reduce.v1"
assert len(result["cells"]) == 10
```

### R2 — Window completeness — BLOCKER

Require a window for **every final live placement**. Without it an item cannot be counted, and a spread flag must not launder a missing energy numerator into a counted row. Require the terminal `ceiling_violation` attempt’s window: that attempt ran beyond its bound, and its gross J belongs on the refusal, outside cell sums. The cold ruling explicitly accepts that terminal window and requires its exclusion; the merged packer counts only live `(block_id, attempt)` keys. [Kernel acceptance](docs/process/state_kernel.json:3832); [terminal ruling](docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:79); [live-key addendum](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:78).

A voided historical attempt’s window is **optional**: when supplied it is bound, retained under `excluded_windows`, and never summed. The same applies to an `unattributed_overrun` terminal attempt that actually ran (`completed` or `cut_off`); attach its gross J if supplied, else null. A `not_started` terminal has no block window. This choice avoids turning a past retry’s missing *block-level attribution* into a refusal of an otherwise complete final result; the rulings specify live counting and terminal ceiling treatment, but do not impose a window for every voided or unattributed attempt. Do not silently omit any supplied window. [Count predicate](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:78); [observation vocabulary](docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:236); [stopped draft’s broad requirement, untrusted](docs/process/state_kernel.json:3861).

Missing final live key raises `missing_live_window`; missing terminal ceiling key raises `missing_ceiling_window`. Missing optional keys do not raise. A roster with an unreported loaded envelope raises the existing `unreported_envelope` **before** any A292 window check. [Reporting addendum](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:82); [merged verifier](joulewise/scored_packer.py:491).

**Executable text:**
```python
required = live_placement_keys | ceiling_terminal_keys
assert required <= supplied_window_keys
assert missing(live_placement_keys) raises_code("missing_live_window")
assert missing(ceiling_terminal_keys) raises_code("missing_ceiling_window")
assert every_supplied_voided_window_is_excluded_from_cell_sums()
assert every_supplied_terminal_window_is_excluded_from_cell_sums()
```

### R3 — Cap policy — BLOCKER

Implement **sealed v4 only** in A292. Derive `cap_hit = generated_tokens >= registration.cap_tokens[registration.arm]`; require `row["truncated"] == cap_hit`, a present nonempty `stop_reason`, and no `correct` outcome on a cap hit. A292 consumes `CAP_BOUND_FRACTION = 0.20` as its schema-pinned M3 label threshold, using `cap_hits / counted_rows` per cell and `>` for the label. The equality boundary needs an explicit test. [Cap ruling](docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md:15); [kernel](docs/process/state_kernel.json:3832); [constant ruling](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:17); [merged constant](joulewise/scored_registration.py:25).

The v5 document expressly calls itself a proposal, supersedes v4’s capped-is-incorrect scoring with separate thinking and answer caps, and leaves A291 v5’s `(model, level, budget)` cells and `night_exhausted` transitions open. Parameterizing those meanings into a v4 roster would create the silent hybrid the question warns against. A later adopted plan needs a new registration, roster, reducer schema, and RED gate. [v5 status](docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:3); [v5 cap semantics](docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:41); [v5 contract boundary](docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:53).

**Executable text:**
```python
assert cap_hit(cap - 1) is False
assert cap_hit(cap) is True
assert reduce_v4(row_at_cap_with_truncated_false) raises_code("row_cap_disagreement")
assert reduce_v4(row_at_cap_with_outcome_correct) raises_code("row_cap_disagreement")
assert cell_cap_bound(1, 5) is False
assert cell_cap_bound(2, 5) is True
assert reduce_v4(v5_budget_cell) raises_code("row_roster_mismatch")
```

### R4 — Executed spread and drift — MATERIAL

Affirm the merged `executed_status` shape for A292: `spread_exceeded` is a ten-cell bool map; `executed_drift_lever_slots` and `drift_exceeded` are five-level maps. Pass the set of **validated, final live window keys** to it; copy all three maps into the reducer output, and copy each cell’s spread flag and counted-parent/envelope counts into `cells`. A293 owns NE/NR disposition; the reducer supplies typed terminals and both flags, including when NE will take precedence. [Contract’s proposed shape and tension](docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:383); [merged return](joulewise/scored_packer.py:498); [status precedence](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:39); [unattributed precedence addendum](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:66).

The executed lever uses each parent’s item-weighted position from counted windows; a partly counted parent may contribute its available item positions to the lever **when both models have at least one fully counted parent**. With zero fully counted parents for either model, the level lever is null and drift false, while that cell is spread-exceeded. This is the behavior implemented and exercised by the named packer test; it merits a direct A292 witness because it is easy to misread as “only fully counted parents enter the mean.” [Ruling on zero parents](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:76); [merged calculation](joulewise/scored_packer.py:137); [partial-parent test](tests/test_scored_packer.py:318).

**Executable text:**
```python
assert set(result["executed_status"]) == {
    "spread_exceeded", "executed_drift_lever_slots", "drift_exceeded"
}
assert set(result["executed_status"]["spread_exceeded"]) == ten_cell_keys
assert set(result["executed_status"]["drift_exceeded"]) == {"1", "2", "3", "4", "5"}
assert zero_fully_counted_parent_cell["spread_exceeded"] is True
assert zero_fully_counted_parent_level["executed_drift_lever_slots"] is None
assert zero_fully_counted_parent_level["drift_exceeded"] is False
```

### R5 — INV-12 — MATERIAL

A292 does **not** need the INV-12 reconciliation to validate row/window reduction: its first-statement verifier remains authoritative for the currently sealed roster. The independent roster checker’s extra single `predicted_item_s` equality clause is explicitly identified as stricter than the contract and seal, and the ruling forbids a claim resting on checker-INV-12 agreement until reconciled. Keep that clause out of A292’s RED assertions and out of any “all checker rows agree” claim. Re-run every A291 provisional R-column witness at the real reducer entry; where an independent checker reports only this known INV-12 difference, record it separately rather than silently normalizing it away. [INV-12 discrepancy ruling](docs/process_traces/2026-09-24-activation-278ebc9e/82-coldgate-packet-a291-r3method/30-addendum/21-coldgate-fable-r4-addendum-ruling.md:63); [contract predicate](docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:485); [real-entry obligation](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:47).

**Executable text:**
```python
assert reduce_calls_verifier_first_ast()
assert every_a291_provisional_R_witness_reaches_real_reduce_entry()
assert "INV-12 prediction equality" not in a292_acceptance_predicates
assert checker_INV12_disagreement_is_reported_separately()
```

### R6 — Stopped draft — MATERIAL

Use `c0998fdb:joulewise/scored_reduce.py` only to generate adversarial cases, then derive every expected result afresh from the sealed rulings. Its `_verify_roster` import, `block["arm"]`, `origin_attempt`, `ceiling_violation`, and stored `roster["drift_exceeded"]` do not match the merged interface; its row/window keys omit the newly required digests and `scorer_id`, its refusal has no `.code`, and its “all active windows” requirement predates the present completeness decision. The kernel explicitly says the draft was not accepted. [Stopped draft lines 7–19 and 33–78](docs/process/state_kernel.json:3861); [merged roster shape](joulewise/scored_packer.py:176); [merged executed status](joulewise/scored_packer.py:498).

**Executable text:**
```python
assert implementation_starts_without_importing_stopped_reduce()
assert no_reference_to("_verify_roster", 'block["arm"]', 'roster["drift_exceeded"]')
assert stopped_draft_cases_are_rewritten_against_A292_R1_to_R5()
```

### R7 — Delegation — MATERIAL

The harness seat should receive `WRITE_SCOPE: ["tests/test_scored_reduce.py", "tests/scored_reduce_checker.py"]`; the latter is an independently written reducer oracle for row partition, window admission, one-time gross-J sums, cap counting, and executed status. It should use the ruled contract and roster data, without importing reducer internals. The implementation seat should receive `WRITE_SCOPE: ["joulewise/scored_reduce.py"]` at the committed RED head. This preserves the packer gate’s independent-checker method while ensuring neither seat can silently edit the other’s oracle or assertions. A292 must also re-run the A291 provisional reduce-column witnesses, including `cap_bound_fraction` consumption. [Independent-checker gate precedent](docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:56); [A292 real-entry and constant obligations](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:17); [A292 kernel gate](docs/process/state_kernel.json:3832).

Do not hand implementation a schema-dependent harness with placeholder “OPEN code” assertions: commit exact R1–R4 assertions after the magistrate rules them. The independent oracle is justified because the existing checker checks rosters and executed status, **not** score-row identity or gross-J accounting. [Checker interface](tests/scored_roster_checker.py:794); [executed-only interface](tests/scored_roster_checker.py:841).

**Executable text:**
```json
{
  "harness_WRITE_SCOPE": ["tests/test_scored_reduce.py", "tests/scored_reduce_checker.py"],
  "implementation_WRITE_SCOPE": ["joulewise/scored_reduce.py"],
  "handoff_gate": "commit exact RED tests and independent oracle before implementation",
  "final_gate": "GREEN focused tests plus every A291 provisional R-column witness at reduce"
}
```

## What would show this design wrong

A ruled v4 source requiring windows for **every** physically run voided attempt would falsify R2’s optional-history rule. A scorer contract permitting a correct result at `generated_tokens == cap_tokens[arm]` would falsify R3. A replay-valid roster for which the independent reducer oracle and merged `executed_status` disagree on counted parents, especially a partly counted parent, would falsify R4. A demonstrated claim that depends on checker INV-12 prediction equality would block R5’s neutrality. These are focused refuters; no live measurement was performed. [Current live-window rule](docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:78); [current INV-12 exception](docs/process_traces/2026-09-24-activation-278ebc9e/82-coldgate-packet-a291-r3method/30-addendum/21-coldgate-fable-r4-addendum-ruling.md:63).

## Expected disagreement

The likeliest dispute is whether a missing voided-attempt window should refuse. I recommend preserving and excluding every supplied one, while making only final live and terminal ceiling windows mandatory. The second is whether partial parents enter the executed drift mean; the merged helper and its test say yes when a fully counted parent exists for each model. [Merged calculation](joulewise/scored_packer.py:137); [test](tests/test_scored_packer.py:318).