```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "A hand-derived eight-record golden payload matches the current producer and, combined with the existing suite, kills all four known surviving mutants.",
  "workspace": {
    "base_requested": "8ab397b554057ffb094b24e72e181480cd38a1db",
    "base_mode": "exact",
    "head_start": "8ab397b554057ffb094b24e72e181480cd38a1db",
    "head_end": "8ab397b554057ffb094b24e72e181480cd38a1db",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "Land one hand-derived eight-record full-payload golden with a compact Markdown field projection, retain the refusal tests, and use a fixed-seed independent differential as the only secondary.",
    "counts": {
      "blocker": 0,
      "should_fix": 0,
      "nit": 0
    },
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/tmp250/dg071-golden-consult/unittest-tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 23 tests in 0.295s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 23 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/tmp250/dg071-golden-consult/unittest-tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics tests.test_issue_dg071_dg075_statistics_golden",
      "cwd": "<scratchpad>/tmp250/dg071-golden-consult/base",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 24 tests in 0.298s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 24 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/tmp250/dg071-golden-consult/unittest-tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics tests.test_issue_dg071_dg075_statistics_golden",
      "cwd": "<scratchpad>/tmp250/dg071-golden-consult/mut-halfup",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 24 tests in 0.290s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/tmp250/dg071-golden-consult/unittest-tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics tests.test_issue_dg071_dg075_statistics_golden",
      "cwd": "<scratchpad>/tmp250/dg071-golden-consult/mut-starts",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 24 tests in 0.319s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/tmp250/dg071-golden-consult/unittest-tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics tests.test_issue_dg071_dg075_statistics_golden",
      "cwd": "<scratchpad>/tmp250/dg071-golden-consult/mut-iqr",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 24 tests in 0.304s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/tmp250/dg071-golden-consult/unittest-tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics tests.test_issue_dg071_dg075_statistics_golden",
      "cwd": "<scratchpad>/tmp250/dg071-golden-consult/mut-gap",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 24 tests in 0.307s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "One valid build_payload golden cannot exercise refusal-only, CLI-only, full-Markdown-prose, or input-conditional mutants.",
      "needs": "Keep the existing refusal suite; add the small deterministic differential and compact renderer projection described in Q1."
    }
  ]
}
```

## Q1 — Coverage shape

Yes: the proposed golden is the right primary shape, with one small strengthening. Assert:

1. The entire normalized `build_payload` dictionary, removing only `producer.git_commit` and `producer.script_sha256`.
2. A compact exact projection of the Markdown lines that publish input identity, counts, tiling fields, and both statistics tables.

Full dictionary equality already serves as a field census: a missing, renamed, added, or changed key fails. A separate source-walking “every key has an assertion” test is redundant and substantially more brittle.

The arithmetic oracle must be visibly independent:

- Put the eight input records in the test as literals.
- Put the expected payload in a literal dictionary, not one produced or updated by the producer.
- Precede it with the sorted width/spacing lists and four type-7 equations below.
- Pin the generated fixture bytes with literal SHA-256 `cc31866f…2d58f`.
- Do not import `_describe`, `_quantile`, or any producer helper to compute expected values.
- Treat the short independent reference implementation as corroboration, not as a golden-file generator.

That makes the hand derivation short: the only derived material is two sorted lists, three quantile positions per statistic, and rendering. Static schema/method strings are contract projection, not arithmetic.

A secondary is worth maintaining: a test-local, fixed-seed differential over several 2–8-record valid bundles, comparing the numeric payload subtree with an independent Decimal/type-7 implementation of roughly 20–30 lines. It complements the single golden by catching input-conditional coincidences. I would not add Hypothesis or a repository mutation gate for this producer.

Mutation tooling check:

```text
$ ls scripts | grep -i mut
<no output>
```

There is no `scripts/mutation_kill*` or other mutation-named script. A mutation-score gate would therefore introduce a new framework, mutant-selection policy, runtime, and maintenance burden. The golden plus a small deterministic differential is cheaper and more transparent.

## Q2 — Mutant classes

Coverage below means the current 23 tests plus the proposed golden and Markdown field projection.

| Mutant class killed | Why this fixture discriminates |
|---|---|
| Output key removal, addition, rename, type change, or static value drift | Exact normalized dictionary equality. |
| Sampler/rail population errors | Eight sampler records expand to 24 rows across exactly three rails; all counts and statistic sample counts are pinned. |
| Per-rail rather than per-record calculation | Counts and distributions change immediately. |
| Omitting sorting | Both width and spacing sequences are deliberately non-monotone in file order. |
| Nearest/midpoint/wrong type-7 position or interpolation weight | DG-071 uses positions 1.75, 3.5, 5.25; DG-075 uses 1.5, 3, 4.5. |
| Wrong even/odd median selection | The middle values are distinct for both distributions. |
| Float conversion before subtraction | Epoch-scale literals retain eight decimal places and expose float precision loss. |
| Wrong seconds-to-ms scale, quantum, value type, or trailing-zero rendering | Every exact and rendered string is pinned. |
| Half-up, truncation, or other tie handling | DG-071 median and IQR and DG-075 median contain exact fifth-decimal millisecond ties. |
| IQR from rendered quartiles | DG-071 correct `iqr_ms=1.0000`; rendered-quartile difference is `1.0001`. |
| Substituting widths `[1:]` for DG-075 timestamp spacings | Six nonzero boundary gaps make the two distributions differ. |
| Zero-only or above-tolerance gap counting | Six of seven boundaries are nonzero, but none exceeds tolerance. |
| Missing `abs` in maximum-gap calculation | The sole 1 μs maximum is negative; the largest positive gap is 0.7 μs. |
| `>= tolerance` refusal | The final boundary is exactly −1 μs and must issue. |
| Wrong Markdown field selection for the published bullets/tables | Exact projected renderer lines are pinned. |
| JSON method/static provenance text drift | The normalized payload contains literal method strings and `producer.script_path`. |

Not killed:

| Class not killed by this valid golden | Can it change a published digit? |
|---|---|
| Refusal-message wording | No statistical digit; diagnostic text only. |
| Pure refusal ordering with all guards intact | No; it changes the first reason for invalid input, not an issued value. |
| Refusal-guard deletion for an invalid shape | Yes, by allowing an invalid bundle to issue. The existing one-refusal-one-test suite must remain; the sibling-start guard mutant is killed there, not by the valid golden. |
| `argparse` defaults, help, or main wiring | A paired default/pin mutation could select another bundle and change digits; most single default mutations instead refuse. Direct `build_payload` coverage does not exercise this layer. |
| CLI stdout rendering | It can print a wrong digit while JSON/Markdown remain correct. The proposed payload/Markdown assertions do not pin stdout. |
| `issue_artifacts` serialization, suffix, partial-write, or atomicity behavior | Usually changes bytes, formatting, or custody rather than the statistic digit; a deliberate post-payload rewrite could change one. |
| `producer.git_commit` and `script_sha256` computation | Can change published provenance hex characters, not DG-071/DG-075 digits. They are deliberately excluded because they vary by checkout/script mutation. |
| Full Markdown explanatory prose outside the projected field lines | Yes for explanatory numbers such as the tolerance or worked example; usually not the tables. Existing method tests partially cover this. |
| A computation mutant that happens to agree on all current fixed cases | Yes, including potentially on the retained bundle. This is the reason for the small fixed-seed differential secondary. |
| Invalid-schema, UTF-8, Decimal, contiguity, monotonicity, and path/SHA branches beyond the existing counterexamples | A missing guard can allow invalid data to issue digits; the golden does not expand refusal-state coverage. |
| Power/source semantics | No under the ratified statistic: those fields do not enter DG-071/DG-075 arithmetic. |

## Q3 — Golden bundle and derivation

The exact CSV header is:

```csv
timestamp_s,power_w,source,rail,interval_start_s,interval_end_s
```

Each logical record below expands to three consecutive CSV rows in rail order `cpu_power`, `gpu_power`, `ane_power`. `source=fixture`; power values are `(3i−2).0`, `(3i−1).0`, `(3i).0`. Thus there are eight sampler records and 24 rail rows.

| i | timestamp/end | interval start | width |
|---:|---:|---:|---:|
| 1 | 1784978889.10000000 | 1784978888.99959995 | 0.10040005 |
| 2 | 1784978889.19900020 | 1784978889.10000020 | 0.09900000 |
| 3 | 1784978889.30000029 | 1784978889.19899990 | 0.10100039 |
| 4 | 1784978889.40000024 | 1784978889.30000029 | 0.09999995 |
| 5 | 1784978889.50200074 | 1784978889.40000074 | 0.10200000 |
| 6 | 1784978889.60200041 | 1784978889.50200034 | 0.10000007 |
| 7 | 1784978889.70300110 | 1784978889.60200111 | 0.10099999 |
| 8 | 1784978889.80360015 | 1784978889.70300010 | 0.10060005 |

Fixture SHA-256:

```text
cc31866f096948d8af0e8c55f80a432086dfb753f907d52825fea00da9e2d58f
```

Signed boundary gaps are:

```text
+0.00000020, -0.00000030, 0.00000000, +0.00000050,
-0.00000040, +0.00000070, -0.00000100
```

Therefore:

```text
max(abs(gap)) = 0.00000100
nonzero boundaries = 6
```

DG-071 sorted widths:

```text
0.09900000
0.09999995
0.10000007
0.10040005
0.10060005
0.10099999
0.10100039
0.10200000
```

For `n=8`:

```text
h25 = 7×0.25 = 1.75
Q1  = 0.09999995 + 0.75×(0.10000007−0.09999995)
    = 0.1000000400

h50 = 3.5
median = 0.10040005 + 0.5×(0.10060005−0.10040005)
       = 0.100500050

h75 = 5.25
Q3  = 0.10099999 + 0.25×(0.10100039−0.10099999)
    = 0.1010000900

IQR = 0.1010000900−0.1000000400 = 0.0010000500
```

Rendered milliseconds:

```text
Q1      100.0000400 → 100.0000
median  100.500050  → 100.5000
Q3      101.0000900 → 101.0001
IQR       1.0000500 →   1.0000
```

The required IQR discriminator is live:

```text
render(IQR) = 1.0000
render(Q3) − render(Q1) = 101.0001 − 100.0000 = 1.0001
```

DG-075 temporal spacings:

```text
0.09900020, 0.10100009, 0.09999995, 0.10200050,
0.09999967, 0.10100069, 0.10059905
```

Sorted:

```text
0.09900020
0.09999967
0.09999995
0.10059905
0.10100009
0.10100069
0.10200050
```

For `n=7`:

```text
Q1     = (0.09999967 + 0.09999995)/2 = 0.0999998100
median = 0.10059905
Q3     = (0.10100009 + 0.10100069)/2 = 0.1010003900
IQR    = 0.0010005800
```

Rendered:

```text
Q1=99.9998, median=100.5990, Q3=101.0004, IQR=1.0006
```

Independent reference output, using only CSV, Decimal, type 7, and half-even:

```json
{
  "widths_s": [
    "0.10040005",
    "0.09900000",
    "0.10100039",
    "0.09999995",
    "0.10200000",
    "0.10000007",
    "0.10099999",
    "0.10060005"
  ],
  "spacings_s": [
    "0.09900020",
    "0.10100009",
    "0.09999995",
    "0.10200050",
    "0.09999967",
    "0.10100069",
    "0.10059905"
  ],
  "gaps_s": [
    "0.00000020",
    "0.00000030",
    "0.00000000",
    "0.00000050",
    "0.00000040",
    "0.00000070",
    "0.00000100"
  ],
  "sampler_record_count": 8,
  "rail_row_count": 24,
  "max_tiling_gap_s": "0.00000100",
  "tiling_gap_nonzero_boundaries": 6,
  "DG-071": {
    "sample_count": 8,
    "q1_s": "0.1000000400",
    "median_s": "0.100500050",
    "q3_s": "0.1010000900",
    "iqr_s": "0.0010000500",
    "q1_ms": "100.0000",
    "median_ms": "100.5000",
    "q3_ms": "101.0001",
    "iqr_ms": "1.0000"
  },
  "DG-075": {
    "sample_count": 7,
    "q1_s": "0.0999998100",
    "median_s": "0.10059905",
    "q3_s": "0.1010003900",
    "iqr_s": "0.0010005800",
    "q1_ms": "99.9998",
    "median_ms": "100.5990",
    "q3_ms": "101.0004",
    "iqr_ms": "1.0006"
  }
}
```

Current producer output through `issue_artifacts`, normalized only by deleting the two dynamic producer fields:

```json
{
  "input_bundle": {
    "path": "runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv",
    "record_schema": [
      "timestamp_s",
      "power_w",
      "source",
      "rail",
      "interval_start_s",
      "interval_end_s"
    ],
    "sha256": "cc31866f096948d8af0e8c55f80a432086dfb753f907d52825fea00da9e2d58f"
  },
  "max_tiling_gap_s": "0.00000100",
  "method": {
    "arithmetic": "Parse timestamp_s, interval_start_s, and interval_end_s literals directly as exact decimals; compute widths, spacings, quantiles, and IQR without binary floating point.",
    "dg075_dependence": "DG-075 is the DG-071 distribution minus the first record: consecutive timestamp differences are the widths of records 2 through n up to the retained writer's endpoint convention.",
    "float64_replication": "A float64 replication (numpy `linear`, R type 7) is guaranteed to agree only to three decimals because a float64 at 1.78e9 s has spacing 2.4e-7 s, coarser than the file's 1e-7 s literals; the digits characterise the retained bytes, not the sampler's physical timing resolution. Worked example: median 120.9186 ms exact vs 120.9185 ms float64.",
    "iqr": "IQR is Q(0.75) - Q(0.25), computed exactly before rendering.",
    "median": "Median is the p = 0.5 quantile, the mean of the two middle values when n is even.",
    "millisecond_rendering": "Multiply exact seconds by 1000 and round to four decimal places with round-half-even; renderings are JSON strings.",
    "population": "A sampler record is one contiguous group sharing an exact timestamp_s literal. Each group has exactly one ane_power, cpu_power, and gpu_power row with byte-identical interval endpoint literals; one width per group enters DG-071.",
    "quantile": "Order n values ascending. At probability p, h = (n - 1) * p (0-based) and linearly interpolate exactly between the two neighbouring order statistics; this is Hyndman-Fan type 7 (numpy linear and R type 7 are cross-references)."
  },
  "producer": {
    "script_path": "scripts/issue_dg071_dg075_statistics.py"
  },
  "rail_row_count": 24,
  "rails": [
    "ane_power",
    "cpu_power",
    "gpu_power"
  ],
  "registry_row_ids": [
    "DG-071",
    "DG-075"
  ],
  "sampler_record_count": 8,
  "schema_version": "joulewise.paper.dg071-dg075-statistics.v2",
  "statistics": {
    "DG-071": {
      "iqr_ms": "1.0000",
      "iqr_s": "0.0010000500",
      "median_ms": "100.5000",
      "median_s": "0.100500050",
      "q1_ms": "100.0000",
      "q1_s": "0.1000000400",
      "q3_ms": "101.0001",
      "q3_s": "0.1010000900",
      "sample_count": 8,
      "statistic": "interval_end_s - interval_start_s per sampler record"
    },
    "DG-075": {
      "iqr_ms": "1.0006",
      "iqr_s": "0.0010005800",
      "median_ms": "100.5990",
      "median_s": "0.10059905",
      "q1_ms": "99.9998",
      "q1_s": "0.0999998100",
      "q3_ms": "101.0004",
      "q3_s": "0.1010003900",
      "sample_count": 7,
      "statistic": "consecutive differences of sorted distinct timestamp_s literals"
    }
  },
  "tiling_gap_nonzero_boundaries": 6
}
```

Every current field matched.

## Q4 — Four known mutants

| Mutant | Existing 23 | Golden alone | Combined 24 | Kill source |
|---|---:|---:|---:|---|
| `ROUND_HALF_EVEN → ROUND_HALF_UP` | FAIL, 1 | FAIL, 1 | FAIL, 2 | Both the existing exact-tie fixture and golden ties |
| Drop `len(starts) != 1` | FAIL, 1 | OK | FAIL, 1 | Existing sibling-start refusal |
| Render IQR as rendered-Q3 minus rendered-Q1 | OK | FAIL, 1 | FAIL, 1 | Golden DG-071 `1.0000` versus mutant `1.0001` |
| Count `gap > TILING_TOLERANCE_S` | OK | FAIL, 1 | FAIL, 1 | Golden expects six; mutant emits zero |

The valid golden should not kill the sibling-start guard mutant: that mutant affects invalid input only. The combined gate kills all four, which is the correct division of responsibility between value coverage and refusal coverage.

Raw combined-suite tails:

```text
base:    Ran 24 tests in 0.298s — OK
halfup:  Ran 24 tests in 0.290s — FAILED (failures=2)
starts:  Ran 24 tests in 0.319s — FAILED (failures=1)
iqr:     Ran 24 tests in 0.304s — FAILED (failures=1)
gap:     Ran 24 tests in 0.307s — FAILED (failures=1)
```

## Q5 — Process

The same-signature reading is correct. Terra found two cases where a published field lacked a discriminating example; after two local fixtures were added, Opus found two more fields with exactly the same weakness. A cold gate would likely find or miss another individual mutant, but it would not decide how to change the test structure. The consult was the right escalation because the problem was no longer “which assertion is missing?” but “what compact oracle systematically pins the producer’s published surface?” The answer is the full-payload golden, backed by existing refusal tests and one small independent differential.

## What this consult did NOT check

- The canonical discovery suite, prohibited by the prompt.
- Any mutation beyond the four named survivors.
- Retained-bundle capture provenance, physics, or claim suitability; only its SHA-256 pin was checked.
- Every CLI/help/diagnostic string or all Markdown explanatory prose.
- Hardware or quiet-machine behavior.
- Any repository write: the checkout remained clean and detached at `8ab397b554057ffb094b24e72e181480cd38a1db`.