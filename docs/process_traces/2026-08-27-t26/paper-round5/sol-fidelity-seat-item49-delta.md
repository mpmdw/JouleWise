```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Delta audit found three blockers: one newly incorrect record-0 product, one newly inaccurate endpoint-rounding gloss, and the unresolved worst-edge/value conflation.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise-wt-r4",
    "base_mode": "exact",
    "head_start": "6bb9e5747d725c07857638e371e84611b1df9c59",
    "head_end": "6bb9e5747d725c07857638e371e84611b1df9c59",
    "upstream_end": "6bb9e5747d725c07857638e371e84611b1df9c59",
    "branch": "paper/t26-round4"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "every_equation_and_number_correct": false,
    "fence": {
      "compared": 43,
      "mismatches": 0
    },
    "b7_adjudication": "writer_correct_ten_fields",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The new record-0 product is one binary64 value too high",
        "location": "A3-fable-draft.md:22",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The exact subtraction of printed bounds is still mislabeled as the retained worst-edge value",
        "location": "A3-fable-draft.md:234",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "The new printed-endpoint rounding gloss gives the wrong excess",
        "location": "A3-fable-draft.md:133",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The work-budget paragraph still says at most 120 seconds while explaining that execution may exceed it",
        "location": "A3-fable-draft.md:240",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "The binding hash does not identify one unique physical machine",
        "location": "A3-fable-draft.md:236",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F6",
        "severity": "should_fix",
        "title": "The new math.fsum gloss promises stronger rounding semantics than the implementation records",
        "location": "A3-fable-draft.md:5",
        "defect_class": "UNTRACEABLE"
      },
      {
        "id": "F7",
        "severity": "nit",
        "title": "The Gaps section says two caveats but now contains three in 1,3,2 order",
        "location": "A3-fable-draft.md:333-337",
        "defect_class": "CONTRADICTED"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /Users/edr/code/JouleWise/scripts/check_paper_replay_fence.py --draft docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MEMBER 20260722T145535-e941c821",
          "COMPARED 43",
          "MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MISMATCHES 0$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c \"import plistlib; from decimal import Decimal as D; from pathlib import Path; p=plistlib.loads(Path('/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/raw/powermetrics.plist').read_bytes().split(b'\\\\0',1)[0]); q=p['processor']; pw=sum(float(q[n])/1000 for n in ('cpu_power','gpu_power','ane_power')); prod=pw*(int(p['elapsed_ns'])/1e9); print('COMBINED',repr(pw)); print('PRODUCT',repr(prod)); print('PRINTED_PRODUCT_SAME_DOUBLE',prod==float('0.10299995484180417')); print('BOUND_DIFFERENCE',D('0.030067931757111657')-D('0.0011349971959968978')); print('RETAINED_EDGE','0.02893293456111476')\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "COMBINED 0.9259043699999999",
          "PRODUCT 0.10299995484180416",
          "PRINTED_PRODUCT_SAME_DOUBLE False",
          "BOUND_DIFFERENCE 0.0289329345611147592",
          "RETAINED_EDGE 0.02893293456111476"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PRINTED_PRODUCT_SAME_DOUBLE True"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## paper/t26-round4...origin/paper/t26-round4"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## paper/t26-round4\\.\\.\\.origin/paper/t26-round4$"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The general unit suite was not run because this was a read-only prose audit; the mandated 43-value primary-artifact replay and independent arithmetic checks were run.",
      "needs": ""
    }
  ]
}
```

## Findings

