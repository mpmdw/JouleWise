```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three non-equivalent mutants survive the fast suite and all 200 differential nights; the two-line reducer change matches E2, but the mutation gate remains open.",
  "workspace": {
    "base_requested": "660b32d7b567abcc5bd4b98533c1c05937c14893",
    "base_mode": "exact",
    "head_start": "660b32d7b567abcc5bd4b98533c1c05937c14893",
    "head_end": "660b32d7b567abcc5bd4b98533c1c05937c14893",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "detail": "M033, M045, and M050 survive both gates. Each has a concrete non-equivalent record-type witness missing from the fast suite."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "detail": "The numeric fix admits large integers but still produces uncaught exceptions for an unrestricted integer anchor and oversized window energy."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B /tmp/152c9255/a292-delta-sol/baseline_fast.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 61 tests in 58.936s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/152c9255/a292-delta-sol/sweep.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "M111"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "A292_START=0 A292_STOP=50 python3 -B /tmp/152c9255/a292-delta-sol/differential.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHTS 50 active 4 elapsed 178.1"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHTS 50 active 4"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "A292_START=50 A292_STOP=100 python3 -B /tmp/152c9255/a292-delta-sol/differential.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHTS 100 active 4 elapsed 179.9"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHTS 100 active 4"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "A292_START=100 A292_STOP=150 python3 -B /tmp/152c9255/a292-delta-sol/differential.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHTS 150 active 4 elapsed 175.9"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHTS 150 active 4"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "A292_START=150 A292_STOP=200 python3 -B /tmp/152c9255/a292-delta-sol/differential.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NIGHTS 200 active 4 elapsed 150.8"]},
      "expected": {"exit_code": 0, "tail_regex": "NIGHTS 200 active 4"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3 -B /tmp/152c9255/a292-delta-sol/summarize.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["DIFFERENTIAL_200 variants=A+B survivors=M033,M045,M050,M077", "NON_EQUIVALENT=M033,M045,M050 EQUIVALENT=M077"]},
      "expected": {"exit_code": 0, "tail_regex": "NON_EQUIVALENT=M033,M045,M050 EQUIVALENT=M077"}
    },
    {
      "id": "V8",
      "kind": "smoke",
      "cmd": "python3 -B /tmp/152c9255/a292-delta-sol/type_witness.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["M033 baseline=window_keys mutant=TypeError", "M045 baseline=window_domain mutant=TypeError", "M050 baseline=row_keys mutant=TypeError"]},
      "expected": {"exit_code": 0, "tail_regex": "M050 baseline=row_keys mutant=TypeError"}
    },
    {
      "id": "V9",
      "kind": "smoke",
      "cmd": "python3 -B /tmp/152c9255/a292-delta-sol/numeric_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["positive_anchor_5000 uncaught ValueError", "gross_1000 uncaught OverflowError"]},
      "expected": {"exit_code": 0, "tail_regex": "gross_1000 uncaught OverflowError"}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "git diff --check 8d06633e HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "E2's zero non-equivalent survivor gate is unmet.",
      "needs": "Add the three exact type witnesses in F1 and rerun the mutation sweep."
    },
    {
      "id": "G2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "E2 admits unrestricted finite integers but gives no typed disposition for aggregate energy overflow or Python's canonical-JSON integer digit limit.",
      "needs": "Rule the numeric range or serialization and overflow behavior."
    }
  ]
}
```

## Findings

**F1 — BLOCKER.** The harness fix closes 16 of Sol’s 19 earlier domain-operand survivors, but three remain. The added `[]` witnesses fail the remaining key-set checks, so they never exercise the deleted type operands. These are non-equivalent mutants, not merely uncovered lines:

| Mutant | Exact missing witness | Required baseline result | Mutant result |
|---|---|---|---|
| M033 | Replace one window with `list(WINDOW_KEYS)` | `window_keys` | uncaught `TypeError` |
| M045 | Set a window’s `energy_bound_terms_j` to `[ANCHOR_KEY]` | `window_domain` | uncaught `TypeError` |
| M050 | Replace one score row with `list(ROW_KEYS)` | `row_keys` | uncaught `TypeError` |

Direct replay produced those six outcomes. All three mutants then survived **every one of the 200 nights**, including both the accepted-window and missing-window differential variants.

**F2 — SHOULD-FIX.** The changed `_num` predicate correctly accepts `0` and `10**1000` anchors and refuses a negative `10**1000` anchor as `window_domain`. Its unrestricted integer domain is still incomplete: a positive `10**5000` anchor reaches canonical JSON hashing and raises `ValueError`. A `10**1000` `gross_j` reaches `math.fsum` and raises `OverflowError`. The latter is the aggregate-overflow gap already identified in Astra’s prior report; Sol F5’s uncaught-exception observation remains true. E2 needs a range or typed-disposition ruling before these inputs can be handled consistently.

