```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The claim-bearing gate fails: a sparse merge can produce a false per-level crossover, and required packer mutants survive the named suite.",
  "workspace": {
    "base_requested": "64d4c034a79693be005e812eeaff2ed52a385527",
    "base_mode": "descendant",
    "head_start": "e63fb5418b8c8b28469478a101261019521dec94",
    "head_end": "e63fb5418b8c8b28469478a101261019521dec94",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 2, "should_fix": 3, "nit": 0},
    "findings": [
      {"id": "B1", "severity": "blocker", "title": "A merged 4–5 result can be reported as a Level-4 crossover"},
      {"id": "B2", "severity": "blocker", "title": "Fifteen packer operand-collapse mutants survive the required suite"},
      {"id": "S1", "severity": "should_fix", "title": "The Holm step-down-stop mutant survives the suite"},
      {"id": "S2", "severity": "should_fix", "title": "Failed sparse merges are labelled not resolved rather than not estimable"},
      {"id": "S3", "severity": "should_fix", "title": "Below-floor blocks are accepted by the estimator"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_packer tests.test_scored_reduce tests.test_energy_per_correct",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 15 tests in 0.335s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 15 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a281_mutate.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["EXTRA holm_no_stop SURVIVED", "EXTRA one_sided_flip KILLED FAIL: test_worked_constant_ratio_and_exact_widening (tests.test_energy_per_correct.EnergyPerCorrectTests.test_worked_constant_ratio_and_exact_widening)"]},
      "expected": {"exit_code": 0, "tail_regex": "EXTRA holm_no_stop SURVIVED"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a281_findings.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["HOLM_BASE ['not resolved', 'not resolved', 'not resolved', 'not resolved', 'not resolved']", "HOLM_NO_STOP ['not resolved', '8B cheaper', '8B cheaper', '8B cheaper', '8B cheaper']"]},
      "expected": {"exit_code": 0, "tail_regex": "HOLM_NO_STOP .*8B cheaper"}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "lead_ruling", "level": "nonblocking", "text": "Capture the empty model slot for a full 600 seconds and label it idle_slot.", "needs": "Install the runner rule."},
    {"id": "F2", "kind": "lead_ruling", "level": "nonblocking", "text": "Append-only retries break the palindrome; a tail-dependent headline needs a balanced recapture or an unresolved label.", "needs": "Pre-register the tail sensitivity and claim rule."}
  ]
}
```

## Findings

**B1 — Blocker: a pooled result becomes a false Level-4 crossover.** The sparse merge in [energy_per_correct.py](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/energy_per_correct.py:173) copies one pooled decision onto both constituent levels; the crossover scan at line 193 then treats those copies as separate level decisions. The binding synthesis M9 defines \(L^*\) only on Holm-significant directions. `PYTHONPATH=. python3 -B /tmp/a281_findings.py` produced:

```text
MERGE level4_observed_R=0.5 pooled_4_5_R=5.25 level4_decision=1.7B cheaper crossover=4
```

Level 4’s observed direction is **8B cheaper**. The significant hypothesis is for pooled levels 4–5, so it cannot locate a crossover *at Level 4*. Keep the pooled result labelled as pooled and leave \(L^*\) undefined when a boundary depends on a merge.

**B2 — Blocker: P6’s required mutation gate fails.** The test in [test_scored_packer.py](/Users/edr/code/wt-d8cc9c0a-pure-review/tests/test_scored_packer.py:82) mutates an in-memory copy of whichever packer it imports. When the file itself is mutated, its reference behavior also changes. `python3 -B /tmp/a281_mutate.py` used one `git archive` scratch copy and one mutant at a time:

| Module; comparison and `min`/`max` cuts | Killed | Survived | Representative killing test or survivor |
|---|---:|---:|---|
| Packer, 50 | 35 | **15** | Capacity cuts: `test_capacity_uses_guard_and_sum_not_each_operand`; `len(odd) == 2` survived on both operand cuts |
| Reducer, 30 | 25 | 5 | 20% boundary: `test_cap_bound_strictly_above_twenty_percent` |
| Estimator, 94 | 50 | 44 | Widening cuts: `test_worked_constant_ratio_and_exact_widening`; several zero-correct and direction cuts survived |
| Targeted boundary and policy cuts, 19 | 17 | 2 | Idle inclusion, ratio swap, unseeded RNG, floor/anchor removal, zero-correct guard and 20% boundary were killed; Holm stop and strict-cutoff changes survived |

The parity survivor is behavioral: replacing `if len(odd) == 2` at [scored_packer.py:62](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/scored_packer.py:62) with `if 2` changes a 12-problem, size-2 roster from **12 slots** to **13**, adding an unnecessary empty B slot at index 11, while the named suite passes. The packer acceptance clause requires every operand-collapse cut to die.

