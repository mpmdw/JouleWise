```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The named suite and all 236 independent operand-collapse mutants pass, but split-bootstrap bounds and five other contract edges remain defective.",
  "workspace": {
    "base_requested": "64d4c034a79693be005e812eeaff2ed52a385527",
    "base_mode": "descendant",
    "head_start": "d2f9a273d5be0bad155c1e8cbfd4ff4197d28159",
    "head_end": "d2f9a273d5be0bad155c1e8cbfd4ff4197d28159",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 1, "should_fix": 5, "nit": 0},
    "findings": [
      {"id": "B1", "severity": "blocker", "title": "Split-parent bootstrap draws reuse a fixed, too-small floor bound"},
      {"id": "S1", "severity": "should_fix", "title": "A pooled group can produce a false merged-boundary reason without any 8B-cheaper decision"},
      {"id": "S2", "severity": "should_fix", "title": "The packer can admit a block longer than the available capture window"},
      {"id": "S3", "severity": "should_fix", "title": "Missing retry provenance silently becomes initial"},
      {"id": "S4", "severity": "should_fix", "title": "Sparse decisions bypass floor and anchor input validation"},
      {"id": "S5", "severity": "should_fix", "title": "The balance search accepts rosters with large measured-cell drift"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_packer tests.test_scored_reduce tests.test_energy_per_correct",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 30 tests in 1.124s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 30 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a281_delta_replay.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["TERMINAL active 10 terminal 1 missing_items [] over_capacity []"]},
      "expected": {"exit_code": 0, "tail_regex": "TERMINAL active 10 terminal 1 missing_items \\[\\] over_capacity \\[\\]"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /tmp/a281_delta_mutants.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["RESULT energy_per_correct.py generated 115 killed 115 survived 0 seconds 170.8"]},
      "expected": {"exit_code": 0, "tail_regex": "RESULT energy_per_correct.py generated 115 killed 115 survived 0 seconds .*"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a281_delta_stress.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["RESULT: 220 accepted; 307 refused; worst drift 2.2 slots; zero capacity/cell-rule violations; zero nondeterministic hashes; maximum pack time 1.613 s"]},
      "expected": {"exit_code": 0, "tail_regex": "RESULT .*\"accepted\": 220.*\"violation_count\": 0.*\"nondeterministic_count\": 0.*"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a281_delta_bounds.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["CORRECTED_DRAW_INTERVAL (1.6363636363636365, 2.4444444444444446) CURRENT_INTERVAL (1.7090909090909092, 2.3555555555555556)"]},
      "expected": {"exit_code": 0, "tail_regex": "CORRECTED_DRAW_INTERVAL .* CURRENT_INTERVAL .*"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No live scored-night caller exists here; capture, retry sensitivity, and the eventual registered drift tolerance remain outside this pure-module audit.",
      "needs": ""
    }
  ]
}
```

## Findings

### (a) Round 1 counterexamples

Executed with `PYTHONPATH=. python3 -B /tmp/a281_delta_replay.py`, plus a scratch-copy Holm mutant run.

| Counterexample | Candidate outcome |
|---|---|
| `88111` crossover directions | `crossover=None`, reason `None` |
| `1n888` directions | `crossover=3` |
| Sol merged 4–5 probe | `crossover=None`, reason `boundary_in_merged_group`; one pooled 4–5 decision |
| Requeue twice → reduce → `ratio_interval` | Pairing succeeds; point ratio `2.0` before and after split; split interval widens from `(1.5, 2.75)` to `(1.4667, 2.8)` |
| Capped-correct row | `ValueError: capped attempt cannot be correct` |
| Pack only level `{3}` against registered `{1}` | `ValueError: items do not match registered levels` |
| Mixed arms in `decide` | `ValueError: cell role, arm, or level mismatch` |
| Below-floor block | `BelowFloorError` |
| Holm stop | All five rows stay `not resolved`; removing `still_rejecting and` in a scratch copy fails `test_x12_holm_stop_and_exact_cutoff` |
| Former `len(odd) == 2` parity cut, 12 items of size 2 | 12 envelopes, zero idle slots, zero recorded drift |

Required widening inputs are now keyword-only; invalid family and unchecked ready ratios refuse.

### (b) Independent file-level operand-collapse sweep

`python3 -B /tmp/a281_delta_mutants.py` used a `git archive HEAD` scratch copy and replaced each comparison or `min`/`max` call with each operand, one file-level mutant at a time. The unmodified archive and an AST-unparsed archive both passed the named suite.

| Module | Generated | Killed | Survived |
|---|---:|---:|---:|
| `scored_packer.py` | 87 | 87 | 0 |
| `scored_reduce.py` | 34 | 34 | 0 |
| `energy_per_correct.py` | 115 | 115 | 0 |

