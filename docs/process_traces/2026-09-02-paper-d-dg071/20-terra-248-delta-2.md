```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Issued artifact is exactly reproducible and all execution closures hold; two mutation-surviving test gaps should be fixed, plus one disposition nit.",
  "workspace": {
    "base_requested": "29181d6c",
    "base_mode": "descendant",
    "head_start": "8096cb80e11696aa8b8cb52915dc86fabdada552",
    "head_end": "8096cb80e11696aa8b8cb52915dc86fabdada552",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 2,
      "nit": 1
    },
    "findings": [
      {
        "id": "SF-EXEC-01",
        "severity": "should_fix",
        "title": "No exact-half rendering regression kills a ROUND_HALF_UP mutant.",
        "file": "tests/test_issue_dg071_dg075_statistics.py",
        "line": 212
      },
      {
        "id": "SF-EXEC-02",
        "severity": "should_fix",
        "title": "Sibling interval_start literal mismatch is not covered by the rail-set refusal test.",
        "file": "tests/test_issue_dg071_dg075_statistics.py",
        "line": 434
      },
      {
        "id": "NIT-EXEC-01",
        "severity": "nit",
        "title": "The carried zero-spacing scenario cannot emit an artifact because positive-width or tiling refusal fires first.",
        "file": "docs/process_traces/2026-09-02-paper-d-dg071/18-fix-round-2-disposition-and-reissue.md",
        "line": 50
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/dg071-exec-audit.ZFLR2B PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 22 tests in 0.153s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 22 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/dg071-exec-audit.ZFLR2B PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics.Dg071Dg075StatisticsTests.test_precision_regression_uses_exact_epoch_literals",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.012s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "git clone --no-checkout . <TMP>/replay-repo-29181d6c; git -C <TMP>/replay-repo-29181d6c checkout 29181d6c; run the producer twice with --repository-root <TMP>/replay-repo-29181d6c; cmp both pairs and the committed pair",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DG-071 median_ms=120.9186 iqr_ms=5.9508",
          "DG-075 median_ms=120.9224 iqr_ms=5.8949",
          "JSON+Markdown replay A=B=committed"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "JSON\\+Markdown replay A=B=committed"
      }
    }
  ],
  "flags": []
}
```

VERDICT: SHOULD-FIX 2 / NIT 1

## Findings

- `SF-EXEC-01`: The suite does not kill `ROUND_HALF_EVEN → ROUND_HALF_UP`. Add two through-`main` fixtures at exact fifth-decimal millisecond ties: `1.23445 ms → 1.2344` and `1.23455 ms → 1.2346`.

- `SF-EXEC-02`: `test_record_rail_set_mismatch_refusal_reaches_main` covers missing rails and differing sibling ends, but not a differing sibling `interval_start_s` literal. Add that fixture; deleting the `len(starts) != 1` guard otherwise lets invalid population data issue an artifact.

- `NIT-EXEC-01`: The disposition’s carried scenario is not issuable. Distinct-but-numerically-equal timestamps pass the strict monotone comparison, but a positive second width then fails tiling; a tiled second record has zero width and fails earlier. Correct the trace if desired; no producer change is needed.

## D1 — C1–C7 closure execution

| Closure | Executed check and output tail |
|---|---|
| C1 population | Independent CSV/Decimal grouping produced `DG-071: n=406`; adversarial `fourth_rail`, duplicate CPU/no ANE, sibling-start mismatch, split group, and rail-sorted fixtures all refused as required. |
| C2 exact arithmetic | Independent Decimal/type-7 replication, with no producer import: `DG-071 ... byte-for-byte strings True`; `DG-075 ... byte-for-byte strings True`. |
| C3 method | The 24-line Method-only replica in D9 emitted `median_s=0.12091860`, `median_ms=120.9186`, `iqr_s=0.005950750`, `iqr_ms=5.9508`. |
| C4 tiling | `gap=0.000001` issued successfully; `gap=0.0000011` refused `records_do_not_tile`; literal endpoint mismatch also refused `records_do_not_tile`. |
| C5 main-path refusals | `python -m unittest tests.test_issue_dg071_dg075_statistics` → `Ran 22 tests ... OK`. |
| C6 precision | Targeted precision test → `Ran 1 test in 0.012s` / `OK`; it asserts exact `120.9186` versus float64 `120.9185`. |
| C7 replay | Two producer runs from a temporary clone checked out at `29181d6c` matched each other and both committed artifacts byte-for-byte. |

## D2 — independent values of record

The retained CSV SHA-256 matched the required pin:

```text
6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9
```

Independent Decimal/type-7 output:

```text
DG-071: n=406
seconds ('0.116971950', '0.12091860', '0.122922700', '0.005950750')
ms      ('116.9720', '120.9186', '122.9227', '5.9508')
byte-for-byte strings True

DG-075: n=405
seconds ('0.1170321', '0.1209224', '0.122927', '0.0058949')
ms      ('117.0321', '120.9224', '122.9270', '5.8949')
byte-for-byte strings True
```

No digit differs; no blocker.

## D3 — adversarial population fixtures

