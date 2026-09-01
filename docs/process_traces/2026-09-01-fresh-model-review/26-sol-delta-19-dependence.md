```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTE: the core fixes execute correctly, but the printed deltas do not reproduce seven worked-example values and F9 mutation coverage remains incomplete.",
  "workspace": {
    "base_requested": "HEAD",
    "base_mode": "exact",
    "head_start": "907f58773584dc28e3ee68d04ee5db7ca0cd269e",
    "head_end": "907f58773584dc28e3ee68d04ee5db7ca0cd269e",
    "upstream_end": "907f58773584dc28e3ee68d04ee5db7ca0cd269e",
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "REFUTE",
    "findings": [
      {
        "id": "N1",
        "severity": "blocker",
        "title": "The ten deltas printed in the worked example do not reproduce seven printed results."
      },
      {
        "id": "F9",
        "severity": "should_fix",
        "title": "Eleven of 24 audited mutations survive, and the golden test does not compare document numbers to document inputs."
      },
      {
        "id": "N2",
        "severity": "should_fix",
        "title": "Extreme finite numeric inputs escape the controlled refusal path with exit 1 and a traceback."
      },
      {
        "id": "N3",
        "severity": "nit",
        "title": "The document's fixed-alpha source line references are off by two lines."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_dependence_sensitivity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 12 tests in 7.778s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 12 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --example --alpha 0.10",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": ["dependence_sensitivity.py: error: unrecognized arguments: --alpha 0.10"]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "unrecognized arguments: --alpha 0\\.10"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "python3 -c 'from scripts import dependence_sensitivity as d; from joulewise.analysis_engine.estimators import PairedObservation,StochasticVarianceTerm,DeterministicBoundTerm,estimate_paired_blocks; x=d.analyze_deltas(d.EXAMPLE_BLOCK_DELTAS_J,floor_j=3.5,se_metrology_j=.2,deterministic_bound_total_j=4)[\"models\"][\"independent_blocks\"]; s=StochasticVarianceTerm(\"m\",0,.4,0); b=DeterministicBoundTerm(\"b\",0,0,4); e=estimate_paired_blocks(tuple(PairedObservation(str(i),0,v,(s,),(b,)) for i,v in enumerate(d.EXAMPLE_BLOCK_DELTAS_J))); pairs=[(x[\"metrology_aware_interval_j\"][\"lower\"],e.metrology_aware_ci95.lower),(x[\"metrology_aware_interval_j\"][\"upper\"],e.metrology_aware_ci95.upper),(x[\"decision_interval_j\"][\"lower\"],e.decision_interval.lower),(x[\"decision_interval_j\"][\"upper\"],e.decision_interval.upper)]; print(\"max_endpoint_diff=\",max(abs(a-b) for a,b in pairs),sep=\"\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["max_endpoint_diff=0.0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "max_endpoint_diff=0\\.0"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 2803 tests in 109.455s", "FAILED (errors=1787, skipped=114)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox provides no writable temporary directory. The canonical suite therefore failed broadly with FileNotFoundError from tempfile rather than yielding interpretable repository results; /tmp mutation copies were also impossible.",
      "needs": "Rerun the canonical suite in an environment with a writable temporary directory."
    }
  ]
}
```

## Delta table