### (c) Balance search

`PYTHONPATH=. python3 -B /tmp/a281_delta_stress.py` used seed `281091`, 2–5 levels, 5–40 items per level, block sizes 1–6, and speed ratios 1:1 through 1:8.

| Accepted / refused | Worst per-level `drift_lever_slots` | Levels above 0.5 slots | Capacity or one-block-per-cell violations | Repeated-input SHA mismatch | Max wall time per pack |
|---:|---:|---:|---:|---:|---:|
| 220 / 307 | 2.2 | 41 / 739 | 0 | 0 | 1.613 s |

The worst accepted roster had level sizes `[25, 27, 35, 31]`, block size 6, speed ratio 1:7, and Level 1 measured means 9.8 versus 7.6. The recorded gap matches those measured cells.

### (d) Single packing and terminal accounting

| Probe | Observed |
|---|---|
| Second overrun, two 40 s singles | Both retained in appended envelopes; no declared-capacity overrun |
| One single retry, then another overrun | One `ceiling_violation` terminal record; no original item missing from active blocks plus terminal records |
| Incoherent capture inputs | Declared capacity 601 s, actual available capture 540 s; a 550 s block was accepted |

### Same-signature statement

| Round 1 defect class | New finding in the same class? |
|---|---|
| Crossover direction or merged-level crossover | **Yes — S1:** false merged-boundary metadata. The original direction examples are fixed. |
| Pairing broken by retries or splits | **No:** the split pairing replay succeeds. **B1** is a distinct split-bootstrap bound error. |
| Balance claimed on labels rather than measured cells | **Yes — S5:** accepted measured-cell gaps reach 2.2 slots. The gap is now measured and recorded. |
| Silent defaults that skip a registered guard | **Yes — S3, S4:** retry provenance defaults to `initial`; sparse results bypass bound validation. |
| Surviving operand-collapse mutants | **No:** 236 generated, 236 killed. |

### B1 — Blocker: split-bootstrap bounds are too narrow

In [energy_per_correct.py](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/energy_per_correct.py:99), error allowances are counted once from the original blocks, then reused for every bootstrap draw at line 123. Under binding X2, a drawn split parent contributes one floor-plus-anchor allowance **per single window**.

`PYTHONPATH=. python3 -B /tmp/a281_delta_bounds.py` forced five draws of a parent with two measured windows. The draw requires 10 bounds for 8B; the code used 6. Its interval was `(1.7091, 2.3556)` versus `(1.6364, 2.4444)` when the drawn-window count was applied. This can make a claim interval too narrow.

### S1 — Should fix: false merged-boundary reason

[energy_per_correct.py](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/energy_per_correct.py:241) sets `boundary_in_merged_group` even without a Holm-significant `8B cheaper` group. `PYTHONPATH=. python3 -B /tmp/a281_delta_extra.py` produced four `1.7B cheaper` groups, including pooled 4–5, yet returned `crossover=None, reason=boundary_in_merged_group`. The binding crossover rule has no candidate boundary in that case.

### S2 — Should fix: capture timing is not coherent with packing capacity

[scored_packer.py](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_packer.py:156) checks `interior_s - guard_s` but does not ensure that interior fits after `offset_s` inside `envelope_s`. The extra probe accepted a 550 s block with a 601 s declared capacity inside a 600 s capture starting at 60 s, leaving only 540 s available. It stayed under the *declared* capacity while extending beyond the capture.

### S3 — Should fix: retry stage can be invented

[scored_reduce.py](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_reduce.py:72) defaults a missing `retry_stage` to `initial`. The extra probe omitted the field and returned `{'initial': 1}`. Binding F2 requires retry stage on every item row so the paired retry sensitivity retains its provenance.

### S4 — Should fix: sparse decisions skip bound validation

[decide](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/energy_per_correct.py:146) delegates floor and anchor validation to `ratio_interval`, which is skipped when all groups remain sparse. The extra probe accepted `(floor_j, anchor_j)` values `(None, None)`, `(-1, -1)`, and `(nan, 0)`, each returning `not estimable`. Required registered bounds should be validated regardless of estimability.

### S5 — Should fix: large cell drift remains an accepted roster

The search in [scored_packer.py](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_packer.py:59) minimizes measured-cell gaps but has no acceptance bound. The seeded sweep accepted 41 level results above 0.5 slots, reaching 2.2. Binding F1 calls equal measured-cell means the ordering invariant; the code exposes the residual but does not refuse or mark a roster that misses it. The eventual AP-5M tolerance can supply the threshold.

## Residual risk

This audit exercised pure modules only. It did not validate actual capture timing, the runner’s use of `idle_slot` and terminal records, or the claim decision once a drift tolerance is registered. The detached worktree remained clean at `d2f9a273`.