```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two MATERIAL findings: empty parents defeat the population-safety implication, and formatting alone defeats the similarity threshold. Named regressions are reachable; P/K scopes are disjoint.",
  "workspace": {
    "base_requested": "20cd29de",
    "base_mode": "exact",
    "head_start": "20cd29de4cd8c177ab4f9c12c998cbbb32babac2",
    "head_end": "20cd29de4cd8c177ab4f9c12c998cbbb32babac2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "classification": "MATERIAL",
        "final_texts": ["1", "2a", "3", "6", "7"],
        "claim": "The specified preconditions admit a zero-item parent. Its gate membership is positive and its full-indices relation holds, while the position population is empty; the specified lever still divides by zero."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "classification": "MATERIAL",
        "final_texts": ["8"],
        "claim": "The physical-line similarity metric accepts an AST-identical formatting-only version of the existing transcription: copy ratio 0.050847, control 0.033898."
      }
    ],
    "Q1": "All named regression expectations are reachable; ten concrete operator witnesses were exercised.",
    "Q2": "Final text 3 operationally selects one INV-11 reading. INV-10 is explicitly narrowed, but its delayed formation check leaves F1.",
    "Q3": "No write-scope collision or sequencing deadlock found.",
    "Q4": "Existing transcription detected in original formatting; formatting-only false negative demonstrated.",
    "Q5": "Different gate and position populations are contract-required. Their safety implication is incomplete without positive parent cardinality.",
    "Q6": "R5a reproduces cache bypass and uncached refusal. No additional trusted-cache route was identified in the prescribed replacement."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/278ebc9e/astra-ref/probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "EMPTY_PARENT legal_base_checker [] base_lever None",
          "EMPTY_PARENT structure RETURN INV11_12 RETURN fact {'parent_id': 'large:decode:1:999', 'model': 'large', 'level': 1, 'n_items': 0, 'n_terminal': 0, 'indices': []}",
          "EMPTY_PARENT baseline ZeroDivisionError::division by zero TEXT_MODEL PackingRefusal:inv_52:inv_52: internal:ZeroDivisionError checker ['INV-10', 'INV-36', 'INV-50', 'INV-52']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "EMPTY_PARENT baseline ZeroDivisionError.*internal:ZeroDivisionError"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/278ebc9e/astra-ref/similarity.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SIM canonical=True checker=refresh_derived packer=_derived 18/37=0.486486",
          "SIM canonical=True checker=refresh_derived packer=_structure 8/37=0.216216"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "8/37=0.216216"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/278ebc9e/astra-ref/similarity_evasion.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FORMAT AST_IDENTICAL True",
          "FORMAT checker=_derived packer=_derived 12/236=0.050847",
          "FORMAT checker=_derived packer=executed_status 9/236=0.038136",
          "FORMAT checker=_derived packer=_structure 8/236=0.033898",
          "BASE control 7/33=0.212121"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "BASE control 7/33=0.212121"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_scored_registration tests.test_scored_roster_checker tests.test_scored_packer",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 51 tests in 6.621s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/278ebc9e/astra-ref/targeted.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R4a_SECONDARY 6.199999999999999 checker []",
          "TEXT_MODEL_CENSUS inv_02 inv_03 inv_11 inv_12 inv_38 inv_39 inv_52 stale_derived",
          "BASELINE_FUZZ_RED census lacks inv_11 and inv_12 on these witnesses; R2 raw ZeroDivisionError",
          "EMPTY_PARENT_POPULATIONS gate 1 position 0 full_relation True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "EMPTY_PARENT_POPULATIONS gate 1 position 0 full_relation True"
      }
    }
  ],
  "flags": [
    {
      "id": "L1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "F1 and F2 require amendments to the ruled texts before they are pasted verbatim into implementation briefs.",
      "needs": "Adjudicate the proposed replacement texts."
    },
    {
      "id": "L2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Post-fix outcomes are demonstrated with a scratch model of the specified preconditions, facts, lever, and seal ordering; no future integrated implementation exists yet.",
      "needs": "Repeat the witnesses against the integrated P/K head."
    }
  ]
}
```

## Findings

References: **A** = [Final texts v2](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/07-coldgate-packet-a291-fix2/20-addendum/21-coldgate-fable-addendum-ruling.md:43); **C** = [contract v4](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:351).