The [reducer diff](/Users/edr/code/wt-152c9255-a292m/joulewise/scored_reduce.py:55) is **exactly two line replacements**. The `_num` replacement implements E2’s `int` or finite `float` domain for ordinary and large serializable integers. The binding replacement correctly evaluates `_in_force` at the **window’s declared** `envelope_index` before the later placement-index check. No other reducer line changed.

The [oracle changes](/Users/edr/code/wt-152c9255-a292m/tests/scored_reduce_checker.py:33) retain structural independence: the checker imports only stdlib modules and `tests.scored_roster_checker`; that dependency also has no `joulewise` import. It computes the declared-index binding and the three separate completeness passes itself. Its numeric path shares the unresolved extreme-value range, though it does not import the reducer’s predicate.

| Prior finding | Delta disposition |
|---|---|
| Sol F1, 19 domain-operand survivors | **Partial:** 16 killed; M033, M045, M050 remain blockers. |
| Sol F2, wrong well-formed registration digest | **Closed:** M068 killed. |
| Sol F3, zero anchor and null unmatched answer | **Closed:** M081, M083, M094 killed. |
| Sol F4, four parents with five envelopes | **Closed:** M076 killed by the new focused witness. |
| Sol F5, huge energy raises uncaught exception | **Open:** `10**1000` `gross_j` still raises `OverflowError`; E2’s numeric disposition needs a ruling. |
| Astra F1, binding uses placement index | **Closed:** reducer, oracle, and both cross-event witnesses use the declared index. |
| Astra F2, interleaved oracle completeness | **Closed:** the oracle now uses ordered missing-window, null-anchor, and missing-row passes; competing-defect witnesses pass. |
| Astra F3, large integer anchors | **Partial:** the cited positive and negative large-anchor cases pass; `10**5000` exposes the JSON digit limit. |

**Full mutation ledger.** `K` means killed by the 61-test fast suite; `S` means survived. Only fast-suite survivors entered the 200-night differential. Lines refer to [scored_reduce.py](/Users/edr/code/wt-152c9255-a292m/joulewise/scored_reduce.py). M001–M109 retain the prior IDs: 22 guard deletions, 73 operand deletions, 10 comparison flips, and four named mutations. The revised `_num` has two additional outer-`or` operands, swept as supplemental M110–M111. There were no `max` or `min` calls to collapse.

