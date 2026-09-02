```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Golden arithmetic and prescribed mutants pass, but a plausible large-bundle truncation survives and HEAD cannot byte-reproduce the committed artifacts.",
  "workspace": {
    "base_requested": "8ab397b554057ffb094b24e72e181480cd38a1db",
    "base_mode": "exact",
    "head_start": "6846363dab669149be43307a666f835a811c4e49",
    "head_end": "6846363dab669149be43307a666f835a811c4e49",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 2, "should_fix": 0, "nit": 1},
    "findings": [
      {"id": "EXEC-R3-B1", "severity": "blocker", "title": "A 400-record truncation changes issued values yet all 25 focused tests pass"},
      {"id": "EXEC-R3-B2", "severity": "blocker", "title": "Replaying at candidate HEAD is not byte-identical to either committed issued artifact"},
      {"id": "EXEC-R3-N1", "severity": "nit", "title": "Golden SHA assertion repeats its literal instead of the already-bound golden_sha256 name"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=<scratch>/unittest-tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 25 tests in 0.279s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 25 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python - <<'PY' <17-line Decimal-only reconstruction from golden literals> PY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["sha cc31866f096948d8af0e8c55f80a432086dfb753f907d52825fea00da9e2d58f bytes 2047", "DG075 ... iqr 0.0010005800 render ['99.9998', '100.5990', '101.0004', '1.0006']", "gaps ['0.00000020', '-0.00000030', '0.00000000', '0.00000050', '-0.00000040', '0.00000070', '-0.00000100'] max 0.00000100 nonzero 6"]},
      "expected": {"exit_code": 0, "tail_regex": "sha cc31866f.*nonzero 6"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python scripts/issue_dg071_dg075_statistics.py --repository-root $PWD --out <scratch>/replay-a/issued.json; repeat for replay-b; shasum -a 256 outputs artifacts; cmp outputs",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["replay JSON 02ad2e9b9b021a5754618cc5a687f68270877210a3a660697be4c867432f4187", "replay MD aea11b88670435c0befb0b5983ae6a705fc60da26090136f17776392741e5de5", "committed JSON dda89609054742b66501ef3acfe822a20e3e7da5d5882349f5d5b255ed7b0caf", "committed MD a7bd11e5228716cd7242d3436ff2f7897e32869cf4d151220a1369141065f647"]},
      "expected": {"exit_code": 0, "tail_regex": "json-artifact-identical=0.*md-artifact-identical=0"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "(cd <scratch>/mut2-cap400 && TMPDIR=<scratch>/mut2-cap400/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics)",
      "cwd": "<scratch>/mut2-cap400",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["Ran 25 tests in 0.267s", "OK"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "lead_ruling", "level": "blocking", "text": "D6 same-signature recurrence: the cap-400 value-changing mutant survives because no test pins a >400-record result.", "needs": "Escalate under the stated D6 rule; do not treat as an ordinary fixture request."},
    {"id": "F2", "kind": "verification_gap", "level": "blocking", "text": "The checked-in artifacts record parent 6d30c105 while replay at HEAD records 6846363d; exact artifact replay therefore fails.", "needs": "Adjudicate provenance/reissue semantics before accepting the candidate."}
  ]
}
```

## Findings

1. **EXEC-R3-B1 — blocker.** The focused suite has no statistics fixture above eight records. A scratch mutation `ordered = sorted(values[:400])` passed all 25 tests but changed the retained-bundle result: DG-071 median/IQR became `120.9390 / 5.7079`, DG-075 `120.9391 / 5.7079`, and both statistic sample counts became 400. This is the mandatory D6 escalation signature.

2. **EXEC-R3-B2 — blocker.** Two replays are mutually byte-identical, but neither equals the committed JSON/Markdown. The only diff is `producer.git_commit`: committed artifacts contain `6d30c105…`; replay at required HEAD contains `6846363d…`. Script SHA matches. Thus the stated exact-hash D4 expectation fails.

3. **EXEC-R3-N1 — nit.** `golden_sha256` is used later, so it is not write-only; however, its immediately following hash assertion repeats the same literal rather than using the bound name.

## D1 — Golden bundle credibility

A fresh 17-line Decimal-only stdin script rebuilt all 24 CSV rows from the golden test literals, without importing or executing the producer. Its SHA was exactly:

```text
cc31866f096948d8af0e8c55f80a432086dfb753f907d52825fea00da9e2d58f
```

Output tail:

```text
DG071 sorted ['0.09900000', '0.09999995', '0.10000007', '0.10040005',
'0.10060005', '0.10099999', '0.10100039', '0.10200000']
h/q [('1.75', '0.1000000400'), ('3.5', '0.100500050'),
('5.25', '0.1010000900')] iqr 0.0010000500
render ['100.0000', '100.5000', '101.0001', '1.0000']

DG075 sorted ['0.09900020', '0.09999967', '0.09999995', '0.10059905',
'0.10100009', '0.10100069', '0.10200050']
h/q [('1.50', '0.0999998100'), ('3.0', '0.10059905'),
('4.50', '0.1010003900')] iqr 0.0010005800
render ['99.9998', '100.5990', '101.0004', '1.0006']

spacings ['0.09900020', '0.10100009', '0.09999995', '0.10200050',
'0.09999967', '0.10100069', '0.10059905']
gaps ['0.00000020', '-0.00000030', '0.00000000', '0.00000050',
'-0.00000040', '0.00000070', '-0.00000100'] max 0.00000100 nonzero 6
```