| ID | Severity | Final text | Claim | Evidence | Proposed replacement text |
|---|---|---|---|---|---|
| F1 | **MATERIAL** | 1, 2a, 3; witnesses in 6–7 | **“Gate ⇒ full indices” does not imply a nonempty position population.** Zero-item parents pass the prescribed structural subset. Deferring full INV-10 until replay allows arithmetic to encounter them first. | A:45–46; [packer:135–142](/Users/edr/code/wt-278ebc9e-astra-ref/joulewise/scored_packer.py:135); C:463. Executed witness: start with a legal finished roster whose large-model parents are terminal; append an unscheduled parent with a unique id, `items=[]`, `predicted_item_s=[]`, `predicted_s=0`. Reseal. Existing `_structure` and the specified INV-11/12 predicates pass. Facts give **gate count 1, position count 0, full relation True**. Baseline raises `ZeroDivisionError`; the text model raises `inv_52: internal:ZeroDivisionError`. | “The pre-arithmetic INV-10 subset also requires every parent’s `items` to be nonempty; otherwise refuse `inv_10`. Full formation otherwise remains with replay and the checker. For every gate parent, `_lever` checks **`0 < n_items == len(indices)`** before arithmetic, regardless of nullness, using the specified `inv_11` refusal. Add R4d: the zero-item-parent forgery described above must refuse `inv_10`, never `internal:*`; include it as an additional mandatory targeted mutation alongside the ten seeded operators.” |
| F2 | **MATERIAL** | 8 | **The similarity gate is sensitive to formatting rather than just implementation.** A transcription can pass merely by wrapping expressions. | A:51. Original checker `_derived` versus packer `_derived`: **22/33 = 0.666667**; control: **7/33 = 0.212121**. Parenthesizing assignment RHS expressions and splitting their tokens across physical lines preserves the entire AST but changes the scores to **12/236 = 0.050847** and **8/236 = 0.033898**. Both pass. R4c examines the packer, so it cannot detect this checker-side transformation. | “Before line comparison, canonicalize each function with `ast.parse` followed by `ast.unparse`; then apply the specified identifier/number normalization, preserving keywords and canonicalized strings. Count occurrences of canonical lines. The pasted script must include positive controls comprising the known transcription and AST-identical formatting variants; each must fail the copy threshold. Report recalibrated controls and pairwise scores. This remains a similarity screen, not proof of independent derivation.” |

F1 is MATERIAL rather than BLOCKER because the prescribed backstop still refuses the forged input; the defect is the claimed pre-arithmetic safety guarantee. F2 defeats the numerical screen, but an unchanged parent-centric transcription would still violate the separate item-centric requirement.

**Accepted texts and portions**

- **Text 1:** Contract-required gate/position distinctions and the executed five-envelope clause are correct, subject to F1’s missing domain prerequisite.
- **Text 2:** Accept the three ordered handlers, sole derivation boundary, executed call site, and digest-before-arithmetic ordering.
- **Text 2a:** Accept the fact carrier, wrapper signature, and check-before-nullness requirement; strengthen the relation per F1.
- **Text 3:** Accept the explicitly selected INV-11 predicate and INV-12 ordering; add F1’s nonempty-parent prerequisite.
- **Text 4:** Accept the rename and duplicate-live-placement refusal.
- **Text 5:** Accept cache deletion and unconditional external-entry replay.
- **Text 6:** Accept the named regression expectations; none is unreachable under the specified order.
- **Text 7:** Accept the ten operators, resealed coverage requirement, census, and hard differential failures; add the F1 targeted witness.
- **Text 8:** Accept scopes, compatibility constraints, and integration order; amend the similarity screen per F2.

**Q1 — Regression reachability**

“Text model” below means the scratch execution of the prescribed checks, not completed implementation validation.

| Regression | Executed at `20cd29de` | Specified post-fix result / discrimination |
|---|---|---|
| R1, resealed duplicate placement | `stale_derived` at both requeue and verify entry | Text model reaches `inv_11` before derived-field comparison. |
| R2, all large level-1 placements voided | Raw `ZeroDivisionError` | Text model reaches `inv_11`. |
| R2b, post-split `superseded=false` | Exact route: 11 events, pending 12; `requeue_overrun(...,12,[])` gives `stale_derived`. Checker includes INV-12 and excludes INV-11. | Text model reaches `inv_12`. The replacement witness is feasible. |
| R3, unresealed R2 | Raw `ZeroDivisionError` | Text model reaches `inv_02`. |
| R4a, terminal single/live sibling | Production route gives **1.5999999999999996**, shortfall `True`, checker `[]`. Secondary fixture gives **6.199999999999999**. | Text model preserves the production literal. Dropping the partly-terminal parent yields **0.0**, so the witness discriminates. Already GREEN at baseline, as expected. |
| R4b, injected `(2,0,[])` fact | Patch fails with `AttributeError`: `_parent_facts` does not exist. | Text-model lever raises `inv_11: gate parent without full live positions p`, despite the other model’s empty gate. |
| R4c | `_derived` has nine body statements; `_live` exists; divisions remain outside `_lever`. | Structural requirements are implementable and RED at baseline. |
| R5a | Production finalize **returns**, then cached requeue **returns**. Clearing the cache makes the same input refuse `inv_39`. | Directly demonstrates the replay deletion’s discrimination. |
| R5b | `_TRUSTED_OUTPUTS` mutable container exists. | Deletion/AST requirement is reachable and RED at baseline. |

**Q1 — Ten concrete mutation operators**

| Operator | Resealed baseline outcome | Resealed text-model outcome |
|---|---|---|
| 1. One live placement → voided | `stale_derived` | `inv_11` |
| 2. Duplicate live placement/new envelope | `stale_derived` | `inv_11` |
| 3. Drop terminal refusal | `inv_38` | `inv_11` |
| 4. Add terminal refusal | `stale_derived` | `stale_derived` |
| 5. Remove single from `blocks` only | `inv_52` | `inv_52` |
| 6. Flip split parent’s `superseded` | `stale_derived` | `inv_12` |
| 7. Move placement’s envelope index | `inv_03` | `inv_03` |
| 8. Flip `late` | `inv_39` | `inv_39` |
| 9. Alter earlier event digest | `inv_38` | `inv_38` |
| 10. Increment placement attempt | `inv_39` | `inv_39` |

Unresealed text-model submissions reach `inv_02`, except operator 9: event digests are excluded from the outer digest, so replay reaches `inv_38`. That exception is correct.

The constructed ten-operator sample is RED at baseline for census property **(d)**: no `inv_11` or `inv_12`. The separately specified R2 mutation also demonstrates a totality failure. Operators need not all become newly refused: several already receive valid refusals.

**Q2–Q6**

- **Invariant readings:** Final text 3 expressly chooses C:468’s predicate, so P and K have one operational INV-11 reading. Its alternative remains an acknowledged authority residual. INV-12, INV-02/03/17/38/39/52, root `spread_minima`/`inv_28`, and `stale_derived` have identifiable meanings. The actionable prerequisite gap is F1.
- **Sequencing:** P and K have disjoint file allowlists. P’s imported helpers already exist; text 8 preserves their interfaces and fixed-mode witnesses. P need not wait for `generate_case`.
- **Population semantics:** Different gate and position populations are **required** by RD-4/RD-5/FT-10. Replacing them with one population would repeat the partly-terminal/partly-counted defect. For positive-sized parents, the strengthened relation establishes the needed inclusion without changing those populations.
- **Cache and duplicate placement:** R1’s specified seal refusal is reachable; R5a reproduces the cache bypass and demonstrates refusal when replay runs. No further bypass was identified in the prescribed replacement.

**Q4 — Similarity measurements**

| Checker function | Packer function | Stated normalization | With `ast.unparse` first |
|---|---|---:|---:|
| `_derived` | `_derived` | 22/33 = **0.666667** | 29/33 = **0.878788** |
| `_derived` | `executed_status` | 18/33 = **0.545455** | 23/33 = **0.696970** |
| `_derived` | `_structure` — unrelated control | 7/33 = **0.212121** | 8/33 = **0.242424** |
| `check_executed` | `executed_status` | 20/45 = **0.444444** | 27/45 = **0.600000** |
| `check_executed` | `_structure` — control | 3/45 = **0.066667** | 4/45 = **0.088889** |
| `refresh_derived` | `_derived` | 14/37 = **0.378378** | 18/37 = **0.486486** |
| `refresh_derived` | `_structure` — control | 5/37 = **0.135135** | 8/37 = **0.216216** |

`_parent_facts` and `_lever` do not exist at baseline; their future pairwise scores cannot yet be measured.

**Executed probe commands and tails**

All ran from `/Users/edr/code/wt-278ebc9e-astra-ref`.

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/278ebc9e/astra-ref/probe.py
EMPTY_PARENT baseline ZeroDivisionError::division by zero TEXT_MODEL PackingRefusal:inv_52:inv_52: internal:ZeroDivisionError checker ['INV-10', 'INV-36', 'INV-50', 'INV-52']

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/278ebc9e/astra-ref/similarity.py
SIM canonical=True checker=refresh_derived packer=_derived 18/37=0.486486
SIM canonical=True checker=refresh_derived packer=_structure 8/37=0.216216

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/278ebc9e/astra-ref/similarity_evasion.py
FORMAT AST_IDENTICAL True
FORMAT checker=_derived packer=_derived 12/236=0.050847
FORMAT checker=_derived packer=executed_status 9/236=0.038136
FORMAT checker=_derived packer=_structure 8/236=0.033898
BASE control 7/33=0.212121

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/278ebc9e/astra-ref/targeted.py
EMPTY_PARENT_POPULATIONS gate 1 position 0 full_relation True

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_scored_registration tests.test_scored_roster_checker tests.test_scored_packer
Ran 51 tests in 6.621s
OK

git status --short --branch
## HEAD (no branch)

git rev-parse HEAD
20cd29de4cd8c177ab4f9c12c998cbbb32babac2
```

The first formatting-probe attempt failed because this Python lacks private `ast._Unparser`; the scratch script was corrected to use source-span replacements, then passed as shown.

## Residual risk

No repository files changed; no agents or Claude were called. Full-suite and future integrated P/K verification were not performed. The next exact step is lead adjudication of F1/F2 before issuing the verbatim briefs.