| Fixture | First refusal | Message names actual defect? |
|---|---|---|
| Fourth rail | `record_rail_set_mismatch` | Yes; lists `fourth_power`. |
| Two `cpu_power`, no `ane_power` | `record_rail_set_mismatch` | Yes; lists duplicate CPU rails and absent ANE. |
| One differing sibling start literal | `record_rail_set_mismatch` | Yes; lists `['9', '9.0']`. |
| `A A A B B B A A A` | `records_not_contiguous` | Yes; return to literal `A` after another record began. |
| Rail-sorted rows | `records_not_contiguous` | Yes; first return to timestamp `10` is the causal malformed grouping. |

The contiguity check correctly precedes monotonicity: the rail-sorted fixture would also eventually be numerically non-monotone, but its first, more explanatory defect is interleaving.

## D4 — tiling edges

```text
tile_gap_exact_1us: rc=0
tile_gap_1p1us: rc=2; REFUSED records_do_not_tile ... max boundary gap=0.0000011 s
end_literal_trailing_zero: rc=2; REFUSED records_do_not_tile: end/timestamp literal mismatches=1
```

The implementation performs literal equality for endpoint/timestamp before Decimal comparison. That matches C4’s explicit literal-equality contract. I do not flag it: changing this to numeric equality would be a new policy decision, not an execution repair.

## D5 — numeric edges

Hand-computable type-7 checks all passed:

```text
n2                   [1.5, 2, 2.5, 1] PASS=True
n3                   [2, 3, 4, 2] PASS=True
n4                   [2.5, 4, 5.5, 3] PASS=True
n5_h_integer_q1      [2, 3, 4, 2] PASS=True
ties                 [2, 2, 2, 0] PASS=True
```

Through `main`, exact-half rendering produced both round-half-even directions:

```text
half_even_down: DG-071 median_ms=1.2344
half_even_up:   DG-071 median_ms=1.2346
```

The code is correct; the missing regression tests are `SF-EXEC-01`.

## D6 — numerically equal timestamp literals

With `1784978889.1000000` followed by `1784978889.10000000`:

```text
numeric_equal_positive_width: rc=2
REFUSED records_do_not_tile ... max boundary gap=0.10000000 s

numeric_equal_zero_width: rc=2
REFUSED record_interval_not_positive: row 5 has interval width 0.00000000
```

Thus no artifact with a zero DG-075 spacing can issue. Tiling catches the positive-width construction; the only tiled construction is rejected earlier for zero width. Severity is a NIT in the disposition wording, not a producer defect.

## D7 — three further mutants

| Mutant | 22-test result | Assessment |
|---|---|---|
| `ROUND_HALF_EVEN → ROUND_HALF_UP` | Survived: `Ran 22 tests ... OK` | `SF-EXEC-01`; it changes `1.2344` to `1.2345`. |
| `len(ordered)-1 → len(ordered)` | Killed: 2 failures, 1 error | Adequately detected by hand-computable/type-7 tests. |
| Drop `len(starts) != 1` | Survived: `Ran 22 tests ... OK` | `SF-EXEC-02`; a differing sibling start then issues successfully. |

## D8 — artifact and producer consistency

```text
git show 29181d6c:scripts/issue_dg071_dg075_statistics.py | shasum -a 256
d769f05b050d56e49e55b1aac3d30a21e1a1ad7ddd181f7d15ad62988edf4899
```

This equals JSON `producer.script_sha256`; JSON `git_commit` is `29181d6cdf7bcea89540c52eba39965363f5446f`.

`git diff --stat 29181d6c 8096cb80` contains only the reissued artifacts and process traces; the producer file is unchanged.

Replay outputs:

```text
5d96505f...693b0d  replay-a/dg071-dg075-statistics.json
5d96505f...693b0d  replay-b/dg071-dg075-statistics.json
357410c6...6396d  replay-a/dg071-dg075-statistics.md
357410c6...6396d  replay-b/dg071-dg075-statistics.md
JSON+Markdown replay A=B=committed
```

## D9 — Method-only replication

This 24-line script uses only the Markdown Method’s population rule, Decimal arithmetic, type-7 formula, and rendering rule:

```python
import csv
import sys
from decimal import Decimal as D, ROUND_HALF_EVEN

def q(xs, p):
    xs = sorted(xs)
    h = D(len(xs) - 1) * p
    lo = int(h)
    return xs[lo] if h == lo else xs[lo] + (h - lo) * (xs[lo + 1] - xs[lo])

groups, current = [], []
for row in csv.DictReader(open(sys.argv[1], newline="", encoding="utf-8")):
    if current and row["timestamp_s"] != current[0]["timestamp_s"]:
        groups.append(current)
        current = []
    current.append(row)
groups.append(current)
widths = [D(g[0]["interval_end_s"]) - D(g[0]["interval_start_s"]) for g in groups]
median = q(widths, D("0.5"))
iqr = q(widths, D("0.75")) - q(widths, D("0.25"))
def ms(x):
    return format((x * 1000).quantize(D("0.0001"), rounding=ROUND_HALF_EVEN), "f")
print("median_s=", str(median), "median_ms=", ms(median))
print("iqr_s=", str(iqr), "iqr_ms=", ms(iqr))
```

Output:

```text
median_s= 0.12091860 median_ms= 120.9186
iqr_s= 0.005950750 iqr_ms= 5.9508
```

No additional Method sentence was needed.

## Residual risk

The two SHOULD-FIX items are coverage gaps, not observed errors in the issued artifact.

## What this review did NOT check

I did not run the prohibited canonical discovery suite, conduct live hardware measurement, or modify any checkout file.