**S1 — Should fix: the Holm stop is untested.** Removing `still_rejecting and` at [energy_per_correct.py:184](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/energy_per_correct.py:184) survived the named suite. `PYTHONPATH=. python3 -B /tmp/a281_findings.py` gave:

```text
HOLM_BASE    ['not resolved', 'not resolved', 'not resolved', 'not resolved', 'not resolved']
HOLM_NO_STOP ['not resolved', '8B cheaper', '8B cheaper', '8B cheaper', '8B cheaper']
```

The hand-computed test checks an all-pass table and one failed row, but does not assert that **later** rows remain unrejected after the first failure. Add that assertion and an exact-cutoff case.

**S2 — Should fix: failed estimation is reported as uncertainty.** Packet C §3 says a cell still below three correct after all valid merges is `not estimable`. At [energy_per_correct.py:161–175](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/energy_per_correct.py:161), `ratio=None` leaves the decision as `not resolved`. The same probe produced:

```text
ZERO_CORRECT decision=not resolved merged=1–2–3–4–5 ratio=None
```

Preserve the brief’s three decision labels if needed, but add an explicit estimability status so an undefined estimate is distinguishable from an interval spanning one.

**S3 — Should fix: the estimator accepts below-floor blocks.** Packet C §3’s floor gate and disqualifiers require every block window to exceed its operative floor. [ratio_interval](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/energy_per_correct.py:48) widens by `floor_j` but does not check block energy against it. A probe with five **1 J** blocks per model and `floor_j=2` returned `estimate=1.0`, interval `(0.0, inf)`, rather than a refusal. The future runner could own this gate, but no caller exists yet; pin its owner before claim use.

### Execution checks

With capacity **60 s**, two levels, and predictions **2 s/item for A** versus **10 s/item for B**, hand-built sizes 10, 11, 13 and 17 at block sizes 1–4 gave:

| Level size | Size 1 | Size 2 | Size 3 | Size 4 |
|---:|---:|---:|---:|---:|
| 10 | 10 envelopes/cell | 5 | refused: fewer than 5 blocks | refused |
| 11 | 11 | 6 | refused | refused |
| 13 | 13 | 7 | 5 | refused |
| 17 | 17 | 9 | 6 | 5 |

Every accepted roster had identical block membership across models, at most one block per cell per envelope, no envelope above capacity, and a palindromic model order. A second probe at **31 s/item for B** refused oversized blocks instead of scheduling them.

The worked numbers check: \(120+80=200\) gross J with one correct gives **200 J/correct**. For five paired correct blocks, \(R=(100/5)/(50/5)=2\). Five blocks × \((1+1)\) J floor and anchor bounds give 10 J per model, hence low \((90/5)/(60/5)=1.5\) and high \((110/5)/(40/5)=2.75\). The reported p-values were `p_above=.01`, `p_below=1`, two-sided `.02`. The Holm example’s sorted p-values `.001, .006, .011, .020, .040` all pass cutoffs `.010, .0125, .0167, .025, .050`; its Level-3 crossover arithmetic matches.

M9’s two-stage resampling is present: [energy_per_correct.py:84–97](/Users/edr/code/wt-d8cc9c0a-pure-review/joulewise/energy_per_correct.py:84) draws blocks within each level, then paired problem IDs within each drawn block, applying the same draws to both models. Lines 71 and 98–104 add floor plus anchor **per drawn block**; the low bound subtracts 8B energy and adds 1.7B energy, while the high bound does the reverse. Both directions widen as required.

## F1 recommendation

**Capture the empty slot for the full 600 s**, with the designated model worker loaded and idle; label it `idle_slot` in the eventual runner record and exclude it from every gross block numerator. The roster’s sequence is `A B A B B A B B A B A`, with empty B at index 9. Counting it gives both models mean index **5.0**. Skipping it gives A **4.8** and B **4.2** on the executed timeline.

There is no symmetry-safe position to omit a single slot in this 5/5 case: an even-length palindrome needs an even count of each model, while both executed counts would be odd. Moving the empty slot cannot fix that parity.

## F2 recommendation

Accept append-only tails as a **recovery schedule**, with `retry_stage` and the paired exclusion sensitivity pre-registered. Do not describe the tail-inclusive estimate as drift-cancelled by the original palindrome. If including versus pairwise excluding retried blocks changes a Holm direction or \(L^*\), report that claim as unresolved until balanced recapture. One adjacent retry of the other model improves local matching but does not by itself restore an exact global palindrome.

Keep **one problem per envelope** after a second overrun. Synthesis M12 explicitly says “single-problem envelopes”; packing several separately edged problems into one capture would change that rule. An eight-problem split therefore costs eight 600 s captures, or **80 minutes**, unless the magistrate formally amends M12 before registration.

## Residual risk

These are pure modules with no scored-night caller. The review cannot verify actual 600 s idle-slot capture, item-edge energy windows, or the runner’s overrun and floor-gate enforcement. The checkout remained clean at `e63fb541`; all scratch mutations were under `/tmp`.