| ID | Mutation @ line | Fast | 200-night |
|---|---|:---:|:---:|
| M001 | guard− @ 90 | K | — |
| M002 | guard− @ 92 | K | — |
| M003 | guard− @ 100 | K | — |
| M004 | guard− @ 102 | K | — |
| M005 | guard− @ 104 | K | — |
| M006 | guard− @ 106 | K | — |
| M007 | guard− @ 107 | K | — |
| M008 | guard− @ 112 | K | — |
| M009 | guard− @ 113 | K | — |
| M010 | guard− @ 122 | K | — |
| M011 | guard− @ 123 | K | — |
| M012 | guard− @ 125 | K | — |
| M013 | guard− @ 126 | K | — |
| M014 | guard− @ 129 | K | — |
| M015 | guard− @ 131 | K | — |
| M016 | guard− @ 132 | K | — |
| M017 | guard− @ 133 | K | — |
| M018 | guard− @ 145 | K | — |
| M019 | and−1/2 @ 44 | K | — |
| M020 | and−2/2 @ 44 | K | — |
| M021 | and−1/2 @ 48 | K | — |
| M022 | and−2/2 @ 48 | K | — |
| M023 | and−1/2 @ 52 | K | — |
| M024 | and−2/2 @ 52 | K | — |
| M025 | and−1/2 @ 56 | K | — |
| M026 | and−2/2 @ 56 | K | — |
| M027 | ≥→> @ 139 | K | — |
| M028 | guard− @ 164 | K | — |
| M029 | guard− @ 167 | K | — |
| M030 | guard− @ 284 | K | — |
| M031 | ≥→> @ 52 | K | — |
| M032 | <→≤ @ 66 | K | — |
| M033 | and−1/2 @ 90 | S | S |
| M034 | and−2/2 @ 90 | K | — |
| M035 | and−1/13 @ 92 | K | — |
| M036 | and−2/13 @ 92 | K | — |
| M037 | and−3/13 @ 92 | K | — |
| M038 | and−4/13 @ 92 | K | — |
| M039 | and−5/13 @ 92 | K | — |
| M040 | and−6/13 @ 92 | K | — |
| M041 | and−7/13 @ 92 | K | — |
| M042 | and−8/13 @ 92 | K | — |
| M043 | and−9/13 @ 92 | K | — |
| M044 | and−10/13 @ 92 | K | — |
| M045 | and−11/13 @ 92 | S | S |
| M046 | and−12/13 @ 92 | K | — |
| M047 | and−13/13 @ 92 | K | — |
| M048 | and−1/2 @ 102 | K | — |
| M049 | and−2/2 @ 102 | K | — |
| M050 | and−1/2 @ 112 | S | S |
| M051 | and−2/2 @ 112 | K | — |
| M052 | and−1/14 @ 113 | K | — |
| M053 | and−2/14 @ 113 | K | — |
| M054 | and−3/14 @ 113 | K | — |
| M055 | and−4/14 @ 113 | K | — |
| M056 | and−5/14 @ 113 | K | — |
| M057 | and−6/14 @ 113 | K | — |
| M058 | and−7/14 @ 113 | K | — |
| M059 | and−8/14 @ 113 | K | — |
| M060 | and−9/14 @ 113 | K | — |
| M061 | and−10/14 @ 113 | K | — |
| M062 | and−11/14 @ 113 | K | — |
| M063 | and−12/14 @ 113 | K | — |
| M064 | and−13/14 @ 113 | K | — |
| M065 | and−14/14 @ 113 | K | — |
| M066 | and−1/2 @ 125 | K | — |
| M067 | and−2/2 @ 125 | K | — |
| M068 | and−1/2 @ 126 | K | — |
| M069 | and−2/2 @ 126 | K | — |
| M070 | ≤→< @ 132 | K | — |
| M071 | and−1/2 @ 140 | K | — |
| M072 | and−2/2 @ 140 | K | — |
| M073 | and−1/2 @ 145 | K | — |
| M074 | and−2/2 @ 145 | K | — |
| M075 | guard− @ 171 | K | — |
| M076 | or−1/2 @ 283 | K | — |
| M077 | or−2/2 @ 283 | S | S |
| M078 | >→≥ @ 95 | K | — |
| M079 | or−1/2 @ 97 | K | — |
| M080 | or−2/2 @ 97 | K | — |
| M081 | or−1/2 @ 118 | K | — |
| M082 | or−2/2 @ 118 | K | — |
| M083 | or−1/2 @ 120 | K | — |
| M084 | or−2/2 @ 120 | K | — |
| M085 | ≥→> @ 133 | K | — |
| M086 | or−1/2 @ 167 | K | — |
| M087 | or−2/2 @ 167 | K | — |
| M088 | <→≤ @ 283 | K | — |
| M089 | <→≤ @ 283 | K | — |
| M090 | and−1/2 @ 294 | K | — |
| M091 | and−2/2 @ 294 | K | — |
| M092 | and−1/2 @ 97 | K | — |
| M093 | and−2/2 @ 97 | K | — |
| M094 | ≥→> @ 97 | K | — |
| M095 | or−1/2 @ 238 | K | — |
| M096 | or−2/2 @ 238 | K | — |
| M097 | and−1/2 @ 254 | K | — |
| M098 | and−2/2 @ 254 | K | — |
| M099 | and−1/2 @ 262 | K | — |
| M100 | and−2/2 @ 262 | K | — |
| M101 | >→≥ @ 278 | K | — |
| M102 | and−1/2 @ 208 | K | — |
| M103 | and−2/2 @ 208 | K | — |
| M104 | and−1/2 @ 272 | K | — |
| M105 | and−2/2 @ 272 | K | — |
| M106 | fraction→0.2 @ 278 | K | — |
| M107 | drop paired filter @ 256 | K | — |
| M108 | parent energy per item @ 245 | K | — |
| M109 | cell energy per item @ 271 | K | — |
| M110 | or−1/2 @ 56 | K | — |
| M111 | or−2/2 @ 56 | K | — |

**M077 is equivalent on verified rosters.** Both minimums are five. The packer’s `inv_24` permits at most one root parent per cell in an envelope. Each fully counted parent has a counted window, giving an injection from fully counted parents to distinct envelopes. Thus `distinct_envelopes ≥ fully_counted_parents`; if distinct envelopes are below five, fully counted parents are necessarily below five. Removing M077’s second `or` operand cannot change the result.

## Residual risk

The requested review did not run the full discovery suite or live hardware gates. The repository remained clean at the requested hash; this session wrote only `/tmp` sweep artifacts.