| Finding | Result | Execution evidence |
|---|---|---|
| F1 | cured | Total composition uses `hypot(repeat, metrology)`, widens by the deterministic total, derives raw *p* from total SE, and applies strict direction to both intervals at [dependence_sensitivity.py:193](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:193), [dependence_sensitivity.py:198](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:198), [dependence_sensitivity.py:209](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:209), and [dependence_sensitivity.py:213](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:213). Engine parity is tested at [test_dependence_sensitivity.py:225](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:225). Executed endpoint difference: exactly `0.0`. |
| F2 | cured, with N3 | Alpha is fixed at [dependence_sensitivity.py:34](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:34); the parser has no alpha option at [dependence_sensitivity.py:378](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:378); rejection tests are at [test_dependence_sensitivity.py:409](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:409). Both `--alpha 0.05` and `0.10` exited 2 with empty stdout. |
| F3 | cured | Exact-ten enforcement is at [dependence_sensitivity.py:89](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:89), directly tested at [test_dependence_sensitivity.py:371](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:371) and through the CLI at [test_dependence_sensitivity.py:390](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:390). Executed \(n=9\) and \(n=11\): exit 2, zero stdout. |
| F4 | cured | New placements and STOP_FILL rules are at [dependence-sensitivity.md:99](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:99); existing placements remain unchanged at [dependence-sensitivity.md:110](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:110). The artifact emits both hashes and metrology values at [dependence_sensitivity.py:336](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:336), tested at [test_dependence_sensitivity.py:161](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:161). |
| F5 | cured | Inclusive Holm equality is explicit at [dependence-sensitivity.md:51](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:51) and locked by [test_dependence_sensitivity.py:194](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:194). |
| F6 | cured | Correct scenario name and both counterexamples appear at [dependence-sensitivity.md:49](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:49); the emitted description agrees at [dependence_sensitivity.py:313](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:313). |
| F7 | cured | The ratified H30 sentence is reproduced at [dependence-sensitivity.md:63](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:63), matching [retensing-plan.md:569](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/retensing-plan.md:569); literal regression test at [test_dependence_sensitivity.py:209](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:209). |
| F8 | cured | Required definitions precede the table at [dependence-sensitivity.md:7](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:7), [dependence-sensitivity.md:9](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:9), and [dependence-sensitivity.md:13](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:13); ordering is tested at [test_dependence_sensitivity.py:218](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:218). |
| F9 | not cured | The suite now covers the named refusal examples and key semantics, but 11 guard/CLI mutations survive. The “document-aligned” golden test hard-codes expectations at [test_dependence_sensitivity.py:61](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:61); its document-reading test at [test_dependence_sensitivity.py:187](/Users/edr/code/JouleWise-wt-dependence/tests/test_dependence_sensitivity.py:187) checks prose only, allowing N1. |

## Recomputation diff

Using the hidden full-precision constants at [dependence_sensitivity.py:44](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:44), the independent calculation matched all 62 compared document fields at their printed precision and matched `--example` at full floating precision.

Base quantities:

- Sum `49.999999999999`; mean `4.9999999999999`
- Squared deviations `20.250000000000295`; \(s=1.5000000000000109\)
- Rho numerator `4.657970807596104`; denominator `15.526569358646732`; \(\hat\rho=0.30000000000013427\)
- Nine terms: `0.270000000000121, 0.072000000000064, 0.018900000000025, 0.004860000000009, 0.001215000000003, 0.000291600000001, 0.000065610000000, 0.000013122000000, 0.000001968300000`

| Model | \(V\) | \(n_\text{eff}\), \(\nu\) | Repeat SE / interval | Total SE / critical / half-width | Metrology-aware; decision | \(t\); raw \(p\) |
|---|---:|---|---|---|---|---|
| Independent | 1 | 10, 9 | 0.474341649; `[3.927039190, 6.072960810]` | 0.514781507; 2.262; 1.164435769 | `[3.835564231, 6.164435769]`; `[-0.164435769, 10.164435769]` | 9.712858624; 0.000004557791 |
| AR(1) | 1.734694601 | 5.764703480, 4 | 0.624744976; `[3.265707946, 6.734292054]` | 0.655977351; 2.776; 1.820993127 | `[3.179006873, 6.820993127]`; `[-0.820993127, 10.820993127]` | 7.622214382; 0.001590617065 |
| Halving | 2 | 5, 4 | 0.670820393; `[3.137802588, 6.862197412]` | 0.700000000; 2.776; 1.943200000 | `[3.056800000, 6.943200000]`; `[-0.943200000, 10.943200000]` | 7.142857143; 0.002032095296 |

However, recomputing from the ten six-decimal values actually presented at [dependence-sensitivity.md:72](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:72) produces seven printed-precision differences:

| Field | From printed deltas | Document |
|---|---:|---:|
| Sum | 50.000002 | 50.000000 |
| Squared deviations | 20.250002 | 20.250000 |
| Rho denominator | 15.526573 | 15.526569 |
| AR \(V\) | 1.734694 | 1.734695 |
| AR \(n_\text{eff}\) | 5.764704 | 5.764703 |
| AR \(t\) | 7.622215 | 7.622214 |
| Halving repeat upper endpoint | 6.862198 | 6.862197 |

### Refusal execution

Every requested ordinary refusal returned exit 2 with empty stdout: \(n=9\), \(n=11\), NaN delta, constant sequence, \(|\hat\rho|=1\), both alpha values, negative floor, non-finite metrology SE, and negative deterministic total. `--example` emitted no key containing `holm`, `verdict`, or a final support/claim outcome.

### Engine parity