| ID | Location | Verbatim quote | Defect class | Severity | Governing file:line | Proposed correction |
|---|---:|---|---|---|---|---|
| F1 | 22 | “*p_0* · 0.111242541 s = 0.10299995484180417 J” | CONTRADICTED | blocker | `joulewise/adapters/powermetrics.py:1791-1805`; `joulewise/uncertainty_evidence.py:933-937` | The executed binary64 multiplication is `0.10299995484180416 J`. The printed `...417` is the adjacent higher binary64 value. The combined-power literal itself, `0.9259043699999999 W`, is correct. |
| F2 | 234 | “the worst edge excursion is the difference, 0.0289329345611147592 s” | CONTRADICTED | blocker | `joulewise/powermetrics_fiducial.py:1022-1043`; `docs/paper/draft-v1.md:79` | `0.0289329345611147592` is only the exact decimal subtraction of the two printed output literals. The detector’s retained maximum edge value is `0.02893293456111476`. Preserve both only with their distinct meanings. |
| F3 | 133 | “about 2.4·10⁻⁷ s or one binary64 spacing … above the exact *H*” | CONTRADICTED | blocker | `joulewise/uncertainty_evidence.py:1179-1196` | Binary64 subtraction gives the displayed half-width `0.0006871223449707031`; its excess over exact *H* is `2.06310472828825e-7 s`, or `0.8653288414` epoch-scale ulp. This is newly added worked arithmetic and must be corrected. |
| F4 | 240 | “at most 120 s of wall time” / “the last cell evaluated may run past the 120 s mark” | CONTRADICTED | should_fix | `joulewise/powermetrics_fiducial.py:533-550,666-680` | Call it a “120 s pre-cell deadline.” The new operational explanation is correct, but “at most” remains false for total execution time. |
| F5 | 236 | “whose hash pins the calibration to one machine” | CONTRADICTED | should_fix | `joulewise/powermetrics_fiducial.py:106-120,1489-1500` | Say the hash pins the ten-field configuration/binding vector. `hardware_model` identifies a model class, not a unique physical machine. The Evidence section should also cite `1492-1500` for the hash calculation. |
| F6 | 5 | “a compensated, correctly rounded sum … the true sum of the inputs rounded once” | UNTRACEABLE | should_fix | `joulewise/adapters/powermetrics.py:1845-1848` | State the executable rule directly: “an accurate floating-point sum using `math.fsum`.” The repository records the call but not the stronger universal correctly-rounded/one-round guarantee. |
| F7 | 333-337 | “Two caveats … both stated” followed by items `1`, `3`, `2` | CONTRADICTED | nit | Draft itself, lines 333-337 | Change to “three caveats” and renumber them `1, 2, 3`. |

## Details

### Claimed fixes

| Claim | Result |
|---|---|
| B1 monotonic resolution | PASS. `4.166666666666666e-8` is present exactly. |
| B2 cell count | PASS. `122{,}859` now matches Section 2’s printed lexeme. |
| B3 other Section 2 restatements | PASS at the literal level. The semantic misuse of the subtraction remains F2. |
| B4 record-0 combined power | PARTIAL. The combined power is correct, but the newly expanded multiplication is wrong by one binary64 unit (F1). |
| B5 *H* from exact endpoints | PASS for the estimator definition and four-term sum. The added comparison with printed endpoints contains F3. |
| B6 pulse-0 stamp half-width | PASS. Executed bracket width `2.500019036233425e-7` and half-width `1.1250009518116714e-6` both reproduce. |
| B7 validity conjunction | PASS on field count and core conjunction; see adjudication below. |
| B8 van der Corput general term | PASS. The digit-reversal equation and values for indices 1–8 match `powermetrics_fiducial.py:355-367`. |
| B9 traversal | PASS. `stack.pop()` is LIFO; lower is pushed before upper, so upper is processed next (`:657-696`). |
| B10 pulse-0 provenance | PASS. The prose now plainly distinguishes the first-issued v2 anchor point from the current v3 point. The quoted pulse-0 values match the stored v2-anchored row. |

The substantive S1–S9 and S11 additions—symbol disambiguation, later-record gap rule, explicit cumulative baseline, binary64 trace accumulation, MAD definition, rejected-record shapes, depth-first traversal, validity explanation, and pre-cell deadline semantics—are present and trace to code. F4 and F6 are residual precision problems in those new explanations.

### B7 adjudication

The writer is right; the earlier four-field assertion is wrong.

`LEGACY_BINDING_FIELDS` has eight fields at `powermetrics_fiducial.py:106-115`. `V2_BINDING_FIELDS` adds `estimator_revision` and `protocol_sha256` at `:116-119`, for ten total. Protocol v2 and v3 select that ten-field tuple at `:1407-1416`.

Validity additionally requires a computed bound, no missing binding values, all pulses detected, zero spurious plateaus, exact protocol pulse count, valid raw/event digest syntax, no detection reasons, a valid capture time, and no projection disposition (`:1417-1445`). The corrected prose substantially captures that conjunction.

### S10 rationale check

The gap is honest:

- `MAX_FIRST_PARSE_LAG_S = 0.25` is a bare constant at `uncertainty_evidence.py:36`.
- `MIN_NATIVE_ROLLOVERS = 2` is a count—not two seconds—at `:40`.