This reproduces every data-derived golden value, including the deliberately different rendered-IQR calculation. Static expected fields are contractual literals/prose, not claimed CSV derivations.

## D2 — Differential-reference independence

`_independent_reference` imports no producer helper or producer-defined constant. It has independent grouping, quantile, IQR, rendering, and tiling code; its only common pieces are standard-library `csv`, `Decimal`, and `ROUND_HALF_EVEN`. It does share the producer schema indirectly through the test fixture writer, so it is an independent arithmetic oracle, not an independent end-to-end contract oracle.

It does not catch:

- Invalid-input/refusal ordering, rail/schema/path/hash/git failures: differential inputs are valid. These can change refusal outcomes, not a valid issued digit.
- Metadata, method prose, Markdown/stdout, provenance, or output-path defects: it compares only numeric statistics and two tiling fields. These can alter published text/fields, but not a statistic digit through this oracle.
- Input-size-conditional behavior above eight records: the fixed-seed differential draws 2–8 records. This can change published digits; B1 demonstrates it.
- Some fixture-generation/schema coupling: reordered schema semantics can be hidden by producer-driven fixture headers; the full golden payload separately pins the emitted schema on its one case.

## D3 — Mutant replay

Baseline focused suite:

```text
Ran 25 tests in 0.279s

OK
```

All six requested mutants were independently applied to scratch copies with valid scratch Git repositories:

| Mutant | Result | Failing tests |
|---|---|---|
| half-even → half-up, including import | killed | `test_differential_against_independent_reference`; `test_golden_bundle_pins_every_reported_field`; `test_millisecond_rendering_ties_round_half_even_through_main` |
| drop `len(starts) != 1` | killed | `test_record_rail_set_mismatch_refusal_reaches_main` |
| rendered-quartile IQR | killed | differential; golden |
| nonzero count via tolerance | killed | differential; golden |
| drop `abs` | killed | differential; golden |
| `>` → `>=` tiling tolerance | killed | differential; golden; `test_precision_regression_uses_exact_epoch_literals` (refusal errors) |

My two requested additional mutants were also killed:

| Mutant | Result | Failing tests |
|---|---|---|
| Compute DG-075 from records 2–n widths rather than timestamp spacings | killed | differential; golden |
| Accept zero-width intervals (`<=` → `<`) | killed | `test_record_interval_not_positive_refusal_reaches_main` |

For D6, I additionally tested `sorted(values[:400])`. It survived: 25/25 passed while changing the issued retained-bundle fields shown in B1.

## D4 — Values of record

Both replays printed the required values:

```text
DG-071 median_ms=120.9186 iqr_ms=5.9508
DG-075 median_ms=120.9224 iqr_ms=5.8949
```

The full eight values and counts match the committed artifacts. Replays match each other byte-for-byte, but not the committed artifacts:

```text
replay JSON 02ad2e9b9b021a5754618cc5a687f68270877210a3a660697be4c867432f4187
replay MD   aea11b88670435c0befb0b5983ae6a705fc60da26090136f17776392741e5de5
artifact JSON dda89609054742b66501ef3acfe822a20e3e7da5d5882349f5d5b255ed7b0caf
artifact MD   a7bd11e5228716cd7242d3436ff2f7897e32869cf4d151220a1369141065f647
```

The only byte difference is the Git commit provenance. Current script SHA is the expected `c745bcf…5386`.

## D5 — Method-only replication

A fresh 26-line stdin script was written from the artifact’s `## Method` text alone; it did not import, read, or call the producer. It reproduced all values and header tiling fields:

```text
DG-071 n 406 seconds 0.116971950 0.12091860 0.122922700 0.005950750 ms 116.9720 120.9186 122.9227 5.9508
DG-075 n 405 seconds 0.1170321 0.1209224 0.122927 0.0058949 ms 117.0321 120.9224 122.9270 5.8949
tiling max 0.0000004 nonzero 100 boundaries 405
```

No prose sentence forced a guess. The type-7 reference and linear-interpolation wording adequately determine the integral-position case.

## D6 — Same-signature statement

**Yes: this round still exhibits the same signature, so this is an escalation rather than an ordinary fix request.** The full-payload golden pins reported fields only on an eight-record bundle, and the differential covers only 2–8 records; neither pins a result on an input where a plausible fixed-cap aggregation bug differs. The `[:400]` mutation passed all 25 tests but changed multiple published values and statistic sample counts on the 406-record retained bundle. This directly meets the stated definition: reported fields lack a value-pinning test on an input where the wrong computation differs.

## D7 — Prune check

No unreachable production code or write-only dataclass fields remain in the audited modules. The intentional method-text duplication across docstring, JSON disclosure, Markdown renderer, and golden expected payload is serving distinct outputs/assertions. The only cleanup nit is EXEC-R3-N1.

## Residual risk

The golden and differential give strong small-input coverage, but neither exercises real-bundle cardinality or a synthetic bundle above eight records. Exact artifact reproducibility is also unresolved because output provenance derives the live Git HEAD.

## What this audit did NOT check

I did not run the prohibited canonical discovery suite, edit the checkout, perform live hardware work, or exhaustively mutate every parser/refusal/output-path behavior.