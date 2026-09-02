```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "DG-071 pseudoreplicates rail rows; epoch-float precision, undisclosed quartiles, and refusal-test gaps also require correction.",
  "workspace": {
    "base_requested": "a3dadadd",
    "base_mode": "exact",
    "head_start": "a3dadaddda58dc0548a47cb4c333a3249c1ca41e",
    "head_end": "a3dadaddda58dc0548a47cb4c333a3249c1ca41e",
    "upstream_end": "a3dadaddda58dc0548a47cb4c333a3249c1ca41e",
    "branch": "feat/2026-09-02-paper-d (detached checkout)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 1,
      "should_fix": 3,
      "nit": 0
    },
    "findings": [
      {
        "id": "B-1",
        "severity": "blocker",
        "title": "DG-071 pseudoreplicates each sampling record as three rail rows",
        "file": "scripts/issue_dg071_dg075_statistics.py",
        "line": 201
      },
      {
        "id": "SF-1",
        "severity": "should_fix",
        "title": "Six-decimal millisecond results expose epoch-float quantization artifacts",
        "file": "scripts/issue_dg071_dg075_statistics.py",
        "line": 195
      },
      {
        "id": "SF-2",
        "severity": "should_fix",
        "title": "Quartile method is neither ratified nor disclosed in the issued artifact",
        "file": "scripts/issue_dg071_dg075_statistics.py",
        "line": 14
      },
      {
        "id": "SF-3",
        "severity": "should_fix",
        "title": "Only two of fourteen named refusal reasons are tested through main",
        "file": "tests/test_issue_dg071_dg075_statistics.py",
        "line": 172
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/tmp245/dg071-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 8 tests in 0.113s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python <scratchpad>/tmp245/dg071-review/physics_audit.py /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "numpy 2.5.1 linear_ms6=116.971970,120.918512,122.922659 producer_formula_exact=True",
          "distribution min_ms=111.839533 p05_ms=112.679183 below_112.5=6/406",
          "artifact DG-071 markdown_seconds_match=True ms_round_only=True",
          "artifact DG-075 markdown_seconds_match=True ms_round_only=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "artifact DG-075 markdown_seconds_match=True ms_round_only=True"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "run producer twice with --repository-root /Users/edr/code/JouleWise-wt-paper-d2 and separate TMPDIR outputs; cmp both JSON and Markdown pairs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d524ef2b7630f7f7a8b1084b82187bd80b0019c784af8f91f859ffee11c1ad7b  .../run1/dg071-dg075-statistics.json",
          "d524ef2b7630f7f7a8b1084b82187bd80b0019c784af8f91f859ffee11c1ad7b  .../run2/dg071-dg075-statistics.json",
          "4534773160540d1e61fdd892ef510aa83afc4719a66267b840aae3c92ea61594  .../run1/dg071-dg075-statistics.md",
          "4534773160540d1e61fdd892ef510aa83afc4719a66267b840aae3c92ea61594  .../run2/dg071-dg075-statistics.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "run2/dg071-dg075-statistics.md"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch && git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": []
}
```

VERDICT: BLOCKER 1 / SHOULD-FIX 3 / NIT 0

## Findings

### B-1 — DG-071 pseudoreplicates each sampling record as three rail rows

The bundle has 406 sampling records, each fanned out into three rail rows with identical support. The producer appends one width per CSV row and therefore reports `n=1218`. Type-7 quartiles are not invariant under triplication: the median happens to remain unchanged, but Q1, Q3, and IQR do not.

The project’s own terminology resolves the semantic ambiguity: `joulewise/bundle.py:17-19` says `power_trace.csv` contains one row per rail per sample, while `scripts/paper_prefill_resolvability_projection.py:181-185` explicitly de-duplicates rail rows because “the reducer counts records, not rail rows.” Thus the draft’s “sampling-record interval width” denotes the 406 sampling instants, not the 1218 rail rows.

Required correction:

- Artifact: distinguish `rail_row_count: 1218` from `sampling_record_count: 406`; DG-071’s `sample_count` must be 406.
- Registry/ratification: say “one distinct support interval per sample timestamp, after verifying and collapsing the three identical rail rows.”
- Under current float arithmetic, DG-071 becomes Q1 `116.971970`, median `120.918512`, Q3 `122.922659`, IQR `5.950689` ms.
- If SF-1 is fixed with exact decimal arithmetic, the corresponding values are Q1 `116.971950`, median `120.918600`, Q3 `122.922700`, IQR `5.950750` ms.