The independent model matched `estimate_paired_blocks` exactly for mean, \(s\), repeat/metrology/total SE, critical value, both composed intervals, deterministic total, *t*, and raw *p*. Feeding each model’s intervals to `claims.evaluate_claim(..., adjusted_rejected=True)` returned `not_resolvable` with `deterministic_bound_obscures_direction`, agreeing with all three script direction failures and the strict checks at [claims.py:362](/Users/edr/code/JouleWise-wt-dependence/joulewise/analysis_engine/claims.py:362).

### Mutation table

The committed 12-test suite passed under the in-memory baseline. Results:

| Mutation | Line | Result |
|---|---|---|
| Delete finite-type guard | [script:61](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:61) | **survived** |
| Delete non-finite guard | [script:64](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:64) | killed |
| Delete non-negative guard | [script:73](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:73) | killed |
| Delete delta-list type guard | [script:81](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:81) | **survived** |
| Delete exact-ten guard | [script:89](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:89) | killed |
| Delete rho-denominator guard | [script:102](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:102) | killed |
| Delete estimator rho-range guard | [script:109](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:109) | killed |
| Delete AR \(n\ge2\) guard | [script:121](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:121) | killed |
| Delete second rho-range guard | [script:124](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:124) | killed |
| Delete positive-finite \(V\) guard | [script:140](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:140) | **survived** |
| Delete positive-finite effective-\(n\) guard | [script:148](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:148) | **survived** |
| Delete minimum-df guard | [script:151](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:151) | killed |
| Delete interval-finiteness guard | [script:162](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:162) | **survived** |
| Delete decision-finiteness guard | [script:202](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:202) | **survived** |
| Delete test-evidence finiteness guard | [script:211](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:211) | **survived** |
| Delete example-exclusivity guard | [script:405](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:405) | **survived** |
| Delete missing-source guard | [script:422](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:422) | **survived** |
| Delete required-metrology guard | [script:426](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:426) | **survived** |
| Delete parsed-JSON-list guard | [script:373](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:373) | **survived** |
| Change alpha to 0.10 | [script:34](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:34) | killed |
| Drop metrology from total SE | [script:194](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:194) | killed |
| Do not widen decision interval | [script:198](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:198) | killed |
| Make direction boundary inclusive | [script:170](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:170) | killed |
| Emit a Holm verdict | [script:362](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:362) | killed |

Total: 13 killed, 11 survived.

## Findings

### N1 — BLOCKER — printed inputs do not reproduce the worked example

The prose says to use the six-decimal list at [dependence-sensitivity.md:69](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:69), then asserts incompatible arithmetic at [dependence-sensitivity.md:75](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:75), [dependence-sensitivity.md:79](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:79), and [dependence-sensitivity.md:81](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:81). The results instead come from hidden higher-precision constants. A reader rebuilding the example from the paper-facing input gets seven different printed values.

### F9 — SHOULD-FIX — mutation and document-agreement coverage remains incomplete

Eleven guard/CLI deletions remain green. More importantly, the golden test consumes the script’s hidden constants through `--example` and compares them with hard-coded expected numbers; it never extracts the document’s displayed deltas or numeric claims. Thus it certified the exact inconsistency in N1.

### N2 — SHOULD-FIX — overflow is not converted into a controlled refusal

`float(value)` at [dependence_sensitivity.py:63](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:63) and `math.fsum` at [dependence_sensitivity.py:276](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:276) can raise `OverflowError`, while the CLI catches only `ValueError` at [dependence_sensitivity.py:450](/Users/edr/code/JouleWise-wt-dependence/scripts/dependence_sensitivity.py:450). Ten `1e308` deltas and a 400-digit integer both produced exit 1, empty stdout, and a traceback instead of the calculator’s exit-2 refusal form.

### N3 — NIT — fixed-alpha citation line drift

[dependence-sensitivity.md:11](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:11) cites generator lines 1857 and 2576. The actual alpha fields are at [generate_configs.py:1859](/Users/edr/code/JouleWise-wt-dependence/configs/campaigns/d117_contrast_v5/generate_configs.py:1859) and [generate_configs.py:2578](/Users/edr/code/JouleWise-wt-dependence/configs/campaigns/d117_contrast_v5/generate_configs.py:2578).

## Residual risk

The full repository suite could not be interpreted under the read-only environment because Python had no writable temporary directory. Targeted tests, independent arithmetic, refusal execution, engine parity, claims parity, and in-memory mutation testing completed without repository writes. No measurement or `[QUIET-MAC]` command ran, and Claude was not called.

VERDICT: **REFUTE**