The design record repeats “at least two native rollovers” and “first-parse lag >0.25 s” as gates, but supplies no rationale for those particular magnitudes (`docs/process_traces/2026-08-18-anchor-v3-science-review/02-design-consult.md:84-85,110-111`). Logging the gap instead of inventing an explanation is correct.

### Fence-verified restatements

The mandatory replay compared all 43 Section 2 values with zero mismatches. The fenced quantities actually restated in the appendix are:

| Quantity | Appendix literal | Section 2 source | Result |
|---|---|---|---|
| Pulse count | `59` | `59` | MATCH |
| Evaluated rectangles | `122{,}859` | `122{,}859` | MATCH |
| Wall resolution | `0.0000010000000000000002` | same table literal | MATCH |
| Monotonic resolution | `4.166666666666666e-8` | same numeric fenced value | MATCH |
| `pre_spawn` monotonic-before | `458736.4081875` | same | MATCH |
| `first_parse` monotonic-after | `458737.509840291` | same | MATCH |
| Anchor bound | `0.0011349971959968978` | same | MATCH |
| Capture bound | `0.030067931757111657` | same | MATCH |
| Exact printed subtraction | `0.0289329345611147592` | same | LITERAL MATCH; semantic defect F2 |

The four-term anchor identity remains correct:

`0.0006869160344978743 + 0.00044608116149902344 + 0.0000010000000000000002 + 0.000001 = 0.0011349971959968977402`

and outward rounding produces `0.0011349971959968978`.

The causal text also correctly states that `k_pre = e_0 − r_pre`: the difference is exactly one recorded resolution unit by design.

### Equation and rule trace

| Draft region | Status | Independent governing source |
|---|---|---|
| A.3.1 record fields, channel sums, energy consistency, cumulative elapsed, stamp half-width, trace intervals | TRACED except F1/F6 | `adapters/powermetrics.py:1753-1858`; `uncertainty_evidence.py:933-975`; `powermetrics_fiducial.py:1067-1081,1249-1260` |
| A.3.2 protocol sequence, constants, van der Corput schedule, pulse-loop origin, fenced workload | TRACED | `powermetrics_fiducial.py:45,61-68,355-398,1554-1585`; validator `:1883-2040` |
| A.3.3 affine model, stamp/native/causal rows, Fourier–Motzkin elimination, boxes, refusal order, rate and lag gates | TRACED | `uncertainty_evidence.py:721-811,871-1177` |
| A.3.3 four-term bound and outward conversion | TRACED except F3’s new gloss | `uncertainty_evidence.py:1179-1235` |
| A.3.4 trace placement, event pairing, warm-up trimming, schedule authentication | TRACED | `adapters/powermetrics.py:1770-1785`; `powermetrics_fiducial.py:401-441,1084-1263` |
| A.3.5 baseline, MAD scale, spurious check, fit, grids, Huber objective, accepted-region projection and widening | TRACED | `powermetrics_fiducial.py:553-907` |
| A.3.6 maximum-plus-anchor equation, order statistics and validity | TRACED except F2/F5 | `powermetrics_fiducial.py:1022-1048,1366-1500` |
| A.3.7 shared budget, check order, clock origin and exhaustion behavior | TRACED; wording issue F4 | `powermetrics_fiducial.py:524-550,975-1010` |

### Changed-value audit

No previously correct fenced value was accidentally replaced. The intended resolution and cell-count changes are correct. The fix round nevertheless introduced two new incorrect numeric glosses:

- `0.10299995484180417` at line 22; executed result is `0.10299995484180416`.
- “about `2.4·10⁻⁷`” at line 133; actual binary64-endpoint excess is `2.06310472828825e-7`.

The worst-edge defect at line 234 was unchanged from the backup when it should have been corrected.

## Verdict

No. Every equation and number is not yet correct against the implementation and fence.

The mandatory fence is clean, the four-term anchor sum is correct, `k_pre` differs from `e_0` by exactly one resolution unit by design, and the B7 writer is correct that v2/v3 bind ten fields. Three blockers remain: F1 and F3 were introduced in newly added explanatory text, while F2 survived the fix round.

## Residual risk

The retained primary capture was mounted and the full 43-value replay completed. The relevant implementation and fence files are byte-identical between `/Users/edr/code/JouleWise-wt-r4` and the checkout used by the replay script. No additional evidence-availability limitation remains.