### SF-1 — Epoch-float arithmetic cannot support the claimed nanosecond rendering

At these epoch magnitudes, a binary64 timestamp ULP is `238.418579 ns`, while six decimal places in milliseconds claim a `1 ns` rendering quantum. Subtraction is exact relative to the parsed binary endpoints in all 1218 rows, but those endpoints already differ from the CSV decimal literals; widths differ by as much as `185.104370 ns`.

The issued values therefore reproduce Python’s round-tripped epoch floats, not exact subtraction of the retained CSV numbers. Decimal parsing changes reported results at the issued sixth decimal. Use `Decimal` over the CSV strings, or explicitly weaken the reported precision and ratification. Because the current contract asks for six-decimal milliseconds, exact decimal parsing is the consistent repair.

### SF-2 — Quartile convention is not part of the ratified or issued evidence

The implementation is Hyndman–Fan type 7: R’s default `type=7` and NumPy’s default/`method="linear"`. NumPy 2.5.1 matched it exactly.

The cited ratification only says “median with IQR”; it does not pin a quartile definition. The artifact likewise records neither a method name nor its interpolation formula. The producer’s comment attributes this to “Ruling R-167-1,” but an executed repository search found that identifier and its linear-interpolation language only inside the producer itself.

This matters: standard methods give different six-decimal quartiles on the 406-record sample. Ratify and emit something equivalent to:

`quantile_method: "Hyndman-Fan type 7; h=(n-1)p; NumPy method=linear; R type=7"`.

### SF-3 — Refusal coverage does not establish the CLI contract

There are fourteen distinct `IssuanceRefused` names. Only `record_field_missing` and `bundle_path_mismatch` have tests that reach their raise sites through `main`. Direct helper tests cover `bundle_sha256_mismatch` and `timestamps_non_monotone`, but do not test CLI catching, exit status, or stable reason rendering. The remaining reasons have no trigger test.

Both tested main-path guards were mutation-proven and bit correctly. The gap is the other production refusal sites.

## P1 — Record multiplicity

Executed input authentication and census:

```text
$ shasum -a 256 /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv
6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9  .../power_trace.csv

$ awk -F, 'NR>1{print $4}' .../power_trace.csv | sort | uniq -c
 406 ane_power
 406 cpu_power
 406 gpu_power
```

Executed independent audit:

```text
$ PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python \
  <scratchpad>/tmp245/dg071-review/physics_audit.py \
  /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv \
  docs/paper/round7/dg071-dg075-statistics.json \
  docs/paper/round7/dg071-dg075-statistics.md

multiplicity 1218 406 Counter({3: 406})
rails Counter({('ane_power', 'cpu_power', 'gpu_power'): 406})
same_support 406
rows 1218 116.951942 120.918512 122.926950 5.975008
records 406 116.971970 120.918512 122.922659 5.950689
triples_exact True
```

Answer to P1(a): no. Triplication preserves the median here but changes Q1 by `−0.020027161 ms`, Q3 by `+0.004291534 ms`, and IQR by `+0.024318695 ms`. All changes survive the issued six decimals.

Answer to P1(b): “every retained record” is ambiguous in isolation, but the repository’s measurement semantics and the paper’s “sampling-record” language mean a sampler record/sample instant. Calling 1218 rail rows “Retained record count” would mislead the paper reader. This is B-1 and blocks filling DG-071.

## P2 — Quartile method

Executed NumPy comparison on the 406-record sample:

```text
$ /Users/edr/code/JouleWise/.venv/bin/python ...physics_audit.py ...
numpy 2.5.1 linear_ms6=116.971970,120.918512,122.922659 producer_formula_exact=True
```

The formula at producer lines 106–112 uses zero-based position `(n−1)p`, interpolating between the surrounding order statistics. That is Hyndman–Fan type 7, NumPy `method="linear"`, and R’s default `type=7`.

Executed disclosure search:

```text
$ rg -n "linear-interpolated|quantile|quartile|type 7|method" \
  docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md \
  docs/paper/round7/dg071-dg075-statistics.json \
  docs/paper/round7/dg071-dg075-statistics.md
```

Output: no matches.

Other standard methods materially differ; for example, executed NumPy results included:

```text
inverted_cdf              q1=116.951942 q3=122.926950 iqr=5.975008
weibull                   q1=116.936982 q3=122.927964 iqr=5.990982
linear                    q1=116.971970 q3=122.922659 iqr=5.950689
median_unbiased           q1=116.946956 q3=122.927288 iqr=5.980333
```

The ratification does not pin the method, and the artifact does not disclose it. This fails the stated replication bar.

## P3 — DG-075 versus DG-071 physics

The first records initially appear to tile:

```text
timestamp_s,...,interval_start_s,interval_end_s
1784978889.2106586,...,1784978889.09877,1784978889.2106586
1784978889.3265338,...,1784978889.2106586,1784978889.3265338
```

Whole-file executed result:

```text
tiling end_mismatch=0 start_mismatch=100/405 negative=48 positive=52 range_ms=[-0.0004000,0.0003000]
drop_first_vs_spacing pointwise=False q1=True
```

Thus:

- `interval_end_s == timestamp_s` for all 406 sampling records.
- Only 305 of 405 following records have a textually exact `interval_start_s == previous timestamp_s`.
- The other 100 differ by only −0.4 to +0.3 microseconds: 48 tiny overlaps and 52 tiny gaps.
- DG-071-with-first-record-removed and DG-075 are not pointwise-identical samples.

The adapter constructs `interval_start_s = interval_end_s - elapsed_ns/1e9`, while timestamps are separately formed from an epoch anchor plus cumulative elapsed time. Given the magnitudes and mixed signs, I infer the 100 discrepancies are floating-point reconstruction artifacts, not physical sampler pauses or merged intervals.

Executed Q1 decomposition:

```text
issued_DG071_q1_ms=116.951942444
dedup_DG071_q1_ms=116.971969604
dedup_drop_first_q1_ms=117.032051086
DG075_q1_ms=117.032051086
tripling_effect_us=20.027161
drop_first_effect_us=60.081482
issued_total_difference_us=80.108643
```

Therefore the issued Q1 difference is not entirely the dropped first record:

- `20.027161 µs` comes from tripling the sample before type-7 interpolation.
- `60.081482 µs` comes from removing the first width.
- The 100 submicrosecond pointwise discrepancies do not alter Q1 in this particular ordering: after dropping the first record, the Q1 summaries match exactly.

## P4 — Float and rounding

Executed precision audit:

```text
precision rows decimal_ms6=116.951900,120.918600,122.927000,5.975100 float_ms6=116.951942,120.918512,122.926950,5.975008 error_ns=42.443848,-87.655640,-49.545288,-91.989136
precision records decimal_ms6=116.971950,120.918600,122.922700,5.950750 float_ms6=116.971970,120.918512,122.922659,5.950689 error_ns=19.604492,-87.655640,-41.079712,-60.684204
precision spacings decimal_ms6=117.032100,120.922400,122.927000,5.894900 float_ms6=117.032051,120.922327,122.926950,5.894899 error_ns=-48.913574,-72.958374,-49.545288,-0.631714
precision_limits ulp_ns=238.418579 max_parse_error_ns=118.7286376953125000000000 max_width_error_ns=185.1043701171875000000000 binary_subtractions_exact=1218/1218 render_quantum_ns=1
```

A concrete first-row check:

```text
subtraction_exact_relative_to_parsed_binary_endpoints=1218/1218
text_start=1784978889.09877 text_end=1784978889.2106586
float_width_s=0.11188864707946777 decimal_text_width_s=0.1118886
difference_ns=47.0794677734375000000000
```

So the subtraction itself introduces no additional rounding relative to the parsed binary endpoints, but binary parsing at epoch scale has already lost resolution relevant to the final six-decimal millisecond digits.

Artifact consistency is otherwise correct:

```text
artifact DG-071 markdown_seconds_match=True ms_round_only=True
artifact DG-075 markdown_seconds_match=True ms_round_only=True
```

The Markdown seconds are exactly Python `repr` of the JSON floats. Each JSON `*_ms` equals `round(*_s * 1000, 6)`; Markdown adds fixed-width formatting and trailing zeros. That is the only explicit final rounding, but it follows earlier float quantization.

## P5 — Refusal guards at `main`

Executed suite:

```text
$ TMPDIR=.../tmp245/dg071-review PYTHONDONTWRITEBYTECODE=1 \
  /Users/edr/code/JouleWise/.venv/bin/python \
  -m unittest tests.test_issue_dg071_dg075_statistics
........
----------------------------------------------------------------------
Ran 8 tests in 0.113s

OK
```

Executed AST refusal census found fourteen distinct names:

| Refusal name | Test reaching it through `main` | Mutation status |
|---|---|---|
| `record_schema_mismatch` | None | No through-main killer |
| `record_field_missing` | `test_missing_required_field_is_refused_without_output` | Killed; executed |
| `record_field_invalid` | None | No through-main killer |
| `timestamps_non_monotone` | None; direct `_issue` test exists | Direct test kills, CLI path untested |
| `record_interval_not_positive` | None | No through-main killer |
| `record_set_empty` | None | No through-main killer |
| `insufficient_unique_timestamps` | None | No through-main killer |
| `statistic_sample_empty` | None; unreachable through `main` after upstream guards | No main-path mutant |
| `bundle_path_mismatch` | `test_cli_refusal_is_nonzero_and_names_reason` | Killed; executed |
| `bundle_path_unavailable` | None | No through-main killer |
| `bundle_sha256_mismatch` | None; direct `_issue` test exists | Direct test kills, CLI path untested |
| `git_commit_unavailable` | None | No through-main killer |
| `git_commit_invalid` | None | No through-main killer |
| `output_path_invalid` | None | No through-main killer |

Two allowed mutation checks were run in isolated TMPDIR copies.

Deleting `record_field_missing`:

```text
FAIL: test_missing_required_field_is_refused_without_output
AssertionError: 'REFUSED record_field_missing:' not found in
"REFUSED record_field_invalid: row 2 field interval_end_s is not a float: ''
no output written"

Ran 1 test in 0.001s
FAILED (failures=1)
```

Deleting `bundle_path_mismatch`:

```text
FAIL: test_cli_refusal_is_nonzero_and_names_reason
AssertionError: 'REFUSED bundle_path_mismatch:' not found in
'REFUSED bundle_sha256_mismatch: expected 694516...e9, observed 0212c6...c4a
no output written'

Ran 1 test in 0.002s
FAILED (failures=1)
```

Both existing main-path tests genuinely bind the production refusal name; SF-3 concerns the much larger unbound remainder.

## P6 — Additional execution and physics checks

Two real producer runs were written outside every checkout and compared:

```text
$ ... issue_dg071_dg075_statistics.py --repository-root \
  /Users/edr/code/JouleWise-wt-paper-d2 --out .../run1/dg071-dg075-statistics.json
$ ... issue_dg071_dg075_statistics.py --repository-root \
  /Users/edr/code/JouleWise-wt-paper-d2 --out .../run2/dg071-dg075-statistics.json
$ cmp .../run1/dg071-dg075-statistics.json .../run2/dg071-dg075-statistics.json
$ cmp .../run1/dg071-dg075-statistics.md .../run2/dg071-dg075-statistics.md
```

Both comparisons exited zero:

```text
d524ef2b...1ad7b  .../run1/dg071-dg075-statistics.json
d524ef2b...1ad7b  .../run2/dg071-dg075-statistics.json
45347731...61594  .../run1/dg071-dg075-statistics.md
45347731...61594  .../run2/dg071-dg075-statistics.md
```

The former `111.8–112.5 ms` band is indeed only the bottom tail:

```text
distribution min_ms=111.839533 p05_ms=112.679183 below_112.5=6/406
```

Only 6 of 406 sampling-record widths, about 1.48%, are below `112.5 ms`; the fifth percentile is already `112.679183 ms`. That ratification statement is supported.

Ordering assumptions also held for this pinned file: the real producer completed twice, thereby passing its non-monotone timestamp guard; all 406 groups were contiguous triples containing exactly the expected three rails and identical supports.

## Residual risk

No additional residual risk beyond the explicitly reported refusal-test gap and the limitations below.

## What this review did NOT check

- It did not run the canonical test suite, as explicitly prohibited.
- It did not mutate more than the permitted two refusal sites.
- It did not inspect or reinterpret the raw 328k-record cross-corpus evidence; physics checks were limited to the pinned R03P CSV and relevant producer/adapter code.
- It did not edit the artifact, registry, draft, or any repository file. Final `git status --short --branch` remained `## HEAD (no branch)`.
- It did not perform live hardware validation or any `[QUIET-MAC